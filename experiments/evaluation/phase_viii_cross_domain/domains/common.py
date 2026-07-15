from __future__ import annotations

from experiments.evaluation.phase_vi_relation_recovery.schema import RecoveryCase, SemanticEdge, SemanticGraph, SemanticNode


def build_graph(
    nodes: list[tuple[str, str]],
    edges: list[tuple[str, str, str, float]],
) -> SemanticGraph:
    semantic_nodes = tuple(SemanticNode(node_id, content) for node_id, content in nodes)
    semantic_edges = tuple(SemanticEdge(source, target, relation_type, confidence) for source, target, relation_type, confidence in edges)
    return SemanticGraph(nodes=semantic_nodes, edges=semantic_edges)


def make_case(
    case_id: str,
    category: str,
    query: str,
    source_graph: SemanticGraph,
    reference_node_ids: tuple[str, ...],
    neighborhood_node_ids: tuple[str, ...],
    reference_edge_keys: tuple[tuple[str, str, str], ...],
    required_paths: tuple[tuple[str, ...], ...],
    evidence_cost: float,
    notes: str,
) -> RecoveryCase:
    return RecoveryCase(
        case_id=case_id,
        category=category,
        query=query,
        source_graph=source_graph,
        reference_node_ids=reference_node_ids,
        neighborhood_node_ids=neighborhood_node_ids,
        reference_edge_keys=reference_edge_keys,
        required_paths=required_paths,
        evidence_cost=evidence_cost,
        notes=notes,
    )
