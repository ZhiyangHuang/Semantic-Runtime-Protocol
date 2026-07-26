from __future__ import annotations

from dataclasses import asdict
from typing import Any, Iterable

from srp_runtime.config import RuntimeConfig, load_default_profile
from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.operators.activation import ActivationUpdateOperator
from srp_runtime.operators.recovery import RecoveryOperator
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit

from .config import InteractionExperimentConfig
from .metrics import InteractionMetrics, metrics_to_dict


def build_interaction_state() -> SemanticState:
    state = SemanticState(state_id="interaction:activation_recovery", version_id="v0", timestamp_round=1)
    state.units["u1"] = SemanticUnit(
        unit_id="u1",
        canonical_name="alpha",
        semantic_payload={"entity_type": "concept"},
        activation=0.4,
        confidence=0.5,
        version_id="v0",
    )
    state.units["u2"] = SemanticUnit(
        unit_id="u2",
        canonical_name="beta",
        semantic_payload={"entity_type": "concept"},
        activation=0.2,
        confidence=0.6,
        lifecycle_state="approximated",
        version_id="v0",
    )
    return state


def build_activation_event() -> RuntimeEvent:
    return RuntimeEvent(
        event_id="event:interaction:activation:1",
        event_type="ActivationUpdate",
        schema_version="1",
        causal_parent=None,
        actor="tester",
        targets=["u1"],
        payload={},
        mutation_mode="update",
        operator_name="ActivationUpdate",
    )


def build_recovery_event() -> RuntimeEvent:
    return RuntimeEvent(
        event_id="event:interaction:recovery:1",
        event_type="Recovery",
        schema_version="1",
        causal_parent="event:interaction:activation:1",
        actor="tester",
        targets=["u2"],
        payload={
            "evidence_refs": ["ev:1", "ev:2"],
            "recovery_source": "lineage",
            "recovery_mode": "restore",
            "restored_lifecycle_state": "active",
            "restored_activation": 0.8,
            "restored_confidence": 0.7,
            "restored_provenance": ["ev:0"],
        },
        mutation_mode="update",
        operator_name="Recovery",
    )


def _state_signature(state: SemanticState) -> tuple[Any, ...]:
    rows = []
    for unit_id in sorted(state.units):
        unit = state.units[unit_id]
        rows.append(
            (
                unit_id,
                unit.activation,
                unit.confidence,
                unit.lifecycle_state,
                unit.decay_state,
                tuple(unit.provenance),
                tuple(unit.relation_ids),
            )
        )
    return (state.version_id, state.timestamp_round, tuple(rows))


def _apply_interaction_sequence(
    state: SemanticState,
    runtime_config: RuntimeConfig,
) -> tuple[Any, Any, SemanticState]:
    activation_operator = ActivationUpdateOperator()
    activation_operator.runtime_config = runtime_config
    recovery_operator = RecoveryOperator()
    recovery_operator.runtime_config = runtime_config

    activation_transition = activation_operator.apply(state, build_activation_event())
    recovery_transition = recovery_operator.apply(state, build_recovery_event())
    return activation_transition, recovery_transition, state


def _boundary_consistency_score(
    *,
    activation_boundary_preserved: bool,
    recovery_boundary_preserved: bool,
    replay_equivalent: bool,
) -> float:
    score = 0.0
    score += 1.0 if activation_boundary_preserved else 0.0
    score += 1.0 if recovery_boundary_preserved else 0.0
    score += 1.0 if replay_equivalent else 0.0
    return score / 3.0


