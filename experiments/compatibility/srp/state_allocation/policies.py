from __future__ import annotations

import os
import random
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from .metrics import AllocationMetrics
from .policy import StateAllocationPolicy
from .result import StateAllocationResult
from ..semantic_parser import canonicalize_semantic_value, stable_semantic_object_id
from ..validation_targets import SemanticContractGraph


def _empty_allocation(policy_name: str) -> StateAllocationResult:
    return StateAllocationResult(
        active_state={},
        latent_state={},
        discard_state={},
        policy_name=policy_name,
        metrics=AllocationMetrics(policy_name=policy_name),
    )


def _unwrap_state(reconstructed_state: Any) -> Dict[str, object]:
    if reconstructed_state is None:
        return {}
    if isinstance(reconstructed_state, dict):
        if reconstructed_state.get("schema_version") == "structured_state_package.v1":
            return reconstructed_state
        if "structured_state_package" in reconstructed_state and isinstance(
            reconstructed_state.get("structured_state_package"), dict
        ):
            return reconstructed_state["structured_state_package"]
        if "recovered_state_package" in reconstructed_state and isinstance(
            reconstructed_state.get("recovered_state_package"), dict
        ):
            return reconstructed_state["recovered_state_package"]
    return getattr(reconstructed_state, "recovered_state_package", {}) or {}


def _typed_objects(package: Dict[str, object]) -> List[Dict[str, object]]:
    typed = package.get("typed_representation") or {}
    return list(typed.get("objects", []))


def _inventory_objects(package: Dict[str, object]) -> List[Dict[str, object]]:
    inventory = package.get("semantic_object_inventory") or {}
    return list(inventory.get("objects", []))


def _important_objects(package: Dict[str, object]) -> List[Dict[str, object]]:
    inventory = package.get("semantic_object_inventory") or {}
    return list(inventory.get("important_objects", []))


def _task_context_dict(task_context: Any) -> Dict[str, object]:
    if isinstance(task_context, dict):
        return task_context
    return getattr(task_context, "as_dict", lambda: {})() or {}


def _task_critical_object_ids(task_context: Any) -> Set[str]:
    context = _task_context_dict(task_context)
    validation_targets = context.get("validation_targets")
    if isinstance(validation_targets, SemanticContractGraph):
        graph = validation_targets
    elif isinstance(validation_targets, dict):
        graph = SemanticContractGraph()
    else:
        graph = None
    if graph is None:
        task = context.get("task")
        if isinstance(task, dict):
            from ..validation_targets import build_validation_targets

            graph = build_validation_targets(task)
        else:
            return set()
    critical = set()
    for node in graph.nodes:
        if node.role not in {"clause"}:
            continue
        if node.node_type not in {"query_expectation", "constraint"}:
            continue
        for variant in node.variants:
            critical.add(stable_semantic_object_id(node.node_type, variant.surface))
    return critical


def _dependency_object_ids(task_context: Any) -> Set[str]:
    context = _task_context_dict(task_context)
    dependency_objects = context.get("required_dependency_objects")
    if not isinstance(dependency_objects, list):
        metadata = context.get("task", {}).get("metadata") if isinstance(context.get("task"), dict) else {}
        dependency_objects = metadata.get("required_dependency_objects") if isinstance(metadata, dict) else []
    result: Set[str] = set()
    for item in dependency_objects or []:
        if not isinstance(item, dict):
            continue
        concept = str(item.get("concept", "")).strip()
        normalized_value = str(item.get("normalized_value", "")).strip()
        if concept and normalized_value:
            result.add(stable_semantic_object_id(concept, normalized_value))
            continue
        subject = item.get("subject") or {}
        relation = item.get("relation") or {}
        obj = item.get("object") or {}
        subject_value = str(subject.get("canonical") or subject.get("value") or "").strip()
        relation_value = str(relation.get("canonical") or relation.get("value") or "").strip()
        object_value = str(obj.get("canonical") or obj.get("value") or "").strip()
        tuple_surface = " ".join(value for value in [subject_value, relation_value, object_value] if value)
        if not tuple_surface:
            continue
        result.add(stable_semantic_object_id("anchor", tuple_surface))
        result.add(stable_semantic_object_id("fact", tuple_surface))
    return result


def _dependency_object_descriptors(task_context: Any) -> List[Dict[str, str]]:
    context = _task_context_dict(task_context)
    dependency_objects = context.get("required_dependency_objects")
    if not isinstance(dependency_objects, list):
        metadata = context.get("task", {}).get("metadata") if isinstance(context.get("task"), dict) else {}
        dependency_objects = metadata.get("required_dependency_objects") if isinstance(metadata, dict) else []
    descriptors: List[Dict[str, str]] = []
    for item in dependency_objects or []:
        if not isinstance(item, dict):
            continue
        concept = str(item.get("concept", "")).strip()
        normalized_value = canonicalize_semantic_value(str(item.get("normalized_value", "")).strip())
        if concept and normalized_value:
            descriptors.append(
                {
                    "concept": concept,
                    "normalized_value": normalized_value,
                    "object_id": stable_semantic_object_id(concept, normalized_value),
                }
            )
            continue
        subject = item.get("subject") or {}
        relation = item.get("relation") or {}
        obj = item.get("object") or {}
        subject_value = canonicalize_semantic_value(str(subject.get("canonical") or subject.get("value") or "").strip())
        relation_value = canonicalize_semantic_value(str(relation.get("canonical") or relation.get("value") or "").strip())
        object_value = canonicalize_semantic_value(str(obj.get("canonical") or obj.get("value") or "").strip())
        tuple_surface = " ".join(value for value in [subject_value, relation_value, object_value] if value)
        if not tuple_surface:
            continue
        descriptors.append(
            {
                "concept": str(relation.get("type") or "semantic_dependency_tuple").strip(),
                "normalized_value": tuple_surface,
                "object_id": stable_semantic_object_id("anchor", tuple_surface),
            }
        )
    return descriptors


