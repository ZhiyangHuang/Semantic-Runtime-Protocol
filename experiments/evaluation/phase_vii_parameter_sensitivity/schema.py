from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class SensitivityParameters:
    recovery_strategy: str
    activation_threshold: float
    recovery_min_evidence: int
    preserve_evidence: bool
    archive_relations: bool
    relation_depth: int

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SensitivityRun:
    run_id: str
    axis_name: str
    axis_value: Any
    parameters: SensitivityParameters
    workload_name: str
    objective_name: str
    evidence_backend: str
    notes: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SensitivityRunMetrics:
    mean_semantic_coverage: float
    mean_semantic_drift: float
    mean_fact_accuracy: float
    mean_relation_accuracy: float
    mean_recovery_accuracy: float
    mean_closure_accuracy: float
    mean_path_preservation: float
    mean_neighborhood_completeness: float
    mean_hallucinated_relation_rate: float
    mean_evidence_cost: float
    coverage_delta_vs_baseline: float
    drift_delta_vs_baseline: float
    fact_accuracy_delta_vs_baseline: float
    relation_accuracy_delta_vs_baseline: float
    recovery_accuracy_delta_vs_baseline: float
    closure_accuracy_delta_vs_baseline: float
    path_preservation_delta_vs_baseline: float
    neighborhood_completeness_delta_vs_baseline: float
    hallucinated_relation_rate_delta_vs_baseline: float
    evidence_cost_delta_vs_baseline: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SensitivityRunResult:
    run: SensitivityRun
    metrics: SensitivityRunMetrics

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SensitivityMetricSchema:
    schema_version: str = "phase_vii_parameter_sensitivity_metrics_schema.v1"
    coverage_definition: str = "matched semantic units divided by original semantic units"
    drift_definition: str = "weighted combination of fact drift, relation drift, and hallucinated relation rate"
    closure_definition: str = "preserved semantic paths divided by required semantic paths"
    sensitivity_definition: str = "one-factor-at-a-time parameter sweeps over a frozen relation-aware recovery baseline"
    evidence_cost_definition: str = "scalar cost attached to the recovery case"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SensitivityEvaluationReport:
    report_id: str
    status: str
    baseline_parameters: SensitivityParameters
    metric_schema: SensitivityMetricSchema
    records: list[SensitivityRunResult] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)
    axis_summary: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
