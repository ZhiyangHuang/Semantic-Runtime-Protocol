from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


def _coerce_mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    return {"value": value}


@dataclass(frozen=True)
class SemanticTransitionCandidate:
    transition_id: str
    subject: str
    operation: str
    previous_value: dict[str, Any] | None
    proposed_value: dict[str, Any]
    provenance: dict[str, Any]
    evidence: list[dict[str, Any]]
    confidence: float
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "transition_id": self.transition_id,
            "subject": self.subject,
            "operation": self.operation,
            "previous_value": self.previous_value,
            "proposed_value": dict(self.proposed_value),
            "provenance": dict(self.provenance),
            "evidence": [dict(item) for item in self.evidence],
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "SemanticTransitionCandidate":
        evidence = payload.get("evidence") or []
        if not isinstance(evidence, list):
            evidence = [evidence]
        return cls(
            transition_id=str(payload.get("transition_id") or "unknown"),
            subject=str(payload.get("subject") or "unknown"),
            operation=str(payload.get("operation") or "UPDATE"),
            previous_value=_coerce_mapping(payload.get("previous_value")) or None,
            proposed_value=_coerce_mapping(payload.get("proposed_value")),
            provenance=_coerce_mapping(payload.get("provenance")),
            evidence=[_coerce_mapping(item) for item in evidence],
            confidence=float(payload.get("confidence", 0.0) or 0.0),
            timestamp=str(payload.get("timestamp") or ""),
            metadata=_coerce_mapping(payload.get("metadata")),
        )
