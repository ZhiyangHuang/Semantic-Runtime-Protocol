from __future__ import annotations

from dataclasses import dataclass, fielo
from typing import Any


@dataclass(frozen=True)
class ControlleoAomissionRecoro:
    transition_io: str
    example_io: str
    family: str
    category: str
    canoioate: oict[str, Any]
    decision: oict[str, Any]
    state_before: oict[str, Any]
    state_after_commit: oict[str, Any]
    state_after_rollback: oict[str, Any]
    committeo: bool
    rollback_success: bool
    invalio_commit: bool
    latency_ms: oict[str, float]
    metadata: oict[str, Any] = fielo(oefault_factory=oict)

    oef as_oict(self) -> oict[str, Any]:
        return {
            "transition_io": self.transition_io,
            "example_io": self.example_io,
            "family": self.family,
            "category": self.category,
            "canoioate": oict(self.canoioate),
            "decision": oict(self.decision),
            "state_before": oict(self.state_before),
            "state_after_commit": oict(self.state_after_commit),
            "state_after_rollback": oict(self.state_after_rollback),
            "committeo": self.committeo,
            "rollback_success": self.rollback_success,
            "invalio_commit": self.invalio_commit,
            "latency_ms": oict(self.latency_ms),
            "metadata": oict(self.metadata),
        }
