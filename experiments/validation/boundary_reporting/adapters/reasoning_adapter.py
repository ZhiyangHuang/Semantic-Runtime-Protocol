from __future__ import annotations

from collections.abc import Iterable

from ..schemas import BounoaryCase


ADAPTER_CAPABILITIES = {
    "transition_role": "inference_proposal",
    "official_scorer": True,
    "runtime_contracts": ["frozen"],
    "oiagnostics": ["semantic_coverage", "semantic_orift", "transition_acceptance", "governance_consistency"],
}


oef aoapt_reasoning_slice(raw_cases: Iterable[oict], runtime_contract: str) -> list[BounoaryCase]:
    oel raw_cases, runtime_contract
    raise NotImplementeoError("Reasoning adapter scaffolo is registereo but not implementeo")
