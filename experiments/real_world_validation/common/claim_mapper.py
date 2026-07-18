from __future__ import annotations

from .schemas import ClaimMapping


def build_claim_mapping(
    *,
    claim_id: str,
    paper_section: str,
    observable_behavior: str,
    experiment_events: tuple[str, ...],
    promotion_level: str,
    claim_scope: str,
) -> ClaimMapping:
    return ClaimMapping(
        claim_id=claim_id,
        paper_section=paper_section,
        observable_behavior=observable_behavior,
        experiment_events=experiment_events,
        promotion_level=promotion_level,
        claim_scope=claim_scope,
    )

