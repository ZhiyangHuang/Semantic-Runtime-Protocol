from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from ..semantic_parser import canonicalize_semantic_value, stable_semantic_object_id
from ..validation_targets import SemanticContractGraph
from .edge import SemanticGraphEdge
from .lifecycle import SemanticGraphLifecycle
from .node import SemanticGraphNode
from .validator import (
    SemanticGraphValidation,
    validate_semantic_runtime_graph,
    validate_semantic_runtime_graph_v1_5,
)


def _index_objects(objects: Iterable[Dict[str, object]] | None) -> Dict[str, Dict[str, object]]:
    indexed: Dict[str, Dict[str, object]] = {}
    for item in objects or []:
        if not isinstance(item, dict):
            continue
        object_type = str(item.get("type", "fact")).strip() or "fact"
        label = str(item.get("value", "")).strip()
        if not label:
            continue
        object_id = str(item.get("object_id") or item.get("id") or "").strip() or stable_semantic_object_id(object_type, label)
        indexed[object_id] = {
            "object_id": object_id,
            "type": object_type,
            "value": label,
            "confidence": float(item.get("confidence", 0.0) or 0.0),
            "evidence_pointer": str(item.get("evidence_pointer", "")),
            "metadata": dict(item.get("metadata", {})) if isinstance(item.get("metadata", {}), dict) else {},
        }
    return indexed


def _extract_source_objects(source_package: Dict[str, object] | None) -> List[Dict[str, object]]:
    source_package = source_package or {}
    source_inventory = source_package.get("semantic_object_inventory") or {}
    typed = source_package.get("typed_representation") or {}
    objects = (
        source_inventory.get("objects")
        or source_package.get("semantic_objects")
        or typed.get("objects")
        or []
    )
    return [item for item in objects if isinstance(item, dict)]


def _extract_recovered_objects(recovered_package: Dict[str, object] | None) -> List[Dict[str, object]]:
    recovered_package = recovered_package or {}
    typed = recovered_package.get("typed_representation") or {}
    return [item for item in typed.get("objects", []) if isinstance(item, dict)]


def _contract_nodes(validation_targets: SemanticContractGraph | None) -> List[Dict[str, object]]:
    nodes: List[Dict[str, object]] = []
    if validation_targets is None:
        return nodes
    for node in validation_targets.nodes:
        if node.role == "root":
            continue
        for variant in node.variants:
            canonical_value = canonicalize_semantic_value(variant.surface) or variant.surface
            object_id = stable_semantic_object_id(node.node_type, canonical_value)
            nodes.append(
                {
                    "object_id": object_id,
                    "node_id": f"contract::{object_id}",
                    "type": node.node_type,
                    "value": variant.surface,
                    "confidence": 1.0,
                    "evidence_pointer": f"contract:{node.node_id}",
                    "metadata": {
                        "role": node.role,
                        "node_id": node.node_id,
                    },
                }
            )
    return nodes


def _node_lifecycle(source_present: bool, recovered_present: bool, verified: bool) -> Dict[str, object]:
    return {
        "created": bool(source_present),
        "compressed": bool(source_present),
        "modified": bool(source_present and recovered_present),
        "recovered": bool(recovered_present),
        "verified": bool(verified),
        "retained": bool(source_present and recovered_present),
        "source_present": bool(source_present),
        "recovered_present": bool(recovered_present),
    }


def _node_lifecycle_v1_5(
    source_present: bool,
    recovered_present: bool,
    verified: bool,
    *,
    modified: bool | None = None,
) -> Dict[str, object]:
    lifecycle = _node_lifecycle(source_present, recovered_present, verified)
    if modified is not None:
        lifecycle["modified"] = bool(modified)
    return lifecycle


