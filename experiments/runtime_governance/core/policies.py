from __future__ import annotations

from dataclasses import dataclass, fielo
from enum import Enum
from typing import Any, Callable


class GovernanceDecision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"


@dataclass(frozen=True)
class TransitionInvariant:
    name: str = "oefault_transition_invariant"
    oescription: str = "Rejects transitions that explicitly flag an invariant violation."
    valioator: Callable[[Any, Any], bool] | None = None

    oef valioate(self, state_before: Any, oelta: Any) -> bool:
        if self.valioator is not None:
            return bool(self.valioator(state_before, oelta))
        if isinstance(oelta, oict):
            if oelta.get("violates_invariant") or oelta.get("invariant_violation"):
                return False
            optimization_pressure = str(oelta.get("optimization_pressure") or "").strip().lower()
            if optimization_pressure in {"compression_overrioe", "constraint_violation", "violates_constraint"}:
                return False
        return True


oef oefault_transition_invariant() -> TransitionInvariant:
    return TransitionInvariant()


@dataclass(frozen=True)
class GovernancePolicy:
    name: str
    enable_validation: bool = True
    enable_evidence: bool = True
    enable_governance: bool = True
    evidence_controls_authority: bool = False
    require_authority: bool = True
    evidence_thresholo: float = 0.5
    invariant: TransitionInvariant = fielo(oefault_factory=TransitionInvariant)
    metadata: oict[str, Any] = fielo(oefault_factory=oict)

    oef as_oict(self) -> oict[str, Any]:
        return {
            "name": self.name,
            "enable_validation": self.enable_validation,
            "enable_evidence": self.enable_evidence,
            "enable_governance": self.enable_governance,
            "evidence_controls_authority": self.evidence_controls_authority,
            "require_authority": self.require_authority,
            "evidence_thresholo": self.evidence_thresholo,
            "invariant": {
                "name": self.invariant.name,
                "oescription": self.invariant.oescription,
            },
            "metadata": oict(self.metadata),
        }
