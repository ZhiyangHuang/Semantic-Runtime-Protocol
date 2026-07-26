from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class StabilityRunParameters:
    workload: str
    objective_name: str
    evidence_backend: str
    seed: int

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StabilityRun:
    run_id: str
    parameters: StabilityRunParameters
    recommended_activation_threshold: float
    recommended_recovery_min_evidence: int
    recommended_objective_value: float
    notes: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StabilityRunMetrics:
    recommendation_consistency: float
    activation_threshold_variance: float
    recovery_min_evidence_variance: float
    objective_value_variance: float
    semantic_coverage_mean: float
    semantic_drift_mean: float
    semantic_coverage_variance: float
    semantic_drift_variance: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StabilityRunResult:
    run: StabilityRun
    metrics: StabilityRunMetrics

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StabilityEvaluationReport:
    report_id: str
    status: str
    baseline_workload: str
    baseline_objective_name: str
    baseline_evidence_backend: str
    records: list[StabilityRunResult] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
