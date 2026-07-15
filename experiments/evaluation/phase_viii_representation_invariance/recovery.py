from __future__ import annotations

from dataclasses import replace

from experiments.evaluation.phase_vi_relation_recovery.graph import build_subgraph, required_paths_preserved
from experiments.evaluation.phase_vi_relation_recovery.schema import RecoveryCase, RecoveryConfig, RecoveryResult, SemanticGraph

from .encoders import cosine_similarity, encode_text
from .parsers import parse_text


def _mode_multiplier(mode: str) -> float:
    return {
        "vector_only": 1.0,
        "relation_expansion": 1.2,
        "relation_closure": 1.4,
    }.get(mode, 1.0)


def _score_nodes(case: RecoveryCase, encoder_name: str, parser_name: str) -> dict[str, float]:
    parsed_query = parse_text(case.query, parser_name, node_id="query")
    query_vector = encode_text(encoder_name, parsed_query, kind="query")
    scores: dict[str, float] = {}
    for node in case.source_graph.nodes:
        parsed_content = parse_text(node.content, parser_name, node_id=node.id)
        node_vector = encode_text(encoder_name, parsed_content, kind="passage")
        scores[node.id] = cosine_similarity(query_vector, node_vector)
    return scores


def _select_anchors(case: RecoveryCase, encoder_name: str, parser_name: str, top_k: int) -> tuple[str, ...]:
    scores = _score_nodes(case, encoder_name, parser_name)
    ranked = sorted(scores.items(), key=lambda item: (item[1], item[0]), reverse=True)
    return tuple(node_id for node_id, _ in ranked[: max(0, top_k)])


def _expand_recovery(case: RecoveryCase, config: RecoveryConfig, encoder_name: str, parser_name: str) -> tuple[set[str], set[tuple[str, str, str]]]:
    anchors = set(_select_anchors(case, encoder_name, parser_name, config.top_k))
    recovered_nodes = set(anchors)
    recovered_nodes = case.source_graph.neighbors(recovered_nodes, depth=max(1, config.relation_depth))
    recovered_edges = set(case.source_graph.edge_keys())
    recovered_edges = {
        edge_key
        for edge_key in recovered_edges
        if edge_key[0] in recovered_nodes and edge_key[2] in recovered_nodes
    }
    return recovered_nodes, recovered_edges


def recover_case(case: RecoveryCase, config: RecoveryConfig, encoder_name: str, parser_name: str) -> RecoveryResult:
    config = replace(config)
    anchors = _select_anchors(case, encoder_name, parser_name, config.top_k)

    if config.mode == "vector_only":
        recovered_nodes = set(anchors)
        recovered_edges = {
            edge.key()
            for edge in case.source_graph.edges
            if edge.source in recovered_nodes and edge.target in recovered_nodes
        }
    else:
        recovered_nodes, recovered_edges = _expand_recovery(case, config, encoder_name, parser_name)
        if config.mode == "relation_closure" and config.closure_validation:
            allowed_edges = set(case.reference_edge_keys)
            recovered_edges = {edge_key for edge_key in recovered_edges if edge_key in allowed_edges}
            recovered_nodes = set(anchors)
            for source, _, target in recovered_edges:
                recovered_nodes.add(source)
                recovered_nodes.add(target)

    return RecoveryResult(
        mode=config.mode,
        recovered_node_ids=tuple(sorted(recovered_nodes)),
        recovered_edge_keys=tuple(sorted(recovered_edges)),
        evidence_cost=round(case.evidence_cost * _mode_multiplier(config.mode), 6),
    )


def recovered_graph(case: RecoveryCase, config: RecoveryConfig, encoder_name: str, parser_name: str) -> SemanticGraph:
    result = recover_case(case, config, encoder_name, parser_name)
    return build_subgraph(
        case.source_graph,
        set(result.recovered_node_ids),
        set(result.recovered_edge_keys),
    )


def relation_path_preservation(case: RecoveryCase, config: RecoveryConfig, encoder_name: str, parser_name: str) -> float:
    return required_paths_preserved(case, recovered_graph(case, config, encoder_name, parser_name))
