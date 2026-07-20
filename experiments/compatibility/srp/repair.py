from __future__ import annotations

import os
from typing import Dict, List

from .semantic_parser import canonicalize_semantic_value, stable_semantic_object_id
from .validation_targets import SemanticContractGraph


def _object_lines(objects: List[Dict[str, object]], limit: int = 12) -> List[str]:
    lines = []
    for item in objects[:limit]:
        object_type = str(item.get("type", "fact")).strip() or "fact"
        value = str(item.get("value", "")).strip()
        confidence = item.get("confidence")
        evidence_pointer = str(item.get("evidence_pointer", "")).strip()
        if not value:
            continue
        line = f"[{object_type}] {value}"
        if evidence_pointer:
            line += f" ({evidence_pointer})"
        if confidence is not None:
            line += f" confidence={float(confidence):.2f}"
        lines.append(line)
    return lines


def _task_critical_object_ids(validation_targets: SemanticContractGraph | None) -> set[str]:
    if validation_targets is None:
        return set()
    critical = set()
    for node in validation_targets.nodes:
        if node.role not in {"clause"}:
            continue
        if node.node_type not in {"query_expectation", "constraint"}:
            continue
        for variant in node.variants:
            canonical_value = canonicalize_semantic_value(variant.surface)
            critical.add(stable_semantic_object_id(node.node_type, canonical_value or variant.surface))
    return critical


def _filter_task_critical_objects(
    objects: List[Dict[str, object]],
    validation_targets: SemanticContractGraph | None,
) -> List[Dict[str, object]]:
    critical_ids = _task_critical_object_ids(validation_targets)
    if not critical_ids:
        return list(objects)
    filtered = []
    for item in objects:
        if not isinstance(item, dict):
            continue
        object_id = stable_semantic_object_id(str(item.get("type", "fact")), str(item.get("value", "")))
        if object_id in critical_ids:
            filtered.append(item)
    return filtered


def _repair_constraint_mode() -> str:
    return str(os.getenv("SRP_REPAIR_CONSTRAINT_MODE", "unrestricted")).strip().lower()


def _repair_objective() -> str:
    return str(os.getenv("SRP_REPAIR_OBJECTIVE", "generation")).strip().lower()


def _repair_alignment_ids(validation: Dict) -> tuple[set[str], set[str]]:
    critical_source_ids: set[str] = set()
    aligned_recovered_ids: set[str] = set()
    object_alignment = validation.get("object_alignment") or {}
    for group in object_alignment.values():
        for item in group.get("matches", []):
            source_object_id = str(item.get("source_object_id") or "").strip()
            recovered_object_id = str(item.get("recovered_object_id") or "").strip()
            similarity = float(item.get("similarity", 0.0) or 0.0)
            if similarity < 0.5 and source_object_id:
                critical_source_ids.add(source_object_id)
            if similarity < 0.5 and recovered_object_id:
                aligned_recovered_ids.add(recovered_object_id)
    for failure in validation.get("critical_failures", []):
        source_object_id = str(failure.get("source_object_id") or "").strip()
        if source_object_id:
            critical_source_ids.add(source_object_id)
        recovered_object_id = str(failure.get("recovered_object_id") or "").strip()
        if recovered_object_id:
            aligned_recovered_ids.add(recovered_object_id)
    return critical_source_ids, aligned_recovered_ids


def _filter_objects_by_ids(objects: List[Dict[str, object]], allowed_ids: set[str]) -> List[Dict[str, object]]:
    if not allowed_ids:
        return []
    filtered: List[Dict[str, object]] = []
    seen: set[str] = set()
    for item in objects:
        if not isinstance(item, dict):
            continue
        object_id = stable_semantic_object_id(str(item.get("type", "fact")), str(item.get("value", "")))
        if object_id in allowed_ids and object_id not in seen:
            filtered.append(item)
            seen.add(object_id)
    return filtered


def _build_patch_updates(
    objects: List[Dict[str, object]],
    allowed_ids: set[str],
    *,
    limit: int | None = None,
) -> List[Dict[str, object]]:
    patches: List[Dict[str, object]] = []
    seen: set[str] = set()
    for item in objects:
        if not isinstance(item, dict):
            continue
        object_type = str(item.get("type", "fact")).strip() or "fact"
        value = str(item.get("value", "")).strip()
        if not value:
            continue
        object_id = stable_semantic_object_id(object_type, value)
        if object_id not in allowed_ids or object_id in seen:
            continue
        patches.append(
            {
                "object_id": object_id,
                "type": object_type,
                "field": "value",
                "old": "",
                "new": value,
                "evidence_pointer": str(item.get("evidence_pointer", "")),
            }
        )
        seen.add(object_id)
        if limit is not None and len(patches) >= limit:
            break
    return patches


