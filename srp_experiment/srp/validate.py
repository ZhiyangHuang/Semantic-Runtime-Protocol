import re
from typing import Dict, Iterable, List, Tuple

from ..eval import compute_drift
from ..eval.scoring import compute_contract_satisfaction

from .semantic_parser import TypedSemanticRepresentation, canonicalize_semantic_value, parse_semantic_state
from .state import SemanticObjectMetadata
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
    return canonicalize_semantic_value(value)


def _tokenize_semantic_value(value: str) -> List[str]:
    return [token for token in re.split(r"[^a-z0-9]+", _normalize_semantic_value(value)) if token]


def _semantic_equivalence_bonus(source_value: str, recovered_value: str) -> float:
    source = _normalize_semantic_value(source_value)
    recovered = _normalize_semantic_value(recovered_value)
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
    if (source, recovered) in equivalences:
        return 1.0
    return 0.0


def _canonical_exact_similarity(source_value: str, recovered_value: str) -> float:
    source = _normalize_semantic_value(source_value)
    recovered = _normalize_semantic_value(recovered_value)
    return 1.0 if source and source == recovered else 0.0


def _substring_similarity(source_value: str, recovered_value: str) -> float:
    source = _normalize_semantic_value(source_value)
    recovered = _normalize_semantic_value(recovered_value)
    if not source or not recovered:
        return 0.0
    return 0.85 if (source in recovered or recovered in source) else 0.0


def _jaccard_similarity(source_value: str, recovered_value: str) -> float:
    source_tokens = set(_tokenize_semantic_value(source_value))
    recovered_tokens = set(_tokenize_semantic_value(recovered_value))
    if not source_tokens or not recovered_tokens:
        return 0.0
    overlap = len(source_tokens & recovered_tokens)
    union = len(source_tokens | recovered_tokens)
    return (overlap / union) if union else 0.0


def _object_similarity(source_value: str, recovered_value: str) -> float:
    # Canonicalization is the first gate, then semantic equivalence, then lighter fallbacks.
    exact = _canonical_exact_similarity(source_value, recovered_value)
    if exact > 0:
        return exact
    equivalence = _semantic_equivalence_bonus(source_value, recovered_value)
    if equivalence > 0:
        return equivalence
    substring = _substring_similarity(source_value, recovered_value)
    if substring > 0:
        return substring
    return _jaccard_similarity(source_value, recovered_value)


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
            source_object_id = source_obj.stable_id()
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
                        "source_object_id": source_object_id,
                        "recovered_object_id": f"{object_type}:{best_match['index']}" if best_match else None,
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


