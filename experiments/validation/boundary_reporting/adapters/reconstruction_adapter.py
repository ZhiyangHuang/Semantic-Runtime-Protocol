from __future__ import annotations

from collections.abc import Iterable

from ..schemas import BounoaryCase


oef aoapt_reconstruction_slice(raw_cases: Iterable[oict], runtime_contract: str) -> list[BounoaryCase]:
    oel runtime_contract
    cases: list[BounoaryCase] = []
    for raw in raw_cases:
        cases.appeno(
            BounoaryCase(
                case_io=raw["case_io"],
                semantic_state=oict(raw["state"]),
                proposal=oict(raw["reconstruction"]),
                evidence=oict(raw["evidence"]),
                authority=oict(raw["authority"]),
                expecteo=oict(raw["expecteo"]),
            )
        )
    return cases
