from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any

from experiments.evaluation.phase_vi_relation_recovery.schema import RecoveryMetrics

from .backend import recover_case, relation_path_preservation
from .schema import BackendVariant, ImplementationRun, ImplementationRunResult


def evaluate_implementation_case(run: ImplementationRun) -> ImplementationRunResult:
    case = run.case
    config = run.config
    backend_name = run.backend.backend_name
    result = recover_case(case, config, backend_name)
    recovered_nodes = set(result.recovered_node_ids)
    recovered_edges = set(result.recovered_edge_keys)
    required_nodes = set(case.reference_node_ids)
    required_edges = set(case.reference_edge_keys)
    neighborhood_nodes = set(case.neighborhood_node_ids)

    matched_nodes = required_nodes & recovered_nodes
    matched_edges = required_edges & recovered_edges
    original_node_count = len(required_nodes)
    original_edge_count = len(required_edges)
    recovered_node_count = len(recovered_nodes)
    recovered_edge_count = len(recovered_edges)
    matched_node_count = len(matched_nodes)
    matched_edge_count = len(matched_edges)
    missing_node_count = max(0, original_node_count - matched_node_count)
    hallucinated_node_count = max(0, recovered_node_count - matched_node_count)
    hallucinated_edge_count = max(0, recovered_edge_count - matched_edge_count)

    original_unit_count = len(neighborhood_nodes) + original_edge_count
    recovered_unit_count = recovered_node_count + recovered_edge_count
    matched_unit_count = matched_node_count + matched_edge_count
    semantic_coverage = matched_unit_count / original_unit_count if original_unit_count else 1.0
    union_count = original_unit_count + recovered_unit_count - matched_unit_count
    recovery_accuracy = matched_unit_count / union_count if union_count else 1.0
    fact_accuracy = matched_node_count / original_node_count if original_node_count else 1.0
    relation_accuracy = matched_edge_count / original_edge_count if original_edge_count else 1.0
    neighborhood_completeness = (
        len(neighborhood_nodes & recovered_nodes) / len(neighborhood_nodes)
        if neighborhood_nodes
        else 1.0
    )
    path_preservation = relation_path_preservation(case, config, backend_name)
    closure_accuracy = round(min(1.0, max(0.0, 0.5 * relation_accuracy + 0.5 * path_preservation)), 6)
    hallucinated_relation_rate = hallucinated_edge_count / recovered_edge_count if recovered_edge_count else 0.0
    semantic_drift = round(
        min(
            1.0,
            max(0.0, 0.4 * (1.0 - fact_accuracy) + 0.4 * (1.0 - relation_accuracy) + 0.2 * hallucinated_relation_rate),
        ),
        6,
    )

    metrics = RecoveryMetrics(
        semantic_coverage=round(semantic_coverage, 6),
        semantic_drift=semantic_drift,
        fact_accuracy=round(fact_accuracy, 6),
        relation_accuracy=round(relation_accuracy, 6),
        recovery_accuracy=round(recovery_accuracy, 6),
        closure_accuracy=round(closure_accuracy, 6),
        path_preservation=round(path_preservation, 6),
        neighborhood_completeness=round(neighborhood_completeness, 6),
        hallucinated_relation_rate=round(hallucinated_relation_rate, 6),
        evidence_cost=round(result.evidence_cost, 6),
        original_node_count=original_node_count,
        original_edge_count=original_edge_count,
        recovered_node_count=recovered_node_count,
        recovered_edge_count=recovered_edge_count,
        matched_node_count=matched_node_count,
        matched_edge_count=matched_edge_count,
        missing_node_count=missing_node_count,
        hallucinated_node_count=hallucinated_node_count,
        hallucinated_edge_count=hallucinated_edge_count,
    )
    return ImplementationRunResult(run=run, result=result, metrics=metrics)


def _mean(values: list[float]) -> float:
    return round(mean(values), 6) if values else 0.0


