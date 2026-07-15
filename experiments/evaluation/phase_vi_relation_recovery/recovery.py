from __future__ import annotations

from dataclasses import replace

from .graph import build_subgraph, induced_edge_keys, expansion_nodes, select_top_nodes
from .schema import RecoveryCase, RecoveryConfig, RecoveryResult, SemanticGraph


def _mode_multiplier(mode: str) -> float:
    return {
        "vector_only": 1.0,
        "relation_expansion": 1.2,
        "relation_closure": 1.4,
    }.get(mode, 1.0)


def _base_recovered_nodes(case: RecoveryCase, config: RecoveryConfig) -> tuple[str, ...]:
    return select_top_nodes(case.query, case.source_graph, config.top_k)


def _expand_recovery(case: RecoveryCase, config: RecoveryConfig) -> tuple[set[str], set[tuple[str, str, str]]]:
    anchors = set(_base_recovered_nodes(case, config))
    recovered_nodes = set(anchors)
    recovered_nodes = expansion_nodes(case.source_graph, recovered_nodes, depth=max(1, config.relation_depth))
    recovered_edges = set(induced_edge_keys(case.source_graph, recovered_nodes))
    return recovered_nodes, recovered_edges


def recover_case(case: RecoveryCase, config: RecoveryConfig) -> RecoveryResult:
    config = replace(config)
    anchors = _base_recovered_nodes(case, config)

    if config.mode == "vector_only":
        recovered_nodes = set(anchors)
        recovered_edges = set(induced_edge_keys(case.source_graph, recovered_nodes))
    else:
        recovered_nodes, recovered_edges = _expand_recovery(case, config)
        if config.mode == "relation_closure" and config.closure_validation:
            allowed_edges = set(case.reference_edge_keys)
            recovered_edges = {edge_key for edge_key in recovered_edges if edge_key in allowed_edges}
            recovered_nodes = set()
            for source, _, target in recovered_edges:
                recovered_nodes.add(source)
                recovered_nodes.add(target)
            recovered_nodes.update(anchors)

    return RecoveryResult(
        mode=config.mode,
        recovered_node_ids=tuple(sorted(recovered_nodes)),
        recovered_edge_keys=tuple(sorted(recovered_edges)),
        evidence_cost=round(case.evidence_cost * _mode_multiplier(config.mode), 6),
    )


def recovered_graph(case: RecoveryCase, config: RecoveryConfig) -> SemanticGraph:
    result = recover_case(case, config)
    return build_subgraph(
        case.source_graph,
        set(result.recovered_node_ids),
        set(result.recovered_edge_keys),
    )
