from __future__ import annotations

from dataclasses import dataclass, field

from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel.transition import TransitionResult
from srp_runtime.operators.base import SemanticOperator
from srp_runtime.semantic.state import SemanticState


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


@dataclass
class RecoveryResult:
    source_state_ref: str
    recovered_state_ref: str
    restored_units: list[str] = field(default_factory=list)
    recovery_loss: float = 0.0
    metric_evidence_ref: str | None = None
    evidence_refs: list[str] = field(default_factory=list)


class RecoveryOperator(SemanticOperator):
    def apply(self, state: SemanticState, event: RuntimeEvent) -> TransitionResult:
        before_state_ref = state.state_ref()
        target_unit_id = self._resolve_target_unit_id(event)
        target_unit = state.units.get(target_unit_id) if target_unit_id is not None else None
        evidence_refs = list(dict.fromkeys(event.payload.get("evidence_refs", [])))
        recovery_source = str(event.payload.get("recovery_source", "lineage"))
        recovery_mode = str(event.payload.get("recovery_mode", "restore"))

        if target_unit is None:
            return TransitionResult(
                transition_id=f"tr:{event.event_id}",
                event_id=event.event_id,
                operator_name="RecoveryOperator",
                before_state_ref=before_state_ref,
                after_state_ref=before_state_ref,
                changed_unit_ids=[],
                changed_relation_ids=[],
                mutation_summary={
                    "operator": "RecoveryOperator",
                    "operation": "recovery",
                    "target_unit_id": target_unit_id,
                    "recovery_source": recovery_source,
                    "recovery_mode": recovery_mode,
                    "evidence_refs": evidence_refs,
                },
                invariant_checks=["recovery.target.present"],
                success=False,
                failure_reason="recovery requires an existing target unit",
                timestamp_round=state.timestamp_round,
            )

        if not evidence_refs:
            return TransitionResult(
                transition_id=f"tr:{event.event_id}",
                event_id=event.event_id,
                operator_name="RecoveryOperator",
                before_state_ref=before_state_ref,
                after_state_ref=before_state_ref,
                changed_unit_ids=[],
                changed_relation_ids=[],
                mutation_summary={
                    "operator": "RecoveryOperator",
                    "operation": "recovery",
                    "target_unit_id": target_unit.unit_id,
                    "recovery_source": recovery_source,
                    "recovery_mode": recovery_mode,
                    "evidence_refs": evidence_refs,
                },
                invariant_checks=["recovery.evidence.present"],
                success=False,
                failure_reason="recovery requires evidence_refs",
                timestamp_round=state.timestamp_round,
            )

        if target_unit.lifecycle_state not in {"approximated", "archived", "forgotten", "merged"}:
            return TransitionResult(
                transition_id=f"tr:{event.event_id}",
                event_id=event.event_id,
                operator_name="RecoveryOperator",
                before_state_ref=before_state_ref,
                after_state_ref=before_state_ref,
                changed_unit_ids=[],
                changed_relation_ids=[],
                mutation_summary={
                    "operator": "RecoveryOperator",
                    "operation": "recovery",
                    "target_unit_id": target_unit.unit_id,
                    "recovery_source": recovery_source,
                    "recovery_mode": recovery_mode,
                    "evidence_refs": evidence_refs,
                },
                invariant_checks=["recovery.target.recoverable"],
                success=False,
                failure_reason="recovery requires a recoverable target state",
                timestamp_round=state.timestamp_round,
            )

        restored_canonical_name = event.payload.get("restored_canonical_name")
        restored_aliases = event.payload.get("restored_aliases")
        restored_lineage = event.payload.get("restored_lineage")
        restored_provenance = event.payload.get("restored_provenance")
        restored_semantic_payload = event.payload.get("restored_semantic_payload")
        restored_relation_ids = event.payload.get("restored_relation_ids")
        restored_neighbors = event.payload.get("restored_neighbors")
        restored_activation = event.payload.get("restored_activation")
        restored_confidence = event.payload.get("restored_confidence")
        restored_drift_score = event.payload.get("restored_drift_score")
        restored_decay_state = event.payload.get("restored_decay_state", "stable")
        restored_version_id = event.payload.get("restored_version_id", event.event_id)
        restored_last_used_round = event.payload.get("restored_last_used_round", state.timestamp_round + 1)
        restored_updated_round = event.payload.get("restored_updated_round", state.timestamp_round + 1)
        restored_lifecycle_state = str(event.payload.get("restored_lifecycle_state", "active"))
        restored_approximation_target = event.payload.get("restored_approximation_target")

        if restored_canonical_name is not None:
            target_unit.canonical_name = str(restored_canonical_name)
        if restored_aliases is not None:
            target_unit.aliases = _dedupe([str(item) for item in restored_aliases])
        if restored_lineage is not None:
            target_unit.lineage = _dedupe([str(item) for item in restored_lineage])
        if restored_provenance is not None:
            target_unit.provenance = _dedupe([str(item) for item in restored_provenance] + evidence_refs + [event.event_id])
        else:
            target_unit.provenance = _dedupe(target_unit.provenance + evidence_refs + [event.event_id])
        if restored_semantic_payload is not None:
            target_unit.semantic_payload = dict(restored_semantic_payload)
        if restored_relation_ids is not None:
            target_unit.relation_ids = _dedupe([str(item) for item in restored_relation_ids])
        if restored_activation is not None:
            target_unit.activation = float(restored_activation)
        if restored_confidence is not None:
            target_unit.confidence = float(restored_confidence)
        if restored_drift_score is not None:
            target_unit.drift_score = float(restored_drift_score)

        if restored_neighbors is not None:
            state.graph.relation_index[target_unit.unit_id] = _dedupe([str(item) for item in restored_neighbors])

        target_unit.lifecycle_state = restored_lifecycle_state
        target_unit.approximation_target = restored_approximation_target
        target_unit.decay_state = str(restored_decay_state)
        target_unit.last_used_round = int(restored_last_used_round)
        target_unit.updated_round = int(restored_updated_round)
        target_unit.version_id = str(restored_version_id)
        state.graph.add_unit(target_unit)

        changed_relation_ids = list(state.graph.relation_index.get(target_unit.unit_id, []))
        changed_unit_ids = [target_unit.unit_id]
        return TransitionResult(
            transition_id=f"tr:{event.event_id}",
            event_id=event.event_id,
            operator_name="RecoveryOperator",
            before_state_ref=before_state_ref,
            after_state_ref=state.state_ref(),
            changed_unit_ids=changed_unit_ids,
            changed_relation_ids=changed_relation_ids,
            mutation_summary={
                "operator": "RecoveryOperator",
                "operation": "recovery",
                "target_unit_id": target_unit.unit_id,
                "recovery_source": recovery_source,
                "recovery_mode": recovery_mode,
                "evidence_refs": evidence_refs,
                "restored_fields": [
                    field
                    for field, value in {
                        "canonical_name": restored_canonical_name,
                        "aliases": restored_aliases,
                        "lineage": restored_lineage,
                        "provenance": restored_provenance,
                        "semantic_payload": restored_semantic_payload,
                        "relation_ids": restored_relation_ids,
                        "neighbors": restored_neighbors,
                        "activation": restored_activation,
                        "confidence": restored_confidence,
                        "drift_score": restored_drift_score,
                        "decay_state": restored_decay_state,
                        "lifecycle_state": restored_lifecycle_state,
                        "approximation_target": restored_approximation_target,
                        "version_id": restored_version_id,
                    }.items()
                    if value is not None
                ],
            },
            invariant_checks=[
                "recovery.evidence.present",
                "identity.unit_id.immutable",
                "provenance.preserved",
                "temporal.forward_only",
            ],
            success=True,
            timestamp_round=state.timestamp_round + 1,
        )

    def _resolve_target_unit_id(self, event: RuntimeEvent) -> str | None:
        target_unit_id = event.payload.get("target_unit_id")
        if target_unit_id is not None:
            return str(target_unit_id)
        if event.targets:
            return str(event.targets[0])
        return None
