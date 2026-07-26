from __future__ import annotations

from srp_runtime.semantic.unit import SemanticUnit
from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel.transition import TransitionResult
from srp_runtime.operators.base import SemanticOperator
from srp_runtime.semantic.state import SemanticState


class IdentityUpdateOperator(SemanticOperator):
    def apply(self, state: SemanticState, event: RuntimeEvent) -> TransitionResult:
        before_state_ref = state.state_ref()
        changed_unit_ids: list[str] = []
        changed_relation_ids: list[str] = []
        for unit_id in event.targets:
            unit = state.units.get(unit_id)
            if unit is None:
                unit = SemanticUnit(
                    unit_id=unit_id,
                    canonical_name=str(event.payload.get("canonical_name", unit_id)),
                )
                state.units[unit_id] = unit
                state.graph.add_unit(unit)
            canonical_name = event.payload.get("canonical_name")
            if canonical_name is not None:
                if unit.canonical_name and canonical_name != unit.canonical_name:
                    unit.aliases = list(dict.fromkeys(unit.aliases + [unit.canonical_name]))
                unit.canonical_name = str(canonical_name)
            aliases = event.payload.get("aliases")
            if aliases is not None:
                unit.aliases = list(dict.fromkeys(unit.aliases + list(aliases)))
            alias = event.payload.get("alias")
            if alias is not None:
                unit.aliases = list(dict.fromkeys(unit.aliases + [str(alias)]))
            provenance = event.payload.get("provenance")
            if provenance is not None:
                unit.provenance = list(dict.fromkeys(unit.provenance + list(provenance)))
            lineage = event.payload.get("lineage")
            if lineage is not None:
                unit.lineage = list(dict.fromkeys(unit.lineage + list(lineage)))
            semantic_payload = event.payload.get("semantic_payload")
            if semantic_payload is not None:
                unit.semantic_payload = dict(semantic_payload)
            version_id = event.payload.get("version_id")
            if version_id is not None:
                unit.version_id = str(version_id)
            unit.lifecycle_state = str(event.payload.get("lifecycle_state", unit.lifecycle_state))
            unit.drift_score = float(event.payload.get("drift_score", unit.drift_score))
            unit.updated_round = int(event.payload.get("updated_round", unit.updated_round))
            changed_unit_ids.append(unit_id)
        return TransitionResult(
            transition_id=f"tr:{event.event_id}",
            event_id=event.event_id,
            operator_name="IdentityUpdateOperator",
            before_state_ref=before_state_ref,
            after_state_ref=state.state_ref(),
            changed_unit_ids=changed_unit_ids,
            changed_relation_ids=changed_relation_ids,
            mutation_summary={
                "operator": "IdentityUpdateOperator",
                "targets": list(event.targets),
            },
            invariant_checks=["unit_id.immutable", "aliases.deduplicated"],
            success=True,
            timestamp_round=state.timestamp_round + 1,
        )
