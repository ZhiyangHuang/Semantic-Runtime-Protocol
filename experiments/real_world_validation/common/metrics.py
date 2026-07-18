from __future__ import annotations

from statistics import mean

from .schemas import GovernanceMetrics, TaskMetrics, TransitionMetrics


def aggregate_transition_metrics(records: list[dict[str, object]]) -> TransitionMetrics:
    accepted = sum(1 for record in records if bool(record.get("accepted")))
    rejected = sum(1 for record in records if not bool(record.get("accepted")))
    invalid = sum(1 for record in records if bool(record.get("failure")))
    invalid_accept_rate = round(
        sum(1 for record in records if bool(record.get("failure")) and bool(record.get("accepted")))
        / invalid,
        6,
    ) if invalid else 0.0
    return TransitionMetrics(
        accepted_transitions=accepted,
        rejected_transitions=rejected,
        invalid_accept_rate=invalid_accept_rate,
    )


def aggregate_governance_metrics(records: list[dict[str, object]]) -> GovernanceMetrics:
    authority_changed_with_evidence = any(bool(record.get("authority_changed")) for record in records)
    recommendation_execution_separated = all(
        bool(record.get("recommendation_execution_separated", True)) for record in records
    )
    replay_consistency = round(mean([float(record.get("replay_consistency", 1.0)) for record in records]) if records else 1.0, 6)
    authority_escalation_rate = round(
        sum(1 for record in records if bool(record.get("failure")) and bool(record.get("authority_changed")))
        / len(records),
        6,
    ) if records else 0.0
    evidence_improvement = round(mean([float(record.get("evidence_improvement", 0.0)) for record in records]) if records else 0.0, 6)
    return GovernanceMetrics(
        authority_changed_with_evidence=authority_changed_with_evidence,
        recommendation_execution_separated=recommendation_execution_separated,
        replay_consistency=replay_consistency,
        authority_escalation_rate=authority_escalation_rate,
        evidence_improvement=evidence_improvement,
    )


def aggregate_task_metrics(records: list[dict[str, object]]) -> TaskMetrics:
    memory_accuracy = round(mean([float(record.get("memory_accuracy", 0.0)) for record in records]) if records else 0.0, 6)
    relation_accuracy = round(mean([float(record.get("relation_accuracy", 0.0)) for record in records]) if records else 0.0, 6)
    fact_accuracy = round(mean([float(record.get("fact_accuracy", 0.0)) for record in records]) if records else 0.0, 6)
    coverage = round(mean([float(record.get("coverage", 0.0)) for record in records]) if records else 0.0, 6)
    return TaskMetrics(
        memory_accuracy=memory_accuracy,
        relation_accuracy=relation_accuracy,
        fact_accuracy=fact_accuracy,
        coverage=coverage,
    )

