from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from experiments.benchmarks.common import BenchmarkPrediction, BenchmarkRunBundle, BenchmarkRunConfig
from experiments.benchmarks.common.metrics import summarize_prediction_records
from experiments.common.local_llm import build_local_client

from .adapter import HumanEvalAdapter
from .config import HumanEvalConfig, load_humaneval_config
from .executor import HumanEvalExecutionResult, HumanEvalExecutor
from .metrics import summarize_humaneval_predictions
from .report import render_humaneval_report


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class _LocalLLMBackend:
    def __init__(self) -> None:
        self.client = build_local_client()

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_output_tokens: int = 128,
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        return self.client.generate_with_usage(
            prompt=prompt,
            system_prompt=system_prompt,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
        )


def _build_run_config(config: HumanEvalConfig) -> BenchmarkRunConfig:
    return BenchmarkRunConfig(
        benchmark_name=config.benchmark_name,
        dataset_version=config.dataset_version,
        model=config.model,
        prompt_format=config.prompt_format,
        sample_limit=config.sample_limit,
        variants=config.variants,
        data_root=config.data_root,
        seed=config.seed,
        system_prompt=config.system_prompt,
        max_output_tokens=config.max_output_tokens,
        temperature=config.temperature,
        srp_configuration={
            "srp_mode": config.srp_mode,
            **dict(config.srp_configuration),
        },
        execution_parameters={
            "execution_timeout_seconds": config.execution_timeout_seconds,
            "execution_sandbox_policy": config.execution_sandbox_policy,
            "allow_network": config.allow_network,
            **dict(config.execution_parameters),
        },
        metadata=dict(config.metadata),
    )


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _build_execution_payloads(
    cases: Sequence[Any],
    predictions: Sequence[BenchmarkPrediction],
    execution_results: Sequence[HumanEvalExecutionResult],
) -> list[dict[str, Any]]:
    result_map = {(result.task_id, result.variant): result for result in execution_results}
    payloads: list[dict[str, Any]] = []
    for prediction in predictions:
        result = result_map.get((prediction.case_id, prediction.variant))
        payloads.append(
            {
                "task_id": prediction.case_id,
                "variant": prediction.variant,
                "passed": bool(result.passed) if result else bool(prediction.is_correct),
                "stdout": result.stdout if result else "",
                "stderr": result.stderr if result else "",
                "execution_time_seconds": result.execution_time_seconds if result else prediction.latency_seconds,
                "failure_category": result.failure_category if result else prediction.error,
                "failure_message": result.failure_message if result else prediction.error,
                "return_code": result.return_code if result else None,
                "sandbox_policy": result.sandbox_policy if result else "",
                "metadata": {
                    **(result.metadata if result else {}),
                    **prediction.metadata,
                },
            }
        )
    return payloads


