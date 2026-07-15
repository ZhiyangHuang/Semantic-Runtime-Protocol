from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from experiments.evaluation.phase_vi_relation_recovery.schema import RecoveryCase, RecoveryConfig, RecoveryMetrics, RecoveryResult


@dataclass(frozen=True)
class CrossDomainRun:
    run_id: str
    domain_name: str
    mode: str
    case: RecoveryCase
    config: RecoveryConfig

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CrossDomainRunResult:
    run: CrossDomainRun
    result: RecoveryResult
    metrics: RecoveryMetrics

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CrossDomainMetricSchema:
    schema_version: str = "phase_viii_cross_domain_metrics_schema.v1"
    coverage_definition: str = "matched semantic units divided by original semantic units"
    drift_definition: str = "weighted combination of fact drift, relation drift, and hallucinated relation rate"
    closure_definition: str = "preserved semantic paths divided by required semantic paths"
    governance_definition: str = "cross-domain validation of relation-aware recovery under fixed SRP governance"
    evidence_cost_definition: str = "scalar cost attached to the recovery case"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CrossDomainEvaluationReport:
    report_id: str
    status: str
    baseline_config: RecoveryConfig
    metric_schema: CrossDomainMetricSchema
    records: list[CrossDomainRunResult] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)
    domain_summary: dict[str, Any] = field(default_factory=dict)
    mode_summary: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