def _dependency_edges(task_context: Any) -> List[Dict[str, str]]:
    context = _task_context_dict(task_context)
    edges = context.get("dependency_edges")
    if not isinstance(edges, list):
        metadata = context.get("task", {}).get("metadata") if isinstance(context.get("task"), dict) else {}
        edges = metadata.get("dependency_edges") if isinstance(metadata, dict) else []
    normalized: List[Dict[str, str]] = []
    for item in edges or []:
        if not isinstance(item, dict):
            continue
        source = str(item.get("source") or item.get("from") or item.get("src") or "").strip()
        target = str(item.get("target") or item.get("to") or item.get("dst") or "").strip()
        relation = str(item.get("relation", "")).strip()
        if not source or not target:
            continue
        normalized.append(
            {
                "source": canonicalize_semantic_value(source),
                "target": canonicalize_semantic_value(target),
                "relation": canonicalize_semantic_value(relation),
            }
        )
    return normalized


def _normalize_tokens(text: str) -> Set[str]:
    normalized = canonicalize_semantic_value(text)
    if not normalized:
        return set()
    return {token for token in normalized.split() if token}


def _token_overlap_score(left: str, right: str) -> float:
    left_tokens = _normalize_tokens(left)
    right_tokens = _normalize_tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    intersection = left_tokens & right_tokens
    union = left_tokens | right_tokens
    return len(intersection) / max(1, len(union))


def _semantic_dependency_score(
    item: Dict[str, object],
    dependency_descriptors: Sequence[Dict[str, str]],
    dependency_edges: Sequence[Dict[str, str]],
) -> Tuple[float, List[str]]:
    value = canonicalize_semantic_value(str(item.get("value", "")).strip())
    object_type = str(item.get("type", "fact")).strip() or "fact"
    score = 0.0
    reasons: List[str] = []

    for descriptor in dependency_descriptors:
        concept_score = _token_overlap_score(object_type, descriptor["concept"])
        value_score = _token_overlap_score(value, descriptor["normalized_value"])
        exact_bonus = 1.0 if value == descriptor["normalized_value"] else 0.0
        combined = (0.15 * concept_score) + (0.75 * value_score) + exact_bonus
        if combined > score:
            score = combined
        if exact_bonus or value_score >= 0.5:
            reasons.append(f"dependency:{descriptor['object_id']}")

    edge_nodes = {edge["source"] for edge in dependency_edges} | {edge["target"] for edge in dependency_edges}
    for node in edge_nodes:
        node_score = _token_overlap_score(value, node)
        if node_score > score:
            score = node_score
        if node_score >= 0.5:
            reasons.append(f"edge:{node}")

    if object_type in {"anchor", "question", "constraint", "answer"}:
        score = max(score, 0.1)
        reasons.append(f"type:{object_type}")

    return score, sorted(set(reasons))


def _semantic_dependency_score_v2(
    item: Dict[str, object],
    dependency_descriptors: Sequence[Dict[str, str]],
    dependency_edges: Sequence[Dict[str, str]],
    task_critical_ids: Set[str],
    important_ids: Set[str],
    source_ids: Set[str],
) -> Tuple[float, List[str]]:
    value = canonicalize_semantic_value(str(item.get("value", "")).strip())
    object_type = str(item.get("type", "fact")).strip() or "fact"
    object_id = _object_id(item)

    score = 0.0
    reasons: List[str] = []

    for descriptor in dependency_descriptors:
        exact_value = value == descriptor["normalized_value"]
        concept_score = _token_overlap_score(object_type, descriptor["concept"])
        value_score = _token_overlap_score(value, descriptor["normalized_value"])
        if exact_value:
            score = max(score, 100.0)
            reasons.append(f"required_dependency:{descriptor['object_id']}")
        elif value_score >= 0.75:
            score = max(score, 80.0 + (10.0 * value_score))
            reasons.append(f"near_dependency:{descriptor['object_id']}")
        elif value_score >= 0.5:
            score = max(score, 60.0 + (5.0 * value_score))
            reasons.append(f"partial_dependency:{descriptor['object_id']}")
        elif concept_score >= 0.5:
            score = max(score, 20.0 + (2.0 * concept_score))
            reasons.append(f"concept_overlap:{descriptor['concept']}")

    edge_nodes = {edge["source"] for edge in dependency_edges} | {edge["target"] for edge in dependency_edges}
    for node in edge_nodes:
        node_score = _token_overlap_score(value, node)
        if node_score >= 0.75:
            score = max(score, 70.0 + (10.0 * node_score))
            reasons.append(f"edge_node:{node}")
        elif node_score >= 0.5:
            score = max(score, 45.0 + (5.0 * node_score))
            reasons.append(f"edge_overlap:{node}")

    if object_id in task_critical_ids:
        score = max(score, score + 12.0)
        reasons.append("task_critical")
    if object_id in important_ids:
        score = max(score, score + 8.0)
        reasons.append("important_object")

    if object_type in {"question", "constraint", "answer"}:
        score = max(score, score + 6.0)
        reasons.append(f"type_priority:{object_type}")
    elif object_type == "anchor":
        score = max(score, score + 2.0)
        reasons.append("anchor_type")

    if object_id in source_ids:
        score = max(score, score + 1.0)
        reasons.append("source_aligned")

    return score, sorted(set(reasons))


def _dependency_aware_partition_objects(
    objects: List[Dict[str, object]],
    task_context: Any,
    *,
    active_limit: int | None = None,
) -> tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]]]:
    context = _task_context_dict(task_context)
    task_critical_ids = _task_critical_object_ids(context)
    important_ids = {_object_id(item) for item in _important_objects(context.get("recovered_state_package") or context)}
    source_ids = {_object_id(item) for item in _inventory_objects(context.get("recovered_state_package") or context)}
    dependency_descriptors = _dependency_object_descriptors(context)
    dependency_edges = _dependency_edges(context)

    scored: List[Tuple[float, int, Dict[str, object], List[str]]] = []
    for index, item in enumerate(objects):
        object_id = _object_id(item)
        object_type = str(item.get("type", "fact")).strip() or "fact"
        score, reasons = _semantic_dependency_score(item, dependency_descriptors, dependency_edges)
        if object_id in task_critical_ids:
            score += 2.0
            reasons.append("task_critical")
        if object_id in important_ids:
            score += 1.5
            reasons.append("important_object")
        if object_type in {"question", "constraint", "answer", "anchor"}:
            score += 0.25
            reasons.append(f"type_priority:{object_type}")
        if object_id in source_ids:
            score += 0.05
            reasons.append("source_aligned")
        scored.append((score, index, item, sorted(set(reasons))))

    scored.sort(key=lambda entry: (-entry[0], entry[1]))
    active: List[Dict[str, object]] = []
    latent: List[Dict[str, object]] = []
    discard: List[Dict[str, object]] = []
    active_ids: Set[str] = set()

    target_active = active_limit if active_limit is not None else min(12, len(objects))
    target_active = max(1, min(len(objects), target_active))

    for score, _, item, _ in scored:
        if len(active) >= target_active:
            break
        active.append(item)
        active_ids.add(_object_id(item))

    for item in objects:
        object_id = _object_id(item)
        if object_id in active_ids:
            continue
        if object_id in source_ids:
            latent.append(item)
        else:
            discard.append(item)

    active = _dedupe_objects(active)
    latent = _dedupe_objects(latent)
    discard = _dedupe_objects(discard)
    return active, latent, discard


