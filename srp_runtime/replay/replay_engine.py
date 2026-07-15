from __future__ import annotations

from dataclasses import dataclass, field

from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel.runtime_kernel import RuntimeKernel
from srp_runtime.semantic.state import SemanticState
from srp_runtime.trace.trace_builder import TraceRecord


@dataclass
class ReplayResult:
    replay_id: str
    initial_state_ref: str
    final_state_ref: str
    replay_mode: str
    reconstructed_state: SemanticState
    applied_event_ids: list[str] = field(default_factory=list)
    failed_event_ids: list[str] = field(default_factory=list)
    divergence_points: list[str] = field(default_factory=list)
    replay_drift: float = 0.0
    validation_result: dict[str, object] = field(default_factory=dict)
    trace_records: list[TraceRecord] = field(default_factory=list)


class ReplayEngine:
    def replay(
        self,
        initial_state: SemanticState,
        event_stream: list[RuntimeEvent],
    ) -> ReplayResult:
        kernel = RuntimeKernel(state=initial_state.snapshot())
        applied_events: list[str] = []
        failed_events: list[str] = []
        for event in event_stream:
            result = kernel.submit_event(event)
            if result.status == "applied":
                applied_events.append(event.event_id)
            else:
                failed_events.append(event.event_id)
        return ReplayResult(
            replay_id=f"replay:{initial_state.state_ref()}:{len(event_stream)}",
            initial_state_ref=initial_state.state_ref(),
            final_state_ref=kernel._state.state_ref(),
            replay_mode="deterministic",
            reconstructed_state=kernel._state,
            applied_event_ids=applied_events,
            failed_event_ids=failed_events,
            trace_records=kernel.trace_records,
        )
