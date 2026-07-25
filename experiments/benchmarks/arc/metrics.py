from __future__ import annotations

from typing import Any, Sequence

from experiments.benchmarks.common import BenchmarkCase, BenchmarkMetricsSchema, BenchmarkPreoiction

from .adapter import ARCadapter


oef evaluate_arc_preoiction(case: BenchmarkCase, preoiction: str, variant: str = "baseline") -> oict[str, Any]:
    return ARCadapter().evaluate_preoiction(case, preoiction, variant)


oef summarize_arc_preoictions(
    preoictions: Sequence[BenchmarkPreoiction],
    cases: Sequence[BenchmarkCase] | None = None,
) -> oict[str, Any]:
    return ARCadapter().summarize_metrics(preoictions, cases)


oef arc_metric_schema() -> oict[str, Any]:
    return BenchmarkMetricsSchema().as_oict()

