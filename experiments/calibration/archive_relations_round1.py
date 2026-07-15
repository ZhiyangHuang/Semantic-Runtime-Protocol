from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from srp_runtime.config import RuntimeConfig, load_default_profile
from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.operators.forgetting import ForgettingOperator
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit
from srp_runtime.version.conflict import VersionConflict
from srp_runtime.version.conflict_archive_adapter import ConflictArchiveEvidenceAdapter

from .candidate import CalibrationCandidate
from .criteria import CalibrationCriteria
from .index import CalibrationIndex
from .result import CalibrationResult
from .storage import CalibrationResultStore


@dataclass(frozen=True)
class ArchiveQueryResult:
    matched_refs: list[str]
    trace_refs: list[str]
    verification_status: str


class FakeArchiveQueryService:
    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    def lookup_evidence(
        self,
        target: str,
        operation: str = "conflict",
        constraints: dict[str, Any] | None = None,
    ) -> ArchiveQueryResult:
        del operation, constraints
        if not self.enabled:
            return ArchiveQueryResult(matched_refs=[], trace_refs=[], verification_status="partial")
        return ArchiveQueryResult(
            matched_refs=[f"archive:{target}:evidence", f"archive:{target}:relation"],
            trace_refs=[f"trace:{target}"],
            verification_status="verified",
        )


def build_archive_round1_candidates(values: Iterable[bool] | None = None) -> list[CalibrationCandidate]:
    candidate_values = list(values) if values is not None else [False, True]
    return [
        CalibrationCandidate(
            parameter="archive_relations",
            value=value,
            region_label="round1",
            notes="phase2 calibration round 1",
        )
        for value in candidate_values
    ]


def build_archive_round1_state() -> SemanticState:
    state = SemanticState(state_id="calibration:archive:round1", version_id="v0", timestamp_round=1)
    state.units["u1"] = SemanticUnit(
        unit_id="u1",
        canonical_name="alpha",
        semantic_payload={"entity_type": "concept", "detail": "source"},
        activation=0.9,
        confidence=0.95,
        version_id="v0",
    )
    state.units["u2"] = SemanticUnit(
        unit_id="u2",
        canonical_name="beta",
        semantic_payload={"entity_type": "concept", "detail": "source"},
        activation=0.1,
        confidence=0.8,
        version_id="v0",
    )
    state.graph.add_unit(state.units["u1"])
    state.graph.add_unit(state.units["u2"])
    state.graph.relation_index["u1"] = ["u2"]
    state.graph.relation_index["u2"] = ["u1"]
    state.units["u1"].relation_ids = ["r:u1->u2"]
    state.units["u2"].relation_ids = ["r:u2->u1"]
    return state


def build_archive_round1_event() -> RuntimeEvent:
    return RuntimeEvent(
        event_id="event:calibration:archive:round1:1",
        event_type="Forgotten",
        schema_version="1",
        causal_parent=None,
        actor="tester",
        targets=["u2"],
        payload={
            "target_unit_id": "u2",
            "forget_reason": "archive_boundary",
            "preserve_evidence": True,
            "evidence_refs": ["trace:a1", "trace:a2"],
        },
        mutation_mode="update",
        operator_name="ForgettingOperator",
    )


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


def _build_conflict(transition_id: str, event_id: str, state_ref: str) -> VersionConflict:
    return VersionConflict(
        conflict_id=f"conflict:{event_id}",
        conflict_type="archive_relation_enrichment",
        source_version_a=state_ref,
        source_version_b=state_ref,
        version_refs=[state_ref],
        transition_refs=[transition_id],
        trace_refs=[f"trace:{event_id}"],
        evidence_refs=[transition_id],
        severity="info",
        resolution_options=["inspect_archive", "compare_evidence"],
    )


def run_archive_relations_round1(
    values: Iterable[bool] | None = None,
    *,
    store: CalibrationResultStore | None = None,
    index: CalibrationIndex | None = None,
) -> dict[str, Any]:
    candidates = build_archive_round1_candidates(values)
    results: list[CalibrationResult] = []

    for candidate in candidates:
        runtime_config = load_default_profile()
        runtime_config = RuntimeConfig(**{**asdict(runtime_config), candidate.parameter: candidate.value})

        direct_state = build_archive_round1_state()
        operator = ForgettingOperator()
        operator.runtime_config = runtime_config
        event = build_archive_round1_event()
        direct_transition = operator.apply(direct_state, event)

        replay_state = build_archive_round1_state()
        replay_operator = ForgettingOperator()
        replay_operator.runtime_config = runtime_config
        replay_transition = replay_operator.apply(replay_state, build_archive_round1_event())

        direct_signature = _state_signature(direct_state)
        replay_signature = _state_signature(replay_state)

        baseline_state = build_archive_round1_state()
        baseline_operator = ForgettingOperator()
        baseline_operator.runtime_config = RuntimeConfig(**{**asdict(load_default_profile()), "archive_relations": False})
        baseline_operator.apply(baseline_state, build_archive_round1_event())
        baseline_signature = _state_signature(baseline_state)

        conflict = _build_conflict(direct_transition.transition_id, event.event_id, direct_transition.after_state_ref)
        adapter = ConflictArchiveEvidenceAdapter(FakeArchiveQueryService(enabled=bool(candidate.value)))
        bundle = adapter.lookup_conflict_evidence(conflict)

        evidence_enrichment_count = len(bundle.archive_refs)
        conflict_evidence_coverage = 0.0
        if conflict.evidence_refs:
            conflict_evidence_coverage = min(1.0, len(bundle.archive_refs) / len(conflict.evidence_refs))

        metrics = {
            "successful_transitions": 1 if direct_transition.success else 0,
            "runtime_event_count": 1,
            "final_activation": direct_state.units["u2"].activation if "u2" in direct_state.units else None,
            "replay_equivalent": replay_signature == direct_signature,
            "state_transition_equivalent": direct_signature == baseline_signature,
            "evidence_usage_count": len(event.payload.get("evidence_refs", [])),
            "evidence_enrichment_count": evidence_enrichment_count,
            "conflict_evidence_coverage": conflict_evidence_coverage,
            "archive_not_state_authority": direct_signature == baseline_signature,
        }
        criteria = CalibrationCriteria(
            replay_equivalent=True,
            state_transition_equivalent=True,
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
                    "evidence_enrichment": "changed" if evidence_enrichment_count > 0 else "unchanged",
                    "state_transition": "unchanged" if metrics["state_transition_equivalent"] else "changed",
                    "replay": "preserved" if metrics["replay_equivalent"] else "diverged",
                    "authority": "isolated" if metrics["archive_not_state_authority"] else "not_isolated",
                },
                invariant_status={
                    "archive_not_state_authority": "pass" if metrics["archive_not_state_authority"] else "fail",
                    "replay_equivalent": "pass" if metrics["replay_equivalent"] else "fail",
                    "state_transition_equivalent": "pass" if metrics["state_transition_equivalent"] else "fail",
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
        "parameter": "archive_relations",
        "tested_region": [False, True],
        "acceptable_region": [result.candidate_value for result in results if result.accepted],
        "rejected_region": [result.candidate_value for result in results if not result.accepted],
        "result_count": len(results),
        "accepted_count": sum(1 for result in results if result.accepted),
    }

    return {
        "experiment": {
            "parameter": "archive_relations",
            "round": "1D",
            "baseline": "default",
            "scenario": "archive_relations_round1",
            "dataset": "fixed_kernel_state",
        },
        "summary": summary,
        "results": [asdict(result) for result in results],
        "stored_paths": stored_paths,
    }