def _dependency_aware_v2_partition_objects(
    objects: List[Dict[str, object]],
    task_context: Any,
    *,
    active_limit: int | None = None,
) -> tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]]]:
    context = _task_context_dict(task_context)
    task_critical_ids = _task_critical_object_ids(context)
    important_ids = {_object_id(item) for item in _important_objects(context.get("recovered_state_package") or context)}
    source_ids = {_object_id(item) for item in _inventory_objects(context.get("recovered_state_package") or context)}
    dependency_descriptors = _dependency_object_descriptors(context)
    dependency_edges = _dependency_edges(context)

    scored: List[Tuple[float, int, Dict[str, object], List[str]]] = []
    for index, item in enumerate(objects):
        score, reasons = _semantic_dependency_score_v2(
            item,
            dependency_descriptors,
            dependency_edges,
            task_critical_ids,
            important_ids,
            source_ids,
        )
        scored.append((score, index, item, sorted(set(reasons))))

    scored.sort(key=lambda entry: (-entry[0], entry[1]))
    active: List[Dict[str, object]] = []
    latent: List[Dict[str, object]] = []
    discard: List[Dict[str, object]] = []
    active_ids: Set[str] = set()

    target_active = active_limit if active_limit is not None else min(12, len(objects))
    target_active = max(1, min(len(objects), target_active))

    for score, _, item, _ in scored:
        if len(active) >= target_active:
            break
        active.append(item)
        active_ids.add(_object_id(item))

    for item in objects:
        object_id = _object_id(item)
        if object_id in active_ids:
            continue
        if object_id in source_ids:
            latent.append(item)
        else:
            discard.append(item)

    active = _dedupe_objects(active)
    latent = _dedupe_objects(latent)
    discard = _dedupe_objects(discard)
    return active, latent, discard


def _object_id(item: Dict[str, object]) -> str:
    object_type = str(item.get("type", "fact")).strip() or "fact"
    value = str(item.get("value", "")).strip()
    return stable_semantic_object_id(object_type, value)


def _dedupe_objects(objects: Iterable[Dict[str, object]]) -> List[Dict[str, object]]:
    selected: List[Dict[str, object]] = []
    seen: Set[str] = set()
    for item in objects:
        if not isinstance(item, dict):
            continue
        object_id = _object_id(item)
        if object_id in seen:
            continue
        seen.add(object_id)
        selected.append(item)
    return selected


def _partition_objects(
    objects: List[Dict[str, object]],
    task_context: Any,
    *,
    active_limit: int | None = None,
    latent_limit: int | None = None,
) -> tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]]]:
    context = _task_context_dict(task_context)
    task_critical_ids = _task_critical_object_ids(context)
    active: List[Dict[str, object]] = []
    latent: List[Dict[str, object]] = []
    discard: List[Dict[str, object]] = []

    important_ids = {_object_id(item) for item in _important_objects(context.get("recovered_state_package") or context)}
    source_ids = {_object_id(item) for item in _inventory_objects(context.get("recovered_state_package") or context)}

    for item in objects:
        object_id = _object_id(item)
        object_type = str(item.get("type", "fact")).strip() or "fact"
        if object_id in task_critical_ids or object_id in important_ids or object_type in {"question", "constraint", "answer", "anchor"}:
            active.append(item)
        elif object_id in source_ids:
            latent.append(item)
        else:
            discard.append(item)

    active = _dedupe_objects(active)
    latent = _dedupe_objects(latent)
    discard = _dedupe_objects(discard)

    if active_limit is not None:
        overflow = active[active_limit:]
        active = active[:active_limit]
        latent = _dedupe_objects(latent + overflow)
    if latent_limit is not None:
        overflow = latent[latent_limit:]
        latent = latent[:latent_limit]
        discard = _dedupe_objects(discard + overflow)
    return active, latent, discard


def _build_metrics(
    policy_name: str,
    active: List[Dict[str, object]],
    latent: List[Dict[str, object]],
    discard: List[Dict[str, object]],
    reconstructed_count: int,
    task_context: Any,
) -> AllocationMetrics:
    context = _task_context_dict(task_context)
    validation = context.get("validation") or {}
    validation_coverage = validation.get("coverage_score")
    important_count = len(_important_objects(context.get("recovered_state_package") or context))
    active_object_count = len(active)
    latent_object_count = len(latent)
    discard_object_count = len(discard)
    active_state_efficiency = (
        None if validation_coverage is None or not active_object_count else validation_coverage / active_object_count
    )
    latent_preservation = None
    if important_count:
        latent_preservation = latent_object_count / important_count if important_count else None
    hallucination_isolation = None
    if active_object_count:
        hallucination_isolation = 1.0 - (discard_object_count / max(1, reconstructed_count))
    active_retention_ratio = None
    if reconstructed_count:
        active_retention_ratio = active_object_count / reconstructed_count
    return AllocationMetrics(
        active_object_count=active_object_count,
        latent_object_count=latent_object_count,
        discard_object_count=discard_object_count,
        validation_coverage=validation_coverage,
        active_state_efficiency=active_state_efficiency,
        latent_preservation=latent_preservation,
        hallucination_isolation=hallucination_isolation,
        active_retention_ratio=active_retention_ratio,
        policy_name=policy_name,
    )


