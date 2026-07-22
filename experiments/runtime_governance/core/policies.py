from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class GovernanceDecision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"


@dataclass(frozen=True)
class TransitionInvariant:
    name: str = "default_transition_invariant"
    description: str = "Rejects transitions that explicitly flag an invariant violation."
    validator: Callable[[Any, Any], bool] | None = None

    def validate(self, state_before: Any, delta: Any) -> bool:
        if self.validator is not None:
            return bool(self.validator(state_before, delta))
        if isinstance(delta, dict):
            if delta.get("violates_invariant") or delta.get("invariant_violation"):
                return False
            optimization_pressure = str(delta.get("optimization_pressure") or "").strip().lower()
            if optimization_pressure in {"compression_override", "constraint_violation", "violates_constraint"}:
                return False
        return True


def default_transition_invariant() -> TransitionInvariant:
    return TransitionInvariant()


@dataclass(frozen=True)
class GovernancePolicy:
    name: str
    enable_validation: bool = True
    enable_evidence: bool = True
    enable_governance: bool = True
    evidence_controls_authority: bool = False
    require_authority: bool = True
    evidence_threshold: float = 0.5
    invariant: TransitionInvariant = field(default_factory=TransitionInvariant)
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "enable_validation": self.enable_validation,
            "enable_evidence": self.enable_evidence,
            "enable_governance": self.enable_governance,
            "evidence_controls_authority": self.evidence_controls_authority,
            "require_authority": self.require_authority,
            "evidence_threshold": self.evidence_threshold,
            "invariant": {
                "name": self.invariant.name,
                "description": self.invariant.description,
            },
            "metadata": dict(self.metadata),
        }
