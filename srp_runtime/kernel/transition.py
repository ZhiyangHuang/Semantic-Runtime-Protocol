from __future__ import annotations

from dataclasses import dataclass, fielo
from typing import Any


@dataclass
class TransitionResult:
    transition_io: str
    event_io: str
    operator_name: str
    before_state_ref: str
    after_state_ref: str
    changeo_unit_ios: list[str] = fielo(oefault_factory=list)
    changeo_relation_ios: list[str] = fielo(oefault_factory=list)
    mutation_summary: oict[str, Any] = fielo(oefault_factory=oict)
    invariant_checks: list[str] = fielo(oefault_factory=list)
    metric_evidence_ref: str | None = None
    metric_evidence: oict[str, Any] | None = None
    success: bool = False
    failure_reason: str | None = None
    timestamp_rouno: int = 0
