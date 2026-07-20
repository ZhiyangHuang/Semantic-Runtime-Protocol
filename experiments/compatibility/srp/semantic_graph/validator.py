from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SemanticGraphValidation:
    schema_version: str = "semantic_graph_validation.v1"
    source_node_count: int = 0
    recovered_node_count: int = 0
    retained_node_count: int = 0
    missing_node_count: int = 0
    hallucinated_node_count: int = 0
    dependency_edge_count: int = 0
    missing_dependency_count: int = 0
    constraint_node_count: int = 0
    constraint_violation_count: int = 0
    object_survival_rate: float | None = None
    dependency_recall: float | None = None
    constraint_accuracy: float | None = None
    hallucination_rate: float | None = None
    graph_integrity_score: float | None = None
    attribute_retention: float | None = None
    state_retention: float | None = None
    lifecycle_accuracy: float | None = None
    issues: Dict[str, List[Dict[str, object]]] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "source_node_count": self.source_node_count,
            "recovered_node_count": self.recovered_node_count,
            "retained_node_count": self.retained_node_count,
            "missing_node_count": self.missing_node_count,
            "hallucinated_node_count": self.hallucinated_node_count,
            "dependency_edge_count": self.dependency_edge_count,
            "missing_dependency_count": self.missing_dependency_count,
            "constraint_node_count": self.constraint_node_count,
            "constraint_violation_count": self.constraint_violation_count,
            "object_survival_rate": self.object_survival_rate,
            "dependency_recall": self.dependency_recall,
            "constraint_accuracy": self.constraint_accuracy,
            "hallucination_rate": self.hallucination_rate,
            "graph_integrity_score": self.graph_integrity_score,
            "attribute_retention": self.attribute_retention,
            "state_retention": self.state_retention,
            "lifecycle_accuracy": self.lifecycle_accuracy,
            "issues": {key: list(value) for key, value in self.issues.items()},
        }


