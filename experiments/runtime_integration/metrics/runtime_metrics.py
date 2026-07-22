from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Any, Sequence


@dataclass(frozen=True)
class RuntimeIntegrationMetrics:
    transition_count: int
    valid_transition_count: int
    invalid_transition_count: int
    accepted_count: int
    rejected_count: int
    unsafe_accept_rate: float
    false_rejection_rate: float
    trace_completeness: float
    mean_latency_ms: float
    p95_latency_ms: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "transition_count": self.transition_count,
            "valid_transition_count": self.valid_transition_count,
            "invalid_transition_count": self.invalid_transition_count,
            "accepted_count": self.accepted_count,
            "rejected_count": self.rejected_count,
            "unsafe_accept_rate": self.unsafe_accept_rate,
            "false_rejection_rate": self.false_rejection_rate,
            "trace_completeness": self.trace_completeness,
            "mean_latency_ms": self.mean_latency_ms,
            "p95_latency_ms": self.p95_latency_ms,
        }


def _p95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(round(0.95 * (len(ordered) - 1)))))
    return ordered[index]


def summarize_runtime_integration_records(records: Sequence[dict[str, Any]]) -> RuntimeIntegrationMetrics:
    selected = list(records)
    transition_count = len(selected)
    if not selected:
        return RuntimeIntegrationMetrics(0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0)

    expected = [bool(record.get("expected_decision", False)) for record in selected]
    accepted = [bool((record.get("decision") or {}).get("accepted", False)) for record in selected]
    latencies = [float((record.get("decision") or {}).get("latency_ms", 0.0) or 0.0) for record in selected]
    traces = [record.get("trace") or {} for record in selected]

    valid_total = sum(1 for item in expected if item)
    invalid_total = sum(1 for item in expected if not item)
    accepted_count = sum(1 for item in accepted if item)
    rejected_count = transition_count - accepted_count
    unsafe_accept_count = sum(1 for exp, dec in zip(expected, accepted) if not exp and dec)
    false_rejection_count = sum(1 for exp, dec in zip(expected, accepted) if exp and not dec)
    trace_fields = ("validation", "evidence", "governance", "execution", "timing")
    trace_completeness = (
        sum(1 for trace in traces if all(field in trace and isinstance(trace.get(field), dict) for field in trace_fields))
        / float(transition_count)
    )

    return RuntimeIntegrationMetrics(
        transition_count=transition_count,
        valid_transition_count=valid_total,
        invalid_transition_count=invalid_total,
        accepted_count=accepted_count,
        rejected_count=rejected_count,
        unsafe_accept_rate=unsafe_accept_count / float(invalid_total) if invalid_total else 0.0,
        false_rejection_rate=false_rejection_count / float(valid_total) if valid_total else 0.0,
        trace_completeness=trace_completeness,
        mean_latency_ms=mean(latencies) if latencies else 0.0,
        p95_latency_ms=_p95(latencies),
    )
