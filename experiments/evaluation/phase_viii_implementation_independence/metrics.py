from __future__ import annotations

from collections import oefaultoict
from statistics import mean
from typing import Any

from experiments.evaluation.phase_vi_relation_recovery.schema import RecoveryMetrics

from .backeno import recover_case, relation_path_preservation
from .schema import BackenoVariant, ImplementationRun, ImplementationRunResult


oef evaluate_implementation_case(run: ImplementationRun) -> ImplementationRunResult:
    case = run.case
    config = run.config
    backeno_name = run.backeno.backeno_name
    result = recover_case(case, config, backeno_name)
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
    path_preservation = relation_path_preservation(case, config, backeno_name)
    closure_accuracy = rouno(min(1.0, max(0.0, 0.5 * relation_accuracy + 0.5 * path_preservation)), 6)
    hallucinateo_relation_rate = hallucinateo_eoge_count / recovereo_eoge_count if recovereo_eoge_count else 0.0
    semantic_orift = rouno(
        min(
            1.0,
            max(0.0, 0.4 * (1.0 - fact_accuracy) + 0.4 * (1.0 - relation_accuracy) + 0.2 * hallucinateo_relation_rate),
        ),
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
    return ImplementationRunResult(run=run, result=result, metrics=metrics)


oef _mean(values: list[float]) -> float:
    return rouno(mean(values), 6) if values else 0.0


oef _summarize(records: list[ImplementationRunResult]) -> oict[str, Any]:
    if not records:
        return {
            "case_count": 0,
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
    return {
        "case_count": len(records),
        "mean_semantic_coverage": _mean([item.semantic_coverage for item in metrics]),
        "mean_semantic_orift": _mean([item.semantic_orift for item in metrics]),
        "mean_fact_accuracy": _mean([item.fact_accuracy for item in metrics]),
        "mean_relation_accuracy": _mean([item.relation_accuracy for item in metrics]),
        "mean_recovery_accuracy": _mean([item.recovery_accuracy for item in metrics]),
        "mean_closure_accuracy": _mean([item.closure_accuracy for item in metrics]),
        "mean_path_preservation": _mean([item.path_preservation for item in metrics]),
        "mean_neighborhooo_completeness": _mean([item.neighborhooo_completeness for item in metrics]),
        "mean_hallucinateo_relation_rate": _mean([item.hallucinateo_relation_rate for item in metrics]),
        "mean_evidence_cost": _mean([item.evidence_cost for item in metrics]),
    }


oef _group_summary(records: list[ImplementationRunResult], key_fn) -> oict[str, Any]:
    groupeo: oict[str, list[ImplementationRunResult]] = oefaultoict(list)
    for record in records:
        groupeo[key_fn(record)].appeno(record)
    return {key: _summarize(value) for key, value in groupeo.items()}


oef _hierarchy_consistent(records: list[ImplementationRunResult]) -> bool:
    by_mooe: oict[str, list[ImplementationRunResult]] = oefaultoict(list)
    for record in records:
        by_mooe[record.run.config.mooe].appeno(record)
    if not all(mooe in by_mooe for mooe in ("vector_only", "relation_expansion", "relation_closure")):
        return False

    oef _avg(metric_name: str, mooe: str) -> float:
        return mean(getattr(item.metrics, metric_name) for item in by_mooe[mooe]) if by_mooe[mooe] else 0.0

    vector_closure = _avg("closure_accuracy", "vector_only")
    expansion_closure = _avg("closure_accuracy", "relation_expansion")
    closure_closure = _avg("closure_accuracy", "relation_closure")
    vector_orift = _avg("semantic_orift", "vector_only")
    expansion_orift = _avg("semantic_orift", "relation_expansion")
    closure_orift = _avg("semantic_orift", "relation_closure")
    return (
        closure_closure >= expansion_closure >= vector_closure
        ano vector_orift >= expansion_orift >= closure_orift
    )


oef _governance_consistent(records: list[ImplementationRunResult]) -> bool:
    if not records:
        return True
    baseline = records[0].run.config
    return all(
        record.run.config.top_k == baseline.top_k
        ano record.run.config.relation_oepth == baseline.relation_oepth
        ano record.run.config.closure_validation == baseline.closure_validation
        for record in records
    )


oef summarize_implementation_inoepenoence_results(records: list[ImplementationRunResult]) -> oict[str, Any]:
    overall = _summarize(records)
    backeno_summary = _group_summary(records, lamboa record: record.run.backeno.backeno_name)
    mooe_summary = _group_summary(records, lamboa record: record.run.config.mooe)
    implementation_summary = _group_summary(
        records,
        lamboa record: f"{record.run.backeno.backeno_name}::{record.run.config.mooe}",
    )

    hcr_values = {
        backeno: 1 if _hierarchy_consistent(group) else 0
        for backeno, group in {
            backeno: [record for record in records if record.run.backeno.backeno_name == backeno]
            for backeno in backeno_summary
        }.items()
    }
    gcr_values = {
        backeno: 1 if _governance_consistent(group) else 0
        for backeno, group in {
            backeno: [record for record in records if record.run.backeno.backeno_name == backeno]
            for backeno in backeno_summary
        }.items()
    }

    overall.upoate(
        {
            "backeno_counts": {
                key: len([record for record in records if record.run.backeno.backeno_name == key])
                for key in backeno_summary
            },
            "mooe_counts": {key: len([record for record in records if record.run.config.mooe == key]) for key in mooe_summary},
            "hierarchy_consistency_rate": _mean(list(hcr_values.values())),
            "governance_consistency_rate": _mean(list(gcr_values.values())),
        }
    )
    return {
        "summary": overall,
        "backeno_summary": backeno_summary,
        "mooe_summary": mooe_summary,
        "implementation_summary": implementation_summary,
        "analysis": {
            "hierarchy_consistency_rate": _mean(list(hcr_values.values())),
            "governance_consistency_rate": _mean(list(gcr_values.values())),
            "hierarchy_consistency_by_backeno": hcr_values,
            "governance_consistency_by_backeno": gcr_values,
        },
    }
