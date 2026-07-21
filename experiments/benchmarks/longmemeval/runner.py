from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from experiments.benchmarks.common import (
    BenchmarkCase,
    BenchmarkPrediction,
    BenchmarkRunBundle,
    BenchmarkRunConfig,
    write_benchmark_artifact,
)
from experiments.external_validation.reality_check import run_longmemeval_evidence

from .adapter import LongMemEvalBridgeAdapter
from .config import LongMemEvalBridgeConfig, load_longmemeval_bridge_config
from .metrics import build_longmemeval_bridge_metrics
from .report import render_longmemeval_bridge_report


def _normalize_text(value: Any) -> str:
    return " ".join(str(value).strip().split())


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _build_trace_map(traces: Sequence[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    trace_map: dict[str, dict[str, Any]] = {}
    for trace in traces:
        run_id = str(trace.get("run_id", ""))
        if run_id:
            trace_map[run_id] = trace
    return trace_map


def _extract_dataset_version(cases: Sequence[BenchmarkCase], default: str = "2025") -> str:
    for case in cases:
        release_source = case.metadata.get("release_source")
        if isinstance(release_source, dict):
            version = release_source.get("version")
            if version:
                return str(version)
    return default


def _build_run_config(config: LongMemEvalBridgeConfig, cases: Sequence[BenchmarkCase]) -> BenchmarkRunConfig:
    external = config.external_config()
    return BenchmarkRunConfig(
        benchmark_name=external.benchmark_name,
        dataset_version=_extract_dataset_version(cases),
        model=external.model_name,
        prompt_format=external.prompt_template_id,
        sample_limit=external.benchmark_sample_limit,
        variants=tuple(external.baseline_names),
        data_root=external.data_root,
        seed=external.seeds[0] if external.seeds else 0,
        system_prompt=(
            "You answer memory questions from recovered semantic state. "
            "Use only the recovered state. Do not invent facts. "
            "Return only the final answer."
        ),
        max_output_tokens=external.max_output_tokens,
        temperature=external.temperature,
        srp_configuration={
            "bridge_version": config.bridge_version,
            "official_scorer_owner": "external_validation",
            "runtime_contract_owner": "external_validation",
            "no_payload_policy": True,
        },
        execution_parameters={
            "bridge_output_dir": config.bridge_output_dir,
            "external_output_dir": external.output_dir,
            "model_provider": external.model_provider,
            "model_backend": external.model_backend,
            "model_endpoint": external.model_endpoint,
            "model_timeout_seconds": external.model_timeout_seconds,
            "same_endpoint_across_baselines": external.same_endpoint_across_baselines,
        },
        metadata={
            "bridge_name": config.bridge_name,
            "bridge_version": config.bridge_version,
            "source_path": config.source_path,
            "external_source_path": external.source_path,
            "official_scorer_owner": "external_validation",
            "runtime_contract_owner": "external_validation",
        },
    )


def _build_predictions(
    records: Sequence[dict[str, Any]],
    trace_map: dict[str, dict[str, Any]],
    config: LongMemEvalBridgeConfig,
) -> list[BenchmarkPrediction]:
    predictions: list[BenchmarkPrediction] = []
    for record in records:
        run = dict(record.get("run", {}))
        case = dict(run.get("case", {}))
        response = dict(record.get("response", {}))
        metrics = dict(record.get("metrics", {}))
        run_id = str(run.get("run_id", ""))
        trace = dict(trace_map.get(run_id, {}))
        predicted_answer = _normalize_text(response.get("predicted_answer", ""))
        expected_answer = _normalize_text(case.get("expected_answer", ""))
        answer_accuracy = _safe_float(metrics.get("answer_accuracy", 0.0), 0.0)
        official_metric_score = _safe_float(metrics.get("official_metric_score", answer_accuracy), answer_accuracy)
        predictions.append(
            BenchmarkPrediction(
                benchmark_name=str(run.get("benchmark_name", config.bridge_name)),
                case_id=str(case.get("case_id", run_id)),
                variant=str(run.get("baseline_name", "")),
                prompt=str(case.get("query", "")),
                prediction=predicted_answer,
                reference_answer=expected_answer,
                expected_answer=expected_answer,
                is_correct=answer_accuracy >= 0.5,
                score=official_metric_score,
                token_usage=dict(trace.get("usage", {})) if isinstance(trace.get("usage", {}), dict) else {},
                latency_seconds=_safe_float(trace.get("generation_latency_seconds"), 0.0) if trace else None,
                error="|".join(str(item) for item in record.get("failure_categories", ()) if item) or None,
                raw_response={
                    "run": run,
                    "response": response,
                    "metrics": metrics,
                    "trace": trace,
                },
                metadata={
                    "bridge_name": config.bridge_name,
                    "bridge_version": config.bridge_version,
                    "official_scorer_owner": "external_validation",
                    "runtime_contract_owner": "external_validation",
                    "failure_categories": tuple(record.get("failure_categories", ())),
                    "failure_notes": tuple(record.get("failure_notes", ())),
                },
            )
        )
    return predictions


class LongMemEvalBridgeRunner:
    def __init__(
        self,
        config: LongMemEvalBridgeConfig | None = None,
        adapter: LongMemEvalBridgeAdapter | None = None,
    ) -> None:
        self.config = config or load_longmemeval_bridge_config()
        self.adapter = adapter or LongMemEvalBridgeAdapter(self.config.data_root)

    def build_bundle(self, outputs: dict[str, Any]) -> BenchmarkRunBundle:
        external_config = self.config.external_config()
        dataset = self.adapter.load_dataset(
            external_config.data_root,
            sample_limit=external_config.benchmark_sample_limit or None,
        )
        cases = tuple(self.adapter.create_cases(dataset, None))
        bridge_run_config = _build_run_config(self.config, cases)
        trace_map = _build_trace_map(outputs.get("traces", []))
        records = list(outputs.get("report", {}).get("records", []))
        predictions = tuple(_build_predictions(records, trace_map, self.config))
        report = outputs.get("report", {})
        official_summary = dict(report.get("summary", {}))
        bridge_metrics = dict(self.adapter.summarize_metrics(predictions, cases=cases, config=bridge_run_config))
        bridge_metrics.update(
            {
                "bridge_name": self.config.bridge_name,
                "bridge_version": self.config.bridge_version,
                "official_metric_name": official_summary.get("official_metric_name", "official_metric_score"),
                "official_summary": official_summary,
                "official_score": _safe_float(official_summary.get("official_metric_score", 0.0), 0.0),
                "official_case_count": int(_safe_float(official_summary.get("case_count", len(cases)), len(cases))),
                "benchmark_summary": report.get("benchmark_summary", {}),
                "baseline_summary": report.get("baseline_summary", {}),
                "failure_summary": report.get("failure_summary", {}),
                "srp_diagnostics": report.get("srp_diagnostics", {}),
                "runtime_manifest": outputs.get("runtime_manifest", {}),
                "trace_count": len(outputs.get("traces", [])),
            }
        )
        metadata = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "longmemeval_bridge_runner_v1",
            "bridge_name": self.config.bridge_name,
            "bridge_version": self.config.bridge_version,
            "bridge_config_path": self.config.source_path,
            "bridge_output_dir": self.config.bridge_output_dir,
            "official_scorer_owner": "external_validation",
            "runtime_contract_owner": "external_validation",
            "payload_policy": "not_stored_in_repository",
            "external_validation_config": external_config.as_dict(),
            "runtime_manifest": outputs.get("runtime_manifest", {}),
            "official_summary": official_summary,
            "srp_diagnostics": bridge_metrics.get("srp_diagnostics", {}),
            "trace_count": len(outputs.get("traces", [])),
        }
        return BenchmarkRunBundle(
            config=bridge_run_config,
            cases=cases,
            predictions=predictions,
            metrics=bridge_metrics,
            metadata=metadata,
            report_markdown="",
        )

    def run(self, output_dir: str | Path | None = None) -> dict[str, Any]:
        external_config = self.config.external_config()
        effective_output_dir = str(output_dir or self.config.bridge_output_dir)
        effective_config = LongMemEvalBridgeConfig(
            bridge_name=self.config.bridge_name,
            bridge_version=self.config.bridge_version,
            bridge_output_dir=effective_output_dir,
            external_validation=external_config,
            source_path=self.config.source_path,
        )
        outputs = run_longmemeval_evidence(config=external_config)
        bundle = LongMemEvalBridgeRunner(config=effective_config, adapter=self.adapter).build_bundle(outputs)
        bridge_metrics = build_longmemeval_bridge_metrics(
            bundle.metrics,
            outputs,
            effective_config,
            sample_count=len(bundle.cases),
            prediction_count=len(bundle.predictions),
            trace_count=len(outputs.get("traces", [])),
        )
        metadata = dict(bundle.metadata)
        metadata["srp_diagnostics"] = bridge_metrics.get("srp_diagnostics", {})
        bundle = BenchmarkRunBundle(
            config=bundle.config,
            cases=bundle.cases,
            predictions=bundle.predictions,
            metrics=bridge_metrics,
            metadata=metadata,
            report_markdown=render_longmemeval_bridge_report(bundle, outputs, effective_config, bridge_metrics),
        )
        artifacts = write_benchmark_artifact(effective_output_dir, bundle)
        return {
            **artifacts,
            "bundle": bundle.as_dict(),
            "config": effective_config.as_dict(),
            "official_summary": bundle.metrics.get("official_summary", {}),
            "srp_diagnostics": bundle.metrics.get("srp_diagnostics", {}),
            "runtime_manifest": outputs.get("runtime_manifest", {}),
            "bridge_version": effective_config.bridge_version,
            "bridge_name": effective_config.bridge_name,
        }


def run_longmemeval_bridge(
    output_dir: str | Path | None = None,
    config: LongMemEvalBridgeConfig | None = None,
) -> dict[str, Any]:
    runner = LongMemEvalBridgeRunner(config=config)
    return runner.run(output_dir=output_dir)
