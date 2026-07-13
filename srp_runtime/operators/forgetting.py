from __future__ import annotations

from dataclasses import dataclass, field

from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel.transition import TransitionResult
from srp_runtime.operators.base import SemanticOperator
from srp_runtime.semantic.state import SemanticState


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


@dataclass
class ForgettingResult:
    source_state_ref: str
    forgotten_state_ref: str
    forgotten_units: list[str] = field(default_factory=list)
    archived_relation_ids: list[str] = field(default_factory=list)
    metric_evidence_ref: str | None = None
    evidence_refs: list[str] = field(default_factory=list)


class ForgettingOperator(SemanticOperator):
    def apply(self, state: SemanticState, event: RuntimeEvent) -> TransitionResult:
        before_state_ref = state.state_ref()
        target_unit_ids = self._resolve_target_unit_ids(event)
        evidence_refs = _dedupe([str(item) for item in event.payload.get("evidence_refs", [])])
        preserve_evidence = bool(event.payload.get("preserve_evidence", True))
        archive_relations = bool(event.payload.get("archive_relations", True))

        if not target_unit_ids:
            return TransitionResult(
                transition_id=f"tr:{event.event_id}",
                event_id=event.event_id,
                operator_name="ForgettingOperator",
                before_state_ref=before_state_ref,
                after_state_ref=before_state_ref,
                changed_unit_ids=[],
                changed_relation_ids=[],
                mutation_summary={
                    "operator": "ForgettingOperator",
                    "operation": "forget",
                    "target_unit_ids": [],
                    "evidence_refs": evidence_refs,
                    "preserve_evidence": preserve_evidence,
                    "archive_relations": archive_relations,
                },
                invariant_checks=["forgetting.targets.present"],
                success=False,
                failure_reason="forgetting requires at least one target unit",
                timestamp_round=state.timestamp_round,
            )

        changed_unit_ids: list[str] = []
        changed_relation_ids: list[str] = []
        forgotten_units: list[str] = []
        archived_relation_ids: list[str] = []

        for target_unit_id in target_unit_ids:
            target_unit = state.units.get(target_unit_id)
            if target_unit is None:
                return TransitionResult(
                    transition_id=f"tr:{event.event_id}",
                    event_id=event.event_id,
                    operator_name="ForgettingOperator",
                    before_state_ref=before_state_ref,
                    after_state_ref=before_state_ref,
                    changed_unit_ids=[],
                    changed_relation_ids=[],
                    mutation_summary={
                        "operator": "ForgettingOperator",
                        "operation": "forget",
                        "target_unit_ids": target_unit_ids,
                        "evidence_refs": evidence_refs,
                        "preserve_evidence": preserve_evidence,
                        "archive_relations": archive_relations,
                    },
                    invariant_checks=["forgetting.target.present"],
                    success=False,
                    failure_reason=f"forgetting requires an existing target unit: {target_unit_id}",
                    timestamp_round=state.timestamp_round,
                )

            if preserve_evidence and not evidence_refs:
                return TransitionResult(
                    transition_id=f"tr:{event.event_id}",
                    event_id=event.event_id,
                    operator_name="ForgettingOperator",
                    before_state_ref=before_state_ref,
                    after_state_ref=before_state_ref,
                    changed_unit_ids=[],
                    changed_relation_ids=[],
                    mutation_summary={
                        "operator": "ForgettingOperator",
                        "operation": "forget",
                        "target_unit_ids": target_unit_ids,
                        "evidence_refs": evidence_refs,
                        "preserve_evidence": preserve_evidence,
                        "archive_relations": archive_relations,
                    },
                    invariant_checks=["forgetting.evidence.present"],
                    success=False,
                    failure_reason="forgetting requires evidence_refs when preserve_evidence is true",
                    timestamp_round=state.timestamp_round,
                )

            if self._is_identity_anchor(target_unit):
                return TransitionResult(
                    transition_id=f"tr:{event.event_id}",
                    event_id=event.event_id,
                    operator_name="ForgettingOperator",
                    before_state_ref=before_state_ref,
                    after_state_ref=before_state_ref,
                    changed_unit_ids=[],
                    changed_relation_ids=[],
                    mutation_summary={
                        "operator": "ForgettingOperator",
                        "operation": "forget",
                        "target_unit_ids": target_unit_ids,
                        "evidence_refs": evidence_refs,
                        "preserve_evidence": preserve_evidence,
                        "archive_relations": archive_relations,
                    },
                    invariant_checks=["forgetting.identity.anchor.protected"],
                    success=False,
                    failure_reason="identity anchors cannot be forgotten",
                    timestamp_round=state.timestamp_round,
                )

            previous_neighbors = list(state.graph.relation_index.get(target_unit.unit_id, []))
            previous_relation_ids = list(target_unit.relation_ids)

            archived_neighbor_ids = _dedupe(previous_neighbors)
            archived_relation_ids_for_unit = _dedupe(previous_relation_ids)

            if preserve_evidence:
                target_unit.provenance = _dedupe(target_unit.provenance + evidence_refs + [event.event_id])

            target_unit.semantic_payload.setdefault("archived_neighbors", [])
            target_unit.semantic_payload["archived_neighbors"] = _dedupe(
                list(target_unit.semantic_payload.get("archived_neighbors", [])) + archived_neighbor_ids
            )
            target_unit.semantic_payload.setdefault("archived_relation_ids", [])
            target_unit.semantic_payload["archived_relation_ids"] = _dedupe(
                list(target_unit.semantic_payload.get("archived_relation_ids", [])) + archived_relation_ids_for_unit
            )
            target_unit.semantic_payload["forgetting_evidence_refs"] = evidence_refs

            target_unit.relation_ids = []
            target_unit.lifecycle_state = "forgotten"
            target_unit.decay_state = "forgotten"
            target_unit.updated_round = state.timestamp_round + 1
            target_unit.version_id = str(event.event_id)
            state.graph.relation_index[target_unit.unit_id] = []
            forgotten_units.append(target_unit.unit_id)
            changed_unit_ids.append(target_unit.unit_id)

            for owner_id, neighbors in list(state.graph.relation_index.items()):
                if owner_id == target_unit.unit_id:
                    continue
                if target_unit.unit_id not in neighbors:
                    continue
                updated_neighbors = [neighbor for neighbor in neighbors if neighbor != target_unit.unit_id]
                state.graph.relation_index[owner_id] = updated_neighbors
                owner_unit = state.units.get(owner_id)
                if owner_unit is not None:
                    owner_unit.semantic_payload.setdefault("archived_neighbors", [])
                    owner_unit.semantic_payload["archived_neighbors"] = _dedupe(
                        list(owner_unit.semantic_payload.get("archived_neighbors", [])) + [target_unit.unit_id]
                    )
                    owner_unit.updated_round = state.timestamp_round + 1
                    owner_unit.version_id = str(event.event_id)
                    changed_unit_ids.append(owner_id)
                removed_relation_id = f"archive:{owner_id}->{target_unit.unit_id}"
                archived_relation_ids.append(removed_relation_id)
                changed_relation_ids.append(removed_relation_id)

            if archive_relations:
                for relation_id in previous_relation_ids:
                    archived_marker = f"archive:{target_unit.unit_id}:{relation_id}"
                    archived_relation_ids.append(archived_marker)
                    changed_relation_ids.append(archived_marker)

            state.graph.add_unit(target_unit)

        state.graph.relation_index = {
            unit_id: _dedupe(neighbors)
            for unit_id, neighbors in state.graph.relation_index.items()
        }

        return TransitionResult(
            transition_id=f"tr:{event.event_id}",
            event_id=event.event_id,
            operator_name="ForgettingOperator",
            before_state_ref=before_state_ref,
            after_state_ref=state.state_ref(),
            changed_unit_ids=_dedupe(changed_unit_ids),
            changed_relation_ids=_dedupe(changed_relation_ids),
            mutation_summary={
                "operator": "ForgettingOperator",
                "operation": "forget",
                "target_unit_ids": target_unit_ids,
                "forgotten_units": forgotten_units,
                "evidence_refs": evidence_refs,
                "preserve_evidence": preserve_evidence,
                "archive_relations": archive_relations,
                "archived_relation_ids": _dedupe(archived_relation_ids),
            },
            invariant_checks=[
                "forgetting.evidence.present",
                "identity.unit_id.immutable",
                "evidence.preserved",
                "relation.archived",
            ],
            success=True,
            timestamp_round=state.timestamp_round + 1,
        )

    def _resolve_target_unit_ids(self, event: RuntimeEvent) -> list[str]:
        target_ids = event.payload.get("target_unit_ids")
        if target_ids:
            return _dedupe([str(item) for item in target_ids])
        if event.targets:
            return _dedupe([str(item) for item in event.targets])
        target_unit_id = event.payload.get("target_unit_id")
        if target_unit_id is not None:
            return [str(target_unit_id)]
        return []

    def _is_identity_anchor(self, unit) -> bool:
        entity_type = str(unit.semantic_payload.get("entity_type", "")).lower()
        if bool(unit.semantic_payload.get("identity_anchor")):
            return True
        return entity_type in {"user_id", "entity_id", "system_invariant", "identity_anchor"}
