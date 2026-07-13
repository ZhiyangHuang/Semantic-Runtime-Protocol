from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ResolutionContext:
    resolution_id: str
    conflict_id: str
    source_versions: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    conflict_type: str = ""
    available_actions: list[str] = field(default_factory=list)
    decision_constraints: list[str] = field(default_factory=list)


@dataclass
class ResolutionDecision:
    resolution_id: str
    conflict_id: str
    selected_action: str
    rationale_refs: list[str] = field(default_factory=list)
    confidence: float = 0.0
    created_event_intent: dict[str, object] = field(default_factory=dict)


class ResolutionDecisionService:
    def evaluate(self, context: ResolutionContext) -> ResolutionDecision:
        selected_action = context.available_actions[0] if context.available_actions else "RejectBranch"
        return ResolutionDecision(
            resolution_id=context.resolution_id,
            conflict_id=context.conflict_id,
            selected_action=selected_action,
            rationale_refs=list(context.evidence_refs),
            confidence=0.5 if context.evidence_refs else 0.0,
            created_event_intent={
                "event_type": "SemanticCorrectionRequested",
                "source_versions": list(context.source_versions),
                "target_intent": selected_action,
                "conflict_id": context.conflict_id,
            },
        )
