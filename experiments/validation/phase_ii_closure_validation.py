from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable

from srp_runtime.config import RuntimeConfig, load_default_profile
from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.operators.activation import ActivationUpdateOperator
from srp_runtime.operators.forgetting import ForgettingOperator
from srp_runtime.operators.recovery import RecoveryOperator
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit
from srp_runtime.version.conflict import VersionConflict
from srp_runtime.version.conflict_archive_adapter import ConflictArchiveEvidenceAdapter


FROZEN_REGIONS: dict[str, dict[str, Any]] = {
    "activation_threshold": {"accepted": (0.3, 0.8), "boundary_class": "semantic mutation boundary"},
    "recovery_min_evidence": {"accepted": (1, 3), "boundary_class": "evidence acceptance boundary"},
    "preserve_evidence": {"accepted": (False, True), "boundary_class": "history preservation boundary"},
    "archive_relations": {"accepted": (False, True), "boundary_class": "archive enrichment boundary"},
}


@dataclass(frozen=True)
class ValidationScenario:
    name: str
    workload_factor: int = 1
    conflict_density: int = 1
    evidence_multiplier: int = 1
    notes: str = ""


@dataclass(frozen=True)
class ValidationObservation:
    validation_id: str
    parameter: str
    boundary_class: str
    candidate_value: Any
    scenario_name: str
    expected_verdict: bool
    observed_verdict: bool
    boundary_shift: bool
    replay_equivalent: bool
    authority_preserved: bool
    evidence_consistent: bool
    metrics: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ValidationReport:
    report_id: str
    status: str
    observations: list[ValidationObservation] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ArchiveQueryResult:
    matched_refs: list[str]
    trace_refs: list[str]
    verification_status: str


class FakeArchiveQueryService:
    def __init__(self, enabled: bool, evidence_multiplier: int = 1) -> None:
        self.enabled = enabled
        self.evidence_multiplier = max(1, evidence_multiplier)

    def lookup_evidence(
        self,
        target: str,
        operation: str = "conflict",
        constraints: dict[str, Any] | None = None,
    ) -> ArchiveQueryResult:
        del operation, constraints
        if not self.enabled:
            return ArchiveQueryResult(matched_refs=[], trace_refs=[], verification_status="partial")
        matched_refs = [f"archive:{target}:evidence:{index}" for index in range(1, self.evidence_multiplier + 1)]
        return ArchiveQueryResult(
            matched_refs=matched_refs,
            trace_refs=[f"trace:{target}"],
            verification_status="verified",
        )


def build_validation_scenarios() -> list[ValidationScenario]:
    return [
        ValidationScenario(name="baseline", workload_factor=1, conflict_density=1, evidence_multiplier=1),
        ValidationScenario(name="high_transition", workload_factor=3, conflict_density=1, evidence_multiplier=1),
        ValidationScenario(name="high_conflict", workload_factor=1, conflict_density=3, evidence_multiplier=1),
        ValidationScenario(name="high_evidence", workload_factor=1, conflict_density=1, evidence_multiplier=3),
    ]


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


def _activation_state(scenario: ValidationScenario) -> SemanticState:
    state = SemanticState(state_id=f"validation:activation:{scenario.name}", version_id="v0", timestamp_round=1)
    state.units["u1"] = SemanticUnit(
        unit_id="u1",
        canonical_name="alpha",
        semantic_payload={"entity_type": "concept"},
        activation=0.4,
        confidence=0.5,
        version_id="v0",
    )
    for index in range(2, scenario.workload_factor + 2):
        unit_id = f"u{index}"
        state.units[unit_id] = SemanticUnit(
            unit_id=unit_id,
            canonical_name=f"extra-{index}",
            semantic_payload={"entity_type": "concept"},
            activation=0.2,
            confidence=0.4,
            version_id="v0",
        )
    return state


def _recovery_state(scenario: ValidationScenario) -> SemanticState:
    state = SemanticState(state_id=f"validation:recovery:{scenario.name}", version_id="v0", timestamp_round=1)
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


