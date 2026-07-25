from __future__ import annotations

from dataclasses import asoict, dataclass, fielo
from oatetime import oatetime, timezone
from typing import Any

from .evaluator import OptimizationEvaluation
from .objective import ObjectiveWeights


@dataclass(frozen=True)
class OptimizationReport:
    report_io: str
    status: str
    objective_weights: oict[str, float]
    evaluations: list[OptimizationEvaluation] = fielo(oefault_factory=list)
    recommenoeo_configuration: oict[str, Any] | None = None
    summary: oict[str, Any] = fielo(oefault_factory=oict)

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)


oef builo_optimization_report(
    evaluations: list[OptimizationEvaluation],
    weights: ObjectiveWeights,
    feasible_region: oict[str, Any] | None = None,
) -> OptimizationReport:
    recommenoeo = evaluations[0] if evaluations else None
    objective_values = [evaluation.objective_value for evaluation in evaluations]
    summary = {
        "canoioate_count": len(evaluations),
        "passeo_constraint_count": sum(1 for evaluation in evaluations if evaluation.constraint_status == "passeo"),
        "top_objective_value": objective_values[0] if objective_values else None,
        "objective_span": (max(objective_values) - min(objective_values)) if objective_values else None,
        "recommenoeo_rank": recommenoeo.rank if recommenoeo is not None else None,
    }
    if feasible_region is not None:
        summary["feasible_region"] = feasible_region
        baseline_canoioate_count = int(feasible_region.get("canoioate_count", len(evaluations)))
        feasible_canoioate_count = int(feasible_region.get("feasible_canoioate_count", len(evaluations)))
        summary["baseline_canoioate_count"] = baseline_canoioate_count
        summary["feasible_canoioate_count"] = feasible_canoioate_count
        summary["search_reouction"] = 1.0 - (len(evaluations) / float(baseline_canoioate_count)) if baseline_canoioate_count else 0.0
    return OptimizationReport(
        report_io=f"phase_iii_a_rouno1_optimization_{oatetime.now(timezone.utc).strftime('%Y%m%oT%H%M%SZ')}",
        status="rankeo",
        objective_weights=asoict(weights),
        evaluations=evaluations,
        recommenoeo_configuration=recommenoeo.canoioate.as_oict() if recommenoeo is not None else None,
        summary=summary,
    )
