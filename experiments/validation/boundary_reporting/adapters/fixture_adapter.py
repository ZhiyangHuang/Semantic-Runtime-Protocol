from __future__ import annotations

from collections.abc import Iterable

from ..schemas import BoundaryCase
from ..generator import generate_cases


def adapt_fixture_slice(raw_cases: Iterable[dict], runtime_contract: str) -> list[BoundaryCase]:
    return generate_cases(raw_cases, runtime_contract)
