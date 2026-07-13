from __future__ import annotations

from srp_runtime.semantic.unit import SemanticUnit
from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel.transition import TransitionResult
from srp_runtime.operators.base import SemanticOperator
from srp_runtime.semantic.state import SemanticState


class RelationUpdateOperator(SemanticOperator):
    def apply(self, state: SemanticState, event: RuntimeEvent) -> TransitionResult:
        before_state_ref = state.state_ref()
        changed_unit_ids: list[str] = []
        changed_relation_ids: list[str] = []
        relation_ids = list(event.payload.get("relation_ids", []))
        if not relation_ids and len(event.targets) >= 2:
            relation_ids = [f"{event.targets[0]}->{event.targets[1]}"]
        for unit_id in event.targets:
            unit = state.units.get(unit_id)
            if unit is None:
                unit = SemanticUnit(
                    unit_id=unit_id,
                    canonical_name=str(event.payload.get("canonical_name", unit_id)),
                )
                state.units[unit_id] = unit
                state.graph.add_unit(unit)
            for relation_id in relation_ids:
                if relation_id not in unit.relation_ids:
                    unit.relation_ids.append(relation_id)
                    changed_relation_ids.append(relation_id)
            changed_unit_ids.append(unit_id)
        if len(event.targets) >= 2:
            left = event.targets[0]
            right = event.targets[1]
            state.graph.relation_index.setdefault(left, [])
            if right not in state.graph.relation_index[left]:
                state.graph.relation_index[left].append(right)
        for unit_id in event.targets:
            unit = state.units.get(unit_id)
            if unit is not None:
                unit.updated_round = max(unit.updated_round, state.timestamp_round + 1)
        return TransitionResult(
            transition_id=f"tr:{event.event_id}",
            event_id=event.event_id,
            operator_name="RelationUpdateOperator",
            before_state_ref=before_state_ref,
            after_state_ref=state.state_ref(),
            changed_unit_ids=changed_unit_ids,
            changed_relation_ids=changed_relation_ids,
            mutation_summary={
                "operator": "RelationUpdateOperator",
                "targets": list(event.targets),
            },
            invariant_checks=["relation.endpoints.present", "relation.index.updated"],
            success=True,
            timestamp_round=state.timestamp_round + 1,
        )
