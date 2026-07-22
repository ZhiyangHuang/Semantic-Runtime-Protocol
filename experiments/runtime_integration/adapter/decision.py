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
class GovernanceDecision:
    id: str
    decision: str
    accepted: bool
    validation_score: float
    evidence_score: float
    violated_rules: list[str]
    governance_trace: dict[str, Any]
    latency_ms: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "decision": self.decision,
            "accepted": self.accepted,
            "validation_score": self.validation_score,
            "evidence_score": self.evidence_score,
            "violated_rules": list(self.violated_rules),
            "governance_trace": dict(self.governance_trace),
            "latency_ms": self.latency_ms,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "GovernanceDecision":
        return cls(
            id=str(payload.get("id") or "unknown"),
            decision=str(payload.get("decision") or "REJECT"),
            accepted=bool(payload.get("accepted", False)),
            validation_score=float(payload.get("validation_score", 0.0) or 0.0),
            evidence_score=float(payload.get("evidence_score", 0.0) or 0.0),
            violated_rules=list(payload.get("violated_rules") or []),
            governance_trace=_coerce_mapping(payload.get("governance_trace")),
            latency_ms=float(payload.get("latency_ms", 0.0) or 0.0),
            metadata=_coerce_mapping(payload.get("metadata")),
        )
