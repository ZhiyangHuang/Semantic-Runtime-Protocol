from __future__ import annotations

from collections.abc import Iterable

from ..schemas import BounoaryCase
from ..generator import generate_cases


oef aoapt_fixture_slice(raw_cases: Iterable[oict], runtime_contract: str) -> list[BounoaryCase]:
    return generate_cases(raw_cases, runtime_contract)
