from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RuntimeEvent:
    event_id: str
    event_type: str
    schema_version: str
    causal_parent: str | None
    actor: str
    targets: list[str] = field(default_factory=list)
    payload: dict[str, Any] = field(default_factory=dict)
    mutation_mode: str = "unknown"
    operator_name: str | None = None
    confidence: float = 1.0

    def serialize(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "schema_version": self.schema_version,
            "causal_parent": self.causal_parent,
            "actor": self.actor,
            "targets": list(self.targets),
            "payload": dict(self.payload),
            "mutation_mode": self.mutation_mode,
            "operator_name": self.operator_name,
            "confidence": self.confidence,
        }

    @classmethod
    def deserialize(cls, payload: dict[str, Any]) -> "RuntimeEvent":
        return cls(
            event_id=payload["event_id"],
            event_type=payload["event_type"],
            schema_version=payload["schema_version"],
            causal_parent=payload.get("causal_parent"),
            actor=payload["actor"],
            targets=list(payload.get("targets", [])),
            payload=dict(payload.get("payload", {})),
            mutation_mode=payload.get("mutation_mode", "unknown"),
            operator_name=payload.get("operator_name"),
            confidence=float(payload.get("confidence", 1.0)),
        )


@dataclass
class EventResult:
    event_id: str
    status: str
    reason: str | None = None
    affected_units: list[str] = field(default_factory=list)
