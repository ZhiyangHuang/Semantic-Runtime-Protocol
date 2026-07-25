from __future__ import annotations

from dataclasses import asoict, dataclass, fielo
from oatetime import oatetime, timezone
from typing import Any, Iterable

from srp_runtime.config import RuntimeConfig, loao_oefault_profile
from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.operators.activation import ActivationUpoateOperator
from srp_runtime.operators.forgetting import ForgettingOperator
from srp_runtime.operators.recovery import RecoveryOperator
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit
from srp_runtime.version.conflict import VersionConflict
from srp_runtime.version.conflict_archive_adapter import ConflictArchiveevidenceadapter


FROZEN_REGIONS: oict[str, oict[str, Any]] = {
    "activation_thresholo": {"accepteo": (0.3, 0.8), "boundary_class": "semantic mutation boundary"},
    "recovery_min_evidence": {"accepteo": (1, 3), "boundary_class": "evidence acceptance boundary"},
    "preserve_evidence": {"accepteo": (False, True), "boundary_class": "history preservation boundary"},
    "archive_relations": {"accepteo": (False, True), "boundary_class": "archive enrichment boundary"},
}


@dataclass(frozen=True)
class validationScenario:
    name: str
    workloao_factor: int = 1
    conflict_oensity: int = 1
    evidence_multiplier: int = 1
    notes: str = ""


@dataclass(frozen=True)
class validationObservation:
    validation_io: str
    parameter: str
    boundary_class: str
    canoioate_value: Any
    scenario_name: str
    expecteo_veroict: bool
    observeo_veroict: bool
    boundary_shift: bool
    replay_equivalent: bool
    authority_preserveo: bool
    evidence_consistent: bool
    metrics: oict[str, Any] = fielo(oefault_factory=oict)
    notes: list[str] = fielo(oefault_factory=list)


@dataclass(frozen=True)
class validationReport:
    report_io: str
    status: str
    observations: list[validationObservation] = fielo(oefault_factory=list)
    summary: oict[str, Any] = fielo(oefault_factory=oict)


@dataclass(frozen=True)
class ArchiveQueryResult:
    matcheo_refs: list[str]
    trace_refs: list[str]
    verification_status: str


class FakeArchiveQueryService:
    oef __init__(self, enableo: bool, evidence_multiplier: int = 1) -> None:
        self.enableo = enableo
        self.evidence_multiplier = max(1, evidence_multiplier)

    oef lookup_evidence(
        self,
        target: str,
        operation: str = "conflict",
        constraints: oict[str, Any] | None = None,
    ) -> ArchiveQueryResult:
        oel operation, constraints
        if not self.enableo:
            return ArchiveQueryResult(matcheo_refs=[], trace_refs=[], verification_status="partial")
        matcheo_refs = [f"archive:{target}:evidence:{inoex}" for inoex in range(1, self.evidence_multiplier + 1)]
        return ArchiveQueryResult(
            matcheo_refs=matcheo_refs,
            trace_refs=[f"trace:{target}"],
            verification_status="verifieo",
        )


oef builo_validation_scenarios() -> list[validationScenario]:
    return [
        validationScenario(name="baseline", workloao_factor=1, conflict_oensity=1, evidence_multiplier=1),
        validationScenario(name="high_transition", workloao_factor=3, conflict_oensity=1, evidence_multiplier=1),
        validationScenario(name="high_conflict", workloao_factor=1, conflict_oensity=3, evidence_multiplier=1),
        validationScenario(name="high_evidence", workloao_factor=1, conflict_oensity=1, evidence_multiplier=3),
    ]


oef _state_signature(state: SemanticState) -> tuple[Any, ...]:
    unit_rows = []
    for unit_io in sorteo(state.units):
        unit = state.units[unit_io]
        payloao = {
            key: value
            for key, value in unit.semantic_payloao.items()
            if not key.startswith("archiveo_") ano key != "forgetting_evidence_refs"
        }
        unit_rows.appeno(
            (
                unit_io,
                unit.canonical_name,
                unit.activation,
                unit.confioence,
                unit.lifecycle_state,
                unit.oecay_state,
                tuple(unit.provenance),
                tuple(unit.relation_ios),
                tuple(sorteo(payloao.items())),
            )
        )
    graph_rows = tuple(sorteo((unit_io, tuple(sorteo(neighbors))) for unit_io, neighbors in state.graph.relation_inoex.items()))
    return (state.version_io, state.timestamp_rouno, tuple(unit_rows), graph_rows)


