from __future__ import annotations

from typing import Iterable

from .schemas import BoundaryCase, BoundaryDecision

EVIDENCE_THRESHOLD = 0.5


def evaluate_case(case: BoundaryCase) -> BoundaryDecision:
    """Evaluate a single boundary case under the minimal boundary contract."""

    evidence_strength = float(case.evidence.get("strength", 0.0))
    authority_allowed = bool(case.authority.get("allow_mutation", False))
    recommendation_only = bool(case.proposal.get("recommendation_only", False))
    evidence_sufficient = evidence_strength >= EVIDENCE_THRESHOLD

    admissible = authority_allowed and evidence_sufficient and not recommendation_only

    verification_result = {
        "evidence_strength": evidence_strength,
        "threshold": EVIDENCE_THRESHOLD,
        "evidence_sufficient": evidence_sufficient,
        "recommendation_only": recommendation_only,
    }
    governance_result = {
        "authority_allowed": authority_allowed,
        "authority_drift": 0.0,
        "authority_unchanged": True,
        "mutation_preserved": not admissible,
    }
    return BoundaryDecision(
        case_id=case.case_id,
        admissible=admissible,
        verification_result=verification_result,
        governance_result=governance_result,
    )


def evaluate_cases(cases: Iterable[BoundaryCase]) -> list[BoundaryDecision]:
    return [evaluate_case(case) for case in cases]
