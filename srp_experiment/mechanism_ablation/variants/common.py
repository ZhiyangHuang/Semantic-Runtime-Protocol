from __future__ import annotations

import os
import random
from typing import Any, Dict, Iterable, List, Sequence, Set, Tuple

from srp_experiment.srp.state_allocation.metrics import AllocationMetrics
from srp_experiment.srp.state_allocation.policy import StateAllocationPolicy
from srp_experiment.srp.state_allocation.policies import (
    _dependency_edges,
    _dependency_object_descriptors,
    _dedupe_objects,
    _important_objects,
    _inventory_objects,
    _object_id,
    _semantic_dependency_score,
    _task_context_dict,
    _task_critical_object_ids,
    _typed_objects,
)
from srp_experiment.srp.state_allocation.result import StateAllocationResult


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return int(default)
    try:
        return max(1, int(float(raw)))
    except (TypeError, ValueError):
        return int(default)


def _target_active_count(objects: Sequence[Dict[str, object]]) -> int:
    raw_budget = _env_int("SRP_ACTIVE_BUDGET", 12)
    return max(1, min(len(objects), raw_budget if raw_budget > 0 else 12))


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
