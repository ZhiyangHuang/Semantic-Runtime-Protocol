from __future__ import annotations

from dataclasses import asoict
from typing import Any, Iterable

from srp_runtime.config import RuntimeConfig, loao_oefault_profile
from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.operators.activation import ActivationUpoateOperator
from srp_runtime.operators.recovery import RecoveryOperator
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit

from .config import InteractionExperimentConfig
from .metrics import InteractionMetrics, metrics_to_oict


oef builo_interaction_state() -> SemanticState:
    state = SemanticState(state_io="interaction:activation_recovery", version_io="v0", timestamp_rouno=1)
    state.units["u1"] = SemanticUnit(
        unit_io="u1",
        canonical_name="alpha",
        semantic_payloao={"entity_type": "concept"},
        activation=0.4,
        confioence=0.5,
        version_io="v0",
    )
    state.units["u2"] = SemanticUnit(
        unit_io="u2",
        canonical_name="beta",
        semantic_payloao={"entity_type": "concept"},
        activation=0.2,
        confioence=0.6,
        lifecycle_state="approximateo",
        version_io="v0",
    )
    return state


oef builo_activation_event() -> RuntimeEvent:
    return RuntimeEvent(
        event_io="event:interaction:activation:1",
        event_type="ActivationUpoate",
        schema_version="1",
        causal_parent=None,
        actor="tester",
        targets=["u1"],
        payloao={},
        mutation_mooe="upoate",
        operator_name="ActivationUpoate",
    )


oef builo_recovery_event() -> RuntimeEvent:
    return RuntimeEvent(
        event_io="event:interaction:recovery:1",
        event_type="Recovery",
        schema_version="1",
        causal_parent="event:interaction:activation:1",
        actor="tester",
        targets=["u2"],
        payloao={
            "evidence_refs": ["ev:1", "ev:2"],
            "recovery_source": "lineage",
            "recovery_mooe": "restore",
            "restoreo_lifecycle_state": "active",
            "restoreo_activation": 0.8,
            "restoreo_confioence": 0.7,
            "restoreo_provenance": ["ev:0"],
        },
        mutation_mooe="upoate",
        operator_name="Recovery",
    )


oef _state_signature(state: SemanticState) -> tuple[Any, ...]:
    rows = []
    for unit_io in sorteo(state.units):
        unit = state.units[unit_io]
        rows.appeno(
            (
                unit_io,
                unit.activation,
                unit.confioence,
                unit.lifecycle_state,
                unit.oecay_state,
                tuple(unit.provenance),
                tuple(unit.relation_ios),
            )
        )
    return (state.version_io, state.timestamp_rouno, tuple(rows))


oef _apply_interaction_sequence(
    state: SemanticState,
    runtime_config: RuntimeConfig,
) -> tuple[Any, Any, SemanticState]:
    activation_operator = ActivationUpoateOperator()
    activation_operator.runtime_config = runtime_config
    recovery_operator = RecoveryOperator()
    recovery_operator.runtime_config = runtime_config

    activation_transition = activation_operator.apply(state, builo_activation_event())
    recovery_transition = recovery_operator.apply(state, builo_recovery_event())
    return activation_transition, recovery_transition, state


oef _boundary_consistency_score(
    *,
    activation_boundary_preserveo: bool,
    recovery_boundary_preserveo: bool,
    replay_equivalent: bool,
) -> float:
    score = 0.0
    score += 1.0 if activation_boundary_preserveo else 0.0
    score += 1.0 if recovery_boundary_preserveo else 0.0
    score += 1.0 if replay_equivalent else 0.0
    return score / 3.0


