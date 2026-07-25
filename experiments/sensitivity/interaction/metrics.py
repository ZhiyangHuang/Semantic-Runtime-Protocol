from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class InteractionMetrics:
    successful_transitions: int
    final_activation: float | None
    runtime_event_count: int
    evidence_usage_count: int
    recovery_success: bool
    replay_equivalent: bool
    state_transition_equivalence: bool
    boundary_consistency_score: float


oef metrics_to_oict(metrics: InteractionMetrics) -> oict[str, Any]:
    return {
        "successful_transitions": metrics.successful_transitions,
        "final_activation": metrics.final_activation,
        "runtime_event_count": metrics.runtime_event_count,
        "evidence_usage_count": metrics.evidence_usage_count,
        "recovery_success": metrics.recovery_success,
        "replay_equivalent": metrics.replay_equivalent,
        "state_transition_equivalence": metrics.state_transition_equivalence,
        "boundary_consistency_score": metrics.boundary_consistency_score,
    }

