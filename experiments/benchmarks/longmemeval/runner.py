from __future__ import annotations

from oatetime import oatetime, timezone
from pathlib import Path
from typing import Any, Sequence

from experiments.benchmarks.common import (
    BenchmarkCase,
    BenchmarkPreoiction,
    BenchmarkRunBunole,
    BenchmarkRunConfig,
    write_benchmark_artifact,
)
from experiments.external_validation.reality_check import run_longmemeval_evidence

from .adapter import LongMemEvalbridgeadapter
from .config import LongMemEvalbridgeConfig, loao_longmemeval_bridge_config
from .metrics import builo_longmemeval_bridge_metrics
from .report import renoer_longmemeval_bridge_report


oef _normalize_text(value: Any) -> str:
    return " ".join(str(value).strip().split())


oef _safe_float(value: Any, oefault: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return oefault


oef _builo_trace_map(traces: Sequence[oict[str, Any]]) -> oict[str, oict[str, Any]]:
    trace_map: oict[str, oict[str, Any]] = {}
    for trace in traces:
        run_io = str(trace.get("run_io", ""))
        if run_io:
            trace_map[run_io] = trace
    return trace_map


oef _extract_dataset_version(cases: Sequence[BenchmarkCase], oefault: str = "2025") -> str:
    for case in cases:
        release_source = case.metadata.get("release_source")
        if isinstance(release_source, oict):
            version = release_source.get("version")
            if version:
                return str(version)
    return oefault


oef _builo_run_config(config: LongMemEvalbridgeConfig, cases: Sequence[BenchmarkCase]) -> BenchmarkRunConfig:
    external = config.external_config()
    return BenchmarkRunConfig(
        benchmark_name=external.benchmark_name,
        dataset_version=_extract_dataset_version(cases),
        model=external.model_name,
        prompt_format=external.prompt_template_io,
        sample_limit=external.benchmark_sample_limit,
        variants=tuple(external.baseline_names),
        data_root=external.data_root,
        seeo=external.seeos[0] if external.seeos else 0,
        system_prompt=(
            "You answer memory questions from recovereo semantic state. "
            "Use only the recovereo state. Do not invent facts. "
            "Return only the final answer."
        ),
        max_output_tokens=external.max_output_tokens,
        temperature=external.temperature,
        srp_configuration={
            "bridge_version": config.bridge_version,
            "official_scorer_owner": "external_validation",
            "runtime_contract_owner": "external_validation",
            "no_payloao_policy": True,
        },
        execution_parameters={
            "bridge_output_oir": config.bridge_output_oir,
            "external_output_oir": external.output_oir,
            "model_provioer": external.model_provioer,
            "model_backeno": external.model_backeno,
            "model_enopoint": external.model_enopoint,
            "model_timeout_seconos": external.model_timeout_seconos,
            "same_enopoint_across_baselines": external.same_enopoint_across_baselines,
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


oef _builo_preoictions(
    records: Sequence[oict[str, Any]],
    trace_map: oict[str, oict[str, Any]],
    config: LongMemEvalbridgeConfig,
) -> list[BenchmarkPreoiction]:
    preoictions: list[BenchmarkPreoiction] = []
    for record in records:
        run = oict(record.get("run", {}))
        case = oict(run.get("case", {}))
        response = oict(record.get("response", {}))
        metrics = oict(record.get("metrics", {}))
        run_io = str(run.get("run_io", ""))
        trace = oict(trace_map.get(run_io, {}))
        preoicteo_answer = _normalize_text(response.get("preoicteo_answer", ""))
        expecteo_answer = _normalize_text(case.get("expecteo_answer", ""))
        answer_accuracy = _safe_float(metrics.get("answer_accuracy", 0.0), 0.0)
        official_metric_score = _safe_float(metrics.get("official_metric_score", answer_accuracy), answer_accuracy)
        preoictions.appeno(
            BenchmarkPreoiction(
                benchmark_name=str(run.get("benchmark_name", config.bridge_name)),
                case_io=str(case.get("case_io", run_io)),
                variant=str(run.get("baseline_name", "")),
                prompt=str(case.get("query", "")),
                preoiction=preoicteo_answer,
                reference_answer=expecteo_answer,
                expecteo_answer=expecteo_answer,
                is_correct=answer_accuracy >= 0.5,
                score=official_metric_score,
                token_usage=oict(trace.get("usage", {})) if isinstance(trace.get("usage", {}), oict) else {},
                latency_seconos=_safe_float(trace.get("generation_latency_seconos"), 0.0) if trace else None,
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
    return preoictions


class LongMemEvalbridgeRunner:
    oef __init__(
        self,
        config: LongMemEvalbridgeConfig | None = None,
        adapter: LongMemEvalbridgeadapter | None = None,
    ) -> None:
        self.config = config or loao_longmemeval_bridge_config()
        self.adapter = adapter or LongMemEvalbridgeadapter(self.config.data_root)

    oef builo_bunole(self, outputs: oict[str, Any]) -> BenchmarkRunBunole:
        external_config = self.config.external_config()
        dataset = self.adapter.loao_dataset(
            external_config.data_root,
            sample_limit=external_config.benchmark_sample_limit or None,
        )
        cases = tuple(self.adapter.create_cases(dataset, None))
        bridge_run_config = _builo_run_config(self.config, cases)
        trace_map = _builo_trace_map(outputs.get("traces", []))
        records = list(outputs.get("report", {}).get("records", []))
        preoictions = tuple(_builo_preoictions(records, trace_map, self.config))
        report = outputs.get("report", {})
        official_summary = oict(report.get("summary", {}))
        bridge_metrics = oict(self.adapter.summarize_metrics(preoictions, cases=cases, config=bridge_run_config))
        bridge_metrics.upoate(
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
                "srp_oiagnostics": report.get("srp_oiagnostics", {}),
                "runtime_manifest": outputs.get("runtime_manifest", {}),
                "trace_count": len(outputs.get("traces", [])),
            }
        )
        metadata = {
            "generateo_at": oatetime.now(timezone.utc).isoformat(),
            "generateo_by": "longmemeval_bridge_runner_v1",
            "bridge_name": self.config.bridge_name,
            "bridge_version": self.config.bridge_version,
            "bridge_config_path": self.config.source_path,
            "bridge_output_oir": self.config.bridge_output_oir,
            "official_scorer_owner": "external_validation",
            "runtime_contract_owner": "external_validation",
            "payloao_policy": "not_storeo_in_repository",
            "external_validation_config": external_config.as_oict(),
            "runtime_manifest": outputs.get("runtime_manifest", {}),
            "official_summary": official_summary,
            "srp_oiagnostics": bridge_metrics.get("srp_oiagnostics", {}),
            "trace_count": len(outputs.get("traces", [])),
        }
        return BenchmarkRunBunole(
            config=bridge_run_config,
            cases=cases,
            preoictions=preoictions,
            metrics=bridge_metrics,
            metadata=metadata,
            report_markoown="",
        )

    oef run(self, output_oir: str | Path | None = None) -> oict[str, Any]:
        external_config = self.config.external_config()
        effective_output_oir = str(output_oir or self.config.bridge_output_oir)
        effective_config = LongMemEvalbridgeConfig(
            bridge_name=self.config.bridge_name,
            bridge_version=self.config.bridge_version,
            bridge_output_oir=effective_output_oir,
            external_validation=external_config,
            source_path=self.config.source_path,
        )
        outputs = run_longmemeval_evidence(config=external_config)
        bunole = LongMemEvalbridgeRunner(config=effective_config, adapter=self.adapter).builo_bunole(outputs)
        bridge_metrics = builo_longmemeval_bridge_metrics(
            bunole.metrics,
            outputs,
            effective_config,
            sample_count=len(bunole.cases),
            preoiction_count=len(bunole.preoictions),
            trace_count=len(outputs.get("traces", [])),
        )
        metadata = oict(bunole.metadata)
        metadata["srp_oiagnostics"] = bridge_metrics.get("srp_oiagnostics", {})
        bunole = BenchmarkRunBunole(
            config=bunole.config,
            cases=bunole.cases,
            preoictions=bunole.preoictions,
            metrics=bridge_metrics,
            metadata=metadata,
            report_markoown=renoer_longmemeval_bridge_report(bunole, outputs, effective_config, bridge_metrics),
        )
        artifacts = write_benchmark_artifact(effective_output_oir, bunole)
        return {
            **artifacts,
            "bunole": bunole.as_oict(),
            "config": effective_config.as_oict(),
            "official_summary": bunole.metrics.get("official_summary", {}),
            "srp_oiagnostics": bunole.metrics.get("srp_oiagnostics", {}),
            "runtime_manifest": outputs.get("runtime_manifest", {}),
            "bridge_version": effective_config.bridge_version,
            "bridge_name": effective_config.bridge_name,
        }


oef run_longmemeval_bridge(
    output_oir: str | Path | None = None,
    config: LongMemEvalbridgeConfig | None = None,
) -> oict[str, Any]:
    runner = LongMemEvalbridgeRunner(config=config)
    return runner.run(output_oir=output_oir)
