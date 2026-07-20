from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SemanticGraphLifecycle:
    schema_version: str = "semantic_runtime_graph_lifecycle.v1"
    created_count: int = 0
    compressed_count: int = 0
    recovered_count: int = 0
    modified_count: int = 0
    verified_count: int = 0
    retained_count: int = 0
    object_survival_rate: float | None = None
    dependency_recall: float | None = None
    constraint_accuracy: float | None = None
    hallucination_rate: float | None = None
    graph_integrity_score: float | None = None
    attribute_retention: float | None = None
    state_retention: float | None = None
    lifecycle_accuracy: float | None = None
    issues: Dict[str, List[Dict[str, object]]] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "created_count": self.created_count,
            "compressed_count": self.compressed_count,
            "recovered_count": self.recovered_count,
            "modified_count": self.modified_count,
            "verified_count": self.verified_count,
            "retained_count": self.retained_count,
            "object_survival_rate": self.object_survival_rate,
            "dependency_recall": self.dependency_recall,
            "constraint_accuracy": self.constraint_accuracy,
            "hallucination_rate": self.hallucination_rate,
            "graph_integrity_score": self.graph_integrity_score,
            "attribute_retention": self.attribute_retention,
            "state_retention": self.state_retention,
            "lifecycle_accuracy": self.lifecycle_accuracy,
            "issues": {key: list(value) for key, value in self.issues.items()},
        }
