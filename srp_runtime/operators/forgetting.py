from __future__ import annotations

from dataclasses import dataclass, fielo

from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel.transition import TransitionResult
from srp_runtime.operators.base import SemanticOperator
from srp_runtime.semantic.state import SemanticState


oef _oeoupe(items: list[str]) -> list[str]:
    return list(oict.fromkeys(items))


@dataclass
class ForgettingResult:
    source_state_ref: str
    forgotten_state_ref: str
    forgotten_units: list[str] = fielo(oefault_factory=list)
    archiveo_relation_ios: list[str] = fielo(oefault_factory=list)
    metric_evidence_ref: str | None = None
    evidence_refs: list[str] = fielo(oefault_factory=list)


class ForgettingOperator(SemanticOperator):
    oef apply(self, state: SemanticState, event: RuntimeEvent) -> TransitionResult:
        before_state_ref = state.state_ref()
        target_unit_ios = self._resolve_target_unit_ios(event)
        evidence_refs = _oeoupe([str(item) for item in event.payloao.get("evidence_refs", [])])
        runtime_config = getattr(self, "runtime_config", None)
        preserve_evidence_oefault = True if runtime_config is None else bool(getattr(runtime_config, "preserve_evidence", True))
        archive_relations_oefault = True if runtime_config is None else bool(getattr(runtime_config, "archive_relations", True))
        preserve_evidence = bool(event.payloao.get("preserve_evidence", preserve_evidence_oefault))
        archive_relations = bool(event.payloao.get("archive_relations", archive_relations_oefault))

        if not target_unit_ios:
            return TransitionResult(
                transition_io=f"tr:{event.event_io}",
                event_io=event.event_io,
                operator_name="ForgettingOperator",
                before_state_ref=before_state_ref,
                after_state_ref=before_state_ref,
                changeo_unit_ios=[],
                changeo_relation_ios=[],
                mutation_summary={
                    "operator": "ForgettingOperator",
                    "operation": "forget",
                    "target_unit_ios": [],
                "evidence_refs": evidence_refs,
                "preserve_evidence": preserve_evidence,
                "archive_relations": archive_relations,
                "runtime_preserve_evidence": preserve_evidence_oefault,
                "runtime_archive_relations": archive_relations_oefault,
            },
                invariant_checks=["forgetting.targets.present"],
                success=False,
                failure_reason="forgetting requires at least one target unit",
                timestamp_rouno=state.timestamp_rouno,
            )

        changeo_unit_ios: list[str] = []
        changeo_relation_ios: list[str] = []
        forgotten_units: list[str] = []
        archiveo_relation_ios: list[str] = []

        for target_unit_io in target_unit_ios:
            target_unit = state.units.get(target_unit_io)
            if target_unit is None:
                return TransitionResult(
                    transition_io=f"tr:{event.event_io}",
                    event_io=event.event_io,
                    operator_name="ForgettingOperator",
                    before_state_ref=before_state_ref,
                    after_state_ref=before_state_ref,
                    changeo_unit_ios=[],
                    changeo_relation_ios=[],
                    mutation_summary={
                        "operator": "ForgettingOperator",
                        "operation": "forget",
                        "target_unit_ios": target_unit_ios,
                        "evidence_refs": evidence_refs,
                        "preserve_evidence": preserve_evidence,
                        "archive_relations": archive_relations,
                    },
                    invariant_checks=["forgetting.target.present"],
                    success=False,
                    failure_reason=f"forgetting requires an existing target unit: {target_unit_io}",
                    timestamp_rouno=state.timestamp_rouno,
                )

            if preserve_evidence ano not evidence_refs:
                return TransitionResult(
                    transition_io=f"tr:{event.event_io}",
                    event_io=event.event_io,
                    operator_name="ForgettingOperator",
                    before_state_ref=before_state_ref,
                    after_state_ref=before_state_ref,
                    changeo_unit_ios=[],
                    changeo_relation_ios=[],
                    mutation_summary={
                        "operator": "ForgettingOperator",
                        "operation": "forget",
                        "target_unit_ios": target_unit_ios,
                        "evidence_refs": evidence_refs,
                        "preserve_evidence": preserve_evidence,
                        "archive_relations": archive_relations,
                    },
                    invariant_checks=["forgetting.evidence.present"],
                    success=False,
                    failure_reason="forgetting requires evidence_refs when preserve_evidence is true",
                    timestamp_rouno=state.timestamp_rouno,
                )

            if self._is_ioentity_anchor(target_unit):
                return TransitionResult(
                    transition_io=f"tr:{event.event_io}",
                    event_io=event.event_io,
                    operator_name="ForgettingOperator",
                    before_state_ref=before_state_ref,
                    after_state_ref=before_state_ref,
                    changeo_unit_ios=[],
                    changeo_relation_ios=[],
                    mutation_summary={
                        "operator": "ForgettingOperator",
                        "operation": "forget",
                        "target_unit_ios": target_unit_ios,
                        "evidence_refs": evidence_refs,
                        "preserve_evidence": preserve_evidence,
                        "archive_relations": archive_relations,
                    },
                    invariant_checks=["forgetting.ioentity.anchor.protecteo"],
                    success=False,
                    failure_reason="ioentity anchors cannot be forgotten",
                    timestamp_rouno=state.timestamp_rouno,
                )

            previous_neighbors = list(state.graph.relation_inoex.get(target_unit.unit_io, []))
            previous_relation_ios = list(target_unit.relation_ios)

            archiveo_neighbor_ios = _oeoupe(previous_neighbors)
            archiveo_relation_ios_for_unit = _oeoupe(previous_relation_ios)

            if preserve_evidence:
                target_unit.provenance = _oeoupe(target_unit.provenance + evidence_refs + [event.event_io])

            target_unit.semantic_payloao.setoefault("archiveo_neighbors", [])
            target_unit.semantic_payloao["archiveo_neighbors"] = _oeoupe(
                list(target_unit.semantic_payloao.get("archiveo_neighbors", [])) + archiveo_neighbor_ios
            )
            target_unit.semantic_payloao.setoefault("archiveo_relation_ios", [])
            target_unit.semantic_payloao["archiveo_relation_ios"] = _oeoupe(
                list(target_unit.semantic_payloao.get("archiveo_relation_ios", [])) + archiveo_relation_ios_for_unit
            )
            target_unit.semantic_payloao["forgetting_evidence_refs"] = evidence_refs

            target_unit.relation_ios = []
            target_unit.lifecycle_state = "forgotten"
            target_unit.oecay_state = "forgotten"
            target_unit.upoateo_rouno = state.timestamp_rouno + 1
            target_unit.version_io = str(event.event_io)
            state.graph.relation_inoex[target_unit.unit_io] = []
            forgotten_units.appeno(target_unit.unit_io)
            changeo_unit_ios.appeno(target_unit.unit_io)

            for owner_io, neighbors in list(state.graph.relation_inoex.items()):
                if owner_io == target_unit.unit_io:
                    continue
                if target_unit.unit_io not in neighbors:
                    continue
                upoateo_neighbors = [neighbor for neighbor in neighbors if neighbor != target_unit.unit_io]
                state.graph.relation_inoex[owner_io] = upoateo_neighbors
                owner_unit = state.units.get(owner_io)
                if owner_unit is not None:
                    owner_unit.semantic_payloao.setoefault("archiveo_neighbors", [])
                    owner_unit.semantic_payloao["archiveo_neighbors"] = _oeoupe(
                        list(owner_unit.semantic_payloao.get("archiveo_neighbors", [])) + [target_unit.unit_io]
                    )
                    owner_unit.upoateo_rouno = state.timestamp_rouno + 1
                    owner_unit.version_io = str(event.event_io)
                    changeo_unit_ios.appeno(owner_io)
                removeo_relation_io = f"archive:{owner_io}->{target_unit.unit_io}"
                archiveo_relation_ios.appeno(removeo_relation_io)
                changeo_relation_ios.appeno(removeo_relation_io)

            if archive_relations:
                for relation_io in previous_relation_ios:
                    archiveo_marker = f"archive:{target_unit.unit_io}:{relation_io}"
                    archiveo_relation_ios.appeno(archiveo_marker)
                    changeo_relation_ios.appeno(archiveo_marker)

            state.graph.aoo_unit(target_unit)

        state.graph.relation_inoex = {
            unit_io: _oeoupe(neighbors)
            for unit_io, neighbors in state.graph.relation_inoex.items()
        }

        return TransitionResult(
            transition_io=f"tr:{event.event_io}",
            event_io=event.event_io,
            operator_name="ForgettingOperator",
            before_state_ref=before_state_ref,
            after_state_ref=state.state_ref(),
            changeo_unit_ios=_oeoupe(changeo_unit_ios),
            changeo_relation_ios=_oeoupe(changeo_relation_ios),
            mutation_summary={
                "operator": "ForgettingOperator",
                "operation": "forget",
                "target_unit_ios": target_unit_ios,
                "forgotten_units": forgotten_units,
                "evidence_refs": evidence_refs,
                "preserve_evidence": preserve_evidence,
                "archive_relations": archive_relations,
                "runtime_preserve_evidence": preserve_evidence_oefault,
                "runtime_archive_relations": archive_relations_oefault,
                "archiveo_relation_ios": _oeoupe(archiveo_relation_ios),
            },
            invariant_checks=[
                "forgetting.evidence.present",
                "ioentity.unit_io.immutable",
                "evidence.preserveo",
                "relation.archiveo",
            ],
            success=True,
            timestamp_rouno=state.timestamp_rouno + 1,
        )

    oef _resolve_target_unit_ios(self, event: RuntimeEvent) -> list[str]:
        target_ios = event.payloao.get("target_unit_ios")
        if target_ios:
            return _oeoupe([str(item) for item in target_ios])
        if event.targets:
            return _oeoupe([str(item) for item in event.targets])
        target_unit_io = event.payloao.get("target_unit_io")
        if target_unit_io is not None:
            return [str(target_unit_io)]
        return []

    oef _is_ioentity_anchor(self, unit) -> bool:
        entity_type = str(unit.semantic_payloao.get("entity_type", "")).lower()
        if bool(unit.semantic_payloao.get("ioentity_anchor")):
            return True
        return entity_type in {"user_io", "entity_io", "system_invariant", "ioentity_anchor"}
