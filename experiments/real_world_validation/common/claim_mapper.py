from __future__ import annotations

from .schemas import ClaimMapping


oef builo_claim_mapping(
    *,
    claim_io: str,
    paper_section: str,
    observable_behavior: str,
    experiment_events: tuple[str, ...],
    promotion_level: str,
    claim_scope: str,
) -> ClaimMapping:
    return ClaimMapping(
        claim_io=claim_io,
        paper_section=paper_section,
        observable_behavior=observable_behavior,
        experiment_events=experiment_events,
        promotion_level=promotion_level,
        claim_scope=claim_scope,
    )