@dataclass
class SemanticRuntimeGraph:
    schema_version: str = "semantic_runtime_graph.v1"
    root_id: str = "semantic_runtime_graph::root"
    nodes: List[SemanticGraphNode] = field(default_factory=list)
    edges: List[SemanticGraphEdge] = field(default_factory=list)
    lifecycle: SemanticGraphLifecycle = field(default_factory=SemanticGraphLifecycle)
    summary: Dict[str, object] = field(default_factory=dict)

    def add_node(
        self,
        node_id: str,
        node_type: str,
        label: str,
        *,
        importance: float = 0.0,
        confidence: float = 0.0,
        attributes: Dict[str, object] | None = None,
        lifecycle: Dict[str, object] | None = None,
        identity: Dict[str, object] | None = None,
        importance_profile: Dict[str, object] | None = None,
    ) -> SemanticGraphNode:
        node = SemanticGraphNode(
            node_id=node_id,
            node_type=node_type,
            label=label,
            importance=importance,
            confidence=confidence,
            attributes=dict(attributes or {}),
            lifecycle=dict(lifecycle or {}),
            identity=dict(identity or {}),
            importance_profile=dict(importance_profile or {}),
        )
        self.nodes.append(node)
        return node

    def add_edge(
        self,
        source: str,
        target: str,
        relation: str,
        *,
        strength: float = 1.0,
        confidence: float = 1.0,
        evidence_pointer: str = "",
        attributes: Dict[str, object] | None = None,
        lifecycle: Dict[str, object] | None = None,
    ) -> SemanticGraphEdge:
        edge = SemanticGraphEdge(
            edge_id=f"edge:{len(self.edges) + 1}",
            source=source,
            target=target,
            relation=relation,
            strength=strength,
            confidence=confidence,
            evidence_pointer=evidence_pointer,
            attributes=dict(attributes or {}),
            lifecycle=dict(lifecycle or {}),
        )
        self.edges.append(edge)
        return edge

    def get_dependencies(self, node_id: str) -> List[SemanticGraphEdge]:
        return [
            edge
            for edge in self.edges
            if edge.source == node_id and edge.relation in {"depends_on", "constrains", "derived_from", "temporal_before", "same_entity", "refers_to", "causes"}
        ]

    def track_lifecycle(self, node_id: str, stage: str, *, present: bool = True, evidence_pointer: str = "") -> None:
        for node in self.nodes:
            if node.node_id != node_id:
                continue
            node.lifecycle[stage] = bool(present)
            if evidence_pointer:
                node.lifecycle.setdefault("evidence_pointers", [])
                pointers = node.lifecycle["evidence_pointers"]
                if isinstance(pointers, list) and evidence_pointer not in pointers:
                    pointers.append(evidence_pointer)
            break

    def validate_integrity(self) -> SemanticGraphValidation:
        validation = validate_semantic_runtime_graph(self)
        self.lifecycle.created_count = validation.source_node_count
        self.lifecycle.compressed_count = validation.source_node_count - validation.missing_node_count
        self.lifecycle.recovered_count = validation.recovered_node_count
        self.lifecycle.modified_count = sum(1 for node in self.nodes if bool((node.lifecycle or {}).get("modified", False)))
        self.lifecycle.verified_count = validation.retained_node_count
        self.lifecycle.retained_count = validation.retained_node_count
        self.lifecycle.object_survival_rate = validation.object_survival_rate
        self.lifecycle.dependency_recall = validation.dependency_recall
        self.lifecycle.constraint_accuracy = validation.constraint_accuracy
        self.lifecycle.hallucination_rate = validation.hallucination_rate
        self.lifecycle.graph_integrity_score = validation.graph_integrity_score
        self.lifecycle.attribute_retention = validation.attribute_retention
        self.lifecycle.state_retention = validation.state_retention
        self.lifecycle.lifecycle_accuracy = validation.lifecycle_accuracy
        self.lifecycle.issues = validation.issues
        return validation

    def validate_integrity_v1_5(self) -> SemanticGraphValidation:
        validation = validate_semantic_runtime_graph_v1_5(self)
        self.lifecycle.schema_version = "semantic_runtime_graph_lifecycle.v1.5"
        self.lifecycle.created_count = validation.source_node_count
        self.lifecycle.compressed_count = validation.source_node_count - validation.missing_node_count
        self.lifecycle.recovered_count = validation.recovered_node_count
        self.lifecycle.modified_count = sum(1 for node in self.nodes if bool((node.lifecycle or {}).get("modified", False)))
        self.lifecycle.verified_count = validation.retained_node_count
        self.lifecycle.retained_count = validation.retained_node_count
        self.lifecycle.object_survival_rate = validation.object_survival_rate
        self.lifecycle.dependency_recall = validation.dependency_recall
        self.lifecycle.constraint_accuracy = validation.constraint_accuracy
        self.lifecycle.hallucination_rate = validation.hallucination_rate
        self.lifecycle.graph_integrity_score = validation.graph_integrity_score
        self.lifecycle.attribute_retention = validation.attribute_retention
        self.lifecycle.state_retention = validation.state_retention
        self.lifecycle.lifecycle_accuracy = validation.lifecycle_accuracy
        self.lifecycle.issues = validation.issues
        return validation

    def as_dict(self) -> Dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "root_id": self.root_id,
            "nodes": [node.as_dict() for node in self.nodes],
            "edges": [edge.as_dict() for edge in self.edges],
            "lifecycle": self.lifecycle.as_dict(),
            "summary": dict(self.summary),
        }

    def as_v1_5_dict(self) -> Dict[str, object]:
        return {
            "schema_version": "semantic_runtime_graph.v1.5",
            "root_id": self.root_id,
            "nodes": [node.as_v1_5_dict() for node in self.nodes],
            "edges": [edge.as_dict() for edge in self.edges],
            "lifecycle": self.lifecycle.as_dict(),
            "summary": dict(self.summary),
        }


