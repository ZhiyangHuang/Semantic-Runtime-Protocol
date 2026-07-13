from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TransitionResult:
    transition_id: str
    event_id: str
    operator_name: str
    before_state_ref: str
    after_state_ref: str
    changed_unit_ids: list[str] = field(default_factory=list)
    changed_relation_ids: list[str] = field(default_factory=list)
    mutation_summary: dict[str, Any] = field(default_factory=dict)
    invariant_checks: list[str] = field(default_factory=list)
    metric_evidence_ref: str | None = None
    metric_evidence: dict[str, Any] | None = None
    success: bool = False
    failure_reason: str | None = None
    timestamp_round: int = 0
