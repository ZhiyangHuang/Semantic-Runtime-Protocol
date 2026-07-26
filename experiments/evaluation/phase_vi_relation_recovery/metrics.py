from __future__ import annotations

from statistics import mean
from typing import Any

from .graph import required_paths_preserved
from .recovery import recover_case, recovered_graph
from .schema import (
    RecoveryCase,
    RecoveryCaseResult,
    RecoveryConfig,
    RecoveryMetrics,
)


def _unit_sets(case: RecoveryCase, result_nodes: set[str], result_edges: set[tuple[str, str, str]]) -> tuple[set[str], set[tuple[str, str, str]], set[str]]:
    required_nodes = set(case.reference_node_ids)
    required_edges = set(case.reference_edge_keys)
    neighborhood_nodes = set(case.neighborhood_node_ids)
    original_units = neighborhood_nodes | {f"edge::{source}->{relation}->{target}" for source, relation, target in required_edges}
    recovered_units = result_nodes | {f"edge::{source}->{relation}->{target}" for source, relation, target in result_edges}
    matched_units = (required_nodes & result_nodes) | {
        edge for edge in {f"edge::{source}->{relation}->{target}" for source, relation, target in required_edges}
        if edge in recovered_units
    }
    return original_units, recovered_units, matched_units


def evaluate_relation_recovery_case(case: RecoveryCase, config: RecoveryConfig) -> RecoveryCaseResult:
    result = recover_case(case, config)
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
    path_preservation = required_paths_preserved(case, recovered_graph(case, config))
    closure_accuracy = round(min(1.0, max(0.0, 0.5 * relation_accuracy + 0.5 * path_preservation)), 6)
    hallucinated_relation_rate = hallucinated_edge_count / recovered_edge_count if recovered_edge_count else 0.0
    semantic_drift = round(
        min(1.0, max(0.0, 0.4 * (1.0 - fact_accuracy) + 0.4 * (1.0 - relation_accuracy) + 0.2 * hallucinated_relation_rate)),
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
    return RecoveryCaseResult(case=case, config=config, result=result, metrics=metrics)


def summarize_relation_recovery_results(records: list[RecoveryCaseResult]) -> dict[str, Any]:
    if not records:
        return {
            "case_count": 0,
            "mode_counts": {},
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
    mode_counts: dict[str, int] = {}
    for record in records:
        mode_counts[record.config.mode] = mode_counts.get(record.config.mode, 0) + 1

    def _mode_summary(mode: str) -> dict[str, float]:
        mode_metrics = [record.metrics for record in records if record.config.mode == mode]
        return {
            "mean_semantic_coverage": round(mean(item.semantic_coverage for item in mode_metrics), 6),
            "mean_semantic_drift": round(mean(item.semantic_drift for item in mode_metrics), 6),
            "mean_fact_accuracy": round(mean(item.fact_accuracy for item in mode_metrics), 6),
            "mean_relation_accuracy": round(mean(item.relation_accuracy for item in mode_metrics), 6),
            "mean_recovery_accuracy": round(mean(item.recovery_accuracy for item in mode_metrics), 6),
            "mean_closure_accuracy": round(mean(item.closure_accuracy for item in mode_metrics), 6),
            "mean_path_preservation": round(mean(item.path_preservation for item in mode_metrics), 6),
            "mean_neighborhood_completeness": round(mean(item.neighborhood_completeness for item in mode_metrics), 6),
            "mean_hallucinated_relation_rate": round(mean(item.hallucinated_relation_rate for item in mode_metrics), 6),
            "mean_evidence_cost": round(mean(item.evidence_cost for item in mode_metrics), 6),
        }

    modes = sorted(mode_counts)
    return {
        "case_count": len(records),
        "mode_counts": mode_counts,
        "mean_semantic_coverage": round(mean(item.semantic_coverage for item in metrics), 6),
        "mean_semantic_drift": round(mean(item.semantic_drift for item in metrics), 6),
        "mean_fact_accuracy": round(mean(item.fact_accuracy for item in metrics), 6),
        "mean_relation_accuracy": round(mean(item.relation_accuracy for item in metrics), 6),
        "mean_recovery_accuracy": round(mean(item.recovery_accuracy for item in metrics), 6),
        "mean_closure_accuracy": round(mean(item.closure_accuracy for item in metrics), 6),
        "mean_path_preservation": round(mean(item.path_preservation for item in metrics), 6),
        "mean_neighborhood_completeness": round(mean(item.neighborhood_completeness for item in metrics), 6),
        "mean_hallucinated_relation_rate": round(mean(item.hallucinated_relation_rate for item in metrics), 6),
        "mean_evidence_cost": round(mean(item.evidence_cost for item in metrics), 6),
        "total_missing_node_count": sum(item.missing_node_count for item in metrics),
        "total_hallucinated_node_count": sum(item.hallucinated_node_count for item in metrics),
        "total_hallucinated_edge_count": sum(item.hallucinated_edge_count for item in metrics),
        "mode_summary": {mode: _mode_summary(mode) for mode in modes},
    }