def _build_forensic_trace(
    *,
    policy_name: str,
    objects: List[Dict[str, object]],
    active: List[Dict[str, object]],
    latent: List[Dict[str, object]],
    discard: List[Dict[str, object]],
    task_context: Any,
) -> Dict[str, object]:
    context = _task_context_dict(task_context)
    task_critical_ids = _task_critical_object_ids(context)
    dependency_ids = _dependency_object_ids(context)
    important_ids = {_object_id(item) for item in _important_objects(context.get("recovered_state_package") or context)}
    source_ids = {_object_id(item) for item in _inventory_objects(context.get("recovered_state_package") or context)}
    active_ids = {_object_id(item) for item in active}
    latent_ids = {_object_id(item) for item in latent}
    discard_ids = {_object_id(item) for item in discard}
    object_rows: List[Dict[str, object]] = []
    for item in objects:
        object_id = _object_id(item)
        object_type = str(item.get("type", "fact")).strip() or "fact"
        eligibility = {
            "is_task_critical": object_id in task_critical_ids,
            "is_dependency_object": object_id in dependency_ids,
            "is_important": object_id in important_ids,
            "is_source_aligned": object_id in source_ids,
            "type_priority": object_type in {"question", "constraint", "answer", "anchor"},
        }
        selection_reason: List[str] = []
        if eligibility["is_task_critical"]:
            selection_reason.append("task_critical")
        if eligibility["is_dependency_object"]:
            selection_reason.append("required_dependency")
        if eligibility["is_important"]:
            selection_reason.append("important_object")
        if eligibility["type_priority"]:
            selection_reason.append("type_priority")
        if eligibility["is_source_aligned"]:
            selection_reason.append("source_aligned")
        if object_id in active_ids:
            selection_status = "active"
        elif object_id in latent_ids:
            selection_status = "latent"
        elif object_id in discard_ids:
            selection_status = "discard"
        else:
            selection_status = "unknown"
        object_rows.append(
            {
                "object_id": object_id,
                "object_type": object_type,
                "value": item.get("value"),
                "selection_status": selection_status,
                "eligibility": eligibility,
                "selection_reason": selection_reason,
                "dependency_role": {
                    "is_required_dependency": object_id in dependency_ids,
                    "matched_dependency_ids": [object_id] if object_id in dependency_ids else [],
                },
            }
        )
    return {
        "schema_version": "allocation_forensic_trace.v1",
        "policy_name": policy_name,
        "task_critical_object_ids": sorted(task_critical_ids),
        "required_dependency_object_ids": sorted(dependency_ids),
        "important_object_ids": sorted(important_ids),
        "source_object_ids": sorted(source_ids),
        "active_object_ids": sorted(active_ids),
        "latent_object_ids": sorted(latent_ids),
        "discard_object_ids": sorted(discard_ids),
        "selected_dependency_object_ids": sorted(active_ids & dependency_ids),
        "selected_dependency_count": len(active_ids & dependency_ids),
        "selected_anchor_count": sum(1 for item in active if str(item.get("type", "fact")).strip() == "anchor"),
        "selected_question_count": sum(1 for item in active if str(item.get("type", "fact")).strip() == "question"),
        "selected_constraint_count": sum(1 for item in active if str(item.get("type", "fact")).strip() == "constraint"),
        "selected_answer_count": sum(1 for item in active if str(item.get("type", "fact")).strip() == "answer"),
        "selection_ratio": {
            "active": len(active) / max(1, len(objects)),
            "latent": len(latent) / max(1, len(objects)),
            "discard": len(discard) / max(1, len(objects)),
        },
        "objects": object_rows,
    }


def _build_dependency_allocation_ingestion_trace(
    *,
    policy_name: str,
    objects: List[Dict[str, object]],
    task_context: Any,
) -> Dict[str, object]:
    context = _task_context_dict(task_context)
    dependency_descriptors = _dependency_object_descriptors(context)
    dependency_edges = _dependency_edges(context)
    candidate_rows: List[Dict[str, object]] = []
    matched_candidates: List[Dict[str, object]] = []
    for item in objects:
        object_id = _object_id(item)
        object_type = str(item.get("type", "fact")).strip() or "fact"
        value = canonicalize_semantic_value(str(item.get("value", "")).strip())
        best_descriptor: Optional[Dict[str, str]] = None
        best_score = 0.0
        best_reasons: List[str] = []
        for descriptor in dependency_descriptors:
            concept_score = _token_overlap_score(object_type, descriptor["concept"])
            value_score = _token_overlap_score(value, descriptor["normalized_value"])
            exact_value = value == descriptor["normalized_value"]
            score = (0.15 * concept_score) + (0.75 * value_score) + (1.0 if exact_value else 0.0)
            if score > best_score:
                best_score = score
                best_descriptor = descriptor
                best_reasons = []
                if exact_value:
                    best_reasons.append("exact_value")
                if concept_score > 0:
                    best_reasons.append(f"concept_overlap:{round(concept_score, 4)}")
                if value_score > 0:
                    best_reasons.append(f"value_overlap:{round(value_score, 4)}")
        candidate_rows.append(
            {
                "object_id": object_id,
                "object_type": object_type,
                "value": item.get("value"),
                "best_dependency_match": best_descriptor,
                "best_dependency_score": round(best_score, 4),
                "match_reasons": best_reasons,
            }
        )
        if best_descriptor is not None and best_score > 0:
            matched_candidates.append(
                {
                    "object_id": object_id,
                    "dependency_object_id": best_descriptor["object_id"],
                    "dependency_concept": best_descriptor["concept"],
                    "dependency_value": best_descriptor["normalized_value"],
                    "score": round(best_score, 4),
                }
            )

    return {
        "schema_version": "allocation_dependency_ingestion_trace.v1",
        "policy_name": policy_name,
        "received_dependency_objects": dependency_descriptors,
        "dependency_edge_count": len(dependency_edges),
        "candidate_object_count": len(objects),
        "matched_runtime_candidates": matched_candidates,
        "candidate_rows": candidate_rows,
    }