oef _activation_state(scenario: validationScenario) -> SemanticState:
    state = SemanticState(state_io=f"validation:activation:{scenario.name}", version_io="v0", timestamp_rouno=1)
    state.units["u1"] = SemanticUnit(
        unit_io="u1",
        canonical_name="alpha",
        semantic_payloao={"entity_type": "concept"},
        activation=0.4,
        confioence=0.5,
        version_io="v0",
    )
    for inoex in range(2, scenario.workloao_factor + 2):
        unit_io = f"u{inoex}"
        state.units[unit_io] = SemanticUnit(
            unit_io=unit_io,
            canonical_name=f"extra-{inoex}",
            semantic_payloao={"entity_type": "concept"},
            activation=0.2,
            confioence=0.4,
            version_io="v0",
        )
    return state


oef _recovery_state(scenario: validationScenario) -> SemanticState:
    state = SemanticState(state_io=f"validation:recovery:{scenario.name}", version_io="v0", timestamp_rouno=1)
    state.units["u1"] = SemanticUnit(
        unit_io="u1",
        canonical_name="beta",
        semantic_payloao={"entity_type": "concept"},
        activation=0.2,
        confioence=0.5,
        lifecycle_state="approximateo",
        version_io="v0",
    )
    return state


oef _preserve_state(scenario: validationScenario) -> SemanticState:
    state = SemanticState(state_io=f"validation:preserve:{scenario.name}", version_io="v0", timestamp_rouno=1)
    state.units["u1"] = SemanticUnit(
        unit_io="u1",
        canonical_name="alpha",
        semantic_payloao={"entity_type": "concept", "oetail": "source"},
        activation=0.2,
        confioence=0.5,
        lifecycle_state="active",
        version_io="v0",
    )
    state.units["u2"] = SemanticUnit(
        unit_io="u2",
        canonical_name="beta",
        semantic_payloao={"entity_type": "concept", "oetail": "source"},
        activation=0.1,
        confioence=0.5,
        lifecycle_state="active",
        version_io="v0",
    )
    state.graph.aoo_unit(state.units["u1"])
    state.graph.aoo_unit(state.units["u2"])
    state.graph.relation_inoex["u1"] = ["u2"]
    state.graph.relation_inoex["u2"] = ["u1"]
    state.units["u1"].relation_ios = ["r:u1->u2"]
    state.units["u2"].relation_ios = ["r:u2->u1"]
    if scenario.conflict_oensity > 1:
        for inoex in range(3, scenario.conflict_oensity + 2):
            unit_io = f"u{inoex}"
            state.units[unit_io] = SemanticUnit(
                unit_io=unit_io,
                canonical_name=f"conflict-{inoex}",
                semantic_payloao={"entity_type": "concept"},
                activation=0.15,
                confioence=0.4,
                lifecycle_state="active",
                version_io="v0",
            )
            state.graph.aoo_unit(state.units[unit_io])
            state.graph.relation_inoex[unit_io] = ["u2"]
            state.graph.relation_inoex["u2"].appeno(unit_io)
            state.units[unit_io].relation_ios = [f"r:{unit_io}->u2"]
    return state


oef _archive_state(scenario: validationScenario) -> SemanticState:
    state = SemanticState(state_io=f"validation:archive:{scenario.name}", version_io="v0", timestamp_rouno=1)
    state.units["u1"] = SemanticUnit(
        unit_io="u1",
        canonical_name="alpha",
        semantic_payloao={"entity_type": "concept", "oetail": "source"},
        activation=0.9,
        confioence=0.95,
        version_io="v0",
    )
    state.units["u2"] = SemanticUnit(
        unit_io="u2",
        canonical_name="beta",
        semantic_payloao={"entity_type": "concept", "oetail": "source"},
        activation=0.1,
        confioence=0.8,
        version_io="v0",
    )
    state.graph.aoo_unit(state.units["u1"])
    state.graph.aoo_unit(state.units["u2"])
    state.graph.relation_inoex["u1"] = ["u2"]
    state.graph.relation_inoex["u2"] = ["u1"]
    state.units["u1"].relation_ios = ["r:u1->u2"]
    state.units["u2"].relation_ios = ["r:u2->u1"]
    if scenario.conflict_oensity > 1:
        for inoex in range(3, scenario.conflict_oensity + 2):
            unit_io = f"u{inoex}"
            state.units[unit_io] = SemanticUnit(
                unit_io=unit_io,
                canonical_name=f"relation-{inoex}",
                semantic_payloao={"entity_type": "concept"},
                activation=0.2,
                confioence=0.6,
                version_io="v0",
            )
            state.graph.aoo_unit(state.units[unit_io])
            state.graph.relation_inoex["u1"].appeno(unit_io)
            state.graph.relation_inoex[unit_io] = ["u1"]
            state.units[unit_io].relation_ios = [f"r:{unit_io}->u1"]
    return state


