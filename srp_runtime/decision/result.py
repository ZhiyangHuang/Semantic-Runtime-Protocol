from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DecisionResult:
    decision_id: str
    event_id: str
    selected_operator: str | None
    candidate_operators: list[str] = field(default_factory=list)
    accepted_candidates: list[str] = field(default_factory=list)
    rejected_candidates: list[str] = field(default_factory=list)
    constraint_evidence_refs: list[str] = field(default_factory=list)
    metric_evidence_refs: list[str] = field(default_factory=list)
    explanation: str = ""
    success: bool = False
    semantic_time: int = 0
    version_id: str = ""