def build_semantic_runtime_graph(
    source_package: Dict[str, object] | None,
    recovered_package: Dict[str, object] | None = None,
    validation_targets: SemanticContractGraph | None = None,
) -> SemanticRuntimeGraph:
    source_package = source_package or {}
    recovered_package = recovered_package or {}
    graph = SemanticRuntimeGraph()
    graph.add_node(
        graph.root_id,
        "graph_root",
        "semantic_runtime_graph",
        confidence=1.0,
        lifecycle={"created": True, "compressed": True, "recovered": True, "verified": True, "retained": True},
        attributes={"schema_version": graph.schema_version},
    )

    source_objects = _index_objects(_extract_source_objects(source_package))
    recovered_objects = _index_objects(_extract_recovered_objects(recovered_package))
    contract_objects = _index_objects(_contract_nodes(validation_targets))

    graph.summary["source_object_count"] = len(source_objects)
    graph.summary["recovered_object_count"] = len(recovered_objects)
    graph.summary["contract_object_count"] = len(contract_objects)

    runtime_metadata = source_package.get("runtime_metadata") or {}
    for object_id, item in source_objects.items():
        recovered_present = object_id in recovered_objects
        metadata = runtime_metadata.get(object_id) or {}
        node = graph.add_node(
            object_id,
            str(item.get("type", "fact")),
            str(item.get("value", "")),
            importance=float(metadata.get("importance", 0.0) or 0.0),
            confidence=float(item.get("confidence", 0.0) or 0.0),
            attributes={
                "evidence_pointer": item.get("evidence_pointer", ""),
                "source_present": True,
                "recovered_present": recovered_present,
                "object_origin": "source",
                "metadata": dict(item.get("metadata", {})),
            },
            lifecycle=_node_lifecycle(True, recovered_present, recovered_present),
        )
        graph.add_edge(graph.root_id, node.node_id, "contains", confidence=node.confidence)
        if recovered_present:
            graph.add_edge(node.node_id, node.node_id, "retains_identity", confidence=1.0)

    for object_id, item in recovered_objects.items():
        if object_id in source_objects:
            continue
        node = graph.add_node(
            object_id,
            str(item.get("type", "fact")),
            str(item.get("value", "")),
            importance=float(item.get("confidence", 0.0) or 0.0),
            confidence=float(item.get("confidence", 0.0) or 0.0),
            attributes={
                "evidence_pointer": item.get("evidence_pointer", ""),
                "source_present": False,
                "recovered_present": True,
                "object_origin": "recovered_only",
                "metadata": dict(item.get("metadata", {})),
            },
            lifecycle=_node_lifecycle(False, True, False),
        )
        graph.add_edge(graph.root_id, node.node_id, "hallucinated", confidence=node.confidence)

    for object_id, item in contract_objects.items():
        contract_node_id = str(item.get("node_id") or f"contract::{object_id}")
        contract_node = graph.add_node(
            contract_node_id,
            f"contract_{str(item.get('type', 'constraint'))}",
            str(item.get("value", "")),
            importance=1.0,
            confidence=float(item.get("confidence", 1.0) or 1.0),
            attributes={
                "evidence_pointer": item.get("evidence_pointer", ""),
                "source_present": False,
                "recovered_present": False,
                "object_origin": "contract",
                "contract_object_id": object_id,
                "metadata": dict(item.get("metadata", {})),
            },
            lifecycle=_node_lifecycle(False, False, False),
        )
        graph.add_edge(graph.root_id, contract_node.node_id, "requires", confidence=1.0)
        existing = next((node for node in graph.nodes if node.node_id == object_id), None)
        if existing is not None:
            graph.add_edge(contract_node.node_id, existing.node_id, "depends_on", confidence=1.0)
        else:
            graph.add_node(
                object_id,
                f"contract_{str(item.get('type', 'constraint'))}",
                str(item.get("value", "")),
                importance=1.0,
                confidence=float(item.get("confidence", 1.0) or 1.0),
                attributes={
                    "evidence_pointer": item.get("evidence_pointer", ""),
                    "source_present": False,
                    "recovered_present": False,
                    "object_origin": "contract",
                    "metadata": dict(item.get("metadata", {})),
                },
                lifecycle=_node_lifecycle(False, False, False),
            )

    for node in graph.nodes:
        if node.node_id == graph.root_id:
            continue
        if node.node_type in {"constraint", "query_expectation", "semantic_dependency_tuple"} and node.node_id.startswith("contract::"):
            contract_object_id = str((node.attributes or {}).get("contract_object_id", ""))
            if contract_object_id in source_objects or contract_object_id in recovered_objects:
                graph.add_edge(node.node_id, contract_object_id, "constrains", confidence=node.confidence)

    validation = graph.validate_integrity()
    graph.summary.update(
        {
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
            "validation": validation.as_dict(),
        }
    )
    return graph


