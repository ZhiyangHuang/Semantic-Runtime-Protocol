from __future__ import annotations

from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel.transition import TransitionResult
from srp_runtime.operators.base import SemanticOperator
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


class MergeOperator(SemanticOperator):
    def apply(self, state: SemanticState, event: RuntimeEvent) -> TransitionResult:
        before_state_ref = state.state_ref()
        source_ids = list(dict.fromkeys(event.targets))
        if len(source_ids) < 2:
            return TransitionResult(
                transition_id=f"tr:{event.event_id}",
                event_id=event.event_id,
                operator_name="MergeOperator",
                before_state_ref=before_state_ref,
                after_state_ref=before_state_ref,
                changed_unit_ids=[],
                changed_relation_ids=[],
                mutation_summary={
                    "operator": "MergeOperator",
                    "targets": list(event.targets),
                    "operation": "merge",
                },
                invariant_checks=["merge.targets.minimum"],
                success=False,
                failure_reason="merge requires at least two source units",
                timestamp_round=state.timestamp_round,
            )

        source_units = [state.units[source_id] for source_id in source_ids if source_id in state.units]
        if len(source_units) < 2:
            return TransitionResult(
                transition_id=f"tr:{event.event_id}",
                event_id=event.event_id,
                operator_name="MergeOperator",
                before_state_ref=before_state_ref,
                after_state_ref=before_state_ref,
                changed_unit_ids=[],
                changed_relation_ids=[],
                mutation_summary={
                    "operator": "MergeOperator",
                    "targets": list(event.targets),
                    "operation": "merge",
                },
                invariant_checks=["merge.targets.present"],
                success=False,
                failure_reason="merge requires existing source units",
                timestamp_round=state.timestamp_round,
            )

        merged_id = str(event.payload.get("merged_unit_id") or event.payload.get("target_unit_id") or f"merged:{event.event_id}")
        canonical_name = str(
            event.payload.get(
                "canonical_name",
                source_units[0].canonical_name if source_units else merged_id,
            )
        )
        aliases = list(event.payload.get("aliases", []))
        provenance = list(event.payload.get("provenance", []))
        lineage = list(event.payload.get("lineage", []))
        semantic_payload = dict(event.payload.get("semantic_payload", source_units[0].semantic_payload if source_units else {}))

        merged_aliases: list[str] = list(aliases)
        merged_provenance: list[str] = list(provenance)
        merged_lineage: list[str] = list(lineage)
        merged_relation_ids: list[str] = []
        activations: list[float] = []
        confidences: list[float] = []
        drift_scores: list[float] = []
        last_used_rounds: list[int] = []
        updated_rounds: list[int] = []

        for source in source_units:
            merged_aliases.extend([source.canonical_name, *source.aliases])
            merged_provenance.extend(source.provenance)
            merged_lineage.extend(source.lineage)
            merged_lineage.append(source.unit_id)
            merged_relation_ids.extend(source.relation_ids)
            activations.append(float(source.activation))
            confidences.append(float(source.confidence))
            drift_scores.append(float(source.drift_score))
            last_used_rounds.append(int(source.last_used_round))
            updated_rounds.append(int(source.updated_round))
            source.lifecycle_state = "merged"
            source.updated_round = state.timestamp_round + 1
            source.version_id = event.event_id
            source.provenance = _dedupe(source.provenance + [event.event_id])

        state.units[merged_id] = SemanticUnit(
            unit_id=merged_id,
            canonical_name=canonical_name,
            aliases=_dedupe(merged_aliases),
            lineage=_dedupe(merged_lineage),
            provenance=_dedupe(merged_provenance + [event.event_id]),
            semantic_payload=semantic_payload,
            activation=max(activations) if activations else 0.0,
            confidence=sum(confidences) / len(confidences) if confidences else 0.0,
            lifecycle_state=str(event.payload.get("lifecycle_state", "merged")),
            drift_score=sum(drift_scores) / len(drift_scores) if drift_scores else 0.0,
            last_used_round=max(last_used_rounds) if last_used_rounds else state.timestamp_round,
            updated_round=state.timestamp_round + 1,
            decay_state=str(event.payload.get("decay_state", "stable")),
            approximation_target=None,
            relation_ids=_dedupe(merged_relation_ids + list(event.payload.get("relation_ids", []))),
            version_id=str(event.payload.get("version_id", event.event_id)),
        )
        state.graph.add_unit(state.units[merged_id])
        state.graph.relation_index[merged_id] = _dedupe(
            [neighbor for source_id in source_ids for neighbor in state.graph.relation_index.get(source_id, [])]
        )
        for source_id in source_ids:
            state.graph.relation_index.setdefault(source_id, list(state.graph.relation_index.get(source_id, [])))

        changed_unit_ids = _dedupe([*source_ids, merged_id])
        changed_relation_ids = _dedupe(merged_relation_ids + state.graph.relation_index.get(merged_id, []))

        return TransitionResult(
            transition_id=f"tr:{event.event_id}",
            event_id=event.event_id,
            operator_name="MergeOperator",
            before_state_ref=before_state_ref,
            after_state_ref=state.state_ref(),
            changed_unit_ids=changed_unit_ids,
            changed_relation_ids=changed_relation_ids,
            mutation_summary={
                "operator": "MergeOperator",
                "operation": "merge",
                "targets": source_ids,
                "source_units": source_ids,
                "target_unit": merged_id,
                "canonical_name": canonical_name,
            },
            invariant_checks=[
                "merge.targets.minimum",
                "lineage.preserved",
                "provenance.preserved",
                "identity.continuity",
            ],
            success=True,
            timestamp_round=state.timestamp_round + 1,
        )
