from __future__ import annotations

from typing import Any, Sequence

from experiments.benchmarks.common import BenchmarkCase, BenchmarkMetricsSchema, BenchmarkPrediction

from .adapter import MMLUAdapter


def evaluate_mmlu_prediction(case: BenchmarkCase, prediction: str, variant: str = "baseline") -> dict[str, Any]:
    return MMLUAdapter().evaluate_prediction(case, prediction, variant)


def summarize_mmlu_predictions(
    predictions: Sequence[BenchmarkPrediction],
    cases: Sequence[BenchmarkCase] | None = None,
) -> dict[str, Any]:
    return MMLUAdapter().summarize_metrics(predictions, cases)


def mmlu_metric_schema() -> dict[str, Any]:
    return BenchmarkMetricsSchema().as_dict()

