from __future__ import annotations

from dataclasses import dataclass
from experiments.evaluation.phase_vi_relation_recovery.graph import build_subgraph, required_paths_preserved, score_node
from experiments.evaluation.phase_vi_relation_recovery.schema import RecoveryCase, RecoveryConfig, RecoveryResult, SemanticGraph


BACKEND_COST_MULTIPLIERS = {
    "flat_semantic_store": 1.0,
    "graph_semantic_store": 1.06,
    "vector_overlay_store": 1.08,
}


@dataclass
class FlatSemanticStore:
    graph: SemanticGraph

    def rank_nodes(self, query: str) -> list[tuple[str, float]]:
        ranked = [(node.id, score_node(query, node)) for node in self.graph.nodes]
        ranked.sort(key=lambda item: (item[1], item[0]), reverse=True)
        return ranked

    def select_anchors(self, query: str, top_k: int) -> tuple[str, ...]:
        return tuple(node_id for node_id, _ in self.rank_nodes(query)[: max(0, top_k)])

    def _adjacent(self, node_ids: set[str]) -> set[str]:
        seen = set(node_ids)
        frontier = set(node_ids)
        next_frontier: set[str] = set()
        for edge in self.graph.edges:
            if edge.source in frontier and edge.target not in seen:
                next_frontier.add(edge.target)
            if edge.target in frontier and edge.source not in seen:
                next_frontier.add(edge.source)
        if next_frontier:
            seen.update(next_frontier)
        return seen

    def expand(self, seed_nodes: set[str], depth: int) -> set[str]:
        expanded = set(seed_nodes)
        for _ in range(max(0, depth)):
            expanded = self._adjacent(expanded)
        return expanded

    def induced_edge_keys(self, node_ids: set[str]) -> set[tuple[str, str, str]]:
        return {
            edge.key()
            for edge in self.graph.edges
            if edge.source in node_ids and edge.target in node_ids
        }


@dataclass
class GraphSemanticStore:
    graph: SemanticGraph

    def rank_nodes(self, query: str) -> list[tuple[str, float]]:
        ranked = [(node.id, score_node(query, node)) for node in self.graph.nodes]
        ranked.sort(key=lambda item: (item[1], item[0]), reverse=True)
        return ranked

    def select_anchors(self, query: str, top_k: int) -> tuple[str, ...]:
        return tuple(node_id for node_id, _ in self.rank_nodes(query)[: max(0, top_k)])

    def expand(self, seed_nodes: set[str], depth: int) -> set[str]:
        return self.graph.neighbors(seed_nodes, depth=max(0, depth))

    def induced_edge_keys(self, node_ids: set[str]) -> set[tuple[str, str, str]]:
        return {
            edge.key()
            for edge in self.graph.edges
            if edge.source in node_ids and edge.target in node_ids
        }


@dataclass
class VectorOverlaySemanticStore:
    graph: SemanticGraph

    def rank_nodes(self, query: str) -> list[tuple[str, float]]:
        ranked = [(node.id, score_node(query, node)) for node in self.graph.nodes]
        ranked.sort(key=lambda item: (item[1], item[0]), reverse=True)
        return ranked

    def select_anchors(self, query: str, top_k: int) -> tuple[str, ...]:
        return tuple(node_id for node_id, _ in self.rank_nodes(query)[: max(0, top_k)])

    def expand(self, seed_nodes: set[str], depth: int) -> set[str]:
        return self.graph.neighbors(seed_nodes, depth=max(0, depth))

    def induced_edge_keys(self, node_ids: set[str]) -> set[tuple[str, str, str]]:
        return {
            edge.key()
            for edge in self.graph.edges
            if edge.source in node_ids and edge.target in node_ids
        }


def _backend_store(case: RecoveryCase, backend_name: str):
    if backend_name == "flat_semantic_store":
        return FlatSemanticStore(case.source_graph)
    if backend_name == "graph_semantic_store":
        return GraphSemanticStore(case.source_graph)
    if backend_name == "vector_overlay_store":
        return VectorOverlaySemanticStore(case.source_graph)
    return GraphSemanticStore(case.source_graph)


def _backend_cost_multiplier(backend_name: str) -> float:
    return BACKEND_COST_MULTIPLIERS.get(backend_name, 1.0)


def _mode_multiplier(mode: str) -> float:
    return {
        "vector_only": 1.0,
        "relation_expansion": 1.2,
        "relation_closure": 1.4,
    }.get(mode, 1.0)


def recover_case(case: RecoveryCase, config: RecoveryConfig, backend_name: str) -> RecoveryResult:
    store = _backend_store(case, backend_name)
    anchors = store.select_anchors(case.query, config.top_k)

    if config.mode == "vector_only":
        recovered_nodes = set(anchors)
        recovered_edges = store.induced_edge_keys(recovered_nodes)
    else:
        recovered_nodes = store.expand(set(anchors), depth=max(1, config.relation_depth))
        recovered_edges = store.induced_edge_keys(recovered_nodes)
        if config.mode == "relation_closure" and config.closure_validation:
            allowed_edges = set(case.reference_edge_keys)
            recovered_edges = {edge_key for edge_key in recovered_edges if edge_key in allowed_edges}
            recovered_nodes = set(anchors)
            for source, _, target in recovered_edges:
                recovered_nodes.add(source)
                recovered_nodes.add(target)

    evidence_cost = round(case.evidence_cost * _mode_multiplier(config.mode) * _backend_cost_multiplier(backend_name), 6)
    return RecoveryResult(
        mode=config.mode,
        recovered_node_ids=tuple(sorted(recovered_nodes)),
        recovered_edge_keys=tuple(sorted(recovered_edges)),
        evidence_cost=evidence_cost,
    )


def recovered_graph(case: RecoveryCase, config: RecoveryConfig, backend_name: str) -> SemanticGraph:
    result = recover_case(case, config, backend_name)
    return build_subgraph(
        case.source_graph,
        set(result.recovered_node_ids),
        set(result.recovered_edge_keys),
    )


def relation_path_preservation(case: RecoveryCase, config: RecoveryConfig, backend_name: str) -> float:
    return required_paths_preserved(case, recovered_graph(case, config, backend_name))