def build_semantic_runtime_graph_v1_5(
    source_package: Dict[str, object] | None,
    recovered_package: Dict[str, object] | None = None,
    validation_targets: SemanticContractGraph | None = None,
) -> SemanticRuntimeGraph:
    source_package = source_package or {}
    recovered_package = recovered_package or {}
    graph = SemanticRuntimeGraph(schema_version="semantic_runtime_graph.v1.5")
    graph.lifecycle.schema_version = "semantic_runtime_graph_lifecycle.v1.5"
    graph.add_node(
        graph.root_id,
        "graph_root",
        "semantic_runtime_graph",
        confidence=1.0,
        lifecycle={
            "created": True,
            "modified": False,
            "compressed": True,
            "recovered": True,
            "verified": True,
            "retained": True,
        },
        attributes={
            "properties": {"schema_version": graph.schema_version},
            "state": {
                "source_present": True,
                "recovered_present": True,
                "retained": True,
                "root": True,
            },
        },
        identity={
            "canonical_name": "semantic_runtime_graph",
            "aliases": ["runtime_graph"],
            "entity_key": graph.root_id,
        },
        importance_profile={"score": 1.0, "critical": True},
    )

    source_objects = _index_objects(_extract_source_objects(source_package))
    recovered_objects = _index_objects(_extract_recovered_objects(recovered_package))
    contract_objects = _index_objects(_contract_nodes(validation_targets))

    graph.summary["source_object_count"] = len(source_objects)
    graph.summary["recovered_object_count"] = len(recovered_objects)
    graph.summary["contract_object_count"] = len(contract_objects)

    runtime_metadata = source_package.get("runtime_metadata") or {}
    important_ids = {
        str(item.get("object_id"))
        for item in ((source_package.get("semantic_object_inventory") or {}).get("important_objects") or [])
        if isinstance(item, dict) and item.get("object_id")
    }

    def _node_properties(item: Dict[str, object], origin: str) -> Dict[str, object]:
        metadata = dict(item.get("metadata", {})) if isinstance(item.get("metadata", {}), dict) else {}
        return {
            "evidence_pointer": item.get("evidence_pointer", ""),
            "origin": origin,
            "type": item.get("type", "fact"),
            "value": item.get("value", ""),
            "metadata": metadata,
        }

    def _node_state(source_present: bool, recovered_present: bool, item: Dict[str, object]) -> Dict[str, object]:
        return {
            "source_present": bool(source_present),
            "recovered_present": bool(recovered_present),
            "retained": bool(source_present and recovered_present),
            "canonical_value": item.get("value", ""),
        }

    for object_id, item in source_objects.items():
        recovered_present = object_id in recovered_objects
        metadata = runtime_metadata.get(object_id) or {}
        importance_score = float(metadata.get("importance", 0.0) or 0.0)
        node = graph.add_node(
            object_id,
            str(item.get("type", "fact")),
            str(item.get("value", "")),
            importance=importance_score,
            confidence=float(item.get("confidence", 0.0) or 0.0),
            attributes={
                "identity": {
                    "canonical_name": str(item.get("value", "")),
                    "aliases": [str(item.get("value", ""))],
                    "entity_key": object_id,
                },
                "properties": _node_properties(item, "source"),
                "state": _node_state(True, recovered_present, item),
                "evidence_pointer": item.get("evidence_pointer", ""),
                "source_present": True,
                "recovered_present": recovered_present,
                "object_origin": "source",
                "metadata": dict(item.get("metadata", {})),
            },
            lifecycle=_node_lifecycle_v1_5(True, recovered_present, recovered_present, modified=recovered_present),
            identity={
                "canonical_name": str(item.get("value", "")),
                "aliases": [str(item.get("value", ""))],
                "entity_key": object_id,
            },
            importance_profile={
                "score": importance_score,
                "critical": object_id in important_ids or importance_score >= 0.8,
            },
        )
        graph.add_edge(graph.root_id, node.node_id, "contains", confidence=node.confidence)
        if recovered_present:
            graph.add_edge(node.node_id, node.node_id, "same_entity", confidence=1.0)

    for object_id, item in recovered_objects.items():
        if object_id in source_objects:
            continue
        importance_score = float(item.get("confidence", 0.0) or 0.0)
        node = graph.add_node(
            object_id,
            str(item.get("type", "fact")),
            str(item.get("value", "")),
            importance=importance_score,
            confidence=float(item.get("confidence", 0.0) or 0.0),
            attributes={
                "identity": {
                    "canonical_name": str(item.get("value", "")),
                    "aliases": [str(item.get("value", ""))],
                    "entity_key": object_id,
                },
                "properties": _node_properties(item, "recovered_only"),
                "state": _node_state(False, True, item),
                "evidence_pointer": item.get("evidence_pointer", ""),
                "source_present": False,
                "recovered_present": True,
                "object_origin": "recovered_only",
                "metadata": dict(item.get("metadata", {})),
            },
            lifecycle=_node_lifecycle_v1_5(False, True, False, modified=True),
            identity={
                "canonical_name": str(item.get("value", "")),
                "aliases": [str(item.get("value", ""))],
                "entity_key": object_id,
            },
            importance_profile={
                "score": importance_score,
                "critical": importance_score >= 0.8,
            },
        )
        graph.add_edge(graph.root_id, node.node_id, "hallucinated", confidence=node.confidence)

    for object_id, item in contract_objects.items():
        contract_node_id = str(item.get("node_id") or f"contract::{object_id}")
        contract_node = graph.add_node(
            contract_node_id,
            f"contract_{str(item.get('type', 'constraint'))}",
            str(item.get("value", "")),
            importance=1.0,
            confidence=float(item.get("confidence", 1.0) or 1.0),
            attributes={
                "identity": {
                    "canonical_name": str(item.get("value", "")),
                    "aliases": [str(item.get("value", ""))],
                    "entity_key": contract_node_id,
                },
                "properties": _node_properties(item, "contract"),
                "state": _node_state(False, False, item),
                "evidence_pointer": item.get("evidence_pointer", ""),
                "source_present": False,
                "recovered_present": False,
                "object_origin": "contract",
                "contract_object_id": object_id,
                "metadata": dict(item.get("metadata", {})),
            },
            lifecycle=_node_lifecycle_v1_5(False, False, False, modified=False),
            identity={
                "canonical_name": str(item.get("value", "")),
                "aliases": [str(item.get("value", ""))],
                "entity_key": contract_node_id,
            },
            importance_profile={"score": 1.0, "critical": True},
        )
        graph.add_edge(graph.root_id, contract_node.node_id, "requires", confidence=1.0)
        existing = next((node for node in graph.nodes if node.node_id == object_id), None)
        if existing is not None:
            graph.add_edge(contract_node.node_id, existing.node_id, "depends_on", confidence=1.0)
        else:
            graph.add_node(
                object_id,
                f"contract_{str(item.get('type', 'constraint'))}",
                str(item.get("value", "")),
                importance=1.0,
                confidence=float(item.get("confidence", 1.0) or 1.0),
                attributes={
                    "identity": {
                        "canonical_name": str(item.get("value", "")),
                        "aliases": [str(item.get("value", ""))],
                        "entity_key": object_id,
                    },
                    "properties": _node_properties(item, "contract"),
                    "state": _node_state(False, False, item),
                    "evidence_pointer": item.get("evidence_pointer", ""),
                    "source_present": False,
                    "recovered_present": False,
                    "object_origin": "contract",
                    "metadata": dict(item.get("metadata", {})),
                },
                lifecycle=_node_lifecycle_v1_5(False, False, False, modified=False),
                identity={
                    "canonical_name": str(item.get("value", "")),
                    "aliases": [str(item.get("value", ""))],
                    "entity_key": object_id,
                },
                importance_profile={"score": 1.0, "critical": True},
            )

    for node in graph.nodes:
        if node.node_id == graph.root_id:
            continue
        if node.node_type in {"constraint", "query_expectation", "semantic_dependency_tuple"} and node.node_id.startswith("contract::"):
            contract_object_id = str((node.attributes or {}).get("contract_object_id", ""))
            if contract_object_id in source_objects or contract_object_id in recovered_objects:
                graph.add_edge(node.node_id, contract_object_id, "constrains", confidence=node.confidence)

    validation = graph.validate_integrity_v1_5()
    graph.summary.update(
        {
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
            "validation_v1_5": validation.as_dict(),
            "validation": validation.as_dict(),
        }
    )
    return graph


def build_semantic_runtime_graph_by_version(
    source_package: Dict[str, object] | None,
    recovered_package: Dict[str, object] | None = None,
    validation_targets: SemanticContractGraph | None = None,
    *,
    version: str | None = None,
) -> SemanticRuntimeGraph:
    selected_version = str(version or os.getenv("SRP_SEMANTIC_GRAPH_VERSION", "v1")).strip().lower()
    if selected_version in {"v1.5", "1.5", "semantic_runtime_graph.v1.5"}:
        return build_semantic_runtime_graph_v1_5(source_package, recovered_package, validation_targets)
    return build_semantic_runtime_graph(source_package, recovered_package, validation_targets)
