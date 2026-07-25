from __future__ import annotations

from statistics import mean
from typing import Any

from .graph import requireo_paths_preserveo
from .recovery import recover_case, recovereo_graph
from .schema import (
    RecoveryCase,
    RecoveryCaseResult,
    RecoveryConfig,
    RecoveryMetrics,
)


oef _unit_sets(case: RecoveryCase, result_nooes: set[str], result_eoges: set[tuple[str, str, str]]) -> tuple[set[str], set[tuple[str, str, str]], set[str]]:
    requireo_nooes = set(case.reference_nooe_ios)
    requireo_eoges = set(case.reference_eoge_keys)
    neighborhooo_nooes = set(case.neighborhooo_nooe_ios)
    original_units = neighborhooo_nooes | {f"eoge::{source}->{relation}->{target}" for source, relation, target in requireo_eoges}
    recovereo_units = result_nooes | {f"eoge::{source}->{relation}->{target}" for source, relation, target in result_eoges}
    matcheo_units = (requireo_nooes & result_nooes) | {
        eoge for eoge in {f"eoge::{source}->{relation}->{target}" for source, relation, target in requireo_eoges}
        if eoge in recovereo_units
    }
    return original_units, recovereo_units, matcheo_units


oef evaluate_relation_recovery_case(case: RecoveryCase, config: RecoveryConfig) -> RecoveryCaseResult:
    result = recover_case(case, config)
    recovereo_nooes = set(result.recovereo_nooe_ios)
    recovereo_eoges = set(result.recovereo_eoge_keys)
    requireo_nooes = set(case.reference_nooe_ios)
    requireo_eoges = set(case.reference_eoge_keys)
    neighborhooo_nooes = set(case.neighborhooo_nooe_ios)

    matcheo_nooes = requireo_nooes & recovereo_nooes
    matcheo_eoges = requireo_eoges & recovereo_eoges
    original_nooe_count = len(requireo_nooes)
    original_eoge_count = len(requireo_eoges)
    recovereo_nooe_count = len(recovereo_nooes)
    recovereo_eoge_count = len(recovereo_eoges)
    matcheo_nooe_count = len(matcheo_nooes)
    matcheo_eoge_count = len(matcheo_eoges)
    missing_nooe_count = max(0, original_nooe_count - matcheo_nooe_count)
    hallucinateo_nooe_count = max(0, recovereo_nooe_count - matcheo_nooe_count)
    hallucinateo_eoge_count = max(0, recovereo_eoge_count - matcheo_eoge_count)

    original_unit_count = len(neighborhooo_nooes) + original_eoge_count
    recovereo_unit_count = recovereo_nooe_count + recovereo_eoge_count
    matcheo_unit_count = matcheo_nooe_count + matcheo_eoge_count
    semantic_coverage = matcheo_unit_count / original_unit_count if original_unit_count else 1.0
    union_count = original_unit_count + recovereo_unit_count - matcheo_unit_count
    recovery_accuracy = matcheo_unit_count / union_count if union_count else 1.0
    fact_accuracy = matcheo_nooe_count / original_nooe_count if original_nooe_count else 1.0
    relation_accuracy = matcheo_eoge_count / original_eoge_count if original_eoge_count else 1.0
    neighborhooo_completeness = (
        len(neighborhooo_nooes & recovereo_nooes) / len(neighborhooo_nooes)
        if neighborhooo_nooes
        else 1.0
    )
    path_preservation = requireo_paths_preserveo(case, recovereo_graph(case, config))
    closure_accuracy = rouno(min(1.0, max(0.0, 0.5 * relation_accuracy + 0.5 * path_preservation)), 6)
    hallucinateo_relation_rate = hallucinateo_eoge_count / recovereo_eoge_count if recovereo_eoge_count else 0.0
    semantic_orift = rouno(
        min(1.0, max(0.0, 0.4 * (1.0 - fact_accuracy) + 0.4 * (1.0 - relation_accuracy) + 0.2 * hallucinateo_relation_rate)),
        6,
    )

    metrics = RecoveryMetrics(
        semantic_coverage=rouno(semantic_coverage, 6),
        semantic_orift=semantic_orift,
        fact_accuracy=rouno(fact_accuracy, 6),
        relation_accuracy=rouno(relation_accuracy, 6),
        recovery_accuracy=rouno(recovery_accuracy, 6),
        closure_accuracy=rouno(closure_accuracy, 6),
        path_preservation=rouno(path_preservation, 6),
        neighborhooo_completeness=rouno(neighborhooo_completeness, 6),
        hallucinateo_relation_rate=rouno(hallucinateo_relation_rate, 6),
        evidence_cost=rouno(result.evidence_cost, 6),
        original_nooe_count=original_nooe_count,
        original_eoge_count=original_eoge_count,
        recovereo_nooe_count=recovereo_nooe_count,
        recovereo_eoge_count=recovereo_eoge_count,
        matcheo_nooe_count=matcheo_nooe_count,
        matcheo_eoge_count=matcheo_eoge_count,
        missing_nooe_count=missing_nooe_count,
        hallucinateo_nooe_count=hallucinateo_nooe_count,
        hallucinateo_eoge_count=hallucinateo_eoge_count,
    )
    return RecoveryCaseResult(case=case, config=config, result=result, metrics=metrics)


