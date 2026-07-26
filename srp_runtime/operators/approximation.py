from __future__ import annotations

from dataclasses import dataclass, field

from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel.transition import TransitionResult
from srp_runtime.operators.base import SemanticOperator
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


@dataclass
class ApproximationResult:
    source_state_ref: str
    approximate_state_ref: str
    preserved_units: list[str] = field(default_factory=list)
    removed_units: list[str] = field(default_factory=list)
    approximation_loss: float = 0.0
    metric_evidence_ref: str | None = None
    constraints_checked: list[str] = field(default_factory=list)


class ApproximationOperator(SemanticOperator):
    def apply(self, state: SemanticState, event: RuntimeEvent) -> TransitionResult:
        before_state_ref = state.state_ref()
        threshold = float(event.payload.get("activation_threshold", 0.2))
        preserve_fields = list(event.payload.get("preserve_fields", ["entity_type", "name"]))
        representative_id = self._resolve_representative_id(state, event)

        changed_unit_ids: list[str] = []
        changed_relation_ids: list[str] = []
        preserved_units: list[str] = []
        removed_units: list[str] = []
        approximation_losses: list[float] = []

        for unit_id in list(event.targets):
            unit = state.units.get(unit_id)
            if unit is None:
                continue

            if unit.activation >= threshold:
                preserved_units.append(unit_id)
                continue

            removed_units.append(unit_id)
            approximation_loss = max(0.0, min(1.0, 1.0 - float(unit.activation)))
            approximation_losses.append(approximation_loss)

            unit.lifecycle_state = "approximated"
            unit.approximation_target = representative_id
            unit.decay_state = "approximate"
            unit.updated_round = max(unit.updated_round, state.timestamp_round + 1)
            unit.drift_score = max(unit.drift_score, approximation_loss)
            unit.confidence = max(0.0, min(1.0, unit.confidence * 0.9))

            reduced_payload = {
                key: value
                for key, value in unit.semantic_payload.items()
                if key in preserve_fields
            }
            if reduced_payload:
                unit.semantic_payload = reduced_payload

            if representative_id is not None and representative_id != unit.unit_id:
                unit.relation_ids = _dedupe(unit.relation_ids + [f"approx->{representative_id}"])
            changed_unit_ids.append(unit_id)

        if representative_id is not None and representative_id in state.units:
            representative = state.units[representative_id]
            representative.updated_round = max(representative.updated_round, state.timestamp_round + 1)
            changed_unit_ids.append(representative_id)

        approximation_loss = sum(approximation_losses) / len(approximation_losses) if approximation_losses else 0.0
        event_targets = list(dict.fromkeys(event.targets))
        return TransitionResult(
            transition_id=f"tr:{event.event_id}",
            event_id=event.event_id,
            operator_name="ApproximationOperator",
            before_state_ref=before_state_ref,
            after_state_ref=state.state_ref(),
            changed_unit_ids=_dedupe(changed_unit_ids),
            changed_relation_ids=changed_relation_ids,
            mutation_summary={
                "operator": "ApproximationOperator",
                "operation": "approximation",
                "targets": event_targets,
                "preserved_units": preserved_units,
                "removed_units": removed_units,
                "representative_unit_id": representative_id,
                "activation_threshold": threshold,
                "approximation_loss": approximation_loss,
            },
            invariant_checks=[
                "identity.unit_id.immutable",
                "approximation.identity.preserved",
                "approximation.relation.integrity",
            ],
            success=True,
            timestamp_round=state.timestamp_round + 1,
        )

    def _resolve_representative_id(self, state: SemanticState, event: RuntimeEvent) -> str | None:
        candidate_id = event.payload.get("approximation_target_id") or event.payload.get("representative_unit_id")
        if candidate_id is not None and str(candidate_id) in state.units:
            return str(candidate_id)
        if event.targets:
            candidate_units = [state.units[target] for target in event.targets if target in state.units]
            if candidate_units:
                candidate_units.sort(key=lambda unit: (unit.activation, unit.confidence, unit.updated_round), reverse=True)
                return candidate_units[0].unit_id
        return None
