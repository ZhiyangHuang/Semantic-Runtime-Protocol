from __future__ import annotations

from statistics import mean, pvariance
from typing import Any

from .schema import StabilityRun, StabilityRunMetrics, StabilityRunResult


def evaluate_stability_runs(runs: list[StabilityRun]) -> list[StabilityRunResult]:
    if not runs:
        return []

    baseline = runs[0]
    activation_values = [run.recommended_activation_threshold for run in runs]
    recovery_values = [run.recommended_recovery_min_evidence for run in runs]
    objective_values = [run.recommended_objective_value for run in runs]

    activation_variance = pvariance(activation_values) if len(activation_values) > 1 else 0.0
    recovery_variance = pvariance(recovery_values) if len(recovery_values) > 1 else 0.0
    objective_variance = pvariance(objective_values) if len(objective_values) > 1 else 0.0

    same_count = sum(
        1
        for run in runs
        if run.recommended_activation_threshold == baseline.recommended_activation_threshold
        and run.recommended_recovery_min_evidence == baseline.recommended_recovery_min_evidence
    )
    consistency = same_count / len(runs)

    semantic_coverage_mean = 0.0
    semantic_drift_mean = 0.0
    semantic_coverage_variance = 0.0
    semantic_drift_variance = 0.0

    return [
        StabilityRunResult(
            run=run,
            metrics=StabilityRunMetrics(
                recommendation_consistency=1.0 if (
                    run.recommended_activation_threshold == baseline.recommended_activation_threshold
                    and run.recommended_recovery_min_evidence == baseline.recommended_recovery_min_evidence
                ) else 0.0,
                activation_threshold_variance=activation_variance,
                recovery_min_evidence_variance=recovery_variance,
                objective_value_variance=objective_variance,
                semantic_coverage_mean=semantic_coverage_mean,
                semantic_drift_mean=semantic_drift_mean,
                semantic_coverage_variance=semantic_coverage_variance,
                semantic_drift_variance=semantic_drift_variance,
            ),
        )
        for run in runs
    ]


def summarize_stability_results(records: list[StabilityRunResult]) -> dict[str, Any]:
    if not records:
        return {
            "run_count": 0,
            "recommendation_consistency": 0.0,
            "activation_threshold_variance": 0.0,
            "recovery_min_evidence_variance": 0.0,
            "objective_value_variance": 0.0,
            "semantic_coverage_mean": 0.0,
            "semantic_drift_mean": 0.0,
            "semantic_coverage_variance": 0.0,
            "semantic_drift_variance": 0.0,
        }

    activation_values = [item.run.recommended_activation_threshold for item in records]
    recovery_values = [item.run.recommended_recovery_min_evidence for item in records]
    objective_values = [item.run.recommended_objective_value for item in records]

    same_recommendation_count = sum(
        1
        for item in records
        if item.run.recommended_activation_threshold == records[0].run.recommended_activation_threshold
        and item.run.recommended_recovery_min_evidence == records[0].run.recommended_recovery_min_evidence
    )

    return {
        "run_count": len(records),
        "recommendation_consistency": round(same_recommendation_count / len(records), 6),
        "activation_threshold_variance": round(pvariance(activation_values), 6) if len(activation_values) > 1 else 0.0,
        "recovery_min_evidence_variance": round(pvariance(recovery_values), 6) if len(recovery_values) > 1 else 0.0,
        "objective_value_variance": round(pvariance(objective_values), 6) if len(objective_values) > 1 else 0.0,
        "semantic_coverage_mean": 0.0,
        "semantic_drift_mean": 0.0,
        "semantic_coverage_variance": 0.0,
        "semantic_drift_variance": 0.0,
    }
