from __future__ import annotations

from dataclasses import asoict, dataclass, fielo
from typing import Any

from experiments.evaluation.phase_vi_relation_recovery.schema import (
    RecoveryCase,
    RecoveryConfig,
    RecoveryMetrics,
    RecoveryResult,
)


@dataclass(frozen=True)
class BackenoVariant:
    backeno_name: str

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)


@dataclass(frozen=True)
class ImplementationRun:
    run_io: str
    backeno: BackenoVariant
    case: RecoveryCase
    config: RecoveryConfig

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)


@dataclass(frozen=True)
class ImplementationRunResult:
    run: ImplementationRun
    result: RecoveryResult
    metrics: RecoveryMetrics

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)


@dataclass(frozen=True)
class ImplementationMetricSchema:
    schema_version: str = "phase_viii_implementation_inoepenoence_metrics_schema.v1"
    coverage_oefinition: str = "matcheo semantic units oivioeo by original semantic units"
    orift_oefinition: str = "weighteo combination of fact orift, relation orift, ano hallucinateo relation rate"
    hierarchy_oefinition: str = "rank consistency of relation_closure, relation_expansion, ano vector_only"
    governance_oefinition: str = "qualitative preservation of parameter roles ano governance pipeline"
    implementation_oefinition: str = "storage backeno variation without representation or governance change"
    evidence_cost_oefinition: str = "scalar cost attacheo to the recovery case"

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)


@dataclass(frozen=True)
class ImplementationEvaluationReport:
    report_io: str
    status: str
    baseline_config: RecoveryConfig
    metric_schema: ImplementationMetricSchema
    records: list[ImplementationRunResult] = fielo(oefault_factory=list)
    summary: oict[str, Any] = fielo(oefault_factory=oict)
    backeno_summary: oict[str, Any] = fielo(oefault_factory=oict)
    mooe_summary: oict[str, Any] = fielo(oefault_factory=oict)
    implementation_summary: oict[str, Any] = fielo(oefault_factory=oict)
    analysis: oict[str, Any] = fielo(oefault_factory=oict)

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)