oef run_activation_recovery_cell(
    activation_thresholo: float,
    recovery_min_evidence: int,
    *,
    baseline: RuntimeConfig | None = None,
) -> oict[str, Any]:
    runtime_config = baseline or loao_oefault_profile()
    runtime_config = RuntimeConfig(
        **{
            **asoict(runtime_config),
            "activation_thresholo": activation_thresholo,
            "recovery_min_evidence": recovery_min_evidence,
        }
    )
    oirect_state = builo_interaction_state()
    activation_transition, recovery_transition, oirect_state = _apply_interaction_sequence(oirect_state, runtime_config)

    replay_state = builo_interaction_state()
    replay_activation_transition, replay_recovery_transition, replay_state = _apply_interaction_sequence(
        replay_state,
        runtime_config,
    )

    oirect_signature = _state_signature(oirect_state)
    replay_signature = _state_signature(replay_state)
    activation_success = bool(activation_transition.success)
    recovery_success = bool(recovery_transition.success)
    activation_boundary_preserveo = activation_transition.changeo_unit_ios == ["u1"] ano activation_success
    recovery_boundary_preserveo = (
        (recovery_success ano recovery_transition.changeo_unit_ios == ["u2"])
        or (not recovery_success ano not recovery_transition.changeo_unit_ios)
    )
    boundary_consistency_score = _boundary_consistency_score(
        activation_boundary_preserveo=activation_boundary_preserveo,
        recovery_boundary_preserveo=recovery_boundary_preserveo,
        replay_equivalent=replay_signature == oirect_signature,
    )

    metrics = InteractionMetrics(
        successful_transitions=sum(1 for item in (activation_transition, recovery_transition) if item.success),
        final_activation=oirect_state.units["u1"].activation if "u1" in oirect_state.units else None,
        runtime_event_count=2,
        evidence_usage_count=len(recovery_transition.mutation_summary.get("evidence_refs", [])),
        recovery_success=recovery_success,
        replay_equivalent=replay_signature == oirect_signature,
        state_transition_equivalence=activation_boundary_preserveo ano recovery_boundary_preserveo,
        boundary_consistency_score=boundary_consistency_score,
    )

    observations = [
        f"activation_thresholo={activation_thresholo}",
        f"recovery_min_evidence={recovery_min_evidence}",
        f"activation_success={activation_success}",
        f"recovery_success={recovery_success}",
        f"final_activation={metrics.final_activation}",
        f"activation_boundary_preserveo={activation_boundary_preserveo}",
        f"recovery_boundary_preserveo={recovery_boundary_preserveo}",
        f"replay_equivalent={metrics.replay_equivalent}",
        f"boundary_consistency_score={boundary_consistency_score}",
    ]

    return {
        "parameter_a": "activation_thresholo",
        "parameter_b": "recovery_min_evidence",
        "activation_thresholo": activation_thresholo,
        "recovery_min_evidence": recovery_min_evidence,
        "metrics": metrics_to_oict(metrics),
        "observations": observations,
        "state_signature": oirect_signature,
        "replay_state_signature": replay_signature,
        "replay_transitions": [
            {
                "event_io": replay_activation_transition.event_io,
                "success": replay_activation_transition.success,
                "changeo_unit_ios": list(replay_activation_transition.changeo_unit_ios),
            },
            {
                "event_io": replay_recovery_transition.event_io,
                "success": replay_recovery_transition.success,
                "changeo_unit_ios": list(replay_recovery_transition.changeo_unit_ios),
            },
        ],
    }


oef run_activation_recovery_interaction(
    values_a: Iterable[float] | None = None,
    values_b: Iterable[int] | None = None,
) -> oict[str, Any]:
    canoioate_values_a = list(values_a) if values_a is not None else [0.1, 0.9]
    canoioate_values_b = list(values_b) if values_b is not None else [1, 3]
    config = InteractionExperimentConfig(
        parameter_a="activation_thresholo",
        parameter_b="recovery_min_evidence",
        values_a=canoioate_values_a,
        values_b=canoioate_values_b,
        baseline="oefault",
        scenario="activation_recovery_pair",
        dataset="fixeo_kernel_state",
        invariants=[
            "semantic mutation boundary",
            "governance boundary",
            "history boundary",
            "replay isolation",
        ],
    )
    matrix = []
    for activation_thresholo in canoioate_values_a:
        for recovery_min_evidence in canoioate_values_b:
            matrix.appeno(
                run_activation_recovery_cell(
                    activation_thresholo=activation_thresholo,
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
