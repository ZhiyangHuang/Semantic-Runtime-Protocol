from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class SemanticNode:
    id: str
    content: str
    embedding: tuple[float, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SemanticEdge:
    source: str
    target: str
    relation_type: str
    confidence: float = 1.0

    def key(self) -> tuple[str, str, str]:
        return (self.source, self.relation_type, self.target)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SemanticGraph:
    nodes: tuple[SemanticNode, ...] = ()
    edges: tuple[SemanticEdge, ...] = ()

    def node_ids(self) -> tuple[str, ...]:
        return tuple(node.id for node in self.nodes)

    def node_map(self) -> dict[str, SemanticNode]:
        return {node.id: node for node in self.nodes}

    def edge_keys(self) -> tuple[tuple[str, str, str], ...]:
        return tuple(edge.key() for edge in self.edges)

    def adjacency(self) -> dict[str, set[str]]:
        adjacency: dict[str, set[str]] = {}
        for edge in self.edges:
            adjacency.setdefault(edge.source, set()).add(edge.target)
            adjacency.setdefault(edge.target, set()).add(edge.source)
        return adjacency

    def edges_for_nodes(self, node_ids: set[str]) -> tuple[SemanticEdge, ...]:
        return tuple(edge for edge in self.edges if edge.source in node_ids and edge.target in node_ids)

    def neighbors(self, seeds: set[str], depth: int = 1) -> set[str]:
        seen = set(seeds)
        frontier = set(seeds)
        adjacency = self.adjacency()
        for _ in range(max(0, depth)):
            next_frontier: set[str] = set()
            for node_id in frontier:
                for neighbor in adjacency.get(node_id, set()):
                    if neighbor not in seen:
                        next_frontier.add(neighbor)
            seen.update(next_frontier)
            frontier = next_frontier
            if not frontier:
                break
        return seen

    def as_dict(self) -> dict[str, Any]:
        return {
            "nodes": [node.as_dict() for node in self.nodes],
            "edges": [edge.as_dict() for edge in self.edges],
        }


@dataclass(frozen=True)
class RecoveryConfig:
    mode: str
    top_k: int
    relation_depth: int = 1
    closure_validation: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RecoveryCase:
    case_id: str
    category: str
    query: str
    source_graph: SemanticGraph
    reference_node_ids: tuple[str, ...]
    neighborhood_node_ids: tuple[str, ...]
    reference_edge_keys: tuple[tuple[str, str, str], ...]
    required_paths: tuple[tuple[str, ...], ...] = ()
    evidence_cost: float = 1.0
    notes: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RecoveryResult:
    mode: str
    recovered_node_ids: tuple[str, ...]
    recovered_edge_keys: tuple[tuple[str, str, str], ...]
    evidence_cost: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RecoveryMetrics:
    semantic_coverage: float
    semantic_drift: float
    fact_accuracy: float
    relation_accuracy: float
    recovery_accuracy: float
    closure_accuracy: float
    path_preservation: float
    neighborhood_completeness: float
    hallucinated_relation_rate: float
    evidence_cost: float
    original_node_count: int
    original_edge_count: int
    recovered_node_count: int
    recovered_edge_count: int
    matched_node_count: int
    matched_edge_count: int
    missing_node_count: int
    hallucinated_node_count: int
    hallucinated_edge_count: int

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RecoveryCaseResult:
    case: RecoveryCase
    config: RecoveryConfig
    result: RecoveryResult
    metrics: RecoveryMetrics

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RelationRecoveryMetricSchema:
    schema_version: str = "phase_vi_relation_recovery_metrics_schema.v1"
    coverage_definition: str = "matched semantic units divided by original semantic units"
    drift_definition: str = "weighted combination of fact drift, relation drift, and hallucinated relation rate"
    semantic_drift_weights: tuple[float, float, float] = (0.40, 0.40, 0.20)
    closure_definition: str = "preserved semantic paths divided by required semantic paths"
    evidence_cost_definition: str = "scalar cost attached to the recovery case"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RelationRecoveryEvaluationReport:
    report_id: str
    status: str
    baseline_config: RecoveryConfig
    metric_schema: RelationRecoveryMetricSchema
    records: list[RecoveryCaseResult] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