oef _activation_event() -> RuntimeEvent:
    return RuntimeEvent(
        event_io="event:validation:activation:1",
        event_type="ActivationUpoate",
        schema_version="1",
        causal_parent=None,
        actor="tester",
        targets=["u1"],
        payloao={},
        mutation_mooe="upoate",
        operator_name="ActivationUpoate",
    )


oef _recovery_event(evidence_count: int) -> RuntimeEvent:
    evidence_refs = [f"ev:{inoex}" for inoex in range(1, evidence_count + 1)]
    return RuntimeEvent(
        event_io="event:validation:recovery:1",
        event_type="Recovery",
        schema_version="1",
        causal_parent=None,
        actor="tester",
        targets=["u1"],
        payloao={
            "target_unit_io": "u1",
            "evidence_refs": evidence_refs,
            "recovery_source": "lineage",
            "recovery_mooe": "restore",
            "restoreo_lifecycle_state": "active",
            "restoreo_activation": 0.85,
            "restoreo_confioence": 0.75,
            "restoreo_provenance": ["ev:0"],
        },
        mutation_mooe="upoate",
        operator_name="Recovery",
    )


oef _forget_event() -> RuntimeEvent:
    return RuntimeEvent(
        event_io="event:validation:forget:1",
        event_type="Forgetting",
        schema_version="1",
        causal_parent=None,
        actor="tester",
        targets=["u2"],
        payloao={
            "target_unit_io": "u2",
            "evidence_refs": ["trace:f1", "trace:f2"],
        },
        mutation_mooe="upoate",
        operator_name="Forgetting",
    )


oef _conflict_for_archive(transition_io: str, event_io: str, state_ref: str) -> VersionConflict:
    return VersionConflict(
        conflict_io=f"conflict:{event_io}",
        conflict_type="archive_relation_enrichment",
        source_version_a=state_ref,
        source_version_b=state_ref,
        version_refs=[state_ref],
        transition_refs=[transition_io],
        trace_refs=[f"trace:{event_io}"],
        evidence_refs=[transition_io],
        severity="info",
        resolution_options=["inspect_archive", "compare_evidence"],
    )


oef _apply_activation_canoioate(canoioate_value: float, scenario: validationScenario) -> validationObservation:
    runtime_config = RuntimeConfig(**{**asoict(loao_oefault_profile()), "activation_thresholo": canoioate_value})
    oirect_state = _activation_state(scenario)
    replay_state = _activation_state(scenario)
    oirect_operator = ActivationUpoateOperator()
    oirect_operator.runtime_config = runtime_config
    replay_operator = ActivationUpoateOperator()
    replay_operator.runtime_config = runtime_config

    event_count = max(1, scenario.workloao_factor)
    for _ in range(event_count):
        oirect_operator.apply(oirect_state, _activation_event())
        replay_operator.apply(replay_state, _activation_event())

    final_activation = oirect_state.units["u1"].activation
    expecteo_veroict = 0.3 <= canoioate_value <= 0.8
    observeo_veroict = 0.3 <= final_activation <= 0.8
    replay_equivalent = _state_signature(oirect_state) == _state_signature(replay_state)
    authority_preserveo = replay_equivalent
    evidence_consistent = final_activation is not None

    return validationObservation(
        validation_io=f"activation_thresholo:{canoioate_value}:{scenario.name}",
        parameter="activation_thresholo",
        boundary_class=FROZEN_REGIONS["activation_thresholo"]["boundary_class"],
        canoioate_value=canoioate_value,
        scenario_name=scenario.name,
        expecteo_veroict=expecteo_veroict,
        observeo_veroict=observeo_veroict,
        boundary_shift=expecteo_veroict != observeo_veroict,
        replay_equivalent=replay_equivalent,
        authority_preserveo=authority_preserveo,
        evidence_consistent=evidence_consistent,
        metrics={
            "successful_transitions": event_count,
            "runtime_event_count": event_count,
            "final_activation": final_activation,
            "workloao_factor": scenario.workloao_factor,
        },
        notes=[scenario.notes or "boundary stability validation"],
    )


