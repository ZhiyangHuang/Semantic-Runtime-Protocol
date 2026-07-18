from __future__ import annotations

import hashlib
import os
import random
from typing import Any, Dict, Iterable, List, Sequence, Set, Tuple

from experiments.common.semantic_text import canonicalize_semantic_value
from experiments.common.state_allocation import AllocationMetrics, StateAllocationPolicy, StateAllocationResult


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return int(default)
    try:
        return max(1, int(float(raw)))
    except (TypeError, ValueError):
        return int(default)


def stable_semantic_object_id(object_type: str, value: str) -> str:
    normalized_type = canonicalize_semantic_value(object_type) or str(object_type).strip().lower() or "object"
    normalized_value = canonicalize_semantic_value(value) or str(value).strip().lower()
    digest = hashlib.sha1(f"{normalized_type}|{normalized_value}".encode("utf-8")).hexdigest()[:16]
    return f"{normalized_type}:{digest}"


def _object_id(item: Dict[str, object]) -> str:
    object_type = str(item.get("type", "fact")).strip() or "fact"
    value = str(item.get("value", "")).strip()
    return str(item.get("object_id") or item.get("id") or "").strip() or stable_semantic_object_id(object_type, value)


def _dedupe_objects(objects: Iterable[Dict[str, object]]) -> List[Dict[str, object]]:
    seen: Set[str] = set()
    deduped: List[Dict[str, object]] = []
    for item in objects:
        object_id = _object_id(item)
        if object_id in seen:
            continue
        seen.add(object_id)
        deduped.append(item)
    return deduped


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
    critical: Set[str] = set()

    explicit_ids = context.get("critical_object_ids")
    if isinstance(explicit_ids, list):
        for item in explicit_ids:
            if item is None:
                continue
            critical.add(str(item).strip())

    for key in ["important_objects", "required_dependency_objects"]:
        items = context.get(key)
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    critical.add(_object_id(item))

    task = context.get("task")
    if isinstance(task, dict):
        metadata = task.get("metadata") or {}
        for key in ["important_objects", "required_dependency_objects"]:
            items = metadata.get(key)
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        critical.add(_object_id(item))

    return critical


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


def _score_item(
    item: Dict[str, object],
    *,
    include_dependency: bool,
    include_importance: bool,
    task_context: Any,
) -> float:
    context = _task_context_dict(task_context)
    runtime_metadata = _runtime_metadata_for_context(task_context)
    task_critical_ids = _task_critical_object_ids(context)
    important_ids = {_object_id(obj) for obj in _important_objects(context.get("recovered_state_package") or context)}
    source_ids = {_object_id(obj) for obj in _inventory_objects(context.get("recovered_state_package") or context)}
    dependency_descriptors = _dependency_object_descriptors(context)
    dependency_edges = _dependency_edges(context)

    object_id = _object_id(item)
    object_type = str(item.get("type", "fact")).strip() or "fact"
    metadata_importance = runtime_metadata.get(object_id, {}).get("importance")
    importance = float(item.get("importance", metadata_importance if metadata_importance is not None else 0.0) or 0.0)
    score = 0.0
    if include_importance:
        score += importance
        if object_id in task_critical_ids:
            score += 0.75
        if object_id in important_ids:
            score += 0.5
        if object_type in {"question", "constraint", "answer", "anchor"}:
            score += 0.25
        if object_id in source_ids:
            score += 0.1

    if include_dependency:
        dependency_score, _ = _semantic_dependency_score(item, dependency_descriptors, dependency_edges)
        score += dependency_score * 2.5

    return score