def _write_humaneval_artifact(output_dir: str | Path, bundle: BenchmarkRunBundle, execution_results: Sequence[dict[str, Any]]) -> dict[str, str]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    config_path = output_path / "config.json"
    raw_predictions_path = output_path / "raw_predictions.jsonl"
    execution_results_path = output_path / "execution_results.json"
    metrics_path = output_path / "metrics.json"
    report_path = output_path / "report.md"
    metadata_path = output_path / "metadata.json"

    config_path.write_text(json.dumps(bundle.config.as_dict(), ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    with raw_predictions_path.open("w", encoding="utf-8") as handle:
        for prediction in bundle.predictions:
            handle.write(_canonical_json(prediction.as_dict()))
            handle.write("\n")

    execution_results_path.write_text(json.dumps(list(execution_results), ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    metrics_path.write_text(json.dumps(bundle.metrics, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    report_path.write_text(bundle.report_markdown or render_humaneval_report(bundle, list(execution_results)), encoding="utf-8")

    metadata = dict(bundle.metadata)
    metadata["artifact_hashes"] = {
        "config_json": _hash_file(config_path),
        "raw_predictions_jsonl": _hash_file(raw_predictions_path),
        "execution_results_json": _hash_file(execution_results_path),
        "metrics_json": _hash_file(metrics_path),
        "report_md": _hash_file(report_path),
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    return {
        "output_dir": str(output_path),
        "config_json": str(config_path),
        "raw_predictions_jsonl": str(raw_predictions_path),
        "execution_results_json": str(execution_results_path),
        "metrics_json": str(metrics_path),
        "report_md": str(report_path),
        "metadata_json": str(metadata_path),
    }


class HumanEvalRunner:
    def __init__(
        self,
        config: HumanEvalConfig | None = None,
        adapter: HumanEvalAdapter | None = None,
        backend: Any | None = None,
        executor: HumanEvalExecutor | None = None,
    ) -> None:
        self.config = config or load_humaneval_config()
        self.adapter = adapter or HumanEvalAdapter()
        self.backend = backend or _LocalLLMBackend()
        self.executor = executor or HumanEvalExecutor(
            timeout_seconds=self.config.execution_timeout_seconds,
            sandbox_policy=self.config.execution_sandbox_policy,
            allow_network=self.config.allow_network,
        )

    def _load_cases(self) -> list[Any]:
        dataset = self.adapter.load_dataset(
            data_root=self.config.data_root or None,
            sample_limit=self.config.sample_limit or None,
        )
        cases = self.adapter.create_cases(dataset, _build_run_config(self.config))
        if self.config.sample_limit and len(cases) > self.config.sample_limit:
            return cases[: self.config.sample_limit]
        return cases

    def _run_variant(self, case, variant: str) -> tuple[BenchmarkPrediction, HumanEvalExecutionResult]:
        prompt = self.adapter.build_prompt(case, variant, _build_run_config(self.config))
        leakage_validator = getattr(self.adapter, "validate_prompt_leakage", None)
        if callable(leakage_validator):
            leakage_validator(case, variant, prompt, _build_run_config(self.config))
        response = self.backend.generate(
            prompt=prompt,
            system_prompt=self.config.system_prompt,
            max_output_tokens=self.config.max_output_tokens,
            temperature=self.config.temperature,
        )
        generated_text = str(response.get("text", "")).strip()
        extracted_code, extraction_status = self.adapter.extract_code(generated_text)
        execution_result = self.executor.execute(
            task_id=case.case_id,
            variant=variant,
            generated_code=extracted_code,
            test_specification=str(case.metadata.get("test_specification", "")),
            metadata={
                "entry_point": case.metadata.get("entry_point", ""),
                "task_id": case.case_id,
                "prompt_digest": case.metadata.get("prompt_digest", ""),
            },
        )
        execution_payload = execution_result.as_dict()
        evaluation = self.adapter.evaluate_execution(
            case,
            extraction_status=extraction_status,
            generated_code=extracted_code,
            execution_result=execution_payload,
            variant=variant,
            config=_build_run_config(self.config),
        )
        return (
            BenchmarkPrediction(
                benchmark_name=case.benchmark_name,
                case_id=case.case_id,
                variant=variant,
                prompt=prompt,
                prediction=extracted_code,
                reference_answer=case.reference_answer,
                expected_answer=case.expected_answer,
                is_correct=evaluation.get("is_correct"),
                score=evaluation.get("score"),
                token_usage=dict(response.get("usage") or {}),
                latency_seconds=_safe_float(response.get("latency_seconds"), 0.0) if response.get("latency_seconds") is not None else None,
                error=evaluation.get("failure_category") or execution_payload.get("failure_category"),
                raw_response={
                    "generation": dict(response),
                    "execution_result": execution_payload,
                    "extraction_status": extraction_status,
                },
                metadata={
                    "evaluation": evaluation,
                    "model": response.get("model"),
                    "extraction_status": extraction_status,
                    "execution_result": execution_payload,
                    "task_metadata": dict(case.metadata),
                },
            ),
            execution_result,
        )

    def build_bundle(self) -> tuple[BenchmarkRunBundle, list[dict[str, Any]]]:
        cases = tuple(self._load_cases())
        predictions: list[BenchmarkPrediction] = []
        execution_results: list[HumanEvalExecutionResult] = []
        for case in cases:
            for variant in self.config.variants:
                prediction, execution_result = self._run_variant(case, variant)
                predictions.append(prediction)
                execution_results.append(execution_result)
        bundle_config = _build_run_config(self.config)
        shared_metrics = summarize_prediction_records(predictions)
        adapter_metrics = self.adapter.summarize_metrics(predictions, cases, bundle_config)
        metrics = {**shared_metrics, **adapter_metrics}
        metadata = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "humaneval_runner_v1",
            "benchmark_name": self.config.benchmark_name,
            "dataset_version": self.config.dataset_version,
            "model": self.config.model,
            "prompt_format": self.config.prompt_format,
            "runner_version": "humaneval_runner_v1",
            "executor_version": "humaneval_executor_v1",
            "execution_sandbox_policy": self.config.execution_sandbox_policy,
            "allow_network": self.config.allow_network,
            "execution_timeout_seconds": self.config.execution_timeout_seconds,
            "artifact_contract": {
                "files": [
                    "config.json",
                    "raw_predictions.jsonl",
                    "execution_results.json",
                    "metrics.json",
                    "metadata.json",
                    "report.md",
                ]
            },
            "execution_results_count": len(execution_results),
            "config": self.config.as_dict(),
        }
        bundle = BenchmarkRunBundle(
            config=bundle_config,
            cases=cases,
            predictions=tuple(predictions),
            metrics=metrics,
            metadata=metadata,
        )
        bundle = BenchmarkRunBundle(
            config=bundle.config,
            cases=bundle.cases,
            predictions=bundle.predictions,
            metrics=bundle.metrics,
            metadata=bundle.metadata,
            report_markdown=render_humaneval_report(bundle, [result.as_dict() for result in execution_results]),
        )
        return bundle, [result.as_dict() for result in execution_results]

    def run(self, output_dir: str | Path | None = None) -> dict[str, Any]:
        bundle, execution_results = self.build_bundle()
        effective_output_dir = str(output_dir or self.config.execution_parameters.get("output_dir") or Path("experiments") / "results" / "humaneval_full_v1")
        artifacts = _write_humaneval_artifact(effective_output_dir, bundle, execution_results)
        return {
            **artifacts,
            "bundle": bundle.as_dict(),
            "config": self.config.as_dict(),
            "execution_results": execution_results,
        }


def run_humaneval_benchmark(
    config: HumanEvalConfig | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    runner = HumanEvalRunner(config=config)
    return runner.run(output_dir=output_dir)


def write_humaneval_artifact(output_dir: str | Path, config: HumanEvalConfig | None = None) -> dict[str, Any]:
    runner = HumanEvalRunner(config=config)
    return runner.run(output_dir=output_dir)

