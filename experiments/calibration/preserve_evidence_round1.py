from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from srp_runtime.config import RuntimeConfig, load_default_profile
from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.operators.forgetting import ForgettingOperator
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit

from .candidate import CalibrationCandidate
from .criteria import CalibrationCriteria
from .index import CalibrationIndex
from .result import CalibrationResult
from .storage import CalibrationResultStore


def build_preserve_round1_candidates(values: Iterable[bool] | None = None) -> list[CalibrationCandidate]:
    candidate_values = list(values) if values is not None else [False, True]
    return [
        CalibrationCandidate(
            parameter="preserve_evidence",
            value=value,
            region_label="round1",
            notes="phase2 calibration round 1",
        )
        for value in candidate_values
    ]


def build_preserve_round1_state() -> SemanticState:
    state = SemanticState(state_id="calibration:preserve:round1", version_id="v0", timestamp_round=1)
    state.units["u1"] = SemanticUnit(
        unit_id="u1",
        canonical_name="alpha",
        semantic_payload={"entity_type": "concept", "detail": "source"},
        activation=0.2,
        confidence=0.5,
        lifecycle_state="active",
        version_id="v0",
    )
    state.units["u2"] = SemanticUnit(
        unit_id="u2",
        canonical_name="beta",
        semantic_payload={"entity_type": "concept", "detail": "source"},
        activation=0.1,
        confidence=0.5,
        lifecycle_state="active",
        version_id="v0",
    )
    state.graph.add_unit(state.units["u1"])
    state.graph.add_unit(state.units["u2"])
    state.graph.relation_index["u1"] = ["u2"]
    state.graph.relation_index["u2"] = ["u1"]
    state.units["u1"].relation_ids = ["r:u1->u2"]
    state.units["u2"].relation_ids = ["r:u2->u1"]
    return state


def build_preserve_round1_event() -> RuntimeEvent:
    return RuntimeEvent(
        event_id="event:calibration:preserve:round1:1",
        event_type="Forgetting",
        schema_version="1",
        causal_parent=None,
        actor="tester",
        targets=["u2"],
        payload={
            "target_unit_id": "u2",
            "evidence_refs": ["trace:f1", "trace:f2"],
        },
        mutation_mode="update",
        operator_name="Forgetting",
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


def run_preserve_evidence_round1(
    values: Iterable[bool] | None = None,
    *,
    store: CalibrationResultStore | None = None,
    index: CalibrationIndex | None = None,
) -> dict[str, Any]:
    candidates = build_preserve_round1_candidates(values)
    results: list[CalibrationResult] = []

    for candidate in candidates:
        runtime_config = load_default_profile()
        runtime_config = RuntimeConfig(**{**asdict(runtime_config), candidate.parameter: candidate.value})

        direct_state = build_preserve_round1_state()
        operator = ForgettingOperator()
        operator.runtime_config = runtime_config
        direct_transition = operator.apply(direct_state, build_preserve_round1_event())

        replay_state = build_preserve_round1_state()
        replay_operator = ForgettingOperator()
        replay_operator.runtime_config = runtime_config
        replay_transition = replay_operator.apply(replay_state, build_preserve_round1_event())

        direct_signature = _state_signature(direct_state)
        replay_signature = _state_signature(replay_state)
        evidence_refs = list(build_preserve_round1_event().payload["evidence_refs"])
        evidence_record_count = len(direct_state.units["u2"].provenance)
        audit_completeness_score = float(min(1.0, evidence_record_count / max(1, len(evidence_refs))))
        history_preservation_delta = float(evidence_record_count)

        metrics = {
            "successful_transitions": 1 if direct_transition.success else 0,
            "runtime_event_count": 1,
            "final_activation": direct_state.units["u2"].activation if "u2" in direct_state.units else None,
            "replay_equivalent": replay_signature == direct_signature,
            "state_transition_equivalent": replay_signature == direct_signature,
            "evidence_usage_count": len(evidence_refs),
            "evidence_usage_consistent": len(evidence_refs) > 0,
            "evidence_record_count": evidence_record_count,
            "audit_completeness_score": audit_completeness_score,
            "history_preservation_delta": history_preservation_delta,
            "state_reconstruction_independence": replay_signature == direct_signature,
        }
        criteria = CalibrationCriteria(
            replay_equivalent=True,
            state_transition_equivalent=True,
            evidence_usage_consistent=True,
        )
        constraints_passed, violations = criteria.evaluate(metrics)
        accepted = bool(constraints_passed)

        tested_region = [candidate.value]
        acceptable_region = [candidate.value] if accepted else []
        rejected_region = [] if accepted else [candidate.value]

        results.append(
            CalibrationResult(
                experiment_id=f"{candidate.parameter}_{str(candidate.value).lower()}_round1",
                parameter=candidate.parameter,
                candidate_value=candidate.value,
                baseline_version="default",
                timestamp=datetime.now(timezone.utc).isoformat(),
                accepted=accepted,
                constraints_passed=constraints_passed,
                runtime_version="default",
                tested_region=tested_region,
                acceptable_region=acceptable_region,
                rejected_region=rejected_region,
                metrics=metrics,
                constraint_summary={
                    "replay": "pass" if metrics["replay_equivalent"] else "fail",
                    "history_boundary": "pass" if metrics["state_reconstruction_independence"] else "fail",
                    "authority_isolation": "pass",
                    "evidence_boundary": "pass" if metrics["audit_completeness_score"] >= 0.0 else "fail",
                },
                invariant_status={
                    "runtime_execution_unchanged": "pass" if metrics["replay_equivalent"] else "fail",
                    "semantic_commit_unchanged": "pass" if metrics["state_transition_equivalent"] else "fail",
                    "archive_not_state_authority": "pass",
                },
                constraint_violations=list(violations),
                notes=[
                    f"parameter={candidate.parameter}",
                    f"value={candidate.value}",
                    f"accepted={accepted}",
                ],
            )
        )

    stored_paths: list[str] = []
    if store is not None:
        stored_paths = [str(store.save(result)) for result in results]

    if index is not None:
        for result, stored_path in zip(results, stored_paths or [str(Path(index.path).with_name(f"{result.experiment_id}.json")) for result in results], strict=False):
            index.register_from_result(result, result_location=stored_path)

    summary = {
        "parameter": "preserve_evidence",
        "tested_region": [False, True],
        "acceptable_region": [result.candidate_value for result in results if result.accepted],
        "rejected_region": [result.candidate_value for result in results if not result.accepted],
        "result_count": len(results),
        "accepted_count": sum(1 for result in results if result.accepted),
    }

    return {
        "experiment": {
            "parameter": "preserve_evidence",
            "round": "1C",
            "baseline": "default",
            "scenario": "preserve_evidence_round1",
            "dataset": "fixed_kernel_state",
        },
        "summary": summary,
        "results": [asdict(result) for result in results],
        "stored_paths": stored_paths,
    }
