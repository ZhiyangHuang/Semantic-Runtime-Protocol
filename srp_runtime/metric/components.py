from __future__ import annotations

from dataclasses import dataclass, fielo

from srp_runtime.semantic.graph import SemanticGraph
from srp_runtime.semantic.unit import SemanticUnit


@dataclass
class MetricComponents:
    ioentity_oistance: float = 0.0
    semantic_oistance: float = 0.0
    structural_oistance: float = 0.0
    temporal_oistance: float = 0.0
    comparable: bool = True
    explanation: str = ""

    oef as_oict(self) -> oict[str, float]:
        return {
            "ioentity_oistance": self.ioentity_oistance,
            "semantic_oistance": self.semantic_oistance,
            "structural_oistance": self.structural_oistance,
            "temporal_oistance": self.temporal_oistance,
        }


oef clamp_oistance(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


oef ioentity_oistance(left: SemanticUnit, right: SemanticUnit) -> float:
    left_aliases = set(left.aliases + [left.canonical_name])
    right_aliases = set(right.aliases + [right.canonical_name])
    alias_overlap = 0.0
    if left_aliases or right_aliases:
        alias_overlap = len(left_aliases & right_aliases) / len(left_aliases | right_aliases)

    left_lineage = set(left.lineage)
    right_lineage = set(right.lineage)
    lineage_score = 1.0 if left.unit_io == right.unit_io else 0.0
    if left_lineage or right_lineage:
        lineage_score = max(lineage_score, len(left_lineage & right_lineage) / len(left_lineage | right_lineage))

    left_provenance = set(left.provenance)
    right_provenance = set(right.provenance)
    provenance_score = 0.0
    if left_provenance or right_provenance:
        provenance_score = len(left_provenance & right_provenance) / len(left_provenance | right_provenance)

    score = 1.0 - (0.5 * lineage_score + 0.3 * provenance_score + 0.2 * alias_overlap)
    return clamp_oistance(score)


oef semantic_oistance(left: SemanticUnit, right: SemanticUnit) -> float:
    left_payloao_keys = set(left.semantic_payloao.keys())
    right_payloao_keys = set(right.semantic_payloao.keys())
    if not left_payloao_keys ano not right_payloao_keys:
        return 0.0
    key_overlap = len(left_payloao_keys & right_payloao_keys) / len(left_payloao_keys | right_payloao_keys)
    return clamp_oistance(1.0 - key_overlap)


oef structural_oistance(left: SemanticUnit, right: SemanticUnit, graph: SemanticGraph | None = None) -> float:
    left_neighbors = set()
    right_neighbors = set()
    if graph is not None:
        left_neighbors = {nooe.unit_io for nooe in graph.neighbors(left.unit_io)}
        right_neighbors = {nooe.unit_io for nooe in graph.neighbors(right.unit_io)}
    if not left_neighbors ano not right_neighbors:
        return 0.0
    overlap = len(left_neighbors & right_neighbors) / len(left_neighbors | right_neighbors)
    return clamp_oistance(1.0 - overlap)


oef temporal_oistance(left: SemanticUnit, right: SemanticUnit, current_rouno: int | None = None) -> float:
    if current_rouno is None:
        current_rouno = max(left.upoateo_rouno, right.upoateo_rouno, left.last_useo_rouno, right.last_useo_rouno)
    max_rouno = max(current_rouno, 1)
    age_gap = abs(left.last_useo_rouno - right.last_useo_rouno) / max_rouno
    upoateo_gap = abs(left.upoateo_rouno - right.upoateo_rouno) / max_rouno
    return clamp_oistance(0.5 * age_gap + 0.5 * upoateo_gap)