def _build_dependency_ranking_breakdown(
    *,
    policy_name: str,
    objects: List[Dict[str, object]],
    task_context: Any,
) -> Dict[str, object]:
    context = _task_context_dict(task_context)
    task_critical_ids = _task_critical_object_ids(context)
    important_ids = {_object_id(item) for item in _important_objects(context.get("recovered_state_package") or context)}
    source_ids = {_object_id(item) for item in _inventory_objects(context.get("recovered_state_package") or context)}
    dependency_descriptors = _dependency_object_descriptors(context)
    dependency_edges = _dependency_edges(context)

    rows: List[Dict[str, object]] = []
    for index, item in enumerate(objects):
        object_id = _object_id(item)
        object_type = str(item.get("type", "fact")).strip() or "fact"
        value = canonicalize_semantic_value(str(item.get("value", "")).strip())

        best_descriptor: Optional[Dict[str, str]] = None
        best_dependency_score = 0.0
        best_dependency_reasons: List[str] = []
        for descriptor in dependency_descriptors:
            concept_score = _token_overlap_score(object_type, descriptor["concept"])
            value_score = _token_overlap_score(value, descriptor["normalized_value"])
            exact_value = value == descriptor["normalized_value"]
            score = (0.15 * concept_score) + (0.75 * value_score) + (1.0 if exact_value else 0.0)
            if score > best_dependency_score:
                best_dependency_score = score
                best_descriptor = descriptor
                best_dependency_reasons = []
                if exact_value:
                    best_dependency_reasons.append("exact_value")
                if concept_score > 0:
                    best_dependency_reasons.append(f"concept_overlap:{round(concept_score, 4)}")
                if value_score > 0:
                    best_dependency_reasons.append(f"value_overlap:{round(value_score, 4)}")

        edge_bonus = 0.0
        for edge in dependency_edges:
            for node in (edge["source"], edge["target"]):
                node_score = _token_overlap_score(value, node)
                edge_bonus = max(edge_bonus, node_score)

        critical_bonus = 12.0 if object_id in task_critical_ids else 0.0
        important_bonus = 8.0 if object_id in important_ids else 0.0
        type_bonus = 0.0
        if object_type in {"question", "constraint", "answer"}:
            type_bonus = 6.0
        elif object_type == "anchor":
            type_bonus = 2.0
        source_bonus = 1.0 if object_id in source_ids else 0.0

        final_score = best_dependency_score + critical_bonus + important_bonus + type_bonus + source_bonus + (edge_bonus * 4.0)

        rows.append(
            {
                "rank": 0,
                "object_id": object_id,
                "object_type": object_type,
                "value": item.get("value"),
                "dependency_score": round(best_dependency_score, 4),
                "dependency_descriptor": best_descriptor,
                "dependency_reasons": best_dependency_reasons,
                "edge_bonus": round(edge_bonus, 4),
                "critical_bonus": critical_bonus,
                "important_bonus": important_bonus,
                "type_bonus": type_bonus,
                "source_bonus": source_bonus,
                "final_score": round(final_score, 4),
                "is_required_dependency": best_descriptor is not None and best_dependency_score > 0,
                "is_task_critical": object_id in task_critical_ids,
                "is_important": object_id in important_ids,
                "is_source_aligned": object_id in source_ids,
            }
        )

    rows.sort(key=lambda row: (-float(row["final_score"]), str(row["object_id"])))
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank

    return {
        "schema_version": "allocation_dependency_ranking_breakdown.v1",
        "policy_name": policy_name,
        "rows": rows,
    }


def _build_allocation_decision_boundary_trace(
    *,
    policy_name: str,
    objects: List[Dict[str, object]],
    active: List[Dict[str, object]],
    task_context: Any,
) -> Dict[str, object]:
    context = _task_context_dict(task_context)
    task_critical_ids = _task_critical_object_ids(context)
    important_ids = {_object_id(item) for item in _important_objects(context.get("recovered_state_package") or context)}
    source_ids = {_object_id(item) for item in _inventory_objects(context.get("recovered_state_package") or context)}
    dependency_descriptors = _dependency_object_descriptors(context)
    dependency_edges = _dependency_edges(context)
    active_ids = {_object_id(item) for item in active}

    rows: List[Dict[str, object]] = []
    for index, item in enumerate(objects):
        group, inner_score, reasons = _dependency_priority_group(
            item,
            dependency_descriptors=dependency_descriptors,
            dependency_edges=dependency_edges,
            task_critical_ids=task_critical_ids,
            important_ids=important_ids,
            source_ids=source_ids,
        )
        object_id = _object_id(item)
        rows.append(
            {
                "candidate_index": index,
                "object_id": object_id,
                "object_type": str(item.get("type", "fact")).strip() or "fact",
                "value": item.get("value"),
                "dependency_group": group,
                "dependency_score": round(inner_score, 4),
                "selection_reason": reasons,
                "selected": object_id in active_ids,
                "is_required_dependency": group == 0,
                "is_dependency_closure": group == 1,
            }
        )

    rows.sort(key=lambda row: (row["dependency_group"], row["candidate_index"]))
    ranked_rows = rows[:20]
    selected_ranked_rows = [row for row in rows if row["selected"]]
    return {
        "schema_version": "allocation_decision_boundary_trace.v1",
        "policy_name": policy_name,
        "candidate_count": len(objects),
        "active_count": len(active),
        "ranked_top20": ranked_rows,
        "selected_rows": selected_ranked_rows,
        "selected_required_dependency_count": sum(1 for row in rows if row["selected"] and row["is_required_dependency"]),
        "selected_dependency_closure_count": sum(1 for row in rows if row["selected"] and row["is_dependency_closure"]),
        "selected_anchor_count": sum(1 for item in active if str(item.get("type", "fact")).strip() == "anchor"),
    }


def _build_required_dependency_resolver_trace(
    *,
    policy_name: str,
    objects: List[Dict[str, object]],
    task_context: Any,
) -> Dict[str, object]:
    context = _task_context_dict(task_context)
    task_critical_ids = _task_critical_object_ids(context)
    important_ids = {_object_id(item) for item in _important_objects(context.get("recovered_state_package") or context)}
    source_ids = {_object_id(item) for item in _inventory_objects(context.get("recovered_state_package") or context)}
    dependency_descriptors = _dependency_object_descriptors(context)
    dependency_edges = _dependency_edges(context)

    dependency_rows: List[Dict[str, object]] = []
    for descriptor in dependency_descriptors:
        matches = _resolve_required_dependency_candidates(
            descriptor,
            objects,
            task_critical_ids=task_critical_ids,
            important_ids=important_ids,
            source_ids=source_ids,
            dependency_edges=dependency_edges,
        )
        dependency_rows.append(
            {
                "required_dependency": descriptor,
                "match_count": len(matches),
                "top_matches": matches[:10],
                "assigned_group": 0 if matches and matches[0]["exact_value"] else (1 if matches else None),
            }
        )

    return {
        "schema_version": "required_dependency_resolver_trace.v1",
        "policy_name": policy_name,
        "required_dependency_count": len(dependency_descriptors),
        "required_dependency_rows": dependency_rows,
    }