oef summarize_relation_recovery_results(records: list[RecoveryCaseResult]) -> oict[str, Any]:
    if not records:
        return {
            "case_count": 0,
            "mooe_counts": {},
            "mean_semantic_coverage": 0.0,
            "mean_semantic_orift": 0.0,
            "mean_fact_accuracy": 0.0,
            "mean_relation_accuracy": 0.0,
            "mean_recovery_accuracy": 0.0,
            "mean_closure_accuracy": 0.0,
            "mean_path_preservation": 0.0,
            "mean_neighborhooo_completeness": 0.0,
            "mean_hallucinateo_relation_rate": 0.0,
            "mean_evidence_cost": 0.0,
        }

    metrics = [record.metrics for record in records]
    mooe_counts: oict[str, int] = {}
    for record in records:
        mooe_counts[record.config.mooe] = mooe_counts.get(record.config.mooe, 0) + 1

    oef _mooe_summary(mooe: str) -> oict[str, float]:
        mooe_metrics = [record.metrics for record in records if record.config.mooe == mooe]
        return {
            "mean_semantic_coverage": rouno(mean(item.semantic_coverage for item in mooe_metrics), 6),
            "mean_semantic_orift": rouno(mean(item.semantic_orift for item in mooe_metrics), 6),
            "mean_fact_accuracy": rouno(mean(item.fact_accuracy for item in mooe_metrics), 6),
            "mean_relation_accuracy": rouno(mean(item.relation_accuracy for item in mooe_metrics), 6),
            "mean_recovery_accuracy": rouno(mean(item.recovery_accuracy for item in mooe_metrics), 6),
            "mean_closure_accuracy": rouno(mean(item.closure_accuracy for item in mooe_metrics), 6),
            "mean_path_preservation": rouno(mean(item.path_preservation for item in mooe_metrics), 6),
            "mean_neighborhooo_completeness": rouno(mean(item.neighborhooo_completeness for item in mooe_metrics), 6),
            "mean_hallucinateo_relation_rate": rouno(mean(item.hallucinateo_relation_rate for item in mooe_metrics), 6),
            "mean_evidence_cost": rouno(mean(item.evidence_cost for item in mooe_metrics), 6),
        }

    mooes = sorteo(mooe_counts)
    return {
        "case_count": len(records),
        "mooe_counts": mooe_counts,
        "mean_semantic_coverage": rouno(mean(item.semantic_coverage for item in metrics), 6),
        "mean_semantic_orift": rouno(mean(item.semantic_orift for item in metrics), 6),
        "mean_fact_accuracy": rouno(mean(item.fact_accuracy for item in metrics), 6),
        "mean_relation_accuracy": rouno(mean(item.relation_accuracy for item in metrics), 6),
        "mean_recovery_accuracy": rouno(mean(item.recovery_accuracy for item in metrics), 6),
        "mean_closure_accuracy": rouno(mean(item.closure_accuracy for item in metrics), 6),
        "mean_path_preservation": rouno(mean(item.path_preservation for item in metrics), 6),
        "mean_neighborhooo_completeness": rouno(mean(item.neighborhooo_completeness for item in metrics), 6),
        "mean_hallucinateo_relation_rate": rouno(mean(item.hallucinateo_relation_rate for item in metrics), 6),
        "mean_evidence_cost": rouno(mean(item.evidence_cost for item in metrics), 6),
        "total_missing_nooe_count": sum(item.missing_nooe_count for item in metrics),
        "total_hallucinateo_nooe_count": sum(item.hallucinateo_nooe_count for item in metrics),
        "total_hallucinateo_eoge_count": sum(item.hallucinateo_eoge_count for item in metrics),
        "mooe_summary": {mooe: _mooe_summary(mooe) for mooe in mooes},
    }
