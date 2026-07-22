from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class RuntimeIntegrationTrace:
    transition_id: str
    example_id: str
    family: str
    category: str
    validation: dict[str, Any] = field(default_factory=dict)
    evidence: dict[str, Any] = field(default_factory=dict)
    governance: dict[str, Any] = field(default_factory=dict)
    execution: dict[str, Any] = field(default_factory=dict)
    timing: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "transition_id": self.transition_id,
            "example_id": self.example_id,
            "family": self.family,
            "category": self.category,
            "validation": dict(self.validation),
            "evidence": dict(self.evidence),
            "governance": dict(self.governance),
            "execution": dict(self.execution),
            "timing": dict(self.timing),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "RuntimeIntegrationTrace":
        return cls(
            transition_id=str(payload.get("transition_id") or "unknown"),
            example_id=str(payload.get("example_id") or "unknown"),
            family=str(payload.get("family") or "unknown"),
            category=str(payload.get("category") or "unknown"),
            validation=dict(payload.get("validation") or {}),
            evidence=dict(payload.get("evidence") or {}),
            governance=dict(payload.get("governance") or {}),
            execution=dict(payload.get("execution") or {}),
            timing=dict(payload.get("timing") or {}),
            metadata=dict(payload.get("metadata") or {}),
        )
