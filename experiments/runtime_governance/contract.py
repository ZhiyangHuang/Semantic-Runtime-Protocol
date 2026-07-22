from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

DEFAULT_CONTRACT_ID = "runtime_governance_contract_v1"
DEFAULT_CASE_SCHEMA_VERSION = "transition_case.v1"
DEFAULT_RESULT_SCHEMA_VERSION = "governance_result.v1"


def _coerce_mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    return {"value": value}


@dataclass(frozen=True)
class TransitionCase:
    state_before: Any
    delta: Any
    evidence: Any
    governance_policy: Any
    expected_decision: bool | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "state_before": self.state_before,
            "delta": self.delta,
            "evidence": self.evidence,
            "governance_policy": self.governance_policy,
            "expected_decision": self.expected_decision,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "TransitionCase":
        return cls(
            state_before=payload.get("state_before"),
            delta=payload.get("delta"),
            evidence=payload.get("evidence"),
            governance_policy=payload.get("governance_policy"),
            expected_decision=payload.get("expected_decision"),
            metadata=_coerce_mapping(payload.get("metadata")),
        )


@dataclass(frozen=True)
class TransitionTrace:
    transition_id: str
    validation: dict[str, Any] = field(default_factory=dict)
    evidence: dict[str, Any] = field(default_factory=dict)
    governance: dict[str, Any] = field(default_factory=dict)
    execution: dict[str, Any] = field(default_factory=dict)
    timing: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "transition_id": self.transition_id,
            "validation": dict(self.validation),
            "evidence": dict(self.evidence),
            "governance": dict(self.governance),
            "execution": dict(self.execution),
            "timing": dict(self.timing),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "TransitionTrace":
        return cls(
            transition_id=str(payload.get("transition_id") or "unknown"),
            validation=_coerce_mapping(payload.get("validation")),
            evidence=_coerce_mapping(payload.get("evidence")),
            governance=_coerce_mapping(payload.get("governance")),
            execution=_coerce_mapping(payload.get("execution")),
            timing=_coerce_mapping(payload.get("timing")),
            metadata=_coerce_mapping(payload.get("metadata")),
        )


@dataclass(frozen=True)
class GovernanceResult:
    accepted: bool
    state_changed: bool
    authority_changed: bool
    rollback_valid: bool
    verification_score: float
    decision_reason: str | None = None
    metrics: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    trace: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "state_changed": self.state_changed,
            "authority_changed": self.authority_changed,
            "rollback_valid": self.rollback_valid,
            "verification_score": self.verification_score,
            "decision_reason": self.decision_reason,
            "metrics": dict(self.metrics),
            "metadata": dict(self.metadata),
            "trace": dict(self.trace),
        }

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "GovernanceResult":
        return cls(
            accepted=bool(payload.get("accepted", False)),
            state_changed=bool(payload.get("state_changed", False)),
            authority_changed=bool(payload.get("authority_changed", False)),
            rollback_valid=bool(payload.get("rollback_valid", False)),
            verification_score=float(payload.get("verification_score", 0.0) or 0.0),
            decision_reason=payload.get("decision_reason"),
            metrics=_coerce_mapping(payload.get("metrics")),
            metadata=_coerce_mapping(payload.get("metadata")),
            trace=_coerce_mapping(payload.get("trace")),
        )


@dataclass(frozen=True)
class RuntimeGovernanceEvaluationContract:
    contract_id: str = DEFAULT_CONTRACT_ID
    case_schema_version: str = DEFAULT_CASE_SCHEMA_VERSION
    result_schema_version: str = DEFAULT_RESULT_SCHEMA_VERSION
    description: str = (
        "Frozen evaluation contract for governance-first semantic transition experiments."
    )

    def as_dict(self) -> dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "case_schema_version": self.case_schema_version,
            "result_schema_version": self.result_schema_version,
            "description": self.description,
        }
