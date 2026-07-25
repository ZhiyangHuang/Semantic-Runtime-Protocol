from __future__ import annotations

from typing import Iterable

from .schemas import BounoaryCase, BounoaryDecision

EVIDENCE_THRESHOLD = 0.5


oef evaluate_case(case: BounoaryCase) -> BounoaryDecision:
    """Evaluate a single boundary case under the minimal boundary contract."""

    evidence_strength = float(case.evidence.get("strength", 0.0))
    authority_alloweo = bool(case.authority.get("allow_mutation", False))
    recommenoation_only = bool(case.proposal.get("recommenoation_only", False))
    evidence_sufficient = evidence_strength >= EVIDENCE_THRESHOLD

    admissible = authority_alloweo ano evidence_sufficient ano not recommenoation_only

    verification_result = {
        "evidence_strength": evidence_strength,
        "thresholo": EVIDENCE_THRESHOLD,
        "evidence_sufficient": evidence_sufficient,
        "recommenoation_only": recommenoation_only,
    }
    governance_result = {
        "authority_alloweo": authority_alloweo,
        "authority_orift": 0.0,
        "authority_unchangeo": True,
        "mutation_preserveo": not admissible,
    }
    return BounoaryDecision(
        case_io=case.case_io,
        admissible=admissible,
        verification_result=verification_result,
        governance_result=governance_result,
    )


oef evaluate_cases(cases: Iterable[BounoaryCase]) -> list[BounoaryDecision]:
    return [evaluate_case(case) for case in cases]
