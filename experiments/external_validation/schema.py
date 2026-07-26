from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class SemanticUnit:
    unit_id: str
    kind: str
    content: str
    timestep: int = 0
    salience: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SemanticRelation:
    relation_id: str
    source_id: str
    target_id: str
    relation_type: str
    confidence: float = 1.0
    timestep: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SemanticState:
    units: tuple[SemanticUnit, ...] = ()
    relations: tuple[SemanticRelation, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def unit_map(self) -> dict[str, SemanticUnit]:
        return {unit.unit_id: unit for unit in self.units}

    def relation_map(self) -> dict[str, SemanticRelation]:
        return {relation.relation_id: relation for relation in self.relations}


@dataclass(frozen=True)
class BenchmarkCase:
    benchmark_name: str
    case_id: str
    query: str
    source_state: SemanticState
    target_state: SemanticState
    expected_answer: str
    official_metric_name: str = "task_accuracy"
    focus_unit_ids: tuple[str, ...] = ()
    focus_relation_ids: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MemoryResponse:
    recovered_state: SemanticState
    predicted_answer: str
    retrieved_unit_ids: tuple[str, ...] = ()
    retrieved_relation_ids: tuple[str, ...] = ()
    evidence_cost: float = 0.0
    notes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExternalValidationRun:
    run_id: str
    benchmark_name: str
    baseline_name: str
    seed: int
    case: BenchmarkCase

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExternalValidationMetrics:
    semantic_coverage: float
    semantic_drift: float
    fact_accuracy: float
    relation_accuracy: float
    recovery_accuracy: float
    closure_accuracy: float
    neighborhood_completeness: float
    hallucinated_relation_rate: float
    evidence_cost: float
    answer_accuracy: float
    official_metric_score: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExternalValidationRecord:
    run: ExternalValidationRun
    response: MemoryResponse
    metrics: ExternalValidationMetrics
    failure_categories: tuple[str, ...] = ()
    failure_notes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExternalValidationMetricSchema:
    schema_version: str = "external_validation_metrics_schema.v1"
    coverage_definition: str = "matched semantic units divided by original semantic units"
    drift_definition: str = "weighted combination of fact drift, relation drift, and hallucinated relation rate"
    benchmark_definition: str = "official benchmark score plus SRP diagnostic metrics"
    evidence_cost_definition: str = "scalar cost attached to the recovery case"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExternalValidationReport:
    report_id: str
    status: str
    metric_schema: ExternalValidationMetricSchema
    records: list[ExternalValidationRecord] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)
    benchmark_summary: dict[str, Any] = field(default_factory=dict)
    baseline_summary: dict[str, Any] = field(default_factory=dict)
    pairwise_summary: dict[str, Any] = field(default_factory=dict)
    failure_summary: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
