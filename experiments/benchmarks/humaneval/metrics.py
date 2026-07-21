from __future__ import annotations

from typing import Any, Sequence

from experiments.benchmarks.common import BenchmarkCase, BenchmarkPrediction

from .adapter import HumanEvalAdapter


def evaluate_humaneval_prediction(
    case: BenchmarkCase,
    prediction: str,
    variant: str = "baseline",
    *,
    execution_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if execution_result is None:
        return HumanEvalAdapter().evaluate_prediction(case, prediction, variant)
    return HumanEvalAdapter().evaluate_execution(
        case,
        extraction_status=str((execution_result or {}).get("extraction_status", "")),
        generated_code=prediction,
        execution_result=execution_result,
        variant=variant,
    )


def summarize_humaneval_predictions(
    predictions: Sequence[BenchmarkPrediction],
    cases: Sequence[BenchmarkCase] | None = None,
) -> dict[str, Any]:
    return HumanEvalAdapter().summarize_metrics(predictions, cases)