def _runtime_metadata_for_context(task_context: Any) -> Dict[str, Dict[str, object]]:
    context = _task_context_dict(task_context)
    package = context.get("recovered_state_package") or context
    runtime_metadata = {}
    if isinstance(package, dict):
        runtime_metadata = package.get("runtime_metadata") or package.get("runtime_metadata_snapshot") or {}
    if isinstance(runtime_metadata, dict):
        normalized: Dict[str, Dict[str, object]] = {}
        for object_id, metadata in runtime_metadata.items():
            if isinstance(metadata, dict):
                normalized[str(object_id)] = dict(metadata)
            else:
                normalized[str(object_id)] = getattr(metadata, "as_dict", lambda: {})() or {}
        return normalized
    return {}


def _target_active_count(objects: Sequence[Dict[str, object]]) -> int:
    raw_budget = _env_int("SRP_ACTIVE_BUDGET", 12)
    return max(1, min(len(objects), raw_budget if raw_budget > 0 else 12))


def _partition_objects(
    objects: List[Dict[str, object]],
    task_context: Any,
    *,
    include_dependency: bool,
    include_importance: bool,
) -> tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]]]:
    context = _task_context_dict(task_context)
    source_ids = {_object_id(item) for item in _inventory_objects(context.get("recovered_state_package") or context)}
    rng = random.Random(_env_int("SRP_RANDOM_ALLOCATION_SEED", 0))
    scored: List[Tuple[float, int, Dict[str, object]]] = []
    for index, item in enumerate(objects):
        score = _score_item(
            item,
            include_dependency=include_dependency,
            include_importance=include_importance,
            task_context=task_context,
        ) + (rng.random() * 1e-6)
        scored.append((score, index, item))

    scored.sort(key=lambda entry: (-entry[0], entry[1]))
    active: List[Dict[str, object]] = []
    latent: List[Dict[str, object]] = []
    discard: List[Dict[str, object]] = []
    active_ids: Set[str] = set()

    target_active = _target_active_count(objects)
    for _, _, item in scored:
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

    return _dedupe_objects(active), _dedupe_objects(latent), _dedupe_objects(discard)


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


class _MechanismAblationPolicyBase(StateAllocationPolicy):
    include_importance = True
    include_dependency = False
    name = "mechanism-ablation"

    def allocate(self, reconstructed_state: Any, task_context: Any) -> StateAllocationResult:
        package = reconstructed_state or {}
        if isinstance(package, dict) and package.get("schema_version") == "structured_state_package.v1":
            structured = package
        elif isinstance(package, dict) and isinstance(package.get("recovered_state_package"), dict):
            structured = package["recovered_state_package"]
        elif isinstance(package, dict) and isinstance(package.get("structured_state_package"), dict):
            structured = package["structured_state_package"]
        else:
            structured = getattr(reconstructed_state, "recovered_state_package", {}) or {}
        objects = _typed_objects(structured)
        active, latent, discard = _partition_objects(
            objects,
            task_context,
            include_dependency=self.include_dependency,
            include_importance=self.include_importance,
        )
        metrics = _build_metrics(self.name, active, latent, discard, len(objects), task_context)
        return StateAllocationResult(
            active_state={**structured, "active_objects": active},
            latent_state={**structured, "latent_objects": latent},
            discard_state={**structured, "discard_objects": discard},
            active_objects=active,
            latent_objects=latent,
            discard_objects=discard,
            policy_name=self.name,
            metrics=metrics,
            forensic_trace=None,
        )


__all__ = [
    "AllocationMetrics",
    "StateAllocationPolicy",
    "StateAllocationResult",
    "stable_semantic_object_id",
    "_env_int",
    "_object_id",
    "_dedupe_objects",
    "_typed_objects",
    "_inventory_objects",
    "_important_objects",
    "_task_context_dict",
    "_task_critical_object_ids",
    "_dependency_object_descriptors",
    "_dependency_edges",
    "_normalize_tokens",
    "_token_overlap_score",
    "_semantic_dependency_score",
    "_runtime_metadata_for_context",
    "_score_item",
    "_target_active_count",
    "_partition_objects",
    "_build_metrics",
    "_MechanismAblationPolicyBase",
]
