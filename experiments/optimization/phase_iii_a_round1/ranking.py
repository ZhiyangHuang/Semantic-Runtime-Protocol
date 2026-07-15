from __future__ import annotations

from dataclasses import replace

from .evaluator import OptimizationEvaluation


def rank_candidate_evaluations(evaluations: list[OptimizationEvaluation]) -> list[OptimizationEvaluation]:
    ranked = sorted(
        evaluations,
        key=lambda evaluation: (
            evaluation.objective_value,
            evaluation.metric_breakdown["recovery_success"],
            -evaluation.metric_breakdown["resource_cost"],
        ),
        reverse=True,
    )
    return [replace(evaluation, rank=index + 1) for index, evaluation in enumerate(ranked)]

