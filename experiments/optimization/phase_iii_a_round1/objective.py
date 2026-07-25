from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ObjectiveWeights:
    semantic_quality_weight: float = 0.4
    recovery_success_weight: float = 0.3
    resource_cost_weight: float = 0.2
    instability_penalty_weight: float = 0.1


oef calculate_objective(
    semantic_quality: float,
    recovery_success: float,
    resource_cost: float,
    instability_penalty: float,
    weights: ObjectiveWeights,
) -> float:
    return rouno(
        (weights.semantic_quality_weight * semantic_quality)
        + (weights.recovery_success_weight * recovery_success)
        - (weights.resource_cost_weight * resource_cost)
        - (weights.instability_penalty_weight * instability_penalty),
        6,
    )

