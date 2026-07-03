import re
from typing import Dict, Iterable, List, Tuple

from eval import compute_drift
from eval.scoring import compute_contract_satisfaction

from .semantic_parser import TypedSemanticRepresentation, parse_semantic_state
from .validation_targets import SemanticContractGraph

OBJECT_WEIGHTS = {
    "constraint": 0.5,
    "fact": 0.3,
    "anchor": 0.2,
}

LEAKAGE_PATTERNS = [
    r"\bthe answer is\b",
    r"\bfinal answer\b",
    r"\bthe solution is\b",
    r"\btask completed\b",
    r"\btherefore the answer\b",
    r"\bwe should answer\b",
]

STRONG_ALIGNMENT_SCORE = 0.8
DEFAULT_BLOCKING_DRIFT = 0.9


def _normalize_semantic_value(value: str) -> str:
    return " ".join(str(value).strip().lower().split())


def _tokenize_semantic_value(value: str) -> List[str]:
    return [token for token in re.split(r"[^a-z0-9]+", _normalize_semantic_value(value)) if token]


def _object_similarity(source_value: str, recovered_value: str) -> float:
    normalized_source = _normalize_semantic_value(source_value)
    normalized_recovered = _normalize_semantic_value(recovered_value)
    if not normalized_source or not normalized_recovered:
        return 0.0
    if normalized_source == normalized_recovered:
        return 1.0
    if normalized_source in normalized_recovered or normalized_recovered in normalized_source:
        return 0.85

    source_tokens = set(_tokenize_semantic_value(normalized_source))
    recovered_tokens = set(_tokenize_semantic_value(normalized_recovered))
    if not source_tokens or not recovered_tokens:
        return 0.0
    overlap = len(source_tokens & recovered_tokens)
    union = len(source_tokens | recovered_tokens)
    if union == 0:
        return 0.0
    return overlap / union


def _align_objects_by_type(
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
                "normalized": _normalize_semantic_value(obj.value),
            }
            for idx, obj in enumerate(recovered_objects)
        ]
        matches = []
        for source_obj in source_objects:
            source_value = _normalize_semantic_value(source_obj.value)
            best_match = None
            best_score = 0.0
            for candidate in recovered_pool:
                similarity = _object_similarity(source_value, candidate["normalized"])
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
                    }
                )
            else:
                matches.append(
                    {
                        "source_value": source_obj.value,
                        "recovered_value": None,
                        "similarity": 0.0,
                        "source_evidence_pointer": source_obj.evidence_pointer,
                    }
                )

        alignment[object_type] = {
            "matches": matches,
            "source_count": len(source_objects),
            "recovered_count": len(recovered_objects),
        }

    return alignment


def _weighted_alignment_coverage(
    alignment: Dict[str, Dict[str, object]],
) -> Tuple[float, Dict[str, Dict[str, float]]]:
    details: Dict[str, Dict[str, float]] = {}
    total_weight = 0.0
    matched_weight = 0.0

    for object_type, base_weight in OBJECT_WEIGHTS.items():
        matches = alignment.get(object_type, {}).get("matches", [])
        total = len(matches)
        matched = sum(1 for item in matches if float(item["similarity"]) >= 0.5)
        average_similarity = (sum(float(item["similarity"]) for item in matches) / total) if total else 1.0
        type_weight = total * base_weight
        type_matched_weight = sum(float(item["similarity"]) for item in matches) * base_weight
        total_weight += type_weight
        matched_weight += type_matched_weight
        details[object_type] = {
            "source_count": float(total),
            "matched_count": float(matched),
            "weight_per_object": base_weight,
            "coverage": (matched / total) if total else 1.0,
            "average_similarity": average_similarity,
        }

    if total_weight == 0:
        return 1.0, details
    return matched_weight / total_weight, details


def _detect_answer_leakage(text: str) -> Dict[str, object]:
    lowered = text.lower()
    matches: List[str] = []
    for pattern in LEAKAGE_PATTERNS:
        if re.search(pattern, lowered):
            matches.append(pattern)
    return {
        "detected": bool(matches),
        "matches": matches,
    }


def _flatten_contract_phrases(validation_targets: Iterable | SemanticContractGraph) -> List[str]:
    if isinstance(validation_targets, SemanticContractGraph):
        return validation_targets.flattened_variants()
    flattened: List[str] = []
    for item in validation_targets:
        if isinstance(item, str):
            cleaned = item.strip()
            if cleaned:
                flattened.append(cleaned)
            continue
        try:
            values = [str(value).strip() for value in item if str(value).strip()]
        except TypeError:
            cleaned = str(item).strip()
            if cleaned:
                flattened.append(cleaned)
            continue
        flattened.extend(values)
    return flattened


def _assess_drift_risk(
    drift: float,
    soft_drift_budget: float,
    alignment_score: float,
) -> Dict[str, object]:
    blocking_drift = max(DEFAULT_BLOCKING_DRIFT, soft_drift_budget * 2.0)
    if drift <= soft_drift_budget:
        return {
            "risk": "low",
            "blocks_commit": False,
            "soft_drift_budget": soft_drift_budget,
            "blocking_drift": blocking_drift,
        }
    if drift <= blocking_drift and alignment_score >= STRONG_ALIGNMENT_SCORE:
        return {
            "risk": "medium",
            "blocks_commit": False,
            "soft_drift_budget": soft_drift_budget,
            "blocking_drift": blocking_drift,
        }
    return {
        "risk": "high",
        "blocks_commit": True,
        "soft_drift_budget": soft_drift_budget,
        "blocking_drift": blocking_drift,
    }


def validate_state(
    original_text: str,
    recovered_text: str,
    validation_targets: Iterable,
    max_drift: float = 0.35,
    min_keyword_score: float = 0.5,
    min_coverage_score: float = 0.65,
) -> Dict:
    contract_satisfaction = compute_contract_satisfaction(recovered_text, validation_targets)
    drift = compute_drift(original_text, recovered_text)
    contract_phrases = _flatten_contract_phrases(validation_targets)
    source_semantics = parse_semantic_state(original_text, constraints=contract_phrases)
    recovered_semantics = parse_semantic_state(recovered_text, constraints=contract_phrases)
    alignment = _align_objects_by_type(source_semantics, recovered_semantics)
    coverage_score, coverage_details = _weighted_alignment_coverage(alignment)
    alignment_score = coverage_score
    leakage = _detect_answer_leakage(recovered_text)
    drift_risk = _assess_drift_risk(drift, max_drift, alignment_score)
    passed = (
        contract_satisfaction >= min_keyword_score
        and alignment_score >= min_coverage_score
        and not leakage["detected"]
        and not drift_risk["blocks_commit"]
    )
    return {
        "keyword_hits": None,
        "drift": drift,
        "drift_risk": drift_risk["risk"],
        "drift_blocks_commit": drift_risk["blocks_commit"],
        "score": contract_satisfaction,
        "contract_satisfaction": contract_satisfaction,
        "max_drift": max_drift,
        "blocking_drift": drift_risk["blocking_drift"],
        "min_keyword_score": min_keyword_score,
        "min_coverage_score": min_coverage_score,
        "coverage_score": coverage_score,
        "coverage_details": coverage_details,
        "alignment_score": alignment_score,
        "object_alignment": alignment,
        "leakage_detected": leakage["detected"],
        "leakage_matches": leakage["matches"],
        "typed_validation": {
            "source": source_semantics.as_dict(),
            "recovered": recovered_semantics.as_dict(),
        },
        "passed": passed,
    }
