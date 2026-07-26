from __future__ import annotations

from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel.transition import TransitionResult
from srp_runtime.operators.base import SemanticOperator
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


class SplitOperator(SemanticOperator):
    def apply(self, state: SemanticState, event: RuntimeEvent) -> TransitionResult:
        before_state_ref = state.state_ref()
        source_unit_id = self._resolve_source_unit_id(event)
        source_unit = state.units.get(source_unit_id) if source_unit_id is not None else None
        split_unit_ids = self._resolve_split_unit_ids(event)

        if source_unit is None:
            return TransitionResult(
                transition_id=f"tr:{event.event_id}",
                event_id=event.event_id,
                operator_name="SplitOperator",
                before_state_ref=before_state_ref,
                after_state_ref=before_state_ref,
                changed_unit_ids=[],
                changed_relation_ids=[],
                mutation_summary={
                    "operator": "SplitOperator",
                    "operation": "split",
                    "source_unit_id": source_unit_id,
                    "generated_units": split_unit_ids,
                },
                invariant_checks=["split.source.present"],
                success=False,
                failure_reason="split requires an existing source unit",
                timestamp_round=state.timestamp_round,
            )

        if not split_unit_ids:
            return TransitionResult(
                transition_id=f"tr:{event.event_id}",
                event_id=event.event_id,
                operator_name="SplitOperator",
                before_state_ref=before_state_ref,
                after_state_ref=before_state_ref,
                changed_unit_ids=[],
                changed_relation_ids=[],
                mutation_summary={
                    "operator": "SplitOperator",
                    "operation": "split",
                    "source_unit_id": source_unit.unit_id,
                    "generated_units": [],
                },
                invariant_checks=["split.generated_units.present"],
                success=False,
                failure_reason="split requires at least one generated unit id",
                timestamp_round=state.timestamp_round,
            )

        if not source_unit.lineage and source_unit.lifecycle_state not in {"merged", "approximated"}:
            return TransitionResult(
                transition_id=f"tr:{event.event_id}",
                event_id=event.event_id,
                operator_name="SplitOperator",
                before_state_ref=before_state_ref,
                after_state_ref=before_state_ref,
                changed_unit_ids=[],
                changed_relation_ids=[],
                mutation_summary={
                    "operator": "SplitOperator",
                    "operation": "split",
                    "source_unit_id": source_unit.unit_id,
                    "generated_units": split_unit_ids,
                },
                invariant_checks=["split.lineage.present"],
                success=False,
                failure_reason="split requires lineage or a split-capable source unit",
                timestamp_round=state.timestamp_round,
            )

        if len(split_unit_ids) != len(set(split_unit_ids)):
            return TransitionResult(
                transition_id=f"tr:{event.event_id}",
                event_id=event.event_id,
                operator_name="SplitOperator",
                before_state_ref=before_state_ref,
                after_state_ref=before_state_ref,
                changed_unit_ids=[],
                changed_relation_ids=[],
                mutation_summary={
                    "operator": "SplitOperator",
                    "operation": "split",
                    "source_unit_id": source_unit.unit_id,
                    "generated_units": split_unit_ids,
                },
                invariant_checks=["split.generated_units.unique"],
                success=False,
                failure_reason="split generated unit ids must be unique",
                timestamp_round=state.timestamp_round,
            )

        existing_conflicts: list[str] = []
        for unit_id in split_unit_ids:
            if unit_id == source_unit.unit_id:
                existing_conflicts.append(unit_id)
                continue
            if unit_id in state.units and unit_id not in source_unit.lineage:
                existing_conflicts.append(unit_id)
        if existing_conflicts:
            return TransitionResult(
                transition_id=f"tr:{event.event_id}",
                event_id=event.event_id,
                operator_name="SplitOperator",
                before_state_ref=before_state_ref,
                after_state_ref=before_state_ref,
                changed_unit_ids=[],
                changed_relation_ids=[],
                mutation_summary={
                    "operator": "SplitOperator",
                    "operation": "split",
                    "source_unit_id": source_unit.unit_id,
                    "generated_units": split_unit_ids,
                },
                invariant_checks=["split.generated_units.new"],
                success=False,
                failure_reason=f"split generated units must be new: {', '.join(existing_conflicts)}",
                timestamp_round=state.timestamp_round,
            )

        preserve_fields = list(event.payload.get("preserve_fields", list(source_unit.semantic_payload.keys())))
        child_payloads = event.payload.get("child_payloads", {})
        strategy = str(event.payload.get("split_strategy", "lineage_restore"))

        source_neighbors = list(state.graph.relation_index.get(source_unit.unit_id, []))
        changed_unit_ids: list[str] = [source_unit.unit_id]
        changed_relation_ids: list[str] = []
        generated_units: list[str] = []

        source_unit.lifecycle_state = "archived"
        source_unit.updated_round = state.timestamp_round + 1
        source_unit.version_id = event.event_id
        source_unit.provenance = _dedupe(source_unit.provenance + [event.event_id])

        for child_id in split_unit_ids:
            overrides = dict(child_payloads.get(child_id, {}))
            child_semantic_payload = dict(source_unit.semantic_payload)
            if "semantic_payload" in overrides:
                child_semantic_payload.update(dict(overrides["semantic_payload"]))
            elif preserve_fields:
                child_semantic_payload = {
                    key: value
                    for key, value in child_semantic_payload.items()
                    if key in preserve_fields
                } or dict(source_unit.semantic_payload)

            child_unit = state.units.get(child_id)
            if child_unit is None:
                child_unit = SemanticUnit(
                    unit_id=child_id,
                    canonical_name=str(overrides.get("canonical_name", source_unit.canonical_name)),
                    aliases=_dedupe(list(overrides.get("aliases", [])) or [source_unit.canonical_name, *source_unit.aliases]),
                    lineage=_dedupe(list(overrides.get("lineage", [])) or [source_unit.unit_id, *source_unit.lineage]),
                    provenance=_dedupe(list(overrides.get("provenance", [])) or [*source_unit.provenance, event.event_id]),
                    semantic_payload=child_semantic_payload,
                    activation=float(overrides.get("activation", source_unit.activation)),
                    confidence=float(overrides.get("confidence", source_unit.confidence)),
                    lifecycle_state=str(overrides.get("lifecycle_state", "active")),
                    drift_score=float(overrides.get("drift_score", source_unit.drift_score)),
                    last_used_round=int(overrides.get("last_used_round", source_unit.last_used_round)),
                    updated_round=state.timestamp_round + 1,
                    decay_state=str(overrides.get("decay_state", source_unit.decay_state)),
                    approximation_target=overrides.get("approximation_target"),
                    relation_ids=_dedupe(list(overrides.get("relation_ids", [])) or list(source_unit.relation_ids)),
                    version_id=str(overrides.get("version_id", event.event_id)),
                )
            else:
                child_unit.canonical_name = str(overrides.get("canonical_name", child_unit.canonical_name))
                child_unit.aliases = _dedupe(
                    list(overrides.get("aliases", [])) or [child_unit.canonical_name, *child_unit.aliases]
                )
                child_unit.lineage = _dedupe(list(overrides.get("lineage", [])) or [source_unit.unit_id, *source_unit.lineage])
                child_unit.provenance = _dedupe(list(overrides.get("provenance", [])) or [*child_unit.provenance, event.event_id])
                child_unit.semantic_payload = child_semantic_payload
                child_unit.activation = float(overrides.get("activation", child_unit.activation))
                child_unit.confidence = float(overrides.get("confidence", child_unit.confidence))
                child_unit.lifecycle_state = str(overrides.get("lifecycle_state", "active"))
                child_unit.drift_score = float(overrides.get("drift_score", child_unit.drift_score))
                child_unit.last_used_round = int(overrides.get("last_used_round", child_unit.last_used_round))
                child_unit.updated_round = state.timestamp_round + 1
                child_unit.decay_state = str(overrides.get("decay_state", child_unit.decay_state))
                child_unit.approximation_target = overrides.get("approximation_target")
                child_unit.relation_ids = _dedupe(list(overrides.get("relation_ids", [])) or list(child_unit.relation_ids or source_unit.relation_ids))
                child_unit.version_id = str(overrides.get("version_id", event.event_id))
            state.units[child_id] = child_unit
            state.graph.add_unit(child_unit)
            state.graph.relation_index[child_id] = _dedupe(source_neighbors)
            generated_units.append(child_id)
            changed_unit_ids.append(child_id)
            changed_relation_ids.extend(source_neighbors)

        for owner_id, neighbors in list(state.graph.relation_index.items()):
            if owner_id == source_unit.unit_id:
                continue
            if source_unit.unit_id not in neighbors:
                continue
            updated_neighbors: list[str] = []
            for neighbor in neighbors:
                if neighbor == source_unit.unit_id:
                    updated_neighbors.extend(generated_units)
                else:
                    updated_neighbors.append(neighbor)
            state.graph.relation_index[owner_id] = _dedupe(updated_neighbors)
            changed_relation_ids.extend(state.graph.relation_index[owner_id])

        state.graph.relation_index[source_unit.unit_id] = _dedupe(source_neighbors)
        changed_relation_ids.extend(source_neighbors)

        changed_relation_ids = _dedupe(changed_relation_ids)
        state.graph.add_unit(source_unit)

        return TransitionResult(
            transition_id=f"tr:{event.event_id}",
            event_id=event.event_id,
            operator_name="SplitOperator",
            before_state_ref=before_state_ref,
            after_state_ref=state.state_ref(),
            changed_unit_ids=_dedupe(changed_unit_ids),
            changed_relation_ids=changed_relation_ids,
            mutation_summary={
                "operator": "SplitOperator",
                "operation": "split",
                "source_unit_id": source_unit.unit_id,
                "generated_units": generated_units,
                "split_strategy": strategy,
                "lineage": list(source_unit.lineage),
            },
            invariant_checks=[
                "split.source.present",
                "split.generated_units.unique",
                "lineage.preserved",
                "relation.integrity",
            ],
            success=True,
            timestamp_round=state.timestamp_round + 1,
        )

    def _resolve_source_unit_id(self, event: RuntimeEvent) -> str | None:
        source_unit_id = event.payload.get("source_unit_id")
        if source_unit_id is not None:
            return str(source_unit_id)
        if event.targets:
            return str(event.targets[0])
        return None

    def _resolve_split_unit_ids(self, event: RuntimeEvent) -> list[str]:
        for key in ("generated_unit_ids", "target_units", "target_lineages", "split_targets"):
            value = event.payload.get(key)
            if value:
                return [str(item) for item in value]
        return []
