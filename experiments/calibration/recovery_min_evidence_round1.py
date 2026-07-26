from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable

from srp_runtime.config import RuntimeConfig, load_default_profile
from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.operators.recovery import RecoveryOperator
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit

from .candidate import CalibrationCandidate
from .criteria import CalibrationCriteria
from .index import CalibrationIndex
from .result import CalibrationResult
from .storage import CalibrationResultStore


def build_recovery_min_evidence_round1_candidates(values: Iterable[int] | None = None) -> list[CalibrationCandidate]:
    candidate_values = list(values) if values is not None else [1, 2, 3, 4, 5]
    return [
        CalibrationCandidate(
            parameter="recovery_min_evidence",
            value=value,
            region_label="round1",
            notes="phase2 calibration round 1",
        )
        for value in candidate_values
    ]


def build_recovery_round1_state() -> SemanticState:
    state = SemanticState(state_id="calibration:recovery:round1", version_id="v0", timestamp_round=1)
    state.units["u1"] = SemanticUnit(
        unit_id="u1",
        canonical_name="beta",
        semantic_payload={"entity_type": "concept"},
        activation=0.2,
        confidence=0.6,
        lifecycle_state="approximated",
        version_id="v0",
    )
    return state


def build_recovery_round1_event(evidence_count: int = 3) -> RuntimeEvent:
    evidence_refs = [f"ev:{index}" for index in range(1, evidence_count + 1)]
    return RuntimeEvent(
        event_id="event:calibration:recovery:round1:1",
        event_type="Recovery",
        schema_version="1",
        causal_parent=None,
        actor="tester",
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


def run_recovery_min_evidence_round1(
    values: Iterable[int] | None = None,
    *,
    store: CalibrationResultStore | None = None,
    index: CalibrationIndex | None = None,
) -> dict[str, Any]:
    candidates = build_recovery_min_evidence_round1_candidates(values)
    criteria = CalibrationCriteria(
        replay_equivalent=True,
        state_transition_equivalent=True,
        recovery_success=True,
        evidence_usage_consistent=True,
    )

    results: list[CalibrationResult] = []
    for candidate in candidates:
        runtime_config = load_default_profile()
        runtime_config = RuntimeConfig(**{**asdict(runtime_config), candidate.parameter: candidate.value})
        direct_state = build_recovery_round1_state()
        direct_operator = RecoveryOperator()
        direct_operator.runtime_config = runtime_config
        recovery_event = build_recovery_round1_event()
        direct_transition = direct_operator.apply(direct_state, recovery_event)

        replay_state = build_recovery_round1_state()
        replay_operator = RecoveryOperator()
        replay_operator.runtime_config = runtime_config
        replay_transition = replay_operator.apply(replay_state, build_recovery_round1_event())

        direct_signature = _state_signature(direct_state)
        replay_signature = _state_signature(replay_state)
        evidence_refs = list(recovery_event.payload["evidence_refs"])
        evidence_usage_consistent = len(evidence_refs) == 3

        metrics = {
            "successful_transitions": 1 if direct_transition.success else 0,
            "runtime_event_count": 1,
            "final_activation": direct_state.units["u1"].activation if "u1" in direct_state.units else None,
            "replay_equivalent": replay_signature == direct_signature,
            "state_transition_equivalent": replay_signature == direct_signature,
            "recovery_success": bool(direct_transition.success),
            "evidence_usage_count": len(evidence_refs),
            "evidence_usage_consistent": evidence_usage_consistent,
            "recovery_authority_bounded": direct_transition.changed_unit_ids in ([], ["u1"]),
        }
        constraints_passed, violations = criteria.evaluate(metrics)
        accepted = bool(constraints_passed)

        tested_region = [candidate.value]
        acceptable_region = [candidate.value] if accepted else []
        rejected_region = [] if accepted else [candidate.value]

        results.append(
            CalibrationResult(
                experiment_id=f"{candidate.parameter}_{candidate.value}_round1",
                parameter=candidate.parameter,
                candidate_value=candidate.value,
                baseline_version="default",
                runtime_version="default",
                timestamp="",
                accepted=accepted,
                constraints_passed=constraints_passed,
                tested_region=tested_region,
                acceptable_region=acceptable_region,
                rejected_region=rejected_region,
                metrics=metrics,
                constraint_summary={
                    "replay": "pass" if metrics["replay_equivalent"] else "fail",
                    "transition": "pass" if metrics["state_transition_equivalent"] else "fail",
                    "governance_boundary": "pass" if metrics["recovery_authority_bounded"] else "fail",
                    "evidence_boundary": "pass" if metrics["evidence_usage_consistent"] else "fail",
                },
                invariant_status={
                    "deterministic": "pass" if metrics["replay_equivalent"] else "fail",
                    "authority_isolation": "pass" if metrics["recovery_authority_bounded"] else "fail",
                },
                constraint_violations=list(violations),
                notes=[
                    f"parameter={candidate.parameter}",
                    f"value={candidate.value}",
                    f"accepted={accepted}",
                ],
            )
        )

    from datetime import datetime, timezone

    timestamp = datetime.now(timezone.utc).isoformat()
    results = [
        CalibrationResult(
            **{
                **asdict(result),
                "timestamp": timestamp,
            }
        )
        for result in results
    ]

    stored_paths: list[str] = []
    if store is not None:
        stored_paths = [str(store.save(result)) for result in results]

    if index is not None:
        for result, stored_path in zip(results, stored_paths or [str(Path(index.path).with_name(f"{result.experiment_id}.json")) for result in results], strict=False):
            index.register_from_result(result, result_location=stored_path)

    accepted_values = [result.candidate_value for result in results if result.accepted]
    rejected_values = [result.candidate_value for result in results if not result.accepted]

    def _bounds(values: list[Any]) -> list[Any]:
        if not values:
            return []
        try:
            numeric_values = sorted(int(value) for value in values)
        except (TypeError, ValueError):
            return list(values)
        return [numeric_values[0], numeric_values[-1]]

    summary = {
        "parameter": "recovery_min_evidence",
        "tested_region": _bounds([candidate.value for candidate in candidates]),
        "acceptable_region": _bounds(accepted_values),
        "rejected_region": _bounds(rejected_values),
        "result_count": len(results),
        "accepted_count": len(accepted_values),
    }

    return {
        "experiment": {
            "parameter": "recovery_min_evidence",
            "round": "1B",
            "baseline": "default",
            "scenario": "recovery_min_evidence_round1",
            "dataset": "fixed_kernel_state",
        },
        "summary": summary,
        "results": [asdict(result) for result in results],
        "stored_paths": stored_paths,
    }
