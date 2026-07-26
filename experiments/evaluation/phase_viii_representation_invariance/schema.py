from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from experiments.evaluation.phase_vi_relation_recovery.schema import (
    RecoveryCase,
    RecoveryConfig,
    RecoveryMetrics,
    RecoveryResult,
)


@dataclass(frozen=True)
class RepresentationVariant:
    encoder_name: str
    parser_name: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RepresentationRun:
    run_id: str
    representation: RepresentationVariant
    case: RecoveryCase
    config: RecoveryConfig

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RepresentationRunResult:
    run: RepresentationRun
    result: RecoveryResult
    metrics: RecoveryMetrics

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RepresentationMetricSchema:
    schema_version: str = "phase_viii_representation_invariance_metrics_schema.v1"
    coverage_definition: str = "matched semantic units divided by original semantic units"
    drift_definition: str = "weighted combination of fact drift, relation drift, and hallucinated relation rate"
    hierarchy_definition: str = "rank consistency of relation_closure, relation_expansion, and vector_only"
    governance_definition: str = "qualitative preservation of parameter roles and governance pipeline"
    evidence_cost_definition: str = "scalar cost attached to the recovery case"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RepresentationEvaluationReport:
    report_id: str
    status: str
    baseline_config: RecoveryConfig
    metric_schema: RepresentationMetricSchema
    records: list[RepresentationRunResult] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)
    encoder_summary: dict[str, Any] = field(default_factory=dict)
    parser_summary: dict[str, Any] = field(default_factory=dict)
    mode_summary: dict[str, Any] = field(default_factory=dict)
    representation_summary: dict[str, Any] = field(default_factory=dict)
    analysis: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
