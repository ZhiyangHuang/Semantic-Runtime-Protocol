from typing import Dict, Iterable

from ..eval import compute_drift
from ..eval.scoring import compute_contract_satisfaction

from .semantic_parser import parse_semantic_state, typed_representation_from_dict
from .state import SemanticObjectMetadata
from .object_retention import build_object_retention_breakdown_v2
from .semantic_parser import canonicalize_semantic_value, stable_semantic_object_id
from .validation_failure_summary import (
    assess_drift_risk,
    build_failure_summary,
    build_failure_summary_flat,
    detect_answer_leakage,
)
from .validation_matching import align_objects_by_type, object_similarity
from .validation_scoring import flatten_contract_phrases
from .validation_weighting import weighted_alignment_coverage


def _collect_critical_failures(
    raw_alignment: Dict[str, Dict[str, object]],
    runtime_metadata: Dict[str, SemanticObjectMetadata] | None,
) -> list[Dict[str, object]]:
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
        and (
            runtime_metadata.get(item.get("source_object_id")).importance
            if runtime_metadata and runtime_metadata.get(item.get("source_object_id"))
            else 0.0
        )
        >= 0.8
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
    return critical_failures


def _build_dependency_audit(validation_targets, recovered_state_package: Dict | None) -> Dict[str, object]:
    expected_ids = []
    expected_labels = []
    for node in getattr(validation_targets, "nodes", []) or []:
        if node.role not in {"clause"}:
            continue
        if node.node_type not in {"query_expectation", "constraint"}:
            continue
        for variant in node.variants:
            label = str(variant.surface).strip()
            if not label:
                continue
            expected_labels.append(label)
            expected_ids.append(stable_semantic_object_id(node.node_type, canonicalize_semantic_value(label) or label))

    recovered_objects = typed_representation_from_dict((recovered_state_package or {}).get("typed_representation")).objects
    recovered_ids = [item.stable_id() for item in recovered_objects]
    recovered_by_label = []
    for item in recovered_objects:
        recovered_by_label.append(
            {
                "object_id": item.stable_id(),
                "type": item.object_type,
                "value": item.value,
                "evidence_pointer": item.evidence_pointer,
            }
        )
    expected_set = set(expected_ids)
    recovered_set = set(recovered_ids)
    intersection = sorted(expected_set & recovered_set)
    return {
        "expected_labels": expected_labels,
        "expected_object_ids": sorted(expected_set),
        "recovered_object_ids": sorted(recovered_set),
        "recovered_objects": recovered_by_label,
        "matched_object_ids": intersection,
        "expected_count": len(expected_set),
        "recovered_count": len(recovered_set),
        "matched_count": len(intersection),
        "coverage": (len(intersection) / len(expected_set)) if expected_set else None,
        "precision": (len(intersection) / len(recovered_set)) if recovered_set else None,
    }


