from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from srp_runtime.metric.components import (
    MetricComponents,
    identity_distance,
    semantic_distance,
    structural_distance,
    temporal_distance,
)
from srp_runtime.semantic.graph import SemanticGraph
from srp_runtime.semantic.unit import SemanticUnit


@dataclass
class MetricResult:
    source_id: str
    target_id: str
    total_distance: float
    component_scores: dict[str, float] = field(default_factory=dict)
    comparable: bool = True
    explanation: str = ""


class SemanticMetric:
    def __init__(
        self,
        identity_weight: float = 0.35,
        semantic_weight: float = 0.30,
        structural_weight: float = 0.20,
        temporal_weight: float = 0.15,
    ) -> None:
        self.identity_weight = identity_weight
        self.semantic_weight = semantic_weight
        self.structural_weight = structural_weight
        self.temporal_weight = temporal_weight

    def distance(
        self,
        source: SemanticUnit,
        target: SemanticUnit,
        graph: SemanticGraph | None = None,
        current_round: int | None = None,
    ) -> MetricResult:
        components = MetricComponents(
            identity_distance=identity_distance(source, target),
            semantic_distance=semantic_distance(source, target),
            structural_distance=structural_distance(source, target, graph),
            temporal_distance=temporal_distance(source, target, current_round),
        )
        total_distance = (
            self.identity_weight * components.identity_distance
            + self.semantic_weight * components.semantic_distance
            + self.structural_weight * components.structural_distance
            + self.temporal_weight * components.temporal_distance
        )
        explanation = (
            "identity={:.3f}, semantic={:.3f}, structural={:.3f}, temporal={:.3f}".format(
                components.identity_distance,
                components.semantic_distance,
                components.structural_distance,
                components.temporal_distance,
            )
        )
        return MetricResult(
            source_id=source.unit_id,
            target_id=target.unit_id,
            total_distance=total_distance,
            component_scores=components.as_dict(),
            comparable=components.comparable,
            explanation=explanation,
        )

    def similarity(
        self,
        source: SemanticUnit,
        target: SemanticUnit,
        graph: SemanticGraph | None = None,
        current_round: int | None = None,
    ) -> MetricResult:
        result = self.distance(source, target, graph=graph, current_round=current_round)
        result.total_distance = max(0.0, 1.0 - result.total_distance)
        result.explanation = f"similarity={result.total_distance:.3f}; {result.explanation}"
        return result