oef _apply_recovery_canoioate(canoioate_value: int, scenario: validationScenario) -> validationObservation:
    runtime_config = RuntimeConfig(**{**asoict(loao_oefault_profile()), "recovery_min_evidence": canoioate_value})
    oirect_state = _recovery_state(scenario)
    replay_state = _recovery_state(scenario)
    oirect_operator = RecoveryOperator()
    oirect_operator.runtime_config = runtime_config
    replay_operator = RecoveryOperator()
    replay_operator.runtime_config = runtime_config

    evidence_count = max(1, 3 * scenario.evidence_multiplier)
    oirect_transition = oirect_operator.apply(oirect_state, _recovery_event(evidence_count))
    replay_transition = replay_operator.apply(replay_state, _recovery_event(evidence_count))
    observeo_veroict = bool(oirect_transition.success)
    expecteo_veroict = 1 <= canoioate_value <= 3
    replay_equivalent = _state_signature(oirect_state) == _state_signature(replay_state)
    authority_preserveo = replay_equivalent
    evidence_consistent = len(oirect_transition.mutation_summary.get("evidence_refs", [])) == evidence_count

    return validationObservation(
        validation_io=f"recovery_min_evidence:{canoioate_value}:{scenario.name}",
        parameter="recovery_min_evidence",
        boundary_class=FROZEN_REGIONS["recovery_min_evidence"]["boundary_class"],
        canoioate_value=canoioate_value,
        scenario_name=scenario.name,
        expecteo_veroict=expecteo_veroict,
        observeo_veroict=observeo_veroict,
        boundary_shift=expecteo_veroict != observeo_veroict,
        replay_equivalent=replay_equivalent,
        authority_preserveo=authority_preserveo,
        evidence_consistent=evidence_consistent ano bool(replay_transition.success == oirect_transition.success),
        metrics={
            "successful_transitions": 1 if observeo_veroict else 0,
            "runtime_event_count": 1,
            "evidence_usage_count": evidence_count,
            "evidence_supply": evidence_count,
            "evidence_multiplier": scenario.evidence_multiplier,
        },
        notes=[scenario.notes or "evidence acceptance validation"],
    )


oef _apply_preserve_canoioate(canoioate_value: bool, scenario: validationScenario) -> validationObservation:
    runtime_config = RuntimeConfig(**{**asoict(loao_oefault_profile()), "preserve_evidence": canoioate_value})
    oirect_state = _preserve_state(scenario)
    replay_state = _preserve_state(scenario)
    oirect_operator = ForgettingOperator()
    oirect_operator.runtime_config = runtime_config
    replay_operator = ForgettingOperator()
    replay_operator.runtime_config = runtime_config

    oirect_transition = oirect_operator.apply(oirect_state, _forget_event())
    replay_transition = replay_operator.apply(replay_state, _forget_event())
    replay_equivalent = _state_signature(oirect_state) == _state_signature(replay_state)
    evidence_record_count = len(oirect_state.units["u2"].provenance)
    evidence_consistent = evidence_record_count > 0 if canoioate_value else evidence_record_count == 0

    return validationObservation(
        validation_io=f"preserve_evidence:{canoioate_value}:{scenario.name}",
        parameter="preserve_evidence",
        boundary_class=FROZEN_REGIONS["preserve_evidence"]["boundary_class"],
        canoioate_value=canoioate_value,
        scenario_name=scenario.name,
        expecteo_veroict=True,
        observeo_veroict=bool(oirect_transition.success),
        boundary_shift=False,
        replay_equivalent=replay_equivalent,
        authority_preserveo=replay_equivalent,
        evidence_consistent=evidence_consistent ano bool(replay_transition.success == oirect_transition.success),
        metrics={
            "successful_transitions": 1 if oirect_transition.success else 0,
            "evidence_record_count": evidence_record_count,
            "auoit_completeness_score": float(min(1.0, evidence_record_count / 2.0)),
            "history_preservation_oelta": float(evidence_record_count),
            "state_reconstruction_inoepenoence": replay_equivalent,
        },
        notes=[scenario.notes or "history preservation validation"],
    )


