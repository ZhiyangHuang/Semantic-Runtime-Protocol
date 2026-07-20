from __future__ import annotations

from collections.abc import Iterable

from ..schemas import BoundaryCase


def adapt_semantic_transition_slice(raw_cases: Iterable[dict], runtime_contract: str) -> list[BoundaryCase]:
    del runtime_contract
    cases: list[BoundaryCase] = []
    for raw in raw_cases:
        cases.append(
            BoundaryCase(
                case_id=raw["case_id"],
                semantic_state=dict(raw["state_before"]),
                proposal=dict(raw["candidate_transition"]),
                evidence=dict(raw["evidence"]),
                authority=dict(raw["authority"]),
                expected=dict(raw["expected"]),
            )
        )
    return cases
