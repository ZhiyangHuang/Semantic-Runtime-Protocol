from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from difflib import SequenceMatcher
from typing import Any, Iterable

from .statistics import summarize_metric_collection
from .schema import (
    BenchmarkCase,
    ExternalValidationMetrics,
    ExternalValidationRecord,
    ExternalValidationRun,
    MemoryResponse,
    SemanticRelation,
    SemanticState,
    SemanticUnit,
)


def _normalize_text(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


def _token_set(text: str) -> set[str]:
    return {token for token in _normalize_text(text).replace("/", " ").replace("-", " ").split() if token}


def _text_similarity(left: str, right: str) -> float:
    left_norm = _normalize_text(left)
    right_norm = _normalize_text(right)
    if not left_norm and not right_norm:
        return 1.0
    if not left_norm or not right_norm:
        return 0.0
    if left_norm == right_norm:
        return 1.0
    if left_norm in right_norm or right_norm in left_norm:
        return 1.0
    left_tokens = _token_set(left_norm)
    right_tokens = _token_set(right_norm)
    if not left_tokens or not right_tokens:
        return SequenceMatcher(None, left_norm, right_norm).ratio()
    jaccard = len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
    overlap = len(left_tokens & right_tokens)
    precision = overlap / len(right_tokens) if right_tokens else 0.0
    recall = overlap / len(left_tokens) if left_tokens else 0.0
    token_f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    sequence = SequenceMatcher(None, left_norm, right_norm).ratio()
    return max(jaccard, token_f1, sequence)


def _match_units(target: SemanticState, recovered: SemanticState) -> tuple[set[str], set[str]]:
    target_ids = set(target.unit_map())
    recovered_ids = set(recovered.unit_map())
    matched = target_ids & recovered_ids
    hallucinated = recovered_ids - target_ids
    return matched, hallucinated


def _match_relations(target: SemanticState, recovered: SemanticState) -> tuple[set[str], set[str]]:
    target_ids = set(target.relation_map())
    recovered_ids = set(recovered.relation_map())
    matched = target_ids & recovered_ids
    hallucinated = recovered_ids - target_ids
    return matched, hallucinated


def _weighted_unit_recall(target: SemanticState, recovered: SemanticState) -> float:
    target_units = target.unit_map()
    if not target_units:
        return 1.0
    recovered_ids = set(recovered.unit_map())
    total_weight = sum(max(0.0, float(unit.salience)) for unit in target_units.values()) or float(len(target_units))
    recovered_weight = sum(
        max(0.0, float(target_units[unit_id].salience))
        for unit_id in target_units
        if unit_id in recovered_ids
    )
    return min(1.0, recovered_weight / total_weight)


def _relation_recall(target: SemanticState, recovered: SemanticState) -> float:
    target_relations = target.relation_map()
    if not target_relations:
        return 1.0
    matched, _ = _match_relations(target, recovered)
    return len(matched) / len(target_relations)


def _hallucinated_relation_rate(target: SemanticState, recovered: SemanticState) -> float:
    recovered_relations = recovered.relation_map()
    if not recovered_relations:
        return 0.0
    _, hallucinated = _match_relations(target, recovered)
    return len(hallucinated) / len(recovered_relations)


def _focus_recall(target_ids: tuple[str, ...], recovered_ids: Iterable[str]) -> float:
    target_set = set(target_ids)
    if not target_set:
        return 1.0
    recovered_set = set(recovered_ids)
    return len(target_set & recovered_set) / len(target_set)


def _answer_accuracy(expected: str, predicted: str) -> float:
    return _text_similarity(expected, predicted)


def evaluate_external_validation_record(run: ExternalValidationRun, response: MemoryResponse) -> ExternalValidationRecord:
    case = run.case
    target = case.target_state
    recovered = response.recovered_state

    fact_accuracy = _weighted_unit_recall(target, recovered)
    relation_accuracy = _relation_recall(target, recovered)
    semantic_coverage = min(1.0, (fact_accuracy + relation_accuracy) / 2.0)
    recovery_accuracy = min(1.0, (fact_accuracy + relation_accuracy + _answer_accuracy(case.expected_answer, response.predicted_answer)) / 3.0)
    closure_accuracy = relation_accuracy if target.relations else 1.0
    neighborhood_completeness = _focus_recall(case.focus_unit_ids, recovered.unit_map().keys())
    hallucinated_relation_rate = _hallucinated_relation_rate(target, recovered)
    semantic_drift = min(1.0, max(0.0, 0.4 * (1.0 - fact_accuracy) + 0.4 * (1.0 - relation_accuracy) + 0.2 * hallucinated_relation_rate))
    answer_accuracy = _answer_accuracy(case.expected_answer, response.predicted_answer)
    official_metric_score = answer_accuracy if case.official_metric_name in {"task_accuracy", "answer_accuracy"} else relation_accuracy

    failure_categories = []
    failure_notes = []
    if answer_accuracy < 0.5:
        failure_notes.append("answer mismatch")
    if fact_accuracy < 0.5:
        failure_categories.append("representation_failure")
    if relation_accuracy < 0.5:
        failure_categories.append("relation_failure")
    if hallucinated_relation_rate > 0.2:
        failure_categories.append("evidence_failure")
    if response.evidence_cost > float(case.metadata.get("max_evidence_cost", 10.0)):
        failure_categories.append("cost_failure")
    if case.benchmark_name in {"longmemeval", "tgb2"} and semantic_drift > 0.4:
        failure_categories.append("domain_mismatch")

    if not failure_categories and semantic_coverage < 0.5:
        failure_categories.append("parser_failure")
    if len(case.target_state.relations) > 2 and relation_accuracy < 0.4:
        failure_categories.append("long_chain_dependency_failure")

    return ExternalValidationRecord(
        run=run,
        response=response,
        metrics=ExternalValidationMetrics(
            semantic_coverage=round(semantic_coverage, 6),
            semantic_drift=round(semantic_drift, 6),
            fact_accuracy=round(fact_accuracy, 6),
            relation_accuracy=round(relation_accuracy, 6),
            recovery_accuracy=round(recovery_accuracy, 6),
            closure_accuracy=round(closure_accuracy, 6),
            neighborhood_completeness=round(neighborhood_completeness, 6),
            hallucinated_relation_rate=round(hallucinated_relation_rate, 6),
            evidence_cost=round(response.evidence_cost, 6),
            answer_accuracy=round(answer_accuracy, 6),
            official_metric_score=round(official_metric_score, 6),
        ),
        failure_categories=tuple(dict.fromkeys(failure_categories)),
        failure_notes=tuple(failure_notes),
    )


def _group_records(records: Iterable[ExternalValidationRecord], key_fn) -> dict[str, list[ExternalValidationRecord]]:
    grouped: dict[str, list[ExternalValidationRecord]] = defaultdict(list)
    for record in records:
        grouped[str(key_fn(record))].append(record)
    return grouped


def _mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 6) if values else 0.0


