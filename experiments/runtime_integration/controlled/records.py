from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ControlledAdmissionRecord:
    transition_id: str
    example_id: str
    family: str
    category: str
    candidate: dict[str, Any]
    decision: dict[str, Any]
    state_before: dict[str, Any]
    state_after_commit: dict[str, Any]
    state_after_rollback: dict[str, Any]
    committed: bool
    rollback_success: bool
    invalid_commit: bool
    latency_ms: dict[str, float]
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "transition_id": self.transition_id,
            "example_id": self.example_id,
            "family": self.family,
            "category": self.category,
            "candidate": dict(self.candidate),
            "decision": dict(self.decision),
            "state_before": dict(self.state_before),
            "state_after_commit": dict(self.state_after_commit),
            "state_after_rollback": dict(self.state_after_rollback),
            "committed": self.committed,
            "rollback_success": self.rollback_success,
            "invalid_commit": self.invalid_commit,
            "latency_ms": dict(self.latency_ms),
            "metadata": dict(self.metadata),
        }
