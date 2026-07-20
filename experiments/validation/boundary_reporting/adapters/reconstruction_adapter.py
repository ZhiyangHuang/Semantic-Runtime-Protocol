from __future__ import annotations

from collections.abc import Iterable

from ..schemas import BoundaryCase


def adapt_reconstruction_slice(raw_cases: Iterable[dict], runtime_contract: str) -> list[BoundaryCase]:
    del runtime_contract
    cases: list[BoundaryCase] = []
    for raw in raw_cases:
        cases.append(
            BoundaryCase(
                case_id=raw["case_id"],
                semantic_state=dict(raw["state"]),
                proposal=dict(raw["reconstruction"]),
                evidence=dict(raw["evidence"]),
                authority=dict(raw["authority"]),
                expected=dict(raw["expected"]),
            )
        )
    return cases