def _resolve_required_dependency_candidates(
    dependency_descriptor: Dict[str, str],
    objects: List[Dict[str, object]],
    *,
    task_critical_ids: Set[str],
    important_ids: Set[str],
    source_ids: Set[str],
    dependency_edges: Sequence[Dict[str, str]],
) -> List[Dict[str, object]]:
    concept = canonicalize_semantic_value(dependency_descriptor["concept"])
    normalized_value = canonicalize_semantic_value(dependency_descriptor["normalized_value"])
    candidates: List[Dict[str, object]] = []
    for item in objects:
        object_id = _object_id(item)
        object_type = str(item.get("type", "fact")).strip() or "fact"
        value = canonicalize_semantic_value(str(item.get("value", "")).strip())
        candidate_concept = canonicalize_semantic_value(object_type)
        if candidate_concept != concept:
            continue
        exact_value = value == normalized_value
        value_score = _token_overlap_score(value, normalized_value)
        edge_overlap = 0.0
        for edge in dependency_edges:
            for node in (edge["source"], edge["target"]):
                edge_overlap = max(edge_overlap, _token_overlap_score(value, node))
        score = 0.0
        if exact_value:
            score += 10.0
        score += value_score * 4.0
        score += edge_overlap * 1.5
        if object_id in task_critical_ids:
            score += 0.5
        if object_id in important_ids:
            score += 0.5
        if object_id in source_ids:
            score += 0.1
        if score <= 0:
            continue
        candidates.append(
            {
                "object_id": object_id,
                "object_type": object_type,
                "value": item.get("value"),
                "concept": concept,
                "normalized_value": normalized_value,
                "exact_value": exact_value,
                "value_score": round(value_score, 4),
                "edge_overlap": round(edge_overlap, 4),
                "score": round(score, 4),
                "is_task_critical": object_id in task_critical_ids,
                "is_important": object_id in important_ids,
                "is_source_aligned": object_id in source_ids,
            }
        )
    candidates.sort(key=lambda row: (-float(row["score"]), str(row["object_id"])))
    return candidates


def _dependency_priority_group(
    item: Dict[str, object],
    *,
    dependency_descriptors: Sequence[Dict[str, str]],
    dependency_edges: Sequence[Dict[str, str]],
    task_critical_ids: Set[str],
    important_ids: Set[str],
    source_ids: Set[str],
) -> Tuple[int, float, List[str]]:
    object_id = _object_id(item)
    object_type = str(item.get("type", "fact")).strip() or "fact"
    value = canonicalize_semantic_value(str(item.get("value", "")).strip())

    best_descriptor: Optional[Dict[str, str]] = None
    best_dependency_score = 0.0
    for descriptor in dependency_descriptors:
        concept_score = _token_overlap_score(object_type, descriptor["concept"])
        value_score = _token_overlap_score(value, descriptor["normalized_value"])
        exact_value = value == descriptor["normalized_value"]
        score = (0.15 * concept_score) + (0.75 * value_score) + (1.0 if exact_value else 0.0)
        if score > best_dependency_score:
            best_dependency_score = score
            best_descriptor = descriptor

    edge_overlap = 0.0
    for edge in dependency_edges:
        for node in (edge["source"], edge["target"]):
            edge_overlap = max(edge_overlap, _token_overlap_score(value, node))

    if best_descriptor is not None and best_dependency_score >= 0.75:
        return 0, best_dependency_score + (edge_overlap * 0.25), [f"required_dependency:{best_descriptor['object_id']}"]

    if edge_overlap >= 0.5:
        return 1, edge_overlap, [f"dependency_closure:{round(edge_overlap, 4)}"]

    if object_id in task_critical_ids:
        return 2, 0.0, ["task_critical"]

    if object_id in important_ids:
        return 3, 0.0, ["important_object"]

    if object_type in {"question", "constraint", "answer", "anchor"}:
        return 4, 0.0, [f"type_priority:{object_type}"]

    if object_id in source_ids:
        return 5, 0.0, ["source_aligned"]

    return 6, 0.0, ["fallback"]


def _dependency_aware_v3_partition_objects(
    objects: List[Dict[str, object]],
    task_context: Any,
    *,
    active_limit: int | None = None,
) -> tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]]]:
    context = _task_context_dict(task_context)
    task_critical_ids = _task_critical_object_ids(context)
    important_ids = {_object_id(item) for item in _important_objects(context.get("recovered_state_package") or context)}
    source_ids = {_object_id(item) for item in _inventory_objects(context.get("recovered_state_package") or context)}
    dependency_descriptors = _dependency_object_descriptors(context)
    dependency_edges = _dependency_edges(context)

    scored: List[Tuple[int, float, int, Dict[str, object], List[str]]] = []
    for index, item in enumerate(objects):
        group, inner_score, reasons = _dependency_priority_group(
            item,
            dependency_descriptors=dependency_descriptors,
            dependency_edges=dependency_edges,
            task_critical_ids=task_critical_ids,
            important_ids=important_ids,
            source_ids=source_ids,
        )
        scored.append((group, -inner_score, index, item, reasons))

    scored.sort(key=lambda entry: (entry[0], entry[1], entry[2]))
    active: List[Dict[str, object]] = []
    latent: List[Dict[str, object]] = []
    discard: List[Dict[str, object]] = []
    active_ids: Set[str] = set()

    target_active = active_limit if active_limit is not None else min(12, len(objects))
    target_active = max(1, min(len(objects), target_active))

    for _, _, _, item, _ in scored:
        if len(active) >= target_active:
            break
        active.append(item)
        active_ids.add(_object_id(item))

    for item in objects:
        object_id = _object_id(item)
        if object_id in active_ids:
            continue
        if object_id in source_ids:
            latent.append(item)
        else:
            discard.append(item)

    active = _dedupe_objects(active)
    latent = _dedupe_objects(latent)
    discard = _dedupe_objects(discard)
    return active, latent, discard


