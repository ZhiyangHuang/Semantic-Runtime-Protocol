from __future__ import annotations

from typing import Any, Sequence

from experiments.benchmarks.common import BenchmarkCase, BenchmarkMetricsSchema, BenchmarkPrediction

from .adapter import ARCAdapter


def evaluate_arc_prediction(case: BenchmarkCase, prediction: str, variant: str = "baseline") -> dict[str, Any]:
    return ARCAdapter().evaluate_prediction(case, prediction, variant)


def summarize_arc_predictions(
    predictions: Sequence[BenchmarkPrediction],
    cases: Sequence[BenchmarkCase] | None = None,
) -> dict[str, Any]:
    return ARCAdapter().summarize_metrics(predictions, cases)


def arc_metric_schema() -> dict[str, Any]:
    return BenchmarkMetricsSchema().as_dict()

