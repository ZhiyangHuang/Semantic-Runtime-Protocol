from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from srp_runtime.config import RuntimeConfig, load_default_profile
from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel import RuntimeKernel, RuntimeKernelConfig
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit

from .candidate import CalibrationCandidate
from .criteria import CalibrationCriteria
from .result import CalibrationResult


def build_round1_state() -> SemanticState:
    state = SemanticState(state_id="calibration:round1", version_id="v0", timestamp_round=1)
    state.units["u1"] = SemanticUnit(
        unit_id="u1",
        canonical_name="alpha",
        semantic_payload={"entity_type": "concept"},
        activation=0.4,
        confidence=0.5,
        version_id="v0",
    )
    return state


def build_round1_event() -> RuntimeEvent:
    return RuntimeEvent(
        event_id="event:calibration:round1:1",
        event_type="ActivationUpdate",
        schema_version="1",
        causal_parent=None,
        actor="tester",
        targets=["u1"],
        payload={},
        mutation_mode="update",
        operator_name="ActivationUpdate",
    )


def _state_signature(state: SemanticState) -> tuple[Any, ...]:
    unit_rows = []
    for unit_id in sorted(state.units):
        unit = state.units[unit_id]
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
                tuple(sorted(unit.semantic_payload.items())),
            )
        )
    graph_rows = tuple(sorted((unit_id, tuple(sorted(neighbors))) for unit_id, neighbors in state.graph.relation_index.items()))
    return (state.version_id, state.timestamp_round, tuple(unit_rows), graph_rows)


def run_calibration_candidate(
    candidate: CalibrationCandidate,
    *,
    baseline: RuntimeConfig | None = None,
    criteria: CalibrationCriteria | None = None,
) -> CalibrationResult:
    if candidate.parameter != "activation_threshold":
        raise NotImplementedError("Round 1 calibration currently supports activation_threshold only")

    runtime_config = baseline or load_default_profile()
    runtime_config = RuntimeConfig(**{**asdict(runtime_config), candidate.parameter: candidate.value})
    criteria = criteria or CalibrationCriteria()

    direct_state = build_round1_state()
    direct_kernel = RuntimeKernel(state=direct_state, config=RuntimeKernelConfig(runtime_config=runtime_config))
    direct_transition = direct_kernel.apply_event(build_round1_event())

    replay_state = build_round1_state()
    replay_kernel = RuntimeKernel(state=replay_state, config=RuntimeKernelConfig(runtime_config=runtime_config))
    replay_transition = replay_kernel.apply_event(build_round1_event())

    direct_signature = _state_signature(direct_kernel._state)
    replay_signature = _state_signature(replay_kernel._state)

    metrics = {
        "successful_transitions": 1 if direct_transition.success else 0,
        "runtime_event_count": len(direct_kernel.event_stream),
        "final_activation": direct_kernel._state.units["u1"].activation if "u1" in direct_kernel._state.units else None,
        "replay_equivalent": replay_signature == direct_signature,
        "state_transition_equivalent": replay_signature == direct_signature,
    }
    constraints_passed, violations = criteria.evaluate(metrics)
    accepted = bool(constraints_passed)

    tested_region = [candidate.value]
    acceptable_region = [candidate.value] if accepted else []
    rejected_region = [] if accepted else [candidate.value]

    return CalibrationResult(
        experiment_id=f"{candidate.parameter}_{str(candidate.value).replace('.', 'p')}_round1",
        parameter=candidate.parameter,
        candidate_value=candidate.value,
        baseline_version="default",
        timestamp=datetime.now(timezone.utc).isoformat(),
        accepted=accepted,
        constraints_passed=constraints_passed,
        tested_region=tested_region,
        acceptable_region=acceptable_region,
        rejected_region=rejected_region,
        metrics=metrics,
        constraint_violations=list(violations),
        notes=[
            f"parameter={candidate.parameter}",
            f"value={candidate.value}",
            f"accepted={accepted}",
        ],
    )

