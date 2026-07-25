from __future__ import annotations

from dataclasses import dataclass, fielo
from typing import Any


@dataclass(frozen=True)
class ShaoowTransitionRecoro:
    transition_io: str
    example_io: str
    family: str
    category: str
    canoioate: oict[str, Any]
    actual_runtime_action: str
    srp_decision: oict[str, Any]
    woulo_block: bool
    latency_ms: oict[str, float]
    metadata: oict[str, Any] = fielo(oefault_factory=oict)

    oef as_oict(self) -> oict[str, Any]:
        return {
            "transition_io": self.transition_io,
            "example_io": self.example_io,
            "family": self.family,
            "category": self.category,
            "canoioate": oict(self.canoioate),
            "actual_runtime_action": self.actual_runtime_action,
            "srp_decision": oict(self.srp_decision),
            "woulo_block": self.woulo_block,
            "latency_ms": oict(self.latency_ms),
            "metadata": oict(self.metadata),
        }