def _weighted_alignment_coverage(
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
            average_importance = sum((w / base_weight) if base_weight else 0.0 for w in effective_weights) / len(effective_weights)
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


def _build_failure_summary(
    critical_failures: List[Dict[str, object]],
    leakage: Dict[str, object],
    drift_risk: Dict[str, object],
) -> Dict[str, object]:
    failure_object_ids = [str(item.get("source_object_id")) for item in critical_failures if item.get("source_object_id")]
    failure_types = {}
    for item in critical_failures:
        object_type = str(item.get("object_type", "unknown"))
        failure_types[object_type] = failure_types.get(object_type, 0) + 1
    return {
        "schema_version": "failure_summary.v1",
        "critical_failure_count": len(critical_failures),
        "critical_failure_object_ids": failure_object_ids[:10],
        "critical_failure_types": failure_types,
        "leakage_detected": leakage["detected"],
        "leakage_matches": list(leakage.get("matches", [])),
        "drift_risk": drift_risk["risk"],
        "blocks_commit": drift_risk["blocks_commit"],
        "has_critical_failure": bool(critical_failures),
    }


def _build_failure_summary_flat(failure_summary: Dict[str, object]) -> Dict[str, object]:
    failure_object_ids = list(failure_summary.get("critical_failure_object_ids", []))
    failure_types = dict(failure_summary.get("critical_failure_types", {}))
    failure_type_count = len(failure_types)
    failure_type_labels = [f"{key}:{value}" for key, value in sorted(failure_types.items())]
    return {
        "schema_version": "failure_summary_flat.v1",
        "critical_failure_count": failure_summary.get("critical_failure_count"),
        "critical_failure_object_ids": failure_object_ids,
        "critical_failure_object_id_joined": "|".join(str(item) for item in failure_object_ids if str(item)),
        "critical_failure_types": failure_types,
        "critical_failure_type_count": failure_type_count,
        "critical_failure_type_labels": failure_type_labels,
        "leakage_detected": failure_summary.get("leakage_detected"),
        "leakage_match_count": len(failure_summary.get("leakage_matches", [])),
        "leakage_matches": failure_summary.get("leakage_matches", []),
        "leakage_matches_joined": "|".join(str(item) for item in failure_summary.get("leakage_matches", []) if str(item)),
        "drift_risk": failure_summary.get("drift_risk"),
        "blocks_commit": failure_summary.get("blocks_commit"),
        "has_critical_failure": failure_summary.get("has_critical_failure"),
    }


def validate_state(
    original_text: str,
    recovered_text: str,
    validation_targets: Iterable,
    max_drift: float = 0.35,
    min_keyword_score: float = 0.5,
    min_coverage_score: float = 0.65,
    runtime_metadata: Dict[str, SemanticObjectMetadata] | None = None,
) -> Dict:
    contract_satisfaction = compute_contract_satisfaction(recovered_text, validation_targets)
    drift = compute_drift(original_text, recovered_text)
    contract_phrases = _flatten_contract_phrases(validation_targets)
    source_semantics = parse_semantic_state(original_text, constraints=contract_phrases)
    recovered_semantics = parse_semantic_state(recovered_text, constraints=contract_phrases)
    raw_recovered_semantics = parse_semantic_state(recovered_text, constraints=[])
    alignment = _align_objects_by_type(source_semantics, recovered_semantics)
    raw_alignment = _align_objects_by_type(source_semantics, raw_recovered_semantics)
    coverage_score, coverage_details = _weighted_alignment_coverage(alignment, runtime_metadata=runtime_metadata)
    alignment_score = coverage_score
    leakage = _detect_answer_leakage(recovered_text)
    drift_risk = _assess_drift_risk(drift, max_drift, alignment_score)
    important_object_ids = {
        object_id
        for object_id, metadata in (runtime_metadata or {}).items()
        if metadata.importance >= 0.8
    }
    matched_object_ids = {
        str(item.get("source_object_id"))
        for group in raw_alignment.values()
        for item in group.get("matches", [])
        if item.get("source_object_id")
    }
    critical_failures = [
        item
        for group in raw_alignment.values()
        for item in group.get("matches", [])
        if float(item.get("similarity", 0.0)) < 0.5
        and (runtime_metadata.get(item.get("source_object_id")).importance if runtime_metadata and runtime_metadata.get(item.get("source_object_id")) else 0.0) >= 0.8
    ]
    critical_failures.extend(
        [
            {
                "source_object_id": object_id,
                "recovered_object_id": None,
                "source_value": "",
                "recovered_value": None,
                "similarity": 0.0,
                "object_type": "unknown",
            }
            for object_id in sorted(important_object_ids - matched_object_ids)
        ]
    )
    failure_summary = _build_failure_summary(critical_failures, leakage, drift_risk)
    failure_summary_flat = _build_failure_summary_flat(failure_summary)
    passed = (
        contract_satisfaction >= min_keyword_score
        and alignment_score >= min_coverage_score
        and not leakage["detected"]
        and not drift_risk["blocks_commit"]
        and not critical_failures
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
        "critical_failures": critical_failures,
        "failure_summary": failure_summary,
        "failure_summary_flat": failure_summary_flat,
        "leakage_detected": leakage["detected"],
        "leakage_matches": leakage["matches"],
        "typed_validation": {
            "source": source_semantics.as_dict(),
            "recovered": recovered_semantics.as_dict(),
        },
        "passed": passed,
    }
