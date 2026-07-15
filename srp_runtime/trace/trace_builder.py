from __future__ import annotations

from dataclasses import dataclass, field

from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel.transition import TransitionResult


@dataclass
class TraceRecord:
    trace_id: str
    event_id: str
    transition_id: str
    causal_parent: str | None
    rule_id: str | None
    operator_name: str
    metric_evidence_ref: str | None
    mutation_mode: str
    before_version: str
    after_version: str
    changed_objects: list[str] = field(default_factory=list)
    changed_relations: list[str] = field(default_factory=list)
    explanation: str = ""


class TraceBuilder:
    def record_transition(
        self,
        event: RuntimeEvent,
        transition: TransitionResult,
    ) -> TraceRecord:
        return TraceRecord(
            trace_id=f"trace:{transition.transition_id}",
            event_id=event.event_id,
            transition_id=transition.transition_id,
            causal_parent=event.causal_parent,
            rule_id=transition.mutation_summary.get("rule_id"),
            operator_name=transition.operator_name,
            metric_evidence_ref=transition.metric_evidence_ref,
            mutation_mode=event.mutation_mode,
            before_version=transition.before_state_ref,
            after_version=transition.after_state_ref,
            changed_objects=list(transition.changed_unit_ids),
            changed_relations=list(transition.changed_relation_ids),
            explanation=transition.mutation_summary.get(
                "explanation", f"Transition recorded for {event.event_type}"
            ),
        )
