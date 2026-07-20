from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class EvidenceState:
    evidence_level: str
    support_score: float
    provenance_complete: bool

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AuthorityState:
    authority_rule: str
    scope: str = "semantic_transition"
    locked: bool = True

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TransitionProposal:
    proposal_id: str
    transition_request: str
    evidence_state: EvidenceState
    authority_state: AuthorityState
    srp_admitted: bool
    authority_before: str
    authority_after: str
    counterfactual_authority_after: str
    authority_changed_without_rule_change: bool
    counterfactual_authority_changed: bool
    notes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["evidence_state"] = self.evidence_state.as_dict()
        payload["authority_state"] = self.authority_state.as_dict()
        return payload


@dataclass(frozen=True)
class EvidenceAuthoritySeparationReport:
    report_id: str
    status: str
    cases: list[TransitionProposal] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "status": self.status,
            "cases": [case.as_dict() for case in self.cases],
            "summary": dict(self.summary),
        }