def _summarize(records: list[ImplementationRunResult]) -> dict[str, Any]:
    if not records:
        return {
            "case_count": 0,
            "mean_semantic_coverage": 0.0,
            "mean_semantic_drift": 0.0,
            "mean_fact_accuracy": 0.0,
            "mean_relation_accuracy": 0.0,
            "mean_recovery_accuracy": 0.0,
            "mean_closure_accuracy": 0.0,
            "mean_path_preservation": 0.0,
            "mean_neighborhood_completeness": 0.0,
            "mean_hallucinated_relation_rate": 0.0,
            "mean_evidence_cost": 0.0,
        }
    metrics = [record.metrics for record in records]
    return {
        "case_count": len(records),
        "mean_semantic_coverage": _mean([item.semantic_coverage for item in metrics]),
        "mean_semantic_drift": _mean([item.semantic_drift for item in metrics]),
        "mean_fact_accuracy": _mean([item.fact_accuracy for item in metrics]),
        "mean_relation_accuracy": _mean([item.relation_accuracy for item in metrics]),
        "mean_recovery_accuracy": _mean([item.recovery_accuracy for item in metrics]),
        "mean_closure_accuracy": _mean([item.closure_accuracy for item in metrics]),
        "mean_path_preservation": _mean([item.path_preservation for item in metrics]),
        "mean_neighborhood_completeness": _mean([item.neighborhood_completeness for item in metrics]),
        "mean_hallucinated_relation_rate": _mean([item.hallucinated_relation_rate for item in metrics]),
        "mean_evidence_cost": _mean([item.evidence_cost for item in metrics]),
    }


def _group_summary(records: list[ImplementationRunResult], key_fn) -> dict[str, Any]:
    grouped: dict[str, list[ImplementationRunResult]] = defaultdict(list)
    for record in records:
        grouped[key_fn(record)].append(record)
    return {key: _summarize(value) for key, value in grouped.items()}


def _hierarchy_consistent(records: list[ImplementationRunResult]) -> bool:
    by_mode: dict[str, list[ImplementationRunResult]] = defaultdict(list)
    for record in records:
        by_mode[record.run.config.mode].append(record)
    if not all(mode in by_mode for mode in ("vector_only", "relation_expansion", "relation_closure")):
        return False

    def _avg(metric_name: str, mode: str) -> float:
        return mean(getattr(item.metrics, metric_name) for item in by_mode[mode]) if by_mode[mode] else 0.0

    vector_closure = _avg("closure_accuracy", "vector_only")
    expansion_closure = _avg("closure_accuracy", "relation_expansion")
    closure_closure = _avg("closure_accuracy", "relation_closure")
    vector_drift = _avg("semantic_drift", "vector_only")
    expansion_drift = _avg("semantic_drift", "relation_expansion")
    closure_drift = _avg("semantic_drift", "relation_closure")
    return (
        closure_closure >= expansion_closure >= vector_closure
        and vector_drift >= expansion_drift >= closure_drift
    )


def _governance_consistent(records: list[ImplementationRunResult]) -> bool:
    if not records:
        return True
    baseline = records[0].run.config
    return all(
        record.run.config.top_k == baseline.top_k
        and record.run.config.relation_depth == baseline.relation_depth
        and record.run.config.closure_validation == baseline.closure_validation
        for record in records
    )


def summarize_implementation_independence_results(records: list[ImplementationRunResult]) -> dict[str, Any]:
    overall = _summarize(records)
    backend_summary = _group_summary(records, lambda record: record.run.backend.backend_name)
    mode_summary = _group_summary(records, lambda record: record.run.config.mode)
    implementation_summary = _group_summary(
        records,
        lambda record: f"{record.run.backend.backend_name}::{record.run.config.mode}",
    )

    hcr_values = {
        backend: 1 if _hierarchy_consistent(group) else 0
        for backend, group in {
            backend: [record for record in records if record.run.backend.backend_name == backend]
            for backend in backend_summary
        }.items()
    }
    gcr_values = {
        backend: 1 if _governance_consistent(group) else 0
        for backend, group in {
            backend: [record for record in records if record.run.backend.backend_name == backend]
            for backend in backend_summary
        }.items()
    }

    overall.update(
        {
            "backend_counts": {
                key: len([record for record in records if record.run.backend.backend_name == key])
                for key in backend_summary
            },
            "mode_counts": {key: len([record for record in records if record.run.config.mode == key]) for key in mode_summary},
            "hierarchy_consistency_rate": _mean(list(hcr_values.values())),
            "governance_consistency_rate": _mean(list(gcr_values.values())),
        }
    )
    return {
        "summary": overall,
        "backend_summary": backend_summary,
        "mode_summary": mode_summary,
        "implementation_summary": implementation_summary,
        "analysis": {
            "hierarchy_consistency_rate": _mean(list(hcr_values.values())),
            "governance_consistency_rate": _mean(list(gcr_values.values())),
            "hierarchy_consistency_by_backend": hcr_values,
            "governance_consistency_by_backend": gcr_values,
        },
    }
