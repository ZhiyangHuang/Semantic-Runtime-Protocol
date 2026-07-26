from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class SemanticFact:
    subject: str
    predicate: str
    value: str
    confidence: float = 1.0
    critical: bool = False

    def canonical_key(self) -> tuple[str, str, str]:
        return (self.subject.strip().lower(), self.predicate.strip().lower(), self.value.strip().lower())

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SemanticRelation:
    source: str
    relation: str
    target: str
    confidence: float = 1.0
    critical: bool = False

    def canonical_key(self) -> tuple[str, str, str]:
        return (self.source.strip().lower(), self.relation.strip().lower(), self.target.strip().lower())

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SemanticStateSnapshot:
    state_id: str
    facts: tuple[SemanticFact, ...] = ()
    relations: tuple[SemanticRelation, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def fact_count(self) -> int:
        return len(self.facts)

    def relation_count(self) -> int:
        return len(self.relations)

    def unit_count(self) -> int:
        return self.fact_count() + self.relation_count()

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RetentionParameters:
    activation_threshold: float
    recovery_min_evidence: int
    preserve_evidence: bool
    archive_relations: bool

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RetentionCase:
    case_id: str
    category: str
    source_state: SemanticStateSnapshot
    recovered_state: SemanticStateSnapshot
    parameters: RetentionParameters
    evidence_cost: float
    notes: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RetentionMetrics:
    semantic_coverage: float
    semantic_drift: float
    fact_accuracy: float
    relation_accuracy: float
    recovery_accuracy: float
    fact_drift: float
    relation_drift: float
    confidence_drift: float
    evidence_cost: float
    original_fact_count: int
    original_relation_count: int
    recovered_fact_count: int
    recovered_relation_count: int
    matched_fact_count: int
    matched_relation_count: int
    missing_count: int
    hallucination_count: int
    original_unit_count: int
    recovered_unit_count: int
    matched_unit_count: int

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RetentionCaseResult:
    case: RetentionCase
    metrics: RetentionMetrics

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RetentionMetricSchema:
    schema_version: str = "phase_v_retention_metrics_schema.v1"
    coverage_definition: str = "matched semantic units divided by original semantic units"
    drift_definition: str = "weighted combination of fact drift, relation drift, and confidence drift"
    semantic_drift_weights: tuple[float, float, float] = (0.45, 0.45, 0.10)
    recovery_definition: str = "matched semantic units divided by union of original and recovered units"
    evidence_cost_definition: str = "scalar cost attached to the transition case"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RetentionEvaluationReport:
    report_id: str
    status: str
    baseline_parameters: RetentionParameters
    metric_schema: RetentionMetricSchema
    records: list[RetentionCaseResult] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
