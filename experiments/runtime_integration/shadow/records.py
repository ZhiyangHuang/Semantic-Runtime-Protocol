from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ShadowTransitionRecord:
    transition_id: str
    example_id: str
    family: str
    category: str
    candidate: dict[str, Any]
    actual_runtime_action: str
    srp_decision: dict[str, Any]
    would_block: bool
    latency_ms: dict[str, float]
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "transition_id": self.transition_id,
            "example_id": self.example_id,
            "family": self.family,
            "category": self.category,
            "candidate": dict(self.candidate),
            "actual_runtime_action": self.actual_runtime_action,
            "srp_decision": dict(self.srp_decision),
            "would_block": self.would_block,
            "latency_ms": dict(self.latency_ms),
            "metadata": dict(self.metadata),
        }