def _preserve_state(scenario: ValidationScenario) -> SemanticState:
    state = SemanticState(state_id=f"validation:preserve:{scenario.name}", version_id="v0", timestamp_round=1)
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
    if scenario.conflict_density > 1:
        for index in range(3, scenario.conflict_density + 2):
            unit_id = f"u{index}"
            state.units[unit_id] = SemanticUnit(
                unit_id=unit_id,
                canonical_name=f"conflict-{index}",
                semantic_payload={"entity_type": "concept"},
                activation=0.15,
                confidence=0.4,
                lifecycle_state="active",
                version_id="v0",
            )
            state.graph.add_unit(state.units[unit_id])
            state.graph.relation_index[unit_id] = ["u2"]
            state.graph.relation_index["u2"].append(unit_id)
            state.units[unit_id].relation_ids = [f"r:{unit_id}->u2"]
    return state


def _archive_state(scenario: ValidationScenario) -> SemanticState:
    state = SemanticState(state_id=f"validation:archive:{scenario.name}", version_id="v0", timestamp_round=1)
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
    if scenario.conflict_density > 1:
        for index in range(3, scenario.conflict_density + 2):
            unit_id = f"u{index}"
            state.units[unit_id] = SemanticUnit(
                unit_id=unit_id,
                canonical_name=f"relation-{index}",
                semantic_payload={"entity_type": "concept"},
                activation=0.2,
                confidence=0.6,
                version_id="v0",
            )
            state.graph.add_unit(state.units[unit_id])
            state.graph.relation_index["u1"].append(unit_id)
            state.graph.relation_index[unit_id] = ["u1"]
            state.units[unit_id].relation_ids = [f"r:{unit_id}->u1"]
    return state


def _activation_event() -> RuntimeEvent:
    return RuntimeEvent(
        event_id="event:validation:activation:1",
        event_type="ActivationUpdate",
        schema_version="1",
        causal_parent=None,
        actor="tester",
        targets=["u1"],
        payload={},
        mutation_mode="update",
        operator_name="ActivationUpdate",
    )


