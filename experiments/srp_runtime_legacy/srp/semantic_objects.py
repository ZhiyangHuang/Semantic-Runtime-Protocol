from typing import Dict, List


def build_semantic_object_inventory(state) -> Dict[str, object]:
    representation = state.ensure_typed_representation()
    objects = [item.as_dict() for item in representation.objects]
    object_ids = [item.stable_id() for item in representation.objects]
    type_counts: Dict[str, int] = {}
    important_objects: List[Dict[str, object]] = []
    for semantic_object in representation.objects:
        object_type = semantic_object.object_type
        type_counts[object_type] = type_counts.get(object_type, 0) + 1
        if semantic_object.object_type in {"question", "constraint", "anchor"} or semantic_object.confidence >= 0.8:
            important_objects.append(
                {
                    "object_id": semantic_object.stable_id(),
                    "type": semantic_object.object_type,
                    "value": semantic_object.value,
                    "confidence": round(semantic_object.confidence, 4),
                    "evidence_pointer": semantic_object.evidence_pointer,
                }
            )
    return {
        "schema_version": "semantic_object_inventory.v1",
        "object_count": len(objects),
        "object_ids": object_ids,
        "type_counts": type_counts,
        "important_objects": important_objects[:20],
        "objects": objects,
    }
