from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any

from srp_runtime.config import RuntimeConfig, load_default_profile
from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.operators.activation import ActivationUpdateOperator
from srp_runtime.operators.recovery import RecoveryOperator
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit

from .candidate import CandidateConfiguration
from .objective import ObjectiveWeights, calculate_objective


@dataclass(frozen=True)
class OptimizationMetrics:
    semantic_quality: float
    recovery_success: float
    resource_cost: float
    latency: float
    memory_overhead: float
    instability_penalty: float
    replay_equivalent: bool
    state_transition_equivalent: bool
    authority_preserved: bool
    evidence_consistent: bool

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OptimizationEvaluation:
    candidate: CandidateConfiguration
    objective_value: float
    metric_breakdown: dict[str, float]
    constraint_status: str
    rank: int | None = None
    tradeoff_summary: str = ""
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _state_signature(state: SemanticState) -> tuple[Any, ...]:
    unit_rows = []
    for unit_id in sorted(state.units):
        unit = state.units[unit_id]
        payload = {
            key: value
            for key, value in unit.semantic_payload.items()
            if not key.startswith("archived_") and key != "forgetting_evidence_refs"
        }
        unit_rows.append(
            (
                unit_id,
                unit.canonical_name,
                unit.activation,
                unit.confidence,
                unit.lifecycle_state,
                unit.decay_state,
                tuple(unit.provenance),
                tuple(unit.relation_ids),
                tuple(sorted(payload.items())),
            )
        )
    graph_rows = tuple(sorted((unit_id, tuple(sorted(neighbors))) for unit_id, neighbors in state.graph.relation_index.items()))
    return (state.version_id, state.timestamp_round, tuple(unit_rows), graph_rows)


def _build_activation_state() -> SemanticState:
    state = SemanticState(state_id="optimization:activation", version_id="v0", timestamp_round=1)
    state.units["u1"] = SemanticUnit(
        unit_id="u1",
        canonical_name="alpha",
        semantic_payload={"entity_type": "concept"},
        activation=0.4,
        confidence=0.5,
        version_id="v0",
    )
    return state


def _build_recovery_state() -> SemanticState:
    state = SemanticState(state_id="optimization:recovery", version_id="v0", timestamp_round=1)
    state.units["u1"] = SemanticUnit(
        unit_id="u1",
        canonical_name="beta",
        semantic_payload={"entity_type": "concept"},
        activation=0.2,
        confidence=0.5,
        lifecycle_state="approximated",
        version_id="v0",
    )
    return state


def _activation_event() -> RuntimeEvent:
    return RuntimeEvent(
        event_id="event:optimization:activation:1",
        event_type="ActivationUpdate",
        schema_version="1",
        causal_parent=None,
        actor="optimizer",
        targets=["u1"],
        payload={},
        mutation_mode="update",
        operator_name="ActivationUpdate",
    )


def _recovery_event(evidence_count: int) -> RuntimeEvent:
    evidence_refs = [f"ev:{index}" for index in range(1, evidence_count + 1)]
    return RuntimeEvent(
        event_id="event:optimization:recovery:1",
        event_type="Recovery",
        schema_version="1",
        causal_parent=None,
        actor="optimizer",
        targets=["u1"],
        payload={
            "target_unit_id": "u1",
            "evidence_refs": evidence_refs,
            "recovery_source": "lineage",
            "recovery_mode": "restore",
            "restored_lifecycle_state": "active",
            "restored_activation": 0.85,
            "restored_confidence": 0.75,
            "restored_provenance": ["ev:0"],
        },
        mutation_mode="update",
        operator_name="Recovery",
    )


def evaluate_candidate(
    candidate: CandidateConfiguration,
    weights: ObjectiveWeights | None = None,
) -> OptimizationEvaluation:
    weights = weights or ObjectiveWeights()
    runtime_config = RuntimeConfig(
        **{
            **asdict(load_default_profile()),
            "activation_threshold": candidate.activation_threshold,
            "recovery_min_evidence": candidate.recovery_min_evidence,
        }
    )

    activation_state = _build_activation_state()
    activation_replay_state = _build_activation_state()
    activation_operator = ActivationUpdateOperator()
    activation_operator.runtime_config = runtime_config
    activation_replay_operator = ActivationUpdateOperator()
    activation_replay_operator.runtime_config = runtime_config
    activation_transition = activation_operator.apply(activation_state, _activation_event())
    activation_replay_transition = activation_replay_operator.apply(activation_replay_state, _activation_event())

    recovery_state = _build_recovery_state()
    recovery_replay_state = _build_recovery_state()
    recovery_operator = RecoveryOperator()
    recovery_operator.runtime_config = runtime_config
    recovery_replay_operator = RecoveryOperator()
    recovery_replay_operator.runtime_config = runtime_config
    recovery_event = _recovery_event(2)
    recovery_transition = recovery_operator.apply(recovery_state, recovery_event)
    recovery_replay_transition = recovery_replay_operator.apply(recovery_replay_state, recovery_event)

    final_activation = float(activation_state.units["u1"].activation)
    recovery_success = 1.0 if recovery_transition.success else 0.0
    resource_cost = round(
        0.5 * ((candidate.activation_threshold - 0.3) / 0.5)
        + 0.5 * ((candidate.recovery_min_evidence - 1) / 2.0),
        6,
    )
    latency = round(0.1 + (candidate.activation_threshold * 0.05) + (candidate.recovery_min_evidence * 0.03), 6)
    memory_overhead = round(0.05 + (0.02 * candidate.recovery_min_evidence), 6)
    replay_equivalent = _state_signature(activation_state) == _state_signature(activation_replay_state) and _state_signature(recovery_state) == _state_signature(recovery_replay_state)
    state_transition_equivalent = (
        activation_transition.success == activation_replay_transition.success
        and recovery_transition.success == recovery_replay_transition.success
    )
    authority_preserved = replay_equivalent and state_transition_equivalent
    evidence_consistent = len(recovery_transition.mutation_summary.get("evidence_refs", [])) > 0
    instability_penalty = 0.0 if replay_equivalent and authority_preserved and evidence_consistent else 1.0
    objective_value = calculate_objective(
        semantic_quality=final_activation,
        recovery_success=recovery_success,
        resource_cost=resource_cost,
        instability_penalty=instability_penalty,
        weights=weights,
    )
    constraint_status = "passed" if replay_equivalent and state_transition_equivalent and authority_preserved and evidence_consistent else "failed"
    return OptimizationEvaluation(
        candidate=candidate,
        objective_value=objective_value,
        metric_breakdown={
            "semantic_quality": final_activation,
            "recovery_success": recovery_success,
            "resource_cost": resource_cost,
            "latency": latency,
            "memory_overhead": memory_overhead,
            "instability_penalty": instability_penalty,
        },
        constraint_status=constraint_status,
        tradeoff_summary=(
            f"activation={candidate.activation_threshold:.1f}, "
            f"recovery_min_evidence={candidate.recovery_min_evidence}, "
            f"recovery_success={recovery_success:.1f}, "
            f"resource_cost={resource_cost:.3f}"
        ),
        notes=[
            "constrained optimization round 1",
            "candidate evaluated inside validated feasible region",
        ],
    )

