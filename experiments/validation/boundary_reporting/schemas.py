from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class BoundaryCase:
    case_id: str
    semantic_state: dict[str, Any]
    proposal: dict[str, Any]
    evidence: dict[str, Any]
    authority: dict[str, Any]
    expected: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BoundaryDecision:
    case_id: str
    admissible: bool
    verification_result: dict[str, Any]
    governance_result: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BoundaryReportMetadata:
    version: str
    contract_version: str
    schema_version: str
    evaluator_version: str
    adapter_name: str
    runtime_contract: str
    seed: int
    generated_at: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