def build_repair_package(
    source_package: Dict,
    recovered_state_package: Dict | None,
    validation: Dict,
    validation_targets: SemanticContractGraph | None = None,
) -> Dict:
    if str(os.getenv("SRP_REPAIR_ENABLED", "true")).strip().lower() in {"0", "false", "no", "off"}:
        repaired = dict(source_package)
        repaired["repair_context"] = {
            "schema_version": "repair_context.v1",
            "critical_failure_count": len(validation.get("critical_failures", [])),
            "leakage_detected": bool(validation.get("leakage_detected", False)),
            "drift_blocks_commit": bool(validation.get("drift_blocks_commit", False)),
            "structured_object_count": 0,
            "important_object_count": 0,
            "task_critical_filter_enabled": False,
            "task_critical_object_count": 0,
            "task_critical_important_count": 0,
            "repair_enabled": False,
        }
        repaired["repair_context_flat"] = build_repair_context_flat(repaired["repair_context"])
        repaired["recovered_state_package"] = recovered_state_package or {}
        repaired["structured_state_package"] = recovered_state_package or {}
        return repaired

    repaired = dict(source_package)
    structured = recovered_state_package or {}
    nested_inventory = structured.get("semantic_object_inventory") or {}
    typed_representation = structured.get("typed_representation") or {}
    objects = list(typed_representation.get("objects", []))
    important_objects = list(structured.get("important_objects", []))
    repair_constraint_mode = _repair_constraint_mode()
    repair_objective = _repair_objective()
    task_critical_filter_enabled = str(os.getenv("SRP_TASK_CRITICAL_FILTER", "false")).strip().lower() in {"1", "true", "yes", "on"}
    filtered_objects = _filter_task_critical_objects(objects, validation_targets) if task_critical_filter_enabled else list(objects)
    filtered_important_objects = _filter_task_critical_objects(important_objects, validation_targets) if task_critical_filter_enabled else list(important_objects)
    merged_objects = filtered_important_objects + [item for item in filtered_objects if item not in filtered_important_objects]
    critical_source_ids, aligned_recovered_ids = _repair_alignment_ids(validation)
    patch_updates: List[Dict[str, object]] = []
    patch_rejected_count = 0
    patch_applied_count = 0
    original_object_count = len(objects)
    if repair_constraint_mode == "constrained":
        allowed_ids = critical_source_ids | aligned_recovered_ids
        if not allowed_ids:
            allowed_ids = {
                stable_semantic_object_id(str(item.get("type", "fact")), str(item.get("value", "")))
                for item in filtered_important_objects or filtered_objects
                if isinstance(item, dict)
            }
        filtered_objects = _filter_objects_by_ids(filtered_objects, allowed_ids)
        filtered_important_objects = _filter_objects_by_ids(filtered_important_objects, allowed_ids)
        merged_objects = filtered_important_objects + [item for item in filtered_objects if item not in filtered_important_objects]
    elif repair_constraint_mode == "strict":
        allowed_ids = aligned_recovered_ids or critical_source_ids
        if not allowed_ids:
            allowed_ids = {
                stable_semantic_object_id(str(item.get("type", "fact")), str(item.get("value", "")))
                for item in filtered_objects
                if isinstance(item, dict)
            }
        filtered_objects = _filter_objects_by_ids(filtered_objects, allowed_ids)
        filtered_important_objects = _filter_objects_by_ids(filtered_important_objects, allowed_ids)
        merged_objects = filtered_important_objects + [item for item in filtered_objects if item not in filtered_important_objects]

    if repair_objective == "patch":
        allowed_ids = critical_source_ids or aligned_recovered_ids
        if not allowed_ids:
            allowed_ids = {
                stable_semantic_object_id(str(item.get("type", "fact")), str(item.get("value", "")))
                for item in merged_objects
                if isinstance(item, dict)
            }
        patch_updates = _build_patch_updates(merged_objects, allowed_ids)
        patch_rejected_count = max(0, len(merged_objects) - len(patch_updates))
        patch_applied_count = len(patch_updates)
        merged_objects = [
            {
                "type": patch.get("type", "fact"),
                "value": patch.get("new", ""),
                "confidence": 1.0,
                "evidence_pointer": patch.get("evidence_pointer", ""),
            }
            for patch in patch_updates
        ]
    elif repair_objective == "minimal_patch":
        allowed_ids = critical_source_ids or aligned_recovered_ids
        if not allowed_ids:
            allowed_ids = {
                stable_semantic_object_id(str(item.get("type", "fact")), str(item.get("value", "")))
                for item in merged_objects
                if isinstance(item, dict)
            }
        patch_limit = len(validation.get("critical_failures", [])) or len(allowed_ids)
        patch_updates = _build_patch_updates(merged_objects, allowed_ids, limit=patch_limit)
        patch_rejected_count = max(0, len(merged_objects) - len(patch_updates))
        patch_applied_count = len(patch_updates)
        merged_objects = [
            {
                "type": patch.get("type", "fact"),
                "value": patch.get("new", ""),
                "confidence": 1.0,
                "evidence_pointer": patch.get("evidence_pointer", ""),
            }
            for patch in patch_updates
        ]
    structured_lines = _object_lines(merged_objects, limit=16)
    repair_notes = list(repaired.get("loss_notes", []))
    if validation.get("critical_failures"):
        repair_notes.append("repair: critical failures observed")
    if validation.get("leakage_detected"):
        repair_notes.append("repair: leakage observed")
    if validation.get("drift_blocks_commit"):
        repair_notes.append("repair: drift blocks commit")
    if structured_lines:
        repair_notes.append("repair: structured state package prioritized")
    repaired["memory"] = "\n".join(structured_lines) if structured_lines else repaired.get("memory", "")
    repaired["loss_notes"] = repair_notes
    constrained_package = task_critical_filter_enabled or repair_constraint_mode in {"constrained", "strict"}
    if constrained_package:
        nested_inventory = dict(nested_inventory)
        nested_inventory["objects"] = filtered_objects
        nested_inventory["important_objects"] = filtered_important_objects
        nested_inventory["object_count"] = len(filtered_objects)
        nested_inventory["important_object_count"] = len(filtered_important_objects)
        repaired["semantic_object_inventory"] = nested_inventory or structured
        repaired["structured_state_package"] = {
            **structured,
            "semantic_object_inventory": nested_inventory or structured,
            "typed_representation": {
                **typed_representation,
                "objects": merged_objects,
            },
            "schema_version": structured.get("schema_version", "structured_state_package.v1"),
        }
        repaired["recovered_state_package"] = repaired["structured_state_package"]
    else:
        repaired["semantic_object_inventory"] = nested_inventory or structured
        repaired["structured_state_package"] = structured
        repaired["recovered_state_package"] = structured
    repaired["repair_context"] = {
        "schema_version": "repair_context.v1",
        "critical_failure_count": len(validation.get("critical_failures", [])),
        "leakage_detected": bool(validation.get("leakage_detected", False)),
        "drift_blocks_commit": bool(validation.get("drift_blocks_commit", False)),
        "structured_object_count": len(objects),
        "important_object_count": len(important_objects),
        "task_critical_filter_enabled": task_critical_filter_enabled,
        "task_critical_object_count": len(filtered_objects) if task_critical_filter_enabled else len(objects),
        "task_critical_important_count": len(filtered_important_objects) if task_critical_filter_enabled else len(important_objects),
        "repair_constraint_mode": repair_constraint_mode,
        "repair_objective": repair_objective,
        "critical_source_object_count": len(critical_source_ids),
        "aligned_recovered_object_count": len(aligned_recovered_ids),
        "repair_patch_count": len(patch_updates),
        "repair_applied_count": patch_applied_count,
        "repair_rejected_count": patch_rejected_count,
        "repair_object_delta": len(merged_objects) - original_object_count,
        "repair_enabled": True,
    }
    repaired["repair_context_flat"] = build_repair_context_flat(repaired["repair_context"])
    return repaired


def build_repair_context_flat(context: Dict | None = None) -> Dict[str, object]:
    context = context or {}
    return {
        "schema_version": "repair_context_flat.v1",
        "critical_failure_count": context.get("critical_failure_count"),
        "leakage_detected": context.get("leakage_detected"),
        "drift_blocks_commit": context.get("drift_blocks_commit"),
        "structured_object_count": context.get("structured_object_count"),
        "important_object_count": context.get("important_object_count"),
        "task_critical_filter_enabled": context.get("task_critical_filter_enabled"),
        "task_critical_object_count": context.get("task_critical_object_count"),
        "task_critical_important_count": context.get("task_critical_important_count"),
        "repair_constraint_mode": context.get("repair_constraint_mode"),
        "repair_objective": context.get("repair_objective"),
        "critical_source_object_count": context.get("critical_source_object_count"),
        "aligned_recovered_object_count": context.get("aligned_recovered_object_count"),
        "repair_patch_count": context.get("repair_patch_count"),
        "repair_applied_count": context.get("repair_applied_count"),
        "repair_rejected_count": context.get("repair_rejected_count"),
        "repair_object_delta": context.get("repair_object_delta"),
        "repair_enabled": context.get("repair_enabled"),
    }