def _build_dependency_audit_from_labels(
    dependency_labels,
    recovered_state_package: Dict | None,
) -> Dict[str, object]:
    expected_labels = [str(label).strip() for label in (dependency_labels or []) if str(label).strip()]
    expected_object_ids = []
    for label in expected_labels:
        canonical = canonicalize_semantic_value(label) or label
        if any(keyword in canonical for keyword in {"cannot modify", "only administrators", "depends on", "after version"}):
            expected_object_ids.append(stable_semantic_object_id("anchor", canonical))
        else:
            expected_object_ids.append(stable_semantic_object_id("fact", canonical))

    recovered_objects = typed_representation_from_dict((recovered_state_package or {}).get("typed_representation")).objects
    recovered_map = [
        {
            "object_id": item.stable_id(),
            "type": item.object_type,
            "value": item.value,
            "normalized_value": canonicalize_semantic_value(item.value),
            "evidence_pointer": item.evidence_pointer,
        }
        for item in recovered_objects
    ]
    recovered_object_ids = sorted(item["object_id"] for item in recovered_map)
    matched: list[str] = []
    matched_objects = []
    used_indexes = set()
    for expected_label in expected_labels:
        expected_normalized = canonicalize_semantic_value(expected_label)
        best_index = None
        best_score = 0.0
        for idx, recovered in enumerate(recovered_map):
            if idx in used_indexes:
                continue
            score = object_similarity(expected_normalized, recovered["normalized_value"])
            if score > best_score:
                best_score = score
                best_index = idx
        if best_index is not None and best_score >= 0.45:
            used_indexes.add(best_index)
            recovered = recovered_map[best_index]
            matched.append(recovered["object_id"])
            matched_objects.append(recovered)
    exact_matched = sorted(set(expected_object_ids) & set(recovered_object_ids))
    matched_object_ids = sorted(set(matched) | set(exact_matched))
    return {
        "expected_labels": expected_labels,
        "expected_object_ids": sorted(set(expected_object_ids)),
        "recovered_object_ids": recovered_object_ids,
        "recovered_objects": list(recovered_map),
        "matched_object_ids": matched_object_ids,
        "matched_objects": matched_objects,
        "expected_count": len(set(expected_object_ids)),
        "recovered_count": len(recovered_object_ids),
        "matched_count": len(matched_object_ids),
        "coverage": (len(matched_object_ids) / len(set(expected_object_ids))) if expected_object_ids else None,
        "precision": (len(matched_object_ids) / len(recovered_object_ids)) if recovered_object_ids else None,
    }


def _build_dependency_audit_from_objects(
    dependency_objects,
    recovered_state_package: Dict | None,
) -> Dict[str, object]:
    expected_objects = []
    expected_object_ids = []
    for item in dependency_objects or []:
        if not isinstance(item, dict):
            continue
        concept = str(item.get("concept", "")).strip()
        normalized_value = canonicalize_semantic_value(str(item.get("normalized_value", "")).strip())
        if not concept or not normalized_value:
            subject = item.get("subject") or {}
            relation = item.get("relation") or {}
            obj = item.get("object") or {}
            subject_value = str(subject.get("canonical") or subject.get("value") or "").strip()
            relation_value = str(relation.get("canonical") or relation.get("value") or "").strip()
            object_value = str(obj.get("canonical") or obj.get("value") or "").strip()
            normalized_value = canonicalize_semantic_value(" ".join(value for value in [subject_value, relation_value, object_value] if value))
            concept = str(relation.get("type") or "semantic_dependency_tuple").strip()
        if not concept or not normalized_value:
            continue
        expected_object = {
            "object_id": str(item.get("object_id", "")).strip() or stable_semantic_object_id(concept, normalized_value),
            "concept": concept,
            "normalized_value": normalized_value,
        }
        expected_objects.append(expected_object)
        expected_object_ids.append(expected_object["object_id"])

    recovered_objects = typed_representation_from_dict((recovered_state_package or {}).get("typed_representation")).objects
    recovered_map = [
        {
            "object_id": item.stable_id(),
            "type": item.object_type,
            "value": item.value,
            "normalized_value": canonicalize_semantic_value(item.value),
            "evidence_pointer": item.evidence_pointer,
        }
        for item in recovered_objects
    ]
    matched_objects = []
    matched_object_ids = []
    used_indexes = set()
    for expected_index, expected in enumerate(expected_objects):
        best_index = None
        best_score = 0.0
        for idx, recovered in enumerate(recovered_map):
            if idx in used_indexes:
                continue
            score = object_similarity(expected["normalized_value"], recovered["normalized_value"])
            if score > best_score:
                best_score = score
                best_index = idx
        if best_index is not None and best_score >= 0.45:
            used_indexes.add(best_index)
            recovered = recovered_map[best_index]
            matched_object_ids.append(recovered["object_id"])
            matched_objects.append(
                {
                    "expected_index": expected_index,
                    "expected_object_id": expected["object_id"],
                    "expected_concept": expected["concept"],
                    "expected_value": expected["normalized_value"],
                    "runtime_id": recovered["object_id"],
                    "runtime_type": recovered["type"],
                    "runtime_value": recovered["value"],
                    "runtime_normalized_value": recovered["normalized_value"],
                    "similarity": round(best_score, 4),
                }
            )

    recovered_object_ids = [item["object_id"] for item in recovered_map]
    expected_set = set(expected_object_ids)
    matched_set = set(matched_object_ids)
    return {
        "mode": "semantic_object",
        "expected_objects": expected_objects,
        "expected_labels": [item["normalized_value"] for item in expected_objects],
        "expected_object_ids": sorted(expected_set),
        "recovered_object_ids": sorted(recovered_object_ids),
        "recovered_objects": recovered_map,
        "matched_objects": matched_objects,
        "matched_object_ids": sorted(matched_set),
        "expected_count": len(expected_set),
        "recovered_count": len(recovered_object_ids),
        "matched_count": len(matched_set),
        "coverage": (len(matched_set) / len(expected_set)) if expected_set else None,
        "precision": (len(matched_set) / len(recovered_object_ids)) if recovered_object_ids else None,
    }


