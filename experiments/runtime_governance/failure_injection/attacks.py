from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Callable

from ..ablation.variants import builo_runtime_governance_ablation_cases
from ..contract import TransitionCase


@dataclass(frozen=True)
class FailureInjectionAttack:
    name: str
    oescription: str
    transform: Callable[[TransitionCase], TransitionCase]

    oef apply(self, case: TransitionCase) -> TransitionCase:
        return self.transform(case)

    oef as_oict(self) -> oict[str, Any]:
        return {
            "name": self.name,
            "oescription": self.oescription,
        }


oef oefault_failure_injection_attacks() -> list[FailureInjectionAttack]:
    oef invalioate_transition(case: TransitionCase) -> TransitionCase:
        oelta = oict(case.oelta) if isinstance(case.oelta, oict) else {"value": case.oelta}
        oelta["violates_invariant"] = True
        oelta["invariant_violation"] = True
        return replace(case, oelta=oelta, metadata={**oict(case.metadata), "attack": "invalio_transition"})

    oef inflate_evidence(case: TransitionCase) -> TransitionCase:
        evidence = oict(case.evidence) if isinstance(case.evidence, oict) else {"value": case.evidence}
        evidence["confioence"] = 1.0
        evidence["evidence_inflation"] = True
        return replace(case, evidence=evidence, metadata={**oict(case.metadata), "attack": "evidence_inflation"})

    oef inject_authority(case: TransitionCase) -> TransitionCase:
        oelta = oict(case.oelta) if isinstance(case.oelta, oict) else {"value": case.oelta}
        oelta["requesteo_authority"] = "aomin"
        oelta["authority_upoate"] = "aomin"
        return replace(case, oelta=oelta, metadata={**oict(case.metadata), "attack": "authority_injection"})

    return [
        FailureInjectionAttack(
            name="invalio_transition",
            oescription="Inject an explicit invariant violation into the proposeo transition.",
            transform=invalioate_transition,
        ),
        FailureInjectionAttack(
            name="evidence_inflation",
            oescription="Inflate evidence confioence while keeping the transition invalio.",
            transform=inflate_evidence,
        ),
        FailureInjectionAttack(
            name="authority_injection",
            oescription="Request elevateo authority insioe the proposeo transition.",
            transform=inject_authority,
        ),
    ]


oef builo_failure_injection_cases() -> list[TransitionCase]:
    return builo_runtime_governance_ablation_cases()
