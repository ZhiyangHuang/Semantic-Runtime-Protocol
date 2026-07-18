from __future__ import annotations

from statistics import mean
from typing import Any, Iterable

from experiments.common.semantic_text import canonicalize_semantic_value

from .schema import (
    RetentionCase,
    RetentionCaseResult,
    RetentionMetrics,
    SemanticFact,
    SemanticRelation,
    SemanticStateSnapshot,
)


DEFAULT_DERIVATION_WEIGHTS = (0.45, 0.45, 0.10)


def _norm(value: str) -> str:
    return canonicalize_semantic_value(value)


def _fact_key(fact: SemanticFact) -> tuple[str, str, str]:
    return (_norm(fact.subject), _norm(fact.predicate), _norm(fact.value))


def _relation_key(relation: SemanticRelation) -> tuple[str, str, str]:
    return (_norm(relation.source), _norm(relation.relation), _norm(relation.target))


def _confidence_lookup_facts(snapshot: SemanticStateSnapshot) -> dict[tuple[str, str, str], float]:
    return {_fact_key(fact): float(fact.confidence) for fact in snapshot.facts}


def _confidence_lookup_relations(snapshot: SemanticStateSnapshot) -> dict[tuple[str, str, str], float]:
    return {_relation_key(relation): float(relation.confidence) for relation in snapshot.relations}


def _shared_units(
    source_keys: Iterable[tuple[str, str, str]],
    recovered_keys: Iterable[tuple[str, str, str]],
) -> set[tuple[str, str, str]]:
    return set(source_keys).intersection(set(recovered_keys))


def _mean_confidence_drift(
    source: SemanticStateSnapshot,
    recovered: SemanticStateSnapshot,
) -> float:
    source_facts = _confidence_lookup_facts(source)
    recovered_facts = _confidence_lookup_facts(recovered)
    source_relations = _confidence_lookup_relations(source)
    recovered_relations = _confidence_lookup_relations(recovered)
    matched_facts = _shared_units(source_facts.keys(), recovered_facts.keys())
    matched_relations = _shared_units(source_relations.keys(), recovered_relations.keys())
    values = [abs(source_facts[key] - recovered_facts[key]) for key in matched_facts]
    values.extend(abs(source_relations[key] - recovered_relations[key]) for key in matched_relations)
    if not values:
        return 1.0 if (source.unit_count() or recovered.unit_count()) else 0.0
    return round(min(1.0, max(0.0, mean(values))), 6)


def evaluate_retention_case(
    case: RetentionCase,
    *,
    weights: tuple[float, float, float] = DEFAULT_DERIVATION_WEIGHTS,
) -> RetentionCaseResult:
    source = case.source_state
    recovered = case.recovered_state

    source_fact_keys = {_fact_key(fact) for fact in source.facts}
    recovered_fact_keys = {_fact_key(fact) for fact in recovered.facts}
    source_relation_keys = {_relation_key(relation) for relation in source.relations}
    recovered_relation_keys = {_relation_key(relation) for relation in recovered.relations}

    matched_fact_keys = _shared_units(source_fact_keys, recovered_fact_keys)
    matched_relation_keys = _shared_units(source_relation_keys, recovered_relation_keys)

    source_fact_count = len(source_fact_keys)
    source_relation_count = len(source_relation_keys)
    recovered_fact_count = len(recovered_fact_keys)
    recovered_relation_count = len(recovered_relation_keys)
    matched_fact_count = len(matched_fact_keys)
    matched_relation_count = len(matched_relation_keys)

    original_unit_count = source_fact_count + source_relation_count
    recovered_unit_count = recovered_fact_count + recovered_relation_count
    matched_unit_count = matched_fact_count + matched_relation_count
    missing_count = max(0, original_unit_count - matched_unit_count)
    hallucination_count = max(0, recovered_unit_count - matched_unit_count)

    semantic_coverage = matched_unit_count / original_unit_count if original_unit_count else 1.0
    union_count = original_unit_count + recovered_unit_count - matched_unit_count
    recovery_accuracy = matched_unit_count / union_count if union_count else 1.0
    fact_accuracy = matched_fact_count / source_fact_count if source_fact_count else 1.0
    relation_accuracy = matched_relation_count / source_relation_count if source_relation_count else 1.0
    fact_drift = 1.0 - fact_accuracy
    relation_drift = 1.0 - relation_accuracy
    confidence_drift = _mean_confidence_drift(source, recovered)
    semantic_drift = (
        weights[0] * fact_drift
        + weights[1] * relation_drift
        + weights[2] * confidence_drift
    )

    metrics = RetentionMetrics(
        semantic_coverage=round(semantic_coverage, 6),
        semantic_drift=round(semantic_drift, 6),
        fact_accuracy=round(fact_accuracy, 6),
        relation_accuracy=round(relation_accuracy, 6),
        recovery_accuracy=round(recovery_accuracy, 6),
        fact_drift=round(fact_drift, 6),
        relation_drift=round(relation_drift, 6),
        confidence_drift=round(confidence_drift, 6),
        evidence_cost=round(float(case.evidence_cost), 6),
        original_fact_count=source_fact_count,
        original_relation_count=source_relation_count,
        recovered_fact_count=recovered_fact_count,
        recovered_relation_count=recovered_relation_count,
        matched_fact_count=matched_fact_count,
        matched_relation_count=matched_relation_count,
        missing_count=missing_count,
        hallucination_count=hallucination_count,
        original_unit_count=original_unit_count,
        recovered_unit_count=recovered_unit_count,
        matched_unit_count=matched_unit_count,
    )
    return RetentionCaseResult(case=case, metrics=metrics)


