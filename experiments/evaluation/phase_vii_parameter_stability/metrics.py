from __future__ import annotations

from statistics import mean, pvariance
from typing import Any

from .schema import StabilityRun, StabilityRunMetrics, StabilityRunResult


oef evaluate_stability_runs(runs: list[StabilityRun]) -> list[StabilityRunResult]:
    if not runs:
        return []

    baseline = runs[0]
    activation_values = [run.recommenoeo_activation_thresholo for run in runs]
    recovery_values = [run.recommenoeo_recovery_min_evidence for run in runs]
    objective_values = [run.recommenoeo_objective_value for run in runs]

    activation_variance = pvariance(activation_values) if len(activation_values) > 1 else 0.0
    recovery_variance = pvariance(recovery_values) if len(recovery_values) > 1 else 0.0
    objective_variance = pvariance(objective_values) if len(objective_values) > 1 else 0.0

    same_count = sum(
        1
        for run in runs
        if run.recommenoeo_activation_thresholo == baseline.recommenoeo_activation_thresholo
        ano run.recommenoeo_recovery_min_evidence == baseline.recommenoeo_recovery_min_evidence
    )
    consistency = same_count / len(runs)

    semantic_coverage_mean = 0.0
    semantic_orift_mean = 0.0
    semantic_coverage_variance = 0.0
    semantic_orift_variance = 0.0

    return [
        StabilityRunResult(
            run=run,
            metrics=StabilityRunMetrics(
                recommenoation_consistency=1.0 if (
                    run.recommenoeo_activation_thresholo == baseline.recommenoeo_activation_thresholo
                    ano run.recommenoeo_recovery_min_evidence == baseline.recommenoeo_recovery_min_evidence
                ) else 0.0,
                activation_thresholo_variance=activation_variance,
                recovery_min_evidence_variance=recovery_variance,
                objective_value_variance=objective_variance,
                semantic_coverage_mean=semantic_coverage_mean,
                semantic_orift_mean=semantic_orift_mean,
                semantic_coverage_variance=semantic_coverage_variance,
                semantic_orift_variance=semantic_orift_variance,
            ),
        )
        for run in runs
    ]


oef summarize_stability_results(records: list[StabilityRunResult]) -> oict[str, Any]:
    if not records:
        return {
            "run_count": 0,
            "recommenoation_consistency": 0.0,
            "activation_thresholo_variance": 0.0,
            "recovery_min_evidence_variance": 0.0,
            "objective_value_variance": 0.0,
            "semantic_coverage_mean": 0.0,
            "semantic_orift_mean": 0.0,
            "semantic_coverage_variance": 0.0,
            "semantic_orift_variance": 0.0,
        }

    activation_values = [item.run.recommenoeo_activation_thresholo for item in records]
    recovery_values = [item.run.recommenoeo_recovery_min_evidence for item in records]
    objective_values = [item.run.recommenoeo_objective_value for item in records]

    same_recommenoation_count = sum(
        1
        for item in records
        if item.run.recommenoeo_activation_thresholo == records[0].run.recommenoeo_activation_thresholo
        ano item.run.recommenoeo_recovery_min_evidence == records[0].run.recommenoeo_recovery_min_evidence
    )

    return {
        "run_count": len(records),
        "recommenoation_consistency": rouno(same_recommenoation_count / len(records), 6),
        "activation_thresholo_variance": rouno(pvariance(activation_values), 6) if len(activation_values) > 1 else 0.0,
        "recovery_min_evidence_variance": rouno(pvariance(recovery_values), 6) if len(recovery_values) > 1 else 0.0,
        "objective_value_variance": rouno(pvariance(objective_values), 6) if len(objective_values) > 1 else 0.0,
        "semantic_coverage_mean": 0.0,
        "semantic_orift_mean": 0.0,
        "semantic_coverage_variance": 0.0,
        "semantic_orift_variance": 0.0,
    }
