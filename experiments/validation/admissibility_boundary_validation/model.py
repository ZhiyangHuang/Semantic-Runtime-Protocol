from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class AdmissibilityCase:
    case_id: str
    scenario: str
    evidence_level: str
    authority_level: str
    optimization_pressure: str
    evidence_ok: bool
    authority_ok: bool
    optimization_ok: bool
    srp_admitted: bool
    direct_update_admitted: bool
    evidence_as_authority_admitted: bool
    authority_only_admitted: bool
    failure_modes: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AdmissibilityStressTestReport:
    report_id: str
    status: str
    cases: list[AdmissibilityCase] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "status": self.status,
            "cases": [case.as_dict() for case in self.cases],
            "summary": dict(self.summary),
        }