def run_activation_recovery_cell(
    activation_threshold: float,
    recovery_min_evidence: int,
    *,
    baseline: RuntimeConfig | None = None,
) -> dict[str, Any]:
    runtime_config = baseline or load_default_profile()
    runtime_config = RuntimeConfig(
        **{
            **asdict(runtime_config),
            "activation_threshold": activation_threshold,
            "recovery_min_evidence": recovery_min_evidence,
        }
    )
    direct_state = build_interaction_state()
    activation_transition, recovery_transition, direct_state = _apply_interaction_sequence(direct_state, runtime_config)

    replay_state = build_interaction_state()
    replay_activation_transition, replay_recovery_transition, replay_state = _apply_interaction_sequence(
        replay_state,
        runtime_config,
    )

    direct_signature = _state_signature(direct_state)
    replay_signature = _state_signature(replay_state)
    activation_success = bool(activation_transition.success)
    recovery_success = bool(recovery_transition.success)
    activation_boundary_preserved = activation_transition.changed_unit_ids == ["u1"] and activation_success
    recovery_boundary_preserved = (
        (recovery_success and recovery_transition.changed_unit_ids == ["u2"])
        or (not recovery_success and not recovery_transition.changed_unit_ids)
    )
    boundary_consistency_score = _boundary_consistency_score(
        activation_boundary_preserved=activation_boundary_preserved,
        recovery_boundary_preserved=recovery_boundary_preserved,
        replay_equivalent=replay_signature == direct_signature,
    )

    metrics = InteractionMetrics(
        successful_transitions=sum(1 for item in (activation_transition, recovery_transition) if item.success),
        final_activation=direct_state.units["u1"].activation if "u1" in direct_state.units else None,
        runtime_event_count=2,
        evidence_usage_count=len(recovery_transition.mutation_summary.get("evidence_refs", [])),
        recovery_success=recovery_success,
        replay_equivalent=replay_signature == direct_signature,
        state_transition_equivalence=activation_boundary_preserved and recovery_boundary_preserved,
        boundary_consistency_score=boundary_consistency_score,
    )

    observations = [
        f"activation_threshold={activation_threshold}",
        f"recovery_min_evidence={recovery_min_evidence}",
        f"activation_success={activation_success}",
        f"recovery_success={recovery_success}",
        f"final_activation={metrics.final_activation}",
        f"activation_boundary_preserved={activation_boundary_preserved}",
        f"recovery_boundary_preserved={recovery_boundary_preserved}",
        f"replay_equivalent={metrics.replay_equivalent}",
        f"boundary_consistency_score={boundary_consistency_score}",
    ]

    return {
        "parameter_a": "activation_threshold",
        "parameter_b": "recovery_min_evidence",
        "activation_threshold": activation_threshold,
        "recovery_min_evidence": recovery_min_evidence,
        "metrics": metrics_to_dict(metrics),
        "observations": observations,
        "state_signature": direct_signature,
        "replay_state_signature": replay_signature,
        "replay_transitions": [
            {
                "event_id": replay_activation_transition.event_id,
                "success": replay_activation_transition.success,
                "changed_unit_ids": list(replay_activation_transition.changed_unit_ids),
            },
            {
                "event_id": replay_recovery_transition.event_id,
                "success": replay_recovery_transition.success,
                "changed_unit_ids": list(replay_recovery_transition.changed_unit_ids),
            },
        ],
    }


def run_activation_recovery_interaction(
    values_a: Iterable[float] | None = None,
    values_b: Iterable[int] | None = None,
) -> dict[str, Any]:
    candidate_values_a = list(values_a) if values_a is not None else [0.1, 0.9]
    candidate_values_b = list(values_b) if values_b is not None else [1, 3]
    config = InteractionExperimentConfig(
        parameter_a="activation_threshold",
        parameter_b="recovery_min_evidence",
        values_a=candidate_values_a,
        values_b=candidate_values_b,
        baseline="default",
        scenario="activation_recovery_pair",
        dataset="fixed_kernel_state",
        invariants=[
            "semantic mutation boundary",
            "governance boundary",
            "history boundary",
            "replay isolation",
        ],
    )
    matrix = []
    for activation_threshold in candidate_values_a:
        for recovery_min_evidence in candidate_values_b:
            matrix.append(
                run_activation_recovery_cell(
                    activation_threshold=activation_threshold,
                    recovery_min_evidence=recovery_min_evidence,
                )
            )
    return {
        "experiment": {
            "parameter_a": config.parameter_a,
            "parameter_b": config.parameter_b,
            "values_a": list(config.values_a),
            "values_b": list(config.values_b),
            "baseline": config.baseline,
            "scenario": config.scenario,
            "dataset": config.dataset,
            "invariants": list(config.invariants),
        },
        "matrix": matrix,
    }
