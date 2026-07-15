from __future__ import annotations

from dataclasses import dataclass, field

from srp_runtime.semantic.graph import SemanticGraph
from srp_runtime.semantic.unit import SemanticUnit


@dataclass
class MetricComponents:
    identity_distance: float = 0.0
    semantic_distance: float = 0.0
    structural_distance: float = 0.0
    temporal_distance: float = 0.0
    comparable: bool = True
    explanation: str = ""

    def as_dict(self) -> dict[str, float]:
        return {
            "identity_distance": self.identity_distance,
            "semantic_distance": self.semantic_distance,
            "structural_distance": self.structural_distance,
            "temporal_distance": self.temporal_distance,
        }


def clamp_distance(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def identity_distance(left: SemanticUnit, right: SemanticUnit) -> float:
    left_aliases = set(left.aliases + [left.canonical_name])
    right_aliases = set(right.aliases + [right.canonical_name])
    alias_overlap = 0.0
    if left_aliases or right_aliases:
        alias_overlap = len(left_aliases & right_aliases) / len(left_aliases | right_aliases)

    left_lineage = set(left.lineage)
    right_lineage = set(right.lineage)
    lineage_score = 1.0 if left.unit_id == right.unit_id else 0.0
    if left_lineage or right_lineage:
        lineage_score = max(lineage_score, len(left_lineage & right_lineage) / len(left_lineage | right_lineage))

    left_provenance = set(left.provenance)
    right_provenance = set(right.provenance)
    provenance_score = 0.0
    if left_provenance or right_provenance:
        provenance_score = len(left_provenance & right_provenance) / len(left_provenance | right_provenance)

    score = 1.0 - (0.5 * lineage_score + 0.3 * provenance_score + 0.2 * alias_overlap)
    return clamp_distance(score)


def semantic_distance(left: SemanticUnit, right: SemanticUnit) -> float:
    left_payload_keys = set(left.semantic_payload.keys())
    right_payload_keys = set(right.semantic_payload.keys())
    if not left_payload_keys and not right_payload_keys:
        return 0.0
    key_overlap = len(left_payload_keys & right_payload_keys) / len(left_payload_keys | right_payload_keys)
    return clamp_distance(1.0 - key_overlap)


def structural_distance(left: SemanticUnit, right: SemanticUnit, graph: SemanticGraph | None = None) -> float:
    left_neighbors = set()
    right_neighbors = set()
    if graph is not None:
        left_neighbors = {node.unit_id for node in graph.neighbors(left.unit_id)}
        right_neighbors = {node.unit_id for node in graph.neighbors(right.unit_id)}
    if not left_neighbors and not right_neighbors:
        return 0.0
    overlap = len(left_neighbors & right_neighbors) / len(left_neighbors | right_neighbors)
    return clamp_distance(1.0 - overlap)


def temporal_distance(left: SemanticUnit, right: SemanticUnit, current_round: int | None = None) -> float:
    if current_round is None:
        current_round = max(left.updated_round, right.updated_round, left.last_used_round, right.last_used_round)
    max_round = max(current_round, 1)
    age_gap = abs(left.last_used_round - right.last_used_round) / max_round
    updated_gap = abs(left.updated_round - right.updated_round) / max_round
    return clamp_distance(0.5 * age_gap + 0.5 * updated_gap)

