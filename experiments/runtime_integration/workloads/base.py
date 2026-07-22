from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RuntimeIntegrationExample:
    example_id: str
    family: str
    category: str
    description: str
    conversation: str
    state_before: dict[str, Any]
    candidate_payload: dict[str, Any]
    expected_decision: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "example_id": self.example_id,
            "family": self.family,
            "category": self.category,
            "description": self.description,
            "conversation": self.conversation,
            "state_before": dict(self.state_before),
            "candidate_payload": dict(self.candidate_payload),
            "expected_decision": self.expected_decision,
            "metadata": dict(self.metadata),
        }