def validate_state(
    original_text: str,
    recovered_text: str,
    validation_targets: Iterable,
    max_drift: float = 0.35,
    min_keyword_score: float = 0.5,
    min_coverage_score: float = 0.65,
    runtime_metadata: Dict[str, SemanticObjectMetadata] | None = None,
    recovered_state_package: Dict | None = None,
    dependency_labels=None,
    dependency_objects=None,
) -> Dict:
    contract_satisfaction = compute_contract_satisfaction(recovered_text, validation_targets)
    drift = compute_drift(original_text, recovered_text)
    contract_phrases = flatten_contract_phrases(validation_targets)

    source_semantics = parse_semantic_state(original_text, constraints=contract_phrases)
    structured_recovered = typed_representation_from_dict(
        (recovered_state_package or {}).get("typed_representation")
    )
    recovered_semantics = structured_recovered if structured_recovered.objects else parse_semantic_state(
        recovered_text,
        constraints=contract_phrases,
    )
    raw_recovered_semantics = recovered_semantics if structured_recovered.objects else parse_semantic_state(
        recovered_text,
        constraints=[],
    )

    alignment = align_objects_by_type(source_semantics, recovered_semantics)
    raw_alignment = align_objects_by_type(source_semantics, raw_recovered_semantics)
    coverage_score, coverage_details = weighted_alignment_coverage(alignment, runtime_metadata=runtime_metadata)
    alignment_score = coverage_score

    leakage = detect_answer_leakage(recovered_text)
    drift_risk = assess_drift_risk(drift, max_drift, alignment_score)
    critical_failures = _collect_critical_failures(raw_alignment, runtime_metadata)
    failure_summary = build_failure_summary(critical_failures, leakage, drift_risk)
    failure_summary_flat = build_failure_summary_flat(failure_summary)
    dependency_breakdown = build_object_retention_breakdown_v2(None, recovered_state_package, validation_targets)
    dependency_audit = _build_dependency_audit_from_objects(dependency_objects, recovered_state_package)
    if not dependency_audit.get("expected_objects"):
        dependency_audit = _build_dependency_audit_from_labels(dependency_labels, recovered_state_package)
    if not dependency_audit.get("expected_labels"):
        dependency_audit = _build_dependency_audit(validation_targets, recovered_state_package)
    dependency_coverage = dependency_audit.get("coverage")
    dependency_precision = dependency_audit.get("precision")
    if dependency_coverage is None:
        dependency_coverage = dependency_breakdown.task_critical.get("recall")
    if dependency_precision is None:
        dependency_precision = dependency_breakdown.task_critical.get("precision")
    dependency_f1 = None
    if dependency_coverage is not None and dependency_precision is not None and (dependency_coverage + dependency_precision):
        dependency_f1 = 2 * dependency_precision * dependency_coverage / (dependency_precision + dependency_coverage)

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
        "dependency_coverage": dependency_coverage,
        "dependency_precision": dependency_precision,
        "dependency_f1": dependency_f1,
        "dependency_audit": dependency_audit,
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
