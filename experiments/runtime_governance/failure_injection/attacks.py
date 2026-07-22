from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Callable

from ..ablation.variants import build_runtime_governance_ablation_cases
from ..contract import TransitionCase


@dataclass(frozen=True)
class FailureInjectionAttack:
    name: str
    description: str
    transform: Callable[[TransitionCase], TransitionCase]

    def apply(self, case: TransitionCase) -> TransitionCase:
        return self.transform(case)

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
        }


def default_failure_injection_attacks() -> list[FailureInjectionAttack]:
    def invalidate_transition(case: TransitionCase) -> TransitionCase:
        delta = dict(case.delta) if isinstance(case.delta, dict) else {"value": case.delta}
        delta["violates_invariant"] = True
        delta["invariant_violation"] = True
        return replace(case, delta=delta, metadata={**dict(case.metadata), "attack": "invalid_transition"})

    def inflate_evidence(case: TransitionCase) -> TransitionCase:
        evidence = dict(case.evidence) if isinstance(case.evidence, dict) else {"value": case.evidence}
        evidence["confidence"] = 1.0
        evidence["evidence_inflation"] = True
        return replace(case, evidence=evidence, metadata={**dict(case.metadata), "attack": "evidence_inflation"})

    def inject_authority(case: TransitionCase) -> TransitionCase:
        delta = dict(case.delta) if isinstance(case.delta, dict) else {"value": case.delta}
        delta["requested_authority"] = "admin"
        delta["authority_update"] = "admin"
        return replace(case, delta=delta, metadata={**dict(case.metadata), "attack": "authority_injection"})

    return [
        FailureInjectionAttack(
            name="invalid_transition",
            description="Inject an explicit invariant violation into the proposed transition.",
            transform=invalidate_transition,
        ),
        FailureInjectionAttack(
            name="evidence_inflation",
            description="Inflate evidence confidence while keeping the transition invalid.",
            transform=inflate_evidence,
        ),
        FailureInjectionAttack(
            name="authority_injection",
            description="Request elevated authority inside the proposed transition.",
            transform=inject_authority,
        ),
    ]


def build_failure_injection_cases() -> list[TransitionCase]:
    return build_runtime_governance_ablation_cases()
