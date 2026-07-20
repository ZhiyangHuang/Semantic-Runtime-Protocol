from typing import Dict, Tuple

from .state import SemanticObjectMetadata
from .validation_matching import OBJECT_WEIGHTS


def weighted_alignment_coverage(
    alignment: Dict[str, Dict[str, object]],
    runtime_metadata: Dict[str, SemanticObjectMetadata] | None = None,
) -> Tuple[float, Dict[str, Dict[str, float]]]:
    details: Dict[str, Dict[str, float]] = {}
    total_weight = 0.0
    matched_weight = 0.0

    for object_type, base_weight in OBJECT_WEIGHTS.items():
        matches = alignment.get(object_type, {}).get("matches", [])
        total = len(matches)
        matched = sum(1 for item in matches if float(item["similarity"]) >= 0.5)
        average_similarity = (sum(float(item["similarity"]) for item in matches) / total) if total else 1.0
        average_importance = 1.0
        average_effective_weight = base_weight
        effective_weights = []
        type_weight = 0.0
        type_matched_weight = 0.0
        for item in matches:
            object_id = item.get("source_object_id")
            metadata = runtime_metadata.get(object_id) if runtime_metadata else None
            importance = metadata.importance if metadata else 1.0
            effective_weight = base_weight * importance
            effective_weights.append(effective_weight)
            type_weight += effective_weight
            type_matched_weight += float(item["similarity"]) * effective_weight
        if effective_weights:
            average_importance = sum((w / base_weight) if base_weight else 0.0 for w in effective_weights) / len(
                effective_weights
            )
            average_effective_weight = sum(effective_weights) / len(effective_weights)
        total_weight += type_weight
        matched_weight += type_matched_weight
        details[object_type] = {
            "source_count": float(total),
            "matched_count": float(matched),
            "weight_per_object": base_weight,
            "average_importance": average_importance,
            "average_effective_weight": average_effective_weight,
            "coverage": (matched / total) if total else 1.0,
            "average_similarity": average_similarity,
        }

    if total_weight == 0:
        return 1.0, details
    return matched_weight / total_weight, details