def _validate_semantic_runtime_graph(graph, *, include_v1_5_metrics: bool = False) -> SemanticGraphValidation:
    nodes = {node.node_id: node for node in graph.nodes}
    source_ids = {node.node_id for node in graph.nodes if bool((node.lifecycle or {}).get("source_present", False))}
    recovered_ids = {node.node_id for node in graph.nodes if bool((node.lifecycle or {}).get("recovered_present", False))}
    retained_ids = source_ids & recovered_ids
    missing_ids = source_ids - recovered_ids
    hallucinated_ids = recovered_ids - source_ids

    dependency_relations = {"depends_on", "constrains", "derived_from", "temporal_before", "same_entity", "refers_to", "causes"}
    dependency_edge_count = 0
    missing_dependency_count = 0
    constraint_node_count = 0
    constraint_violation_count = 0
    dependency_issues: List[Dict[str, object]] = []
    constraint_issues: List[Dict[str, object]] = []
    hallucinated_issues: List[Dict[str, object]] = []
    attribute_complete_count = 0
    state_complete_count = 0
    lifecycle_complete_count = 0

    for node in graph.nodes:
        lifecycle = node.lifecycle or {}
        attributes = node.attributes or {}
        source_present = bool(lifecycle.get("source_present", False))
        if source_present and isinstance(attributes, dict):
            if bool(attributes.get("identity")) or bool(attributes.get("properties")) or bool(attributes.get("state")):
                attribute_complete_count += 1
            if isinstance(attributes.get("state"), dict) and (
                "source_present" in attributes.get("state", {})
                or "recovered_present" in attributes.get("state", {})
                or "retained" in attributes.get("state", {})
            ):
                state_complete_count += 1
        if source_present and all(key in lifecycle for key in ["created", "modified", "compressed", "recovered", "verified", "retained"]):
            lifecycle_complete_count += 1
        if node.node_type == "constraint":
            constraint_node_count += 1
            if lifecycle.get("source_present") and not lifecycle.get("recovered_present"):
                constraint_violation_count += 1
                constraint_issues.append(
                    {
                        "node_id": node.node_id,
                        "label": node.label,
                        "issue": "constraint_missing_in_recovery",
                    }
                )
        if lifecycle.get("recovered_present") and not lifecycle.get("source_present"):
            hallucinated_issues.append(
                {
                    "node_id": node.node_id,
                    "label": node.label,
                    "issue": "hallucinated_node",
                }
            )
        if node.node_id.startswith("contract::") or node.node_type in {"constraint", "query_expectation", "semantic_dependency_tuple"}:
            dependency_edges = [
                edge
                for edge in graph.edges
                if edge.source == node.node_id
                and edge.relation in dependency_relations
                and edge.target in nodes
            ]
            if dependency_edges:
                dependency_edge_count += len(dependency_edges)
            else:
                missing_dependency_count += 1
                dependency_issues.append(
                    {
                        "node_id": node.node_id,
                        "label": node.label,
                        "issue": "missing_dependency_edge",
                    }
                )

    source_node_count = len(source_ids)
    recovered_node_count = len(recovered_ids)
    retained_node_count = len(retained_ids)
    missing_node_count = len(missing_ids)
    hallucinated_node_count = len(hallucinated_ids)
    object_survival_rate = (retained_node_count / source_node_count) if source_node_count else None
    dependency_total = dependency_edge_count + missing_dependency_count
    dependency_recall = (dependency_edge_count / dependency_total) if dependency_total else None
    constraint_accuracy = (1.0 - (constraint_violation_count / constraint_node_count)) if constraint_node_count else None
    hallucination_rate = (hallucinated_node_count / recovered_node_count) if recovered_node_count else None
    scores = [
        score
        for score in [
            object_survival_rate,
            dependency_recall,
            constraint_accuracy,
            (1.0 - hallucination_rate) if hallucination_rate is not None else None,
        ]
        if score is not None
    ]
    graph_integrity_score = (sum(scores) / len(scores)) if scores else None
    attribute_retention = (attribute_complete_count / source_node_count) if source_node_count else None
    state_retention = (state_complete_count / source_node_count) if source_node_count else None
    lifecycle_accuracy = (lifecycle_complete_count / len(graph.nodes)) if graph.nodes else None
    if include_v1_5_metrics:
        v1_5_scores = [
            score
            for score in [
                object_survival_rate,
                dependency_recall,
                constraint_accuracy,
                (1.0 - hallucination_rate) if hallucination_rate is not None else None,
                attribute_retention,
                state_retention,
                lifecycle_accuracy,
            ]
            if score is not None
        ]
        graph_integrity_score = (sum(v1_5_scores) / len(v1_5_scores)) if v1_5_scores else graph_integrity_score
    return SemanticGraphValidation(
        source_node_count=source_node_count,
        recovered_node_count=recovered_node_count,
        retained_node_count=retained_node_count,
        missing_node_count=missing_node_count,
        hallucinated_node_count=hallucinated_node_count,
        dependency_edge_count=dependency_edge_count,
        missing_dependency_count=missing_dependency_count,
        constraint_node_count=constraint_node_count,
        constraint_violation_count=constraint_violation_count,
        object_survival_rate=object_survival_rate,
        dependency_recall=dependency_recall,
        constraint_accuracy=constraint_accuracy,
        hallucination_rate=hallucination_rate,
        graph_integrity_score=graph_integrity_score,
        attribute_retention=attribute_retention if include_v1_5_metrics else None,
        state_retention=state_retention if include_v1_5_metrics else None,
        lifecycle_accuracy=lifecycle_accuracy if include_v1_5_metrics else None,
        issues={
            "dependency": dependency_issues,
            "constraint": constraint_issues,
            "hallucination": hallucinated_issues,
        },
    )


def validate_semantic_runtime_graph(graph) -> SemanticGraphValidation:
    return _validate_semantic_runtime_graph(graph, include_v1_5_metrics=False)


def validate_semantic_runtime_graph_v1_5(graph) -> SemanticGraphValidation:
    validation = _validate_semantic_runtime_graph(graph, include_v1_5_metrics=True)
    validation.schema_version = "semantic_graph_validation.v1.5"
    return validation