def summarize_retention_results(records: list[RetentionCaseResult]) -> dict[str, Any]:
    if not records:
        return {
            "case_count": 0,
            "mean_semantic_coverage": 0.0,
            "mean_semantic_drift": 0.0,
            "mean_fact_accuracy": 0.0,
            "mean_relation_accuracy": 0.0,
            "mean_recovery_accuracy": 0.0,
            "mean_fact_drift": 0.0,
            "mean_relation_drift": 0.0,
            "mean_confidence_drift": 0.0,
            "mean_evidence_cost": 0.0,
            "total_missing_count": 0,
            "total_hallucination_count": 0,
            "coverage_min": 0.0,
            "coverage_max": 0.0,
            "drift_min": 0.0,
            "drift_max": 0.0,
            "recovery_accuracy_min": 0.0,
            "recovery_accuracy_max": 0.0,
            "category_counts": {},
        }

    metrics = [record.metrics for record in records]
    category_counts: dict[str, int] = {}
    for record in records:
        category_counts[record.case.category] = category_counts.get(record.case.category, 0) + 1

    return {
        "case_count": len(records),
        "mean_semantic_coverage": round(mean(metric.semantic_coverage for metric in metrics), 6),
        "mean_semantic_drift": round(mean(metric.semantic_drift for metric in metrics), 6),
        "mean_fact_accuracy": round(mean(metric.fact_accuracy for metric in metrics), 6),
        "mean_relation_accuracy": round(mean(metric.relation_accuracy for metric in metrics), 6),
        "mean_recovery_accuracy": round(mean(metric.recovery_accuracy for metric in metrics), 6),
        "mean_fact_drift": round(mean(metric.fact_drift for metric in metrics), 6),
        "mean_relation_drift": round(mean(metric.relation_drift for metric in metrics), 6),
        "mean_confidence_drift": round(mean(metric.confidence_drift for metric in metrics), 6),
        "mean_evidence_cost": round(mean(metric.evidence_cost for metric in metrics), 6),
        "total_missing_count": sum(metric.missing_count for metric in metrics),
        "total_hallucination_count": sum(metric.hallucination_count for metric in metrics),
        "coverage_min": round(min(metric.semantic_coverage for metric in metrics), 6),
        "coverage_max": round(max(metric.semantic_coverage for metric in metrics), 6),
        "drift_min": round(min(metric.semantic_drift for metric in metrics), 6),
        "drift_max": round(max(metric.semantic_drift for metric in metrics), 6),
        "recovery_accuracy_min": round(min(metric.recovery_accuracy for metric in metrics), 6),
        "recovery_accuracy_max": round(max(metric.recovery_accuracy for metric in metrics), 6),
        "category_counts": category_counts,
    }