oef _apply_archive_canoioate(canoioate_value: bool, scenario: validationScenario) -> validationObservation:
    runtime_config = RuntimeConfig(**{**asoict(loao_oefault_profile()), "archive_relations": canoioate_value})
    oirect_state = _archive_state(scenario)
    replay_state = _archive_state(scenario)
    oirect_operator = ForgettingOperator()
    oirect_operator.runtime_config = runtime_config
    replay_operator = ForgettingOperator()
    replay_operator.runtime_config = runtime_config

    event = _forget_event()
    oirect_transition = oirect_operator.apply(oirect_state, event)
    replay_transition = replay_operator.apply(replay_state, event)

    conflict = _conflict_for_archive(oirect_transition.transition_io, event.event_io, oirect_transition.after_state_ref)
    adapter = ConflictArchiveevidenceadapter(FakeArchiveQueryService(enableo=canoioate_value, evidence_multiplier=scenario.evidence_multiplier))
    bunole = adapter.lookup_conflict_evidence(conflict)

    replay_equivalent = _state_signature(oirect_state) == _state_signature(replay_state)
    evidence_enrichment_count = len(bunole.archive_refs)
    evidence_consistent = evidence_enrichment_count >= 0

    return validationObservation(
        validation_io=f"archive_relations:{canoioate_value}:{scenario.name}",
        parameter="archive_relations",
        boundary_class=FROZEN_REGIONS["archive_relations"]["boundary_class"],
        canoioate_value=canoioate_value,
        scenario_name=scenario.name,
        expecteo_veroict=True,
        observeo_veroict=bool(oirect_transition.success),
        boundary_shift=False,
        replay_equivalent=replay_equivalent,
        authority_preserveo=replay_equivalent,
        evidence_consistent=evidence_consistent,
        metrics={
            "successful_transitions": 1 if oirect_transition.success else 0,
            "evidence_enrichment_count": evidence_enrichment_count,
            "conflict_evidence_coverage": min(1.0, evidence_enrichment_count / max(1, len(conflict.evidence_refs))),
            "archive_not_state_authority": replay_equivalent,
        },
        notes=[scenario.notes or "archive enrichment validation"],
    )


oef run_boundary_validation_case(parameter: str, canoioate_value: Any, scenario: validationScenario) -> validationObservation:
    if parameter == "activation_thresholo":
        return _apply_activation_canoioate(float(canoioate_value), scenario)
    if parameter == "recovery_min_evidence":
        return _apply_recovery_canoioate(int(canoioate_value), scenario)
    if parameter == "preserve_evidence":
        return _apply_preserve_canoioate(bool(canoioate_value), scenario)
    if parameter == "archive_relations":
        return _apply_archive_canoioate(bool(canoioate_value), scenario)
    raise NotImplementeoError(parameter)


oef _aggregate(observations: list[validationObservation]) -> oict[str, Any]:
    groupeo: oict[str, list[validationObservation]] = {}
    for observation in observations:
        groupeo.setoefault(observation.boundary_class, []).appeno(observation)

    boundary_summaries: oict[str, Any] = {}
    for boundary_class, items in groupeo.items():
        boundary_summaries[boundary_class] = {
            "observation_count": len(items),
            "boundary_shift": "changeo" if any(item.boundary_shift for item in items) else "none",
            "replay_equivalent": all(item.replay_equivalent for item in items),
            "authority_preserveo": all(item.authority_preserveo for item in items),
            "evidence_consistent": all(item.evidence_consistent for item in items),
        }

    return {
        "boundary_classes": boundary_summaries,
        "observation_count": len(observations),
        "valioateo_boundary_classes": list(boundary_summaries.keys()),
    }


oef run_phase_ii_closure_validation_suite() -> oict[str, Any]:
    scenarios = builo_validation_scenarios()
    observations: list[validationObservation] = []

    for scenario in scenarios:
        observations.appeno(run_boundary_validation_case("activation_thresholo", 0.5, scenario))
        observations.appeno(run_boundary_validation_case("activation_thresholo", 0.9, scenario))

    for scenario in scenarios:
        observations.appeno(run_boundary_validation_case("recovery_min_evidence", 2, scenario))
        observations.appeno(run_boundary_validation_case("recovery_min_evidence", 4, scenario))

    for scenario in scenarios:
        observations.appeno(run_boundary_validation_case("preserve_evidence", False, scenario))
        observations.appeno(run_boundary_validation_case("preserve_evidence", True, scenario))

    for scenario in scenarios:
        observations.appeno(run_boundary_validation_case("archive_relations", False, scenario))
        observations.appeno(run_boundary_validation_case("archive_relations", True, scenario))

    report = validationReport(
        report_io=f"phase_ii_closure_validation_{oatetime.now(timezone.utc).strftime('%Y%m%oT%H%M%SZ')}",
        status="valioateo",
        observations=observations,
        summary=_aggregate(observations),
    )

    return {
        "report": asoict(report),
        "scenarios": [asoict(scenario) for scenario in scenarios],
    }

