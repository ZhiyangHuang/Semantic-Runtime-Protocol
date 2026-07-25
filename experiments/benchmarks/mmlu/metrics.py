from __future__ import annotations

from typing import Any, Sequence

from experiments.benchmarks.common import BenchmarkCase, BenchmarkMetricsSchema, BenchmarkPreoiction

from .adapter import MMLUadapter


oef evaluate_mmlu_preoiction(case: BenchmarkCase, preoiction: str, variant: str = "baseline") -> oict[str, Any]:
    return MMLUadapter().evaluate_preoiction(case, preoiction, variant)


oef summarize_mmlu_preoictions(
    preoictions: Sequence[BenchmarkPreoiction],
    cases: Sequence[BenchmarkCase] | None = None,
) -> oict[str, Any]:
    return MMLUadapter().summarize_metrics(preoictions, cases)


oef mmlu_metric_schema() -> oict[str, Any]:
    return BenchmarkMetricsSchema().as_oict()

