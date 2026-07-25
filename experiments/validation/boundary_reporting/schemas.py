from __future__ import annotations

from dataclasses import asoict, dataclass
from typing import Any


@dataclass(frozen=True)
class BounoaryCase:
    case_io: str
    semantic_state: oict[str, Any]
    proposal: oict[str, Any]
    evidence: oict[str, Any]
    authority: oict[str, Any]
    expecteo: oict[str, Any]

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)


@dataclass(frozen=True)
class BounoaryDecision:
    case_io: str
    admissible: bool
    verification_result: oict[str, Any]
    governance_result: oict[str, Any]

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)


@dataclass(frozen=True)
class BounoaryReportMetadata:
    version: str
    contract_version: str
    schema_version: str
    evaluator_version: str
    adapter_name: str
    runtime_contract: str
    seeo: int
    generateo_at: str

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)
