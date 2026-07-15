from __future__ import annotations

from dataclasses import dataclass, field

from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel.transition import TransitionResult
from srp_runtime.operators.base import SemanticOperator
from srp_runtime.semantic.state import SemanticState


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


@dataclass
class GCResult:
    source_state_ref: str
    collected_state_ref: str
    collected_unit_ids: list[str] = field(default_factory=list)
    preserved_evidence_refs: list[str] = field(default_factory=list)
    released_storage_refs: list[str] = field(default_factory=list)
    archive_ref: str | None = None
    irreversible: bool = True
    metric_evidence_ref: str | None = None


class GarbageCollectionOperator(SemanticOperator):
    def apply(self, state: SemanticState, event: RuntimeEvent) -> TransitionResult:
        before_state_ref = state.state_ref()
        target_unit_ids = self._resolve_target_unit_ids(event)
        evidence_refs = _dedupe([str(item) for item in event.payload.get("evidence_refs", [])])
        retention_policy = str(event.payload.get("retention_policy", "minimal_provenance"))
        gc_mode = str(event.payload.get("gc_mode", "archive_compaction"))
        archive_ref = str(event.payload.get("archive_ref", f"archive:{event.event_id}"))

        if not target_unit_ids:
            return TransitionResult(
                transition_id=f"tr:{event.event_id}",
                event_id=event.event_id,
                operator_name="GarbageCollectionOperator",
                before_state_ref=before_state_ref,
                after_state_ref=before_state_ref,
                changed_unit_ids=[],
                changed_relation_ids=[],
                mutation_summary={
                    "operator": "GarbageCollectionOperator",
                    "operation": "gc",
                    "target_unit_ids": [],
                    "evidence_refs": evidence_refs,
                    "retention_policy": retention_policy,
                    "gc_mode": gc_mode,
                    "archive_ref": archive_ref,
                },
                invariant_checks=["gc.targets.present"],
                success=False,
                failure_reason="garbage collection requires at least one target unit",
                timestamp_round=state.timestamp_round,
            )

        changed_unit_ids: list[str] = []
        changed_relation_ids: list[str] = []
        collected_units: list[str] = []
        preserved_evidence_refs: list[str] = []
        released_storage_refs: list[str] = []

        for target_unit_id in target_unit_ids:
            target_unit = state.units.get(target_unit_id)
            if target_unit is None:
                return TransitionResult(
                    transition_id=f"tr:{event.event_id}",
                    event_id=event.event_id,
                    operator_name="GarbageCollectionOperator",
                    before_state_ref=before_state_ref,
                    after_state_ref=before_state_ref,
                    changed_unit_ids=[],
                    changed_relation_ids=[],
                    mutation_summary={
                        "operator": "GarbageCollectionOperator",
                        "operation": "gc",
                        "target_unit_ids": target_unit_ids,
                        "evidence_refs": evidence_refs,
                        "retention_policy": retention_policy,
                        "gc_mode": gc_mode,
                        "archive_ref": archive_ref,
                    },
                    invariant_checks=["gc.target.present"],
                    success=False,
                    failure_reason=f"garbage collection requires an existing target unit: {target_unit_id}",
                    timestamp_round=state.timestamp_round,
                )

            if not evidence_refs:
                return TransitionResult(
                    transition_id=f"tr:{event.event_id}",
                    event_id=event.event_id,
                    operator_name="GarbageCollectionOperator",
                    before_state_ref=before_state_ref,
                    after_state_ref=before_state_ref,
                    changed_unit_ids=[],
                    changed_relation_ids=[],
                    mutation_summary={
                        "operator": "GarbageCollectionOperator",
                        "operation": "gc",
                        "target_unit_ids": target_unit_ids,
                        "evidence_refs": evidence_refs,
                        "retention_policy": retention_policy,
                        "gc_mode": gc_mode,
                        "archive_ref": archive_ref,
                    },
                    invariant_checks=["gc.evidence.present"],
                    success=False,
                    failure_reason="garbage collection requires evidence_refs",
                    timestamp_round=state.timestamp_round,
                )

            if self._is_protected(target_unit):
                return TransitionResult(
                    transition_id=f"tr:{event.event_id}",
                    event_id=event.event_id,
                    operator_name="GarbageCollectionOperator",
                    before_state_ref=before_state_ref,
                    after_state_ref=before_state_ref,
                    changed_unit_ids=[],
                    changed_relation_ids=[],
                    mutation_summary={
                        "operator": "GarbageCollectionOperator",
                        "operation": "gc",
                        "target_unit_ids": target_unit_ids,
                        "evidence_refs": evidence_refs,
                        "retention_policy": retention_policy,
                        "gc_mode": gc_mode,
                        "archive_ref": archive_ref,
                    },
                    invariant_checks=["gc.identity.anchor.protected"],
                    success=False,
                    failure_reason="identity anchors cannot be garbage collected",
                    timestamp_round=state.timestamp_round,
                )

            if target_unit.lifecycle_state not in {"forgotten", "archived"}:
                return TransitionResult(
                    transition_id=f"tr:{event.event_id}",
                    event_id=event.event_id,
                    operator_name="GarbageCollectionOperator",
                    before_state_ref=before_state_ref,
                    after_state_ref=before_state_ref,
                    changed_unit_ids=[],
                    changed_relation_ids=[],
                    mutation_summary={
                        "operator": "GarbageCollectionOperator",
                        "operation": "gc",
                        "target_unit_ids": target_unit_ids,
                        "evidence_refs": evidence_refs,
                        "retention_policy": retention_policy,
                        "gc_mode": gc_mode,
                        "archive_ref": archive_ref,
                    },
                    invariant_checks=["gc.target.collectable"],
                    success=False,
                    failure_reason="garbage collection requires forgotten or archived targets",
                    timestamp_round=state.timestamp_round,
                )

            previous_neighbors = list(state.graph.relation_index.get(target_unit.unit_id, []))
            previous_relation_ids = list(target_unit.relation_ids)

            preserved_evidence_refs.extend(evidence_refs)
            released_storage_refs.extend(
                _dedupe(
                    [
                        target_unit.unit_id,
                        *previous_relation_ids,
                        *[f"{target_unit.unit_id}->{neighbor}" for neighbor in previous_neighbors],
                    ]
                )
            )

            for owner_id, neighbors in list(state.graph.relation_index.items()):
                if owner_id == target_unit.unit_id:
                    continue
                if target_unit.unit_id not in neighbors:
                    continue
                updated_neighbors = [neighbor for neighbor in neighbors if neighbor != target_unit.unit_id]
                state.graph.relation_index[owner_id] = updated_neighbors
                owner_unit = state.units.get(owner_id)
                if owner_unit is not None:
                    owner_unit.semantic_payload.setdefault("gc_archived_neighbors", [])
                    owner_unit.semantic_payload["gc_archived_neighbors"] = _dedupe(
                        list(owner_unit.semantic_payload.get("gc_archived_neighbors", [])) + [target_unit.unit_id]
                    )
                    owner_unit.semantic_payload["gc_archive_ref"] = archive_ref
                    owner_unit.updated_round = state.timestamp_round + 1
                    owner_unit.version_id = str(event.event_id)
                    changed_unit_ids.append(owner_id)
                changed_relation_ids.append(f"gc:{owner_id}->{target_unit.unit_id}")

            if target_unit.unit_id in state.graph.relation_index:
                del state.graph.relation_index[target_unit.unit_id]

            target_unit.semantic_payload.setdefault("gc_archive_ref", archive_ref)
            target_unit.semantic_payload["gc_archive_ref"] = archive_ref
            target_unit.semantic_payload["gc_retention_policy"] = retention_policy
            target_unit.semantic_payload["gc_mode"] = gc_mode
            target_unit.semantic_payload["gc_evidence_refs"] = evidence_refs
            target_unit.semantic_payload["gc_previous_neighbors"] = _dedupe(previous_neighbors)
            target_unit.semantic_payload["gc_previous_relation_ids"] = _dedupe(previous_relation_ids)
            target_unit.lifecycle_state = "permanently_removed"
            target_unit.decay_state = "gc"
            target_unit.updated_round = state.timestamp_round + 1
            target_unit.version_id = str(event.event_id)

            state.units.pop(target_unit.unit_id, None)
            state.graph.units.pop(target_unit.unit_id, None)
            collected_units.append(target_unit.unit_id)
            changed_unit_ids.append(target_unit.unit_id)
            changed_relation_ids.extend(previous_relation_ids)

        state.graph.relation_index = {
            unit_id: _dedupe(neighbors)
            for unit_id, neighbors in state.graph.relation_index.items()
        }

        return TransitionResult(
            transition_id=f"tr:{event.event_id}",
            event_id=event.event_id,
            operator_name="GarbageCollectionOperator",
            before_state_ref=before_state_ref,
            after_state_ref=state.state_ref(),
            changed_unit_ids=_dedupe(changed_unit_ids),
            changed_relation_ids=_dedupe(changed_relation_ids),
            mutation_summary={
                "operator": "GarbageCollectionOperator",
                "operation": "gc",
                "target_unit_ids": target_unit_ids,
                "collected_units": collected_units,
                "evidence_refs": evidence_refs,
                "retention_policy": retention_policy,
                "gc_mode": gc_mode,
                "archive_ref": archive_ref,
                "preserved_evidence_refs": _dedupe(preserved_evidence_refs),
                "released_storage_refs": _dedupe(released_storage_refs),
                "irreversible": True,
            },
            invariant_checks=[
                "gc.evidence.present",
                "identity.unit_id.immutable",
                "gc.collectable.state",
                "gc.irreversible",
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

    def _is_protected(self, unit) -> bool:
        entity_type = str(unit.semantic_payload.get("entity_type", "")).lower()
        if bool(unit.semantic_payload.get("identity_anchor")):
            return True
        return entity_type in {"user_id", "entity_id", "system_invariant", "identity_anchor"}
