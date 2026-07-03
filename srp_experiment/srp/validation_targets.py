from dataclasses import dataclass, field
from typing import Dict, Iterable, List


def _normalize_phrase(value: str) -> str:
    return " ".join(str(value).strip().lower().split())


def _dedupe_group(values: Iterable[str]) -> List[str]:
    seen = set()
    group = []
    for value in values:
        normalized = _normalize_phrase(value)
        if normalized and normalized not in seen:
            seen.add(normalized)
            group.append(str(value).strip())
    return group


@dataclass
class SemanticContractVariant:
    surface: str
    normalized: str

    def as_dict(self) -> Dict:
        return {
            "surface": self.surface,
            "normalized": self.normalized,
        }


@dataclass
class SemanticContractNode:
    node_id: str
    node_type: str
    role: str
    variants: List[SemanticContractVariant] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> Dict:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "role": self.role,
            "variants": [variant.as_dict() for variant in self.variants],
            "metadata": dict(self.metadata),
        }


@dataclass
class SemanticContractEdge:
    source: str
    target: str
    edge_type: str

    def as_dict(self) -> Dict:
        return {
            "source": self.source,
            "target": self.target,
            "edge_type": self.edge_type,
        }


@dataclass
class SemanticContractGraph:
    nodes: List[SemanticContractNode] = field(default_factory=list)
    edges: List[SemanticContractEdge] = field(default_factory=list)

    def clause_nodes(self) -> List[SemanticContractNode]:
        return [node for node in self.nodes if node.role == "clause"]

    def flattened_variants(self) -> List[str]:
        flattened: List[str] = []
        for node in self.clause_nodes():
            for variant in node.variants:
                if variant.surface.strip():
                    flattened.append(variant.surface.strip())
        return flattened

    def as_dict(self) -> Dict:
        return {
            "nodes": [node.as_dict() for node in self.nodes],
            "edges": [edge.as_dict() for edge in self.edges],
        }


def _build_variant(value: str) -> SemanticContractVariant:
    return SemanticContractVariant(
        surface=str(value).strip(),
        normalized=_normalize_phrase(value),
    )


def build_validation_targets(task: Dict) -> SemanticContractGraph:
    graph = SemanticContractGraph()
    seen_signatures = set()
    root_id = f"{task.get('id', 'task')}::contract"
    graph.nodes.append(
        SemanticContractNode(
            node_id=root_id,
            node_type="contract_root",
            role="root",
            metadata={"task_id": str(task.get("id", "unknown"))},
        )
    )

    def add_clause(role: str, node_type: str, values: Iterable[str], metadata: Dict[str, str]) -> None:
        group = _dedupe_group(values)
        if not group:
            return
        signature = tuple(_normalize_phrase(item) for item in group)
        if signature in seen_signatures:
            return
        seen_signatures.add(signature)
        node_id = f"{root_id}::{len(graph.nodes)}"
        node = SemanticContractNode(
            node_id=node_id,
            node_type=node_type,
            role=role,
            variants=[_build_variant(item) for item in group],
            metadata=metadata,
        )
        graph.nodes.append(node)
        graph.edges.append(
            SemanticContractEdge(
                source=root_id,
                target=node_id,
                edge_type="requires",
            )
        )

    for expectation_idx, expectation_group in enumerate(task.get("query_expectations", []), start=1):
        for clause_idx, raw_group in enumerate(expectation_group, start=1):
            if isinstance(raw_group, str):
                values = [raw_group]
            else:
                values = list(raw_group)
            add_clause(
                role="clause",
                node_type="query_expectation",
                values=values,
                metadata={
                    "source": "query_expectations",
                    "expectation_index": str(expectation_idx),
                    "clause_index": str(clause_idx),
                },
            )

    for keyword_idx, keyword in enumerate(task.get("expected_keywords", []), start=1):
        add_clause(
            role="clause",
            node_type="expected_keyword",
            values=[keyword],
            metadata={
                "source": "expected_keywords",
                "keyword_index": str(keyword_idx),
            },
        )

    for constraint_idx, constraint in enumerate(task.get("initial_state", {}).get("constraints", []), start=1):
        add_clause(
            role="clause",
            node_type="constraint",
            values=[constraint],
            metadata={
                "source": "constraints",
                "constraint_index": str(constraint_idx),
            },
        )

    return graph
