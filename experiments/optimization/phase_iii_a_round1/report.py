from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from .evaluator import OptimizationEvaluation
from .objective import ObjectiveWeights


@dataclass(frozen=True)
class OptimizationReport:
    report_id: str
    status: str
    objective_weights: dict[str, float]
    evaluations: list[OptimizationEvaluation] = field(default_factory=list)
    recommended_configuration: dict[str, Any] | None = None
    summary: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_optimization_report(
    evaluations: list[OptimizationEvaluation],
    weights: ObjectiveWeights,
    feasible_region: dict[str, Any] | None = None,
) -> OptimizationReport:
    recommended = evaluations[0] if evaluations else None
    objective_values = [evaluation.objective_value for evaluation in evaluations]
    summary = {
        "candidate_count": len(evaluations),
        "passed_constraint_count": sum(1 for evaluation in evaluations if evaluation.constraint_status == "passed"),
        "top_objective_value": objective_values[0] if objective_values else None,
        "objective_span": (max(objective_values) - min(objective_values)) if objective_values else None,
        "recommended_rank": recommended.rank if recommended is not None else None,
    }
    if feasible_region is not None:
        summary["feasible_region"] = feasible_region
        baseline_candidate_count = int(feasible_region.get("candidate_count", len(evaluations)))
        feasible_candidate_count = int(feasible_region.get("feasible_candidate_count", len(evaluations)))
        summary["baseline_candidate_count"] = baseline_candidate_count
        summary["feasible_candidate_count"] = feasible_candidate_count
        summary["search_reduction"] = 1.0 - (len(evaluations) / float(baseline_candidate_count)) if baseline_candidate_count else 0.0
    return OptimizationReport(
        report_id=f"phase_iii_a_round1_optimization_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        status="ranked",
        objective_weights=asdict(weights),
        evaluations=evaluations,
        recommended_configuration=recommended.candidate.as_dict() if recommended is not None else None,
        summary=summary,
    )