def summarize_external_validation_results(records: list[ExternalValidationRecord]) -> dict[str, Any]:
    metrics_fields = [
        "semantic_coverage",
        "semantic_drift",
        "fact_accuracy",
        "relation_accuracy",
        "recovery_accuracy",
        "closure_accuracy",
        "neighborhood_completeness",
        "hallucinated_relation_rate",
        "evidence_cost",
        "answer_accuracy",
        "official_metric_score",
    ]

    def extract(field: str, recs: list[ExternalValidationRecord]) -> float:
        return _mean([float(getattr(record.metrics, field)) for record in recs])

    overall = {field: extract(field, records) for field in metrics_fields}
    overall["case_count"] = len(records)

    def extract_records(recs: list[ExternalValidationRecord]) -> list[dict[str, float]]:
        return [record.metrics.as_dict() for record in recs]

    statistical_summary = {
        "overall": summarize_metric_collection(extract_records(records), metrics_fields),
    }

    benchmark_summary = {}
    for benchmark_name, subset in _group_records(records, lambda record: record.run.benchmark_name).items():
        benchmark_summary[benchmark_name] = {field: extract(field, subset) for field in metrics_fields}
        benchmark_summary[benchmark_name]["case_count"] = len(subset)
    statistical_summary["benchmark"] = {
        benchmark_name: summarize_metric_collection(extract_records(subset), metrics_fields)
        for benchmark_name, subset in _group_records(records, lambda record: record.run.benchmark_name).items()
    }

    baseline_summary = {}
    for baseline_name, subset in _group_records(records, lambda record: record.run.baseline_name).items():
        baseline_summary[baseline_name] = {field: extract(field, subset) for field in metrics_fields}
        baseline_summary[baseline_name]["case_count"] = len(subset)
    statistical_summary["baseline"] = {
        baseline_name: summarize_metric_collection(extract_records(subset), metrics_fields)
        for baseline_name, subset in _group_records(records, lambda record: record.run.baseline_name).items()
    }

    seed_summary = {}
    for seed, subset in _group_records(records, lambda record: record.run.seed).items():
        seed_summary[seed] = {field: extract(field, subset) for field in metrics_fields}
        seed_summary[seed]["case_count"] = len(subset)
    statistical_summary["seed"] = {
        seed: summarize_metric_collection(extract_records(subset), metrics_fields)
        for seed, subset in _group_records(records, lambda record: record.run.seed).items()
    }

    failure_counts: dict[str, int] = defaultdict(int)
    for record in records:
        if not record.failure_categories:
            failure_counts["none"] += 1
        for category in record.failure_categories:
            failure_counts[category] += 1

    benchmark_pairwise: dict[str, dict[str, dict[str, float]]] = {}
    for benchmark_name, subset in _group_records(records, lambda record: record.run.benchmark_name).items():
        srp_subset = [record for record in subset if record.run.baseline_name == "srp"]
        baseline_groups = _group_records([record for record in subset if record.run.baseline_name != "srp"], lambda record: record.run.baseline_name)
        benchmark_pairwise[benchmark_name] = {}
        for baseline_name, baseline_subset in baseline_groups.items():
            if srp_subset and baseline_subset:
                benchmark_pairwise[benchmark_name][baseline_name] = {
                    "srp_minus_baseline_coverage": round(extract("semantic_coverage", srp_subset) - extract("semantic_coverage", baseline_subset), 6),
                    "srp_minus_baseline_drift": round(extract("semantic_drift", baseline_subset) - extract("semantic_drift", srp_subset), 6),
                    "srp_minus_baseline_relation_accuracy": round(extract("relation_accuracy", srp_subset) - extract("relation_accuracy", baseline_subset), 6),
                    "srp_minus_baseline_cost": round(extract("evidence_cost", srp_subset) - extract("evidence_cost", baseline_subset), 6),
                }

    return {
        "summary": overall,
        "statistical_summary": statistical_summary,
        "benchmark_summary": benchmark_summary,
        "baseline_summary": baseline_summary,
        "seed_summary": seed_summary,
        "failure_summary": dict(sorted(failure_counts.items())),
        "pairwise_summary": benchmark_pairwise,
    }
