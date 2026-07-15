from __future__ import annotations

from typing import Any

from experiments.config import PhaseIIIAOptimizationConfig
from experiments.validation.phase_ii_boundary.model import FeasibleRegion, load_feasible_region

from .candidate import build_candidate_space_from_feasible_region, build_round1_candidate_space
from .evaluator import evaluate_candidate
from .objective import ObjectiveWeights
from .ranking import rank_candidate_evaluations
from .report import build_optimization_report


def run_phase_iii_a_round1_optimization(
    weights: ObjectiveWeights | None = None,
    config: PhaseIIIAOptimizationConfig | None = None,
    feasible_region: FeasibleRegion | dict[str, Any] | str | None = None,
) -> dict[str, Any]:
    if feasible_region is not None:
        region = feasible_region if isinstance(feasible_region, FeasibleRegion) else load_feasible_region(feasible_region)
        if config is not None:
            weights = weights or ObjectiveWeights(
                semantic_quality_weight=config.objective_semantic_weight,
                recovery_success_weight=config.objective_recovery_weight,
                resource_cost_weight=config.objective_resource_weight,
                instability_penalty_weight=config.objective_stability_weight,
            )
        else:
            weights = weights or ObjectiveWeights()
        candidates = build_candidate_space_from_feasible_region(region)
    elif config is not None:
        weights = weights or ObjectiveWeights(
            semantic_quality_weight=config.objective_semantic_weight,
            recovery_success_weight=config.objective_recovery_weight,
            resource_cost_weight=config.objective_resource_weight,
            instability_penalty_weight=config.objective_stability_weight,
        )
        candidates = build_round1_candidate_space(
            activation_thresholds=config.activation_threshold_values,
            recovery_min_evidence_values=config.recovery_min_evidence_values,
        )
    else:
        weights = weights or ObjectiveWeights()
        candidates = build_round1_candidate_space()
    evaluations = [evaluate_candidate(candidate, weights=weights) for candidate in candidates]
    ranked = rank_candidate_evaluations(evaluations)
    feasible_region_summary = region.as_dict() if feasible_region is not None else None
    report = build_optimization_report(ranked, weights, feasible_region=feasible_region_summary)
    return {
        "report": report.as_dict(),
        "candidates": [candidate.as_dict() for candidate in candidates],
        "feasible_region": feasible_region_summary,
    }
