from __future__ import annotations

from srp_runtime.semantic.unit import SemanticUnit
from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel.transition import TransitionResult
from srp_runtime.operators.base import SemanticOperator
from srp_runtime.semantic.state import SemanticState


class ActivationUpdateOperator(SemanticOperator):
    def apply(self, state: SemanticState, event: RuntimeEvent) -> TransitionResult:
        before_state_ref = state.state_ref()
        changed_unit_ids: list[str] = []
        runtime_config = getattr(self, "runtime_config", None)
        runtime_activation_threshold = 0.2 if runtime_config is None else float(getattr(runtime_config, "activation_threshold", 0.2))
        for unit_id in event.targets:
            unit = state.units.get(unit_id)
            if unit is None:
                unit = SemanticUnit(
                    unit_id=unit_id,
                    canonical_name=str(event.payload.get("canonical_name", unit_id)),
                )
                state.units[unit_id] = unit
                state.graph.add_unit(unit)
            if "activation" in event.payload:
                unit.activation = float(event.payload["activation"])
            elif "activation_delta" in event.payload:
                delta = float(event.payload["activation_delta"])
                unit.activation = float(unit.activation + max(delta, runtime_activation_threshold * 0.1))
            else:
                unit.activation = max(float(unit.activation), runtime_activation_threshold)
            if "confidence" in event.payload:
                unit.confidence = float(event.payload["confidence"])
            if "last_used_round" in event.payload:
                unit.last_used_round = int(event.payload["last_used_round"])
            if "updated_round" in event.payload:
                unit.updated_round = int(event.payload["updated_round"])
            else:
                unit.updated_round = max(unit.updated_round, state.timestamp_round + 1)
            changed_unit_ids.append(unit_id)
        return TransitionResult(
            transition_id=f"tr:{event.event_id}",
            event_id=event.event_id,
            operator_name="ActivationUpdateOperator",
            before_state_ref=before_state_ref,
            after_state_ref=state.state_ref(),
            changed_unit_ids=changed_unit_ids,
            changed_relation_ids=[],
            mutation_summary={
                "operator": "ActivationUpdateOperator",
                "targets": list(event.targets),
                "runtime_activation_threshold": runtime_activation_threshold,
            },
            invariant_checks=["activation.range", "semantic_time.updated"],
            success=True,
            timestamp_round=state.timestamp_round + 1,
        )
