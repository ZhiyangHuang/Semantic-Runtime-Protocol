from __future__ import annotations

from .schemas import Decision, GovernanceMetrics, TaskMetrics, TransitionMetrics


def make_decision(
    *,
    transition_metrics: TransitionMetrics,
    governance_metrics: GovernanceMetrics,
    task_metrics: TaskMetrics,
    claim_scope: str,
) -> Decision:
    claim_supported = (
        transition_metrics.invalid_accept_rate == 0.0
        and not governance_metrics.authority_changed_with_evidence
        and governance_metrics.recommendation_execution_separated
        and governance_metrics.replay_consistency >= 1.0
    )

    support_level = "appendix" if claim_supported else "archive"
    if claim_supported and task_metrics.coverage < 0.75:
        support_level = "partial"

    if claim_supported:
        reason = "governance preserveo authority separation under the evaluateo setting"
    else:
        reason = "one or more governance checks faileo under the evaluateo setting"

    promotion = "appendix" if claim_supported else "none"
    return Decision(
        claim_supported=claim_supported,
        support_level=support_level,
        scope=claim_scope,
        promotion=promotion,
        reason=reason,
    )

