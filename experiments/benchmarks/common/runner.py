from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from .artifact import write_benchmark_artifact
from .metrics import summarize_prediction_records
from .report import render_benchmark_report
from .safety import assert_no_prompt_leakage
from .schema import (
    BenchmarkAdapter,
    BenchmarkCase,
    BenchmarkGenerationBackend,
    BenchmarkPrediction,
    BenchmarkRunBundle,
    BenchmarkRunConfig,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class BenchmarkRunner:
    def __init__(
        self,
        adapter: BenchmarkAdapter,
        backend: BenchmarkGenerationBackend,
        config: BenchmarkRunConfig,
    ) -> None:
        self.adapter = adapter
        self.backend = backend
        self.config = config

    def _load_cases(self) -> list[BenchmarkCase]:
        dataset = self.adapter.load_dataset(
            data_root=self.config.data_root or None,
            sample_limit=self.config.sample_limit or None,
        )
        cases = self.adapter.create_cases(dataset, self.config)
        if self.config.sample_limit and len(cases) > self.config.sample_limit:
            return cases[: self.config.sample_limit]
        return cases

    def _run_variant(self, case: BenchmarkCase, variant: str) -> BenchmarkPrediction:
        prompt = self.adapter.build_prompt(case, variant, self.config)
        leakage_validator = getattr(self.adapter, "validate_prompt_leakage", None)
        if callable(leakage_validator):
            leakage_validator(case, variant, prompt, self.config)
        else:
            assert_no_prompt_leakage(prompt)
        try:
            response = self.backend.generate(
                prompt=prompt,
                system_prompt=self.config.system_prompt,
                max_output_tokens=self.config.max_output_tokens,
                temperature=self.config.temperature,
            )
            prediction_text = str(response.get("text", "")).strip()
            evaluation = self.adapter.evaluate_prediction(case, prediction_text, variant, self.config) or {}
            return BenchmarkPrediction(
                benchmark_name=case.benchmark_name,
                case_id=case.case_id,
                variant=variant,
                prompt=prompt,
                prediction=prediction_text,
                reference_answer=case.reference_answer,
                expected_answer=case.expected_answer,
                is_correct=evaluation.get("is_correct"),
                score=evaluation.get("score"),
                token_usage=dict(response.get("usage") or {}),
                latency_seconds=float(response.get("latency_seconds", 0.0)) if response.get("latency_seconds") is not None else None,
                raw_response=dict(response),
                metadata={
                    "evaluation": evaluation,
                    "model": response.get("model"),
                },
            )
        except Exception as exc:
            evaluation = self.adapter.evaluate_prediction(case, "", variant, self.config) or {}
            return BenchmarkPrediction(
                benchmark_name=case.benchmark_name,
                case_id=case.case_id,
                variant=variant,
                prompt=prompt,
                prediction="",
                reference_answer=case.reference_answer,
                expected_answer=case.expected_answer,
                is_correct=False if evaluation.get("is_correct") is None else evaluation.get("is_correct"),
                score=evaluation.get("score"),
                error=str(exc),
                metadata={
                    "evaluation": evaluation,
                    "model": self.config.model,
                },
            )

    def run(self) -> BenchmarkRunBundle:
        cases = self._load_cases()
        predictions = tuple(
            self._run_variant(case, variant)
            for case in cases
            for variant in self.config.variants
        )
        adapter_metrics = self.adapter.summarize_metrics(predictions, cases, self.config)
        shared_metrics = summarize_prediction_records(predictions)
        metrics = {**shared_metrics, **adapter_metrics}
        metadata = {
            "benchmark_name": self.config.benchmark_name,
            "dataset_version": self.config.dataset_version,
            "adapter_name": getattr(self.adapter, "name", self.config.benchmark_name),
            "generated_at": _utc_now_iso(),
            "runner_version": "benchmark_runner_v1",
            "sample_count": len(cases),
            "variant_count": len(self.config.variants),
            "model": self.config.model,
            "prompt_format": self.config.prompt_format,
            "seed": self.config.seed,
            "srp_configuration": dict(self.config.srp_configuration),
            "execution_parameters": dict(self.config.execution_parameters),
            "config": self.config.as_dict(),
        }
        bundle = BenchmarkRunBundle(
            config=replace(self.config),
            cases=tuple(cases),
            predictions=predictions,
            metrics=metrics,
            metadata=metadata,
        )
        bundle = BenchmarkRunBundle(
            config=bundle.config,
            cases=bundle.cases,
            predictions=bundle.predictions,
            metrics=bundle.metrics,
            metadata=bundle.metadata,
            report_markdown=render_benchmark_report(bundle),
        )
        return bundle

    def run_and_write(self, output_dir: str | Path) -> dict[str, str]:
        bundle = self.run()
        return write_benchmark_artifact(output_dir, bundle)