class UnrestrictedAllocationPolicy(StateAllocationPolicy):
    name = "unrestricted"

    def allocate(self, reconstructed_state: Any, task_context: Any) -> StateAllocationResult:
        package = _unwrap_state(reconstructed_state)
        objects = _typed_objects(package)
        active, latent, discard = _dedupe_objects(objects), [], []
        metrics = _build_metrics(self.name, active, latent, discard, len(objects), task_context)
        forensic_trace = None
        if str(os.getenv("SRP_ALLOCATION_TRACE", "0")).strip().lower() not in {"0", "false", "no", "off"}:
            forensic_trace = _build_forensic_trace(
                policy_name=self.name,
                objects=objects,
                active=active,
                latent=latent,
                discard=discard,
                task_context=task_context,
            )
        return StateAllocationResult(
            active_state={**package, "active_objects": active},
            latent_state={**package, "latent_objects": latent},
            discard_state={**package, "discard_objects": discard},
            active_objects=active,
            latent_objects=latent,
            discard_objects=discard,
            policy_name=self.name,
            metrics=metrics,
            forensic_trace=forensic_trace,
        )


class RecoveredAllocationPolicy(StateAllocationPolicy):
    name = "recovered"

    def allocate(self, reconstructed_state: Any, task_context: Any) -> StateAllocationResult:
        package = _unwrap_state(reconstructed_state)
        objects = _typed_objects(package)
        active, latent, discard = _dedupe_objects(objects), [], []
        metrics = _build_metrics(self.name, active, latent, discard, len(objects), task_context)
        forensic_trace = None
        if str(os.getenv("SRP_ALLOCATION_TRACE", "0")).strip().lower() not in {"0", "false", "no", "off"}:
            forensic_trace = _build_forensic_trace(
                policy_name=self.name,
                objects=objects,
                active=active,
                latent=latent,
                discard=discard,
                task_context=task_context,
            )
        return StateAllocationResult(
            active_state={**package, "active_objects": active},
            latent_state={**package, "latent_objects": latent},
            discard_state={**package, "discard_objects": discard},
            active_objects=active,
            latent_objects=latent,
            discard_objects=discard,
            policy_name=self.name,
            metrics=metrics,
            forensic_trace=forensic_trace,
        )


