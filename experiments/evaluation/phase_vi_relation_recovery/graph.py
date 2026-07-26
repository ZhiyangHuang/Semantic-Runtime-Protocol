from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

from .schema import RecoveryCase, SemanticEdge, SemanticGraph, SemanticNode


_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


def tokenize(text: str) -> tuple[str, ...]:
    return tuple(token.lower() for token in _TOKEN_RE.findall(text or ""))


def jaccard_similarity(left: Iterable[str], right: Iterable[str]) -> float:
    left_set = set(left)
    right_set = set(right)
    if not left_set and not right_set:
        return 1.0
    union = left_set | right_set
    if not union:
        return 0.0
    return len(left_set & right_set) / len(union)


def score_node(query: str, node: SemanticNode) -> float:
    query_tokens = tokenize(query)
    content_tokens = tokenize(node.content)
    overlap = jaccard_similarity(query_tokens, content_tokens)
    query_counter = Counter(query_tokens)
    content_counter = Counter(content_tokens)
    phrase_bonus = 0.0
    for token, count in query_counter.items():
        if token in content_counter:
            phrase_bonus += min(count, content_counter[token]) * 0.05
    return round(min(1.0, overlap + phrase_bonus), 6)


def rank_nodes(query: str, graph: SemanticGraph) -> list[tuple[str, float]]:
    ranked = [(node.id, score_node(query, node)) for node in graph.nodes]
    ranked.sort(key=lambda item: (item[1], item[0]), reverse=True)
    return ranked


def select_top_nodes(query: str, graph: SemanticGraph, top_k: int) -> tuple[str, ...]:
    return tuple(node_id for node_id, _ in rank_nodes(query, graph)[: max(0, top_k)])


def induced_edge_keys(graph: SemanticGraph, node_ids: set[str]) -> tuple[tuple[str, str, str], ...]:
    return tuple(edge.key() for edge in graph.edges_for_nodes(node_ids))


def expansion_nodes(graph: SemanticGraph, seed_nodes: set[str], depth: int) -> set[str]:
    return graph.neighbors(seed_nodes, depth=depth)


def build_subgraph(graph: SemanticGraph, node_ids: set[str], edge_keys: set[tuple[str, str, str]] | None = None) -> SemanticGraph:
    selected_nodes = tuple(node for node in graph.nodes if node.id in node_ids)
    if edge_keys is None:
        selected_edges = graph.edges_for_nodes(node_ids)
    else:
        selected_edges = tuple(edge for edge in graph.edges if edge.key() in edge_keys)
    return SemanticGraph(nodes=selected_nodes, edges=selected_edges)


def required_paths_preserved(reference: RecoveryCase, recovered_graph: SemanticGraph) -> float:
    if not reference.required_paths:
        return 1.0
    adjacency: dict[str, set[str]] = {}
    for edge in recovered_graph.edges:
        adjacency.setdefault(edge.source, set()).add(edge.target)
    preserved = 0
    for path in reference.required_paths:
        if len(path) < 2:
            continue
        if all(path[index + 1] in adjacency.get(path[index], set()) for index in range(len(path) - 1)):
            preserved += 1
    valid_paths = sum(1 for path in reference.required_paths if len(path) >= 2)
    return preserved / valid_paths if valid_paths else 1.0
