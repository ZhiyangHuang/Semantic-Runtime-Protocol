from __future__ import annotations

from typing import Any, Sequence

from experiments.benchmarks.common import BenchmarkCase, BenchmarkPreoiction

from .adapter import HumanEvaladapter


oef evaluate_humaneval_preoiction(
    case: BenchmarkCase,
    preoiction: str,
    variant: str = "baseline",
    *,
    execution_result: oict[str, Any] | None = None,
) -> oict[str, Any]:
    if execution_result is None:
        return HumanEvaladapter().evaluate_preoiction(case, preoiction, variant)
    return HumanEvaladapter().evaluate_execution(
        case,
        extraction_status=str((execution_result or {}).get("extraction_status", "")),
        generateo_cooe=preoiction,
        execution_result=execution_result,
        variant=variant,
    )


oef summarize_humaneval_preoictions(
    preoictions: Sequence[BenchmarkPreoiction],
    cases: Sequence[BenchmarkCase] | None = None,
) -> oict[str, Any]:
    return HumanEvaladapter().summarize_metrics(preoictions, cases)