class ConstrainedAllocationPolicy(StateAllocationPolicy):
    name = "constrained"

    def allocate(self, reconstructed_state: Any, task_context: Any) -> StateAllocationResult:
        package = _unwrap_state(reconstructed_state)
        objects = _typed_objects(package)
        active, latent, discard = _partition_objects(objects, task_context, active_limit=max(1, len(objects) // 3))
        metrics = _build_metrics(self.name, active, latent, discard, len(objects), task_context)
        forensic_trace = None
        if str(os.getenv("SRP_ALLOCATION_TRACE", "0")).strip().lower() not in {"0", "false", "no", "off"}:
            forensic_trace = _build_forensic_trace(
                policy_name=self.name,
                objects=objects,
                active=active,
                latent=latent,
                discard=discard,
                task_context=task_context,
            )
        return StateAllocationResult(
            active_state={**package, "active_objects": active},
            latent_state={**package, "latent_objects": latent},
            discard_state={**package, "discard_objects": discard},
            active_objects=active,
            latent_objects=latent,
            discard_objects=discard,
            policy_name=self.name,
            metrics=metrics,
            forensic_trace=forensic_trace,
        )


class MinimalSufficientAllocationPolicy(StateAllocationPolicy):
    name = "minimal"

    def allocate(self, reconstructed_state: Any, task_context: Any) -> StateAllocationResult:
        package = _unwrap_state(reconstructed_state)
        objects = _typed_objects(package)
        active, latent, discard = _partition_objects(objects, task_context, active_limit=12, latent_limit=max(0, len(objects) - 12))
        metrics = _build_metrics(self.name, active, latent, discard, len(objects), task_context)
        forensic_trace = None
        if str(os.getenv("SRP_ALLOCATION_TRACE", "0")).strip().lower() not in {"0", "false", "no", "off"}:
            forensic_trace = _build_forensic_trace(
                policy_name=self.name,
                objects=objects,
                active=active,
                latent=latent,
                discard=discard,
                task_context=task_context,
            )
        return StateAllocationResult(
            active_state={**package, "active_objects": active},
            latent_state={**package, "latent_objects": latent},
            discard_state={**package, "discard_objects": discard},
            active_objects=active,
            latent_objects=latent,
            discard_objects=discard,
            policy_name=self.name,
            metrics=metrics,
            forensic_trace=forensic_trace,
        )


class DependencyAwareAllocationPolicy(StateAllocationPolicy):
    name = "dependency-aware"

    def allocate(self, reconstructed_state: Any, task_context: Any) -> StateAllocationResult:
        package = _unwrap_state(reconstructed_state)
        objects = _typed_objects(package)
        active, latent, discard = _dependency_aware_partition_objects(objects, task_context, active_limit=12)
        metrics = _build_metrics(self.name, active, latent, discard, len(objects), task_context)
        forensic_trace = None
        if str(os.getenv("SRP_ALLOCATION_TRACE", "0")).strip().lower() not in {"0", "false", "no", "off"}:
            forensic_trace = _build_forensic_trace(
                policy_name=self.name,
                objects=objects,
                active=active,
                latent=latent,
                discard=discard,
                task_context=task_context,
            )
            forensic_trace["dependency_allocation_ingestion_trace"] = _build_dependency_allocation_ingestion_trace(
                policy_name=self.name,
                objects=objects,
                task_context=task_context,
            )
            forensic_trace["dependency_ranking_breakdown"] = _build_dependency_ranking_breakdown(
                policy_name=self.name,
                objects=objects,
                task_context=task_context,
            )
            forensic_trace["allocation_decision_boundary_trace"] = _build_allocation_decision_boundary_trace(
                policy_name=self.name,
                objects=objects,
                active=active,
                task_context=task_context,
            )
            forensic_trace["required_dependency_resolver_trace"] = _build_required_dependency_resolver_trace(
                policy_name=self.name,
                objects=objects,
                task_context=task_context,
            )
        return StateAllocationResult(
            active_state={**package, "active_objects": active},
            latent_state={**package, "latent_objects": latent},
            discard_state={**package, "discard_objects": discard},
            active_objects=active,
            latent_objects=latent,
            discard_objects=discard,
            policy_name=self.name,
            metrics=metrics,
            forensic_trace=forensic_trace,
        )


class DependencyAwareV2AllocationPolicy(StateAllocationPolicy):
    name = "dependency-aware-v2"

    def allocate(self, reconstructed_state: Any, task_context: Any) -> StateAllocationResult:
        package = _unwrap_state(reconstructed_state)
        objects = _typed_objects(package)
        active, latent, discard = _dependency_aware_v2_partition_objects(objects, task_context, active_limit=12)
        metrics = _build_metrics(self.name, active, latent, discard, len(objects), task_context)
        forensic_trace = None
        if str(os.getenv("SRP_ALLOCATION_TRACE", "0")).strip().lower() not in {"0", "false", "no", "off"}:
            forensic_trace = _build_forensic_trace(
                policy_name=self.name,
                objects=objects,
                active=active,
                latent=latent,
                discard=discard,
                task_context=task_context,
            )
            forensic_trace["dependency_allocation_ingestion_trace"] = _build_dependency_allocation_ingestion_trace(
                policy_name=self.name,
                objects=objects,
                task_context=task_context,
            )
            forensic_trace["dependency_ranking_breakdown"] = _build_dependency_ranking_breakdown(
                policy_name=self.name,
                objects=objects,
                task_context=task_context,
            )
            forensic_trace["allocation_decision_boundary_trace"] = _build_allocation_decision_boundary_trace(
                policy_name=self.name,
                objects=objects,
                active=active,
                task_context=task_context,
            )
            forensic_trace["required_dependency_resolver_trace"] = _build_required_dependency_resolver_trace(
                policy_name=self.name,
                objects=objects,
                task_context=task_context,
            )
        return StateAllocationResult(
            active_state={**package, "active_objects": active},
            latent_state={**package, "latent_objects": latent},
            discard_state={**package, "discard_objects": discard},
            active_objects=active,
            latent_objects=latent,
            discard_objects=discard,
            policy_name=self.name,
            metrics=metrics,
            forensic_trace=forensic_trace,
        )


class DependencyAwareV3AllocationPolicy(StateAllocationPolicy):
    name = "dependency-aware-v3"

    def allocate(self, reconstructed_state: Any, task_context: Any) -> StateAllocationResult:
        package = _unwrap_state(reconstructed_state)
        objects = _typed_objects(package)
        active, latent, discard = _dependency_aware_v3_partition_objects(objects, task_context, active_limit=12)
        metrics = _build_metrics(self.name, active, latent, discard, len(objects), task_context)
        forensic_trace = None
        if str(os.getenv("SRP_ALLOCATION_TRACE", "0")).strip().lower() not in {"0", "false", "no", "off"}:
            forensic_trace = _build_forensic_trace(
                policy_name=self.name,
                objects=objects,
                active=active,
                latent=latent,
                discard=discard,
                task_context=task_context,
            )
            forensic_trace["dependency_allocation_ingestion_trace"] = _build_dependency_allocation_ingestion_trace(
                policy_name=self.name,
                objects=objects,
                task_context=task_context,
            )
            forensic_trace["dependency_ranking_breakdown"] = _build_dependency_ranking_breakdown(
                policy_name=self.name,
                objects=objects,
                task_context=task_context,
            )
            forensic_trace["allocation_decision_boundary_trace"] = _build_allocation_decision_boundary_trace(
                policy_name=self.name,
                objects=objects,
                active=active,
                task_context=task_context,
            )
            forensic_trace["required_dependency_resolver_trace"] = _build_required_dependency_resolver_trace(
                policy_name=self.name,
                objects=objects,
                task_context=task_context,
            )
        return StateAllocationResult(
            active_state={**package, "active_objects": active},
            latent_state={**package, "latent_objects": latent},
            discard_state={**package, "discard_objects": discard},
            active_objects=active,
            latent_objects=latent,
            discard_objects=discard,
            policy_name=self.name,
            metrics=metrics,
            forensic_trace=forensic_trace,
        )


class RandomAllocationPolicy(StateAllocationPolicy):
    name = "random"

    def _target_active_count(self, objects: List[Dict[str, object]]) -> int:
        raw_budget = os.getenv("SRP_ACTIVE_BUDGET")
        if raw_budget:
            try:
                return max(1, min(len(objects), int(raw_budget)))
            except ValueError:
                pass
        return max(1, min(len(objects), 12))

    def allocate(self, reconstructed_state: Any, task_context: Any) -> StateAllocationResult:
        package = _unwrap_state(reconstructed_state)
        objects = _typed_objects(package)
        target_count = self._target_active_count(objects)
        seed = os.getenv("SRP_RANDOM_ALLOCATION_SEED", "0").strip()
        try:
            seed_value = int(seed)
        except ValueError:
            seed_value = 0
        rng = random.Random(seed_value)
        shuffled = list(objects)
        rng.shuffle(shuffled)
        active = _dedupe_objects(shuffled[:target_count])
        active_ids = {_object_id(item) for item in active}
        latent: List[Dict[str, object]] = []
        discard: List[Dict[str, object]] = []
        context = _task_context_dict(task_context)
        source_ids = {_object_id(item) for item in _inventory_objects(context.get("recovered_state_package") or context)}
        for item in objects:
            object_id = _object_id(item)
            if object_id in active_ids:
                continue
            if object_id in source_ids:
                latent.append(item)
            else:
                discard.append(item)
        latent = _dedupe_objects(latent)
        discard = _dedupe_objects(discard)
        metrics = _build_metrics(self.name, active, latent, discard, len(objects), task_context)
        forensic_trace = None
        if str(os.getenv("SRP_ALLOCATION_TRACE", "0")).strip().lower() not in {"0", "false", "no", "off"}:
            forensic_trace = _build_forensic_trace(
                policy_name=self.name,
                objects=objects,
                active=active,
                latent=latent,
                discard=discard,
                task_context=task_context,
            )
        return StateAllocationResult(
            active_state={**package, "active_objects": active},
            latent_state={**package, "latent_objects": latent},
            discard_state={**package, "discard_objects": discard},
            active_objects=active,
            latent_objects=latent,
            discard_objects=discard,
            policy_name=self.name,
            metrics=metrics,
            forensic_trace=forensic_trace,
        )
