import re
from typing import Dict, List

from .semantic_parser import TypedSemanticRepresentation, canonicalize_semantic_value

OBJECT_WEIGHTS = {
    "constraint": 0.5,
    "fact": 0.3,
    "anchor": 0.2,
}


def normalize_semantic_value(value: str) -> str:
    return canonicalize_semantic_value(value)


def tokenize_semantic_value(value: str) -> List[str]:
    return [token for token in re.split(r"[^a-z0-9]+", normalize_semantic_value(value)) if token]


def semantic_equivalence_bonus(source_value: str, recovered_value: str) -> float:
    source = normalize_semantic_value(source_value)
    recovered = normalize_semantic_value(recovered_value)
    if source == recovered:
        return 1.0
    equivalences = {
        ("new york city", "nyc"),
        ("nyc", "new york city"),
        ("professor", "prof."),
        ("prof.", "professor"),
        ("computer science", "cs"),
        ("cs", "computer science"),
    }
    return 1.0 if (source, recovered) in equivalences else 0.0


def canonical_exact_similarity(source_value: str, recovered_value: str) -> float:
    source = normalize_semantic_value(source_value)
    recovered = normalize_semantic_value(recovered_value)
    return 1.0 if source and source == recovered else 0.0


def substring_similarity(source_value: str, recovered_value: str) -> float:
    source = normalize_semantic_value(source_value)
    recovered = normalize_semantic_value(recovered_value)
    if not source or not recovered:
        return 0.0
    return 0.85 if (source in recovered or recovered in source) else 0.0


def jaccard_similarity(source_value: str, recovered_value: str) -> float:
    source_tokens = set(tokenize_semantic_value(source_value))
    recovered_tokens = set(tokenize_semantic_value(recovered_value))
    if not source_tokens or not recovered_tokens:
        return 0.0
    overlap = len(source_tokens & recovered_tokens)
    union = len(source_tokens | recovered_tokens)
    return (overlap / union) if union else 0.0


def object_similarity(source_value: str, recovered_value: str) -> float:
    exact = canonical_exact_similarity(source_value, recovered_value)
    if exact > 0:
        return exact
    equivalence = semantic_equivalence_bonus(source_value, recovered_value)
    if equivalence > 0:
        return equivalence
    substring = substring_similarity(source_value, recovered_value)
    if substring > 0:
        return substring
    return jaccard_similarity(source_value, recovered_value)


def align_objects_by_type(
    source: TypedSemanticRepresentation,
    recovered: TypedSemanticRepresentation,
) -> Dict[str, Dict[str, object]]:
    alignment: Dict[str, Dict[str, object]] = {}
    for object_type in OBJECT_WEIGHTS:
        source_objects = source.by_type(object_type)
        recovered_objects = recovered.by_type(object_type)
        recovered_pool = [
            {
                "index": idx,
                "value": obj.value,
                "normalized": normalize_semantic_value(obj.value),
            }
            for idx, obj in enumerate(recovered_objects)
        ]
        matches = []
        for source_obj in source_objects:
            source_value = normalize_semantic_value(source_obj.value)
            source_object_id = source_obj.stable_id()
            best_match = None
            best_score = 0.0
            for candidate in recovered_pool:
                similarity = object_similarity(source_value, candidate["normalized"])
                if similarity > best_score:
                    best_score = similarity
                    best_match = candidate
            if best_match is not None and best_score > 0.0:
                recovered_pool = [item for item in recovered_pool if item["index"] != best_match["index"]]
                matches.append(
                    {
                        "source_value": source_obj.value,
                        "recovered_value": best_match["value"],
                        "similarity": round(best_score, 4),
                        "source_evidence_pointer": source_obj.evidence_pointer,
                        "source_object_id": source_object_id,
                        "recovered_object_id": f"{object_type}:{best_match['index']}",
                        "object_type": object_type,
                    }
                )
            else:
                matches.append(
                    {
                        "source_value": source_obj.value,
                        "recovered_value": None,
                        "similarity": 0.0,
                        "source_evidence_pointer": source_obj.evidence_pointer,
                        "source_object_id": source_object_id,
                        "recovered_object_id": None,
                        "object_type": object_type,
                    }
                )
        alignment[object_type] = {
            "matches": matches,
            "source_count": len(source_objects),
            "recovered_count": len(recovered_objects),
        }
    return alignment