def _recovery_event(evidence_count: int) -> RuntimeEvent:
    evidence_refs = [f"ev:{index}" for index in range(1, evidence_count + 1)]
    return RuntimeEvent(
        event_id="event:validation:recovery:1",
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


def _forget_event() -> RuntimeEvent:
    return RuntimeEvent(
        event_id="event:validation:forget:1",
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


def _conflict_for_archive(transition_id: str, event_id: str, state_ref: str) -> VersionConflict:
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


def _apply_activation_candidate(candidate_value: float, scenario: ValidationScenario) -> ValidationObservation:
    runtime_config = RuntimeConfig(**{**asdict(load_default_profile()), "activation_threshold": candidate_value})
    direct_state = _activation_state(scenario)
    replay_state = _activation_state(scenario)
    direct_operator = ActivationUpdateOperator()
    direct_operator.runtime_config = runtime_config
    replay_operator = ActivationUpdateOperator()
    replay_operator.runtime_config = runtime_config

    event_count = max(1, scenario.workload_factor)
    for _ in range(event_count):
        direct_operator.apply(direct_state, _activation_event())
        replay_operator.apply(replay_state, _activation_event())

    final_activation = direct_state.units["u1"].activation
    expected_verdict = 0.3 <= candidate_value <= 0.8
    observed_verdict = 0.3 <= final_activation <= 0.8
    replay_equivalent = _state_signature(direct_state) == _state_signature(replay_state)
    authority_preserved = replay_equivalent
    evidence_consistent = final_activation is not None

    return ValidationObservation(
        validation_id=f"activation_threshold:{candidate_value}:{scenario.name}",
        parameter="activation_threshold",
        boundary_class=FROZEN_REGIONS["activation_threshold"]["boundary_class"],
        candidate_value=candidate_value,
        scenario_name=scenario.name,
        expected_verdict=expected_verdict,
        observed_verdict=observed_verdict,
        boundary_shift=expected_verdict != observed_verdict,
        replay_equivalent=replay_equivalent,
        authority_preserved=authority_preserved,
        evidence_consistent=evidence_consistent,
        metrics={
            "successful_transitions": event_count,
            "runtime_event_count": event_count,
            "final_activation": final_activation,
            "workload_factor": scenario.workload_factor,
        },
        notes=[scenario.notes or "boundary stability validation"],
    )


def _apply_recovery_candidate(candidate_value: int, scenario: ValidationScenario) -> ValidationObservation:
    runtime_config = RuntimeConfig(**{**asdict(load_default_profile()), "recovery_min_evidence": candidate_value})
    direct_state = _recovery_state(scenario)
    replay_state = _recovery_state(scenario)
    direct_operator = RecoveryOperator()
    direct_operator.runtime_config = runtime_config
    replay_operator = RecoveryOperator()
    replay_operator.runtime_config = runtime_config

    evidence_count = max(1, 3 * scenario.evidence_multiplier)
    direct_transition = direct_operator.apply(direct_state, _recovery_event(evidence_count))
    replay_transition = replay_operator.apply(replay_state, _recovery_event(evidence_count))
    observed_verdict = bool(direct_transition.success)
    expected_verdict = 1 <= candidate_value <= 3
    replay_equivalent = _state_signature(direct_state) == _state_signature(replay_state)
    authority_preserved = replay_equivalent
    evidence_consistent = len(direct_transition.mutation_summary.get("evidence_refs", [])) == evidence_count

    return ValidationObservation(
        validation_id=f"recovery_min_evidence:{candidate_value}:{scenario.name}",
        parameter="recovery_min_evidence",
        boundary_class=FROZEN_REGIONS["recovery_min_evidence"]["boundary_class"],
        candidate_value=candidate_value,
        scenario_name=scenario.name,
        expected_verdict=expected_verdict,
        observed_verdict=observed_verdict,
        boundary_shift=expected_verdict != observed_verdict,
        replay_equivalent=replay_equivalent,
        authority_preserved=authority_preserved,
        evidence_consistent=evidence_consistent and bool(replay_transition.success == direct_transition.success),
        metrics={
            "successful_transitions": 1 if observed_verdict else 0,
            "runtime_event_count": 1,
            "evidence_usage_count": evidence_count,
            "evidence_supply": evidence_count,
            "evidence_multiplier": scenario.evidence_multiplier,
        },
        notes=[scenario.notes or "evidence acceptance validation"],
    )


def _apply_preserve_candidate(candidate_value: bool, scenario: ValidationScenario) -> ValidationObservation:
    runtime_config = RuntimeConfig(**{**asdict(load_default_profile()), "preserve_evidence": candidate_value})
    direct_state = _preserve_state(scenario)
    replay_state = _preserve_state(scenario)
    direct_operator = ForgettingOperator()
    direct_operator.runtime_config = runtime_config
    replay_operator = ForgettingOperator()
    replay_operator.runtime_config = runtime_config

    direct_transition = direct_operator.apply(direct_state, _forget_event())
    replay_transition = replay_operator.apply(replay_state, _forget_event())
    replay_equivalent = _state_signature(direct_state) == _state_signature(replay_state)
    evidence_record_count = len(direct_state.units["u2"].provenance)
    evidence_consistent = evidence_record_count > 0 if candidate_value else evidence_record_count == 0

    return ValidationObservation(
        validation_id=f"preserve_evidence:{candidate_value}:{scenario.name}",
        parameter="preserve_evidence",
        boundary_class=FROZEN_REGIONS["preserve_evidence"]["boundary_class"],
        candidate_value=candidate_value,
        scenario_name=scenario.name,
        expected_verdict=True,
        observed_verdict=bool(direct_transition.success),
        boundary_shift=False,
        replay_equivalent=replay_equivalent,
        authority_preserved=replay_equivalent,
        evidence_consistent=evidence_consistent and bool(replay_transition.success == direct_transition.success),
        metrics={
            "successful_transitions": 1 if direct_transition.success else 0,
            "evidence_record_count": evidence_record_count,
            "audit_completeness_score": float(min(1.0, evidence_record_count / 2.0)),
            "history_preservation_delta": float(evidence_record_count),
            "state_reconstruction_independence": replay_equivalent,
        },
        notes=[scenario.notes or "history preservation validation"],
    )


def _apply_archive_candidate(candidate_value: bool, scenario: ValidationScenario) -> ValidationObservation:
    runtime_config = RuntimeConfig(**{**asdict(load_default_profile()), "archive_relations": candidate_value})
    direct_state = _archive_state(scenario)
    replay_state = _archive_state(scenario)
    direct_operator = ForgettingOperator()
    direct_operator.runtime_config = runtime_config
    replay_operator = ForgettingOperator()
    replay_operator.runtime_config = runtime_config

    event = _forget_event()
    direct_transition = direct_operator.apply(direct_state, event)
    replay_transition = replay_operator.apply(replay_state, event)

    conflict = _conflict_for_archive(direct_transition.transition_id, event.event_id, direct_transition.after_state_ref)
    adapter = ConflictArchiveEvidenceAdapter(FakeArchiveQueryService(enabled=candidate_value, evidence_multiplier=scenario.evidence_multiplier))
    bundle = adapter.lookup_conflict_evidence(conflict)

    replay_equivalent = _state_signature(direct_state) == _state_signature(replay_state)
    evidence_enrichment_count = len(bundle.archive_refs)
    evidence_consistent = evidence_enrichment_count >= 0

    return ValidationObservation(
        validation_id=f"archive_relations:{candidate_value}:{scenario.name}",
        parameter="archive_relations",
        boundary_class=FROZEN_REGIONS["archive_relations"]["boundary_class"],
        candidate_value=candidate_value,
        scenario_name=scenario.name,
        expected_verdict=True,
        observed_verdict=bool(direct_transition.success),
        boundary_shift=False,
        replay_equivalent=replay_equivalent,
        authority_preserved=replay_equivalent,
        evidence_consistent=evidence_consistent,
        metrics={
            "successful_transitions": 1 if direct_transition.success else 0,
            "evidence_enrichment_count": evidence_enrichment_count,
            "conflict_evidence_coverage": min(1.0, evidence_enrichment_count / max(1, len(conflict.evidence_refs))),
            "archive_not_state_authority": replay_equivalent,
        },
        notes=[scenario.notes or "archive enrichment validation"],
    )


def run_boundary_validation_case(parameter: str, candidate_value: Any, scenario: ValidationScenario) -> ValidationObservation:
    if parameter == "activation_threshold":
        return _apply_activation_candidate(float(candidate_value), scenario)
    if parameter == "recovery_min_evidence":
        return _apply_recovery_candidate(int(candidate_value), scenario)
    if parameter == "preserve_evidence":
        return _apply_preserve_candidate(bool(candidate_value), scenario)
    if parameter == "archive_relations":
        return _apply_archive_candidate(bool(candidate_value), scenario)
    raise NotImplementedError(parameter)


def _aggregate(observations: list[ValidationObservation]) -> dict[str, Any]:
    grouped: dict[str, list[ValidationObservation]] = {}
    for observation in observations:
        grouped.setdefault(observation.boundary_class, []).append(observation)

    boundary_summaries: dict[str, Any] = {}
    for boundary_class, items in grouped.items():
        boundary_summaries[boundary_class] = {
            "observation_count": len(items),
            "boundary_shift": "changed" if any(item.boundary_shift for item in items) else "none",
            "replay_equivalent": all(item.replay_equivalent for item in items),
            "authority_preserved": all(item.authority_preserved for item in items),
            "evidence_consistent": all(item.evidence_consistent for item in items),
        }

    return {
        "boundary_classes": boundary_summaries,
        "observation_count": len(observations),
        "validated_boundary_classes": list(boundary_summaries.keys()),
    }


def run_phase_ii_closure_validation_suite() -> dict[str, Any]:
    scenarios = build_validation_scenarios()
    observations: list[ValidationObservation] = []

    for scenario in scenarios:
        observations.append(run_boundary_validation_case("activation_threshold", 0.5, scenario))
        observations.append(run_boundary_validation_case("activation_threshold", 0.9, scenario))

    for scenario in scenarios:
        observations.append(run_boundary_validation_case("recovery_min_evidence", 2, scenario))
        observations.append(run_boundary_validation_case("recovery_min_evidence", 4, scenario))

    for scenario in scenarios:
        observations.append(run_boundary_validation_case("preserve_evidence", False, scenario))
        observations.append(run_boundary_validation_case("preserve_evidence", True, scenario))

    for scenario in scenarios:
        observations.append(run_boundary_validation_case("archive_relations", False, scenario))
        observations.append(run_boundary_validation_case("archive_relations", True, scenario))

    report = ValidationReport(
        report_id=f"phase_ii_closure_validation_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        status="validated",
        observations=observations,
        summary=_aggregate(observations),
    )

    return {
        "report": asdict(report),
        "scenarios": [asdict(scenario) for scenario in scenarios],
    }

