from __future__ import annotations

from statistics import mean
from typing import Any

from experiments.evaluation.phase_vi_relation_recovery.metrics import evaluate_relation_recovery_case
from experiments.evaluation.phase_vi_relation_recovery.schema import RecoveryConfig

from .schema import CrossDomainRun, CrossDomainRunResult


def evaluate_cross_domain_runs(runs: list[CrossDomainRun]) -> list[CrossDomainRunResult]:
    results: list[CrossDomainRunResult] = []
    for run in runs:
        evaluated = evaluate_relation_recovery_case(run.case, run.config)
        results.append(CrossDomainRunResult(run=run, result=evaluated.result, metrics=evaluated.metrics))
    return results


def summarize_cross_domain_results(records: list[CrossDomainRunResult]) -> dict[str, Any]:
    if not records:
        return {
            "case_count": 0,
            "domain_counts": {},
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
            "domain_summary": {},
            "mode_summary": {},
        }

    metrics = [record.metrics for record in records]
    domain_counts: dict[str, int] = {}
    mode_counts: dict[str, int] = {}
    for record in records:
        domain_counts[record.run.domain_name] = domain_counts.get(record.run.domain_name, 0) + 1
        mode_counts[record.run.mode] = mode_counts.get(record.run.mode, 0) + 1

    def _mean(field: str) -> float:
        return round(mean(getattr(item, field) for item in metrics), 6)

    def _group_summary(predicate) -> dict[str, float]:
        group = [record.metrics for record in records if predicate(record)]
        return {
            "mean_semantic_coverage": round(mean(item.semantic_coverage for item in group), 6),
            "mean_semantic_drift": round(mean(item.semantic_drift for item in group), 6),
            "mean_fact_accuracy": round(mean(item.fact_accuracy for item in group), 6),
            "mean_relation_accuracy": round(mean(item.relation_accuracy for item in group), 6),
            "mean_recovery_accuracy": round(mean(item.recovery_accuracy for item in group), 6),
            "mean_closure_accuracy": round(mean(item.closure_accuracy for item in group), 6),
            "mean_path_preservation": round(mean(item.path_preservation for item in group), 6),
            "mean_neighborhood_completeness": round(mean(item.neighborhood_completeness for item in group), 6),
            "mean_hallucinated_relation_rate": round(mean(item.hallucinated_relation_rate for item in group), 6),
            "mean_evidence_cost": round(mean(item.evidence_cost for item in group), 6),
        }

    domain_summary = {domain: _group_summary(lambda record, domain=domain: record.run.domain_name == domain) for domain in sorted(domain_counts)}
    mode_summary = {mode: _group_summary(lambda record, mode=mode: record.run.mode == mode) for mode in sorted(mode_counts)}

    return {
        "case_count": len(records),
        "domain_counts": domain_counts,
        "mode_counts": mode_counts,
        "mean_semantic_coverage": _mean("semantic_coverage"),
        "mean_semantic_drift": _mean("semantic_drift"),
        "mean_fact_accuracy": _mean("fact_accuracy"),
        "mean_relation_accuracy": _mean("relation_accuracy"),
        "mean_recovery_accuracy": _mean("recovery_accuracy"),
        "mean_closure_accuracy": _mean("closure_accuracy"),
        "mean_path_preservation": _mean("path_preservation"),
        "mean_neighborhood_completeness": _mean("neighborhood_completeness"),
        "mean_hallucinated_relation_rate": _mean("hallucinated_relation_rate"),
        "mean_evidence_cost": _mean("evidence_cost"),
        "domain_summary": domain_summary,
        "mode_summary": mode_summary,
    }
