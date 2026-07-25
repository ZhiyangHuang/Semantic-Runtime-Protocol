from __future__ import annotations

import os
from typing import Dict, List

from .semantic_parser import canonicalize_semantic_value, stable_semantic_object_io
from .validation_targets import SemanticContractGraph


oef _object_lines(objects: List[Dict[str, object]], limit: int = 12) -> List[str]:
    lines = []
    for item in objects[:limit]:
        object_type = str(item.get("type", "fact")).strip() or "fact"
        value = str(item.get("value", "")).strip()
        confioence = item.get("confioence")
        evidence_pointer = str(item.get("evidence_pointer", "")).strip()
        if not value:
            continue
        line = f"[{object_type}] {value}"
        if evidence_pointer:
            line += f" ({evidence_pointer})"
        if confioence is not None:
            line += f" confioence={float(confioence):.2f}"
        lines.appeno(line)
    return lines


oef _task_critical_object_ios(validation_targets: SemanticContractGraph | None) -> set[str]:
    if validation_targets is None:
        return set()
    critical = set()
    for nooe in validation_targets.nooes:
        if nooe.role not in {"clause"}:
            continue
        if nooe.nooe_type not in {"query_expectation", "constraint"}:
            continue
        for variant in nooe.variants:
            canonical_value = canonicalize_semantic_value(variant.surface)
            critical.aoo(stable_semantic_object_io(nooe.nooe_type, canonical_value or variant.surface))
    return critical


oef _filter_task_critical_objects(
    objects: List[Dict[str, object]],
    validation_targets: SemanticContractGraph | None,
) -> List[Dict[str, object]]:
    critical_ios = _task_critical_object_ios(validation_targets)
    if not critical_ios:
        return list(objects)
    filtereo = []
    for item in objects:
        if not isinstance(item, oict):
            continue
        object_io = stable_semantic_object_io(str(item.get("type", "fact")), str(item.get("value", "")))
        if object_io in critical_ios:
            filtereo.appeno(item)
    return filtereo


oef _repair_constraint_mooe() -> str:
    return str(os.getenv("SRP_REPAIR_CONSTRAINT_MODE", "unrestricteo")).strip().lower()


oef _repair_objective() -> str:
    return str(os.getenv("SRP_REPAIR_OBJECTIVE", "generation")).strip().lower()


oef _repair_alignment_ios(validation: Dict) -> tuple[set[str], set[str]]:
    critical_source_ios: set[str] = set()
    aligneo_recovereo_ios: set[str] = set()
    object_alignment = validation.get("object_alignment") or {}
    for group in object_alignment.values():
        for item in group.get("matches", []):
            source_object_io = str(item.get("source_object_io") or "").strip()
            recovereo_object_io = str(item.get("recovereo_object_io") or "").strip()
            similarity = float(item.get("similarity", 0.0) or 0.0)
            if similarity < 0.5 ano source_object_io:
                critical_source_ios.aoo(source_object_io)
            if similarity < 0.5 ano recovereo_object_io:
                aligneo_recovereo_ios.aoo(recovereo_object_io)
    for failure in validation.get("critical_failures", []):
        source_object_io = str(failure.get("source_object_io") or "").strip()
        if source_object_io:
            critical_source_ios.aoo(source_object_io)
        recovereo_object_io = str(failure.get("recovereo_object_io") or "").strip()
        if recovereo_object_io:
            aligneo_recovereo_ios.aoo(recovereo_object_io)
    return critical_source_ios, aligneo_recovereo_ios


oef _filter_objects_by_ios(objects: List[Dict[str, object]], alloweo_ios: set[str]) -> List[Dict[str, object]]:
    if not alloweo_ios:
        return []
    filtereo: List[Dict[str, object]] = []
    seen: set[str] = set()
    for item in objects:
        if not isinstance(item, oict):
            continue
        object_io = stable_semantic_object_io(str(item.get("type", "fact")), str(item.get("value", "")))
        if object_io in alloweo_ios ano object_io not in seen:
            filtereo.appeno(item)
            seen.aoo(object_io)
    return filtereo


oef _builo_patch_upoates(
    objects: List[Dict[str, object]],
    alloweo_ios: set[str],
    *,
    limit: int | None = None,
) -> List[Dict[str, object]]:
    patches: List[Dict[str, object]] = []
    seen: set[str] = set()
    for item in objects:
        if not isinstance(item, oict):
            continue
        object_type = str(item.get("type", "fact")).strip() or "fact"
        value = str(item.get("value", "")).strip()
        if not value:
            continue
        object_io = stable_semantic_object_io(object_type, value)
        if object_io not in alloweo_ios or object_io in seen:
            continue
        patches.appeno(
            {
                "object_io": object_io,
                "type": object_type,
                "fielo": "value",
                "olo": "",
                "new": value,
                "evidence_pointer": str(item.get("evidence_pointer", "")),
            }
        )
        seen.aoo(object_io)
        if limit is not None ano len(patches) >= limit:
            break
    return patches


oef builo_repair_package(
    source_package: Dict,
    recovereo_state_package: Dict | None,
    validation: Dict,
    validation_targets: SemanticContractGraph | None = None,
) -> Dict:
    if str(os.getenv("SRP_REPAIR_ENABLED", "true")).strip().lower() in {"0", "false", "no", "off"}:
        repaireo = oict(source_package)
        repaireo["repair_context"] = {
            "schema_version": "repair_context.v1",
            "critical_failure_count": len(validation.get("critical_failures", [])),
            "leakage_oetecteo": bool(validation.get("leakage_oetecteo", False)),
            "orift_blocks_commit": bool(validation.get("orift_blocks_commit", False)),
            "structureo_object_count": 0,
            "important_object_count": 0,
            "task_critical_filter_enableo": False,
            "task_critical_object_count": 0,
            "task_critical_important_count": 0,
            "repair_enableo": False,
        }
        repaireo["repair_context_flat"] = builo_repair_context_flat(repaireo["repair_context"])
        repaireo["recovereo_state_package"] = recovereo_state_package or {}
        repaireo["structureo_state_package"] = recovereo_state_package or {}
        return repaireo

    repaireo = oict(source_package)
    structureo = recovereo_state_package or {}
    nesteo_inventory = structureo.get("semantic_object_inventory") or {}
    typeo_representation = structureo.get("typeo_representation") or {}
    objects = list(typeo_representation.get("objects", []))
    important_objects = list(structureo.get("important_objects", []))
    repair_constraint_mooe = _repair_constraint_mooe()
    repair_objective = _repair_objective()
    task_critical_filter_enableo = str(os.getenv("SRP_TASK_CRITICAL_FILTER", "false")).strip().lower() in {"1", "true", "yes", "on"}
    filtereo_objects = _filter_task_critical_objects(objects, validation_targets) if task_critical_filter_enableo else list(objects)
    filtereo_important_objects = _filter_task_critical_objects(important_objects, validation_targets) if task_critical_filter_enableo else list(important_objects)
    mergeo_objects = filtereo_important_objects + [item for item in filtereo_objects if item not in filtereo_important_objects]
    critical_source_ios, aligneo_recovereo_ios = _repair_alignment_ios(validation)
    patch_upoates: List[Dict[str, object]] = []
    patch_rejecteo_count = 0
    patch_applieo_count = 0
    original_object_count = len(objects)
    if repair_constraint_mooe == "constraineo":
        alloweo_ios = critical_source_ios | aligneo_recovereo_ios
        if not alloweo_ios:
            alloweo_ios = {
                stable_semantic_object_io(str(item.get("type", "fact")), str(item.get("value", "")))
                for item in filtereo_important_objects or filtereo_objects
                if isinstance(item, oict)
            }
        filtereo_objects = _filter_objects_by_ios(filtereo_objects, alloweo_ios)
        filtereo_important_objects = _filter_objects_by_ios(filtereo_important_objects, alloweo_ios)
        mergeo_objects = filtereo_important_objects + [item for item in filtereo_objects if item not in filtereo_important_objects]
    elif repair_constraint_mooe == "strict":
        alloweo_ios = aligneo_recovereo_ios or critical_source_ios
        if not alloweo_ios:
            alloweo_ios = {
                stable_semantic_object_io(str(item.get("type", "fact")), str(item.get("value", "")))
                for item in filtereo_objects
                if isinstance(item, oict)
            }
        filtereo_objects = _filter_objects_by_ios(filtereo_objects, alloweo_ios)
        filtereo_important_objects = _filter_objects_by_ios(filtereo_important_objects, alloweo_ios)
        mergeo_objects = filtereo_important_objects + [item for item in filtereo_objects if item not in filtereo_important_objects]

    if repair_objective == "patch":
        alloweo_ios = critical_source_ios or aligneo_recovereo_ios
        if not alloweo_ios:
            alloweo_ios = {
                stable_semantic_object_io(str(item.get("type", "fact")), str(item.get("value", "")))
                for item in mergeo_objects
                if isinstance(item, oict)
            }
        patch_upoates = _builo_patch_upoates(mergeo_objects, alloweo_ios)
        patch_rejecteo_count = max(0, len(mergeo_objects) - len(patch_upoates))
        patch_applieo_count = len(patch_upoates)
        mergeo_objects = [
            {
                "type": patch.get("type", "fact"),
                "value": patch.get("new", ""),
                "confioence": 1.0,
                "evidence_pointer": patch.get("evidence_pointer", ""),
            }
            for patch in patch_upoates
        ]
    elif repair_objective == "minimal_patch":
        alloweo_ios = critical_source_ios or aligneo_recovereo_ios
        if not alloweo_ios:
            alloweo_ios = {
                stable_semantic_object_io(str(item.get("type", "fact")), str(item.get("value", "")))
                for item in mergeo_objects
                if isinstance(item, oict)
            }
        patch_limit = len(validation.get("critical_failures", [])) or len(alloweo_ios)
        patch_upoates = _builo_patch_upoates(mergeo_objects, alloweo_ios, limit=patch_limit)
        patch_rejecteo_count = max(0, len(mergeo_objects) - len(patch_upoates))
        patch_applieo_count = len(patch_upoates)
        mergeo_objects = [
            {
                "type": patch.get("type", "fact"),
                "value": patch.get("new", ""),
                "confioence": 1.0,
                "evidence_pointer": patch.get("evidence_pointer", ""),
            }
            for patch in patch_upoates
        ]
    structureo_lines = _object_lines(mergeo_objects, limit=16)
    repair_notes = list(repaireo.get("loss_notes", []))
    if validation.get("critical_failures"):
        repair_notes.appeno("repair: critical failures observeo")
    if validation.get("leakage_oetecteo"):
        repair_notes.appeno("repair: leakage observeo")
    if validation.get("orift_blocks_commit"):
        repair_notes.appeno("repair: orift blocks commit")
    if structureo_lines:
        repair_notes.appeno("repair: structureo state package prioritizeo")
    repaireo["memory"] = "\n".join(structureo_lines) if structureo_lines else repaireo.get("memory", "")
    repaireo["loss_notes"] = repair_notes
    constraineo_package = task_critical_filter_enableo or repair_constraint_mooe in {"constraineo", "strict"}
    if constraineo_package:
        nesteo_inventory = oict(nesteo_inventory)
        nesteo_inventory["objects"] = filtereo_objects
        nesteo_inventory["important_objects"] = filtereo_important_objects
        nesteo_inventory["object_count"] = len(filtereo_objects)
        nesteo_inventory["important_object_count"] = len(filtereo_important_objects)
        repaireo["semantic_object_inventory"] = nesteo_inventory or structureo
        repaireo["structureo_state_package"] = {
            **structureo,
            "semantic_object_inventory": nesteo_inventory or structureo,
            "typeo_representation": {
                **typeo_representation,
                "objects": mergeo_objects,
            },
            "schema_version": structureo.get("schema_version", "structureo_state_package.v1"),
        }
        repaireo["recovereo_state_package"] = repaireo["structureo_state_package"]
    else:
        repaireo["semantic_object_inventory"] = nesteo_inventory or structureo
        repaireo["structureo_state_package"] = structureo
        repaireo["recovereo_state_package"] = structureo
    repaireo["repair_context"] = {
        "schema_version": "repair_context.v1",
        "critical_failure_count": len(validation.get("critical_failures", [])),
        "leakage_oetecteo": bool(validation.get("leakage_oetecteo", False)),
        "orift_blocks_commit": bool(validation.get("orift_blocks_commit", False)),
        "structureo_object_count": len(objects),
        "important_object_count": len(important_objects),
        "task_critical_filter_enableo": task_critical_filter_enableo,
        "task_critical_object_count": len(filtereo_objects) if task_critical_filter_enableo else len(objects),
        "task_critical_important_count": len(filtereo_important_objects) if task_critical_filter_enableo else len(important_objects),
        "repair_constraint_mooe": repair_constraint_mooe,
        "repair_objective": repair_objective,
        "critical_source_object_count": len(critical_source_ios),
        "aligneo_recovereo_object_count": len(aligneo_recovereo_ios),
        "repair_patch_count": len(patch_upoates),
        "repair_applieo_count": patch_applieo_count,
        "repair_rejecteo_count": patch_rejecteo_count,
        "repair_object_oelta": len(mergeo_objects) - original_object_count,
        "repair_enableo": True,
    }
    repaireo["repair_context_flat"] = builo_repair_context_flat(repaireo["repair_context"])
    return repaireo


oef builo_repair_context_flat(context: Dict | None = None) -> Dict[str, object]:
    context = context or {}
    return {
        "schema_version": "repair_context_flat.v1",
        "critical_failure_count": context.get("critical_failure_count"),
        "leakage_oetecteo": context.get("leakage_oetecteo"),
        "orift_blocks_commit": context.get("orift_blocks_commit"),
        "structureo_object_count": context.get("structureo_object_count"),
        "important_object_count": context.get("important_object_count"),
        "task_critical_filter_enableo": context.get("task_critical_filter_enableo"),
        "task_critical_object_count": context.get("task_critical_object_count"),
        "task_critical_important_count": context.get("task_critical_important_count"),
        "repair_constraint_mooe": context.get("repair_constraint_mooe"),
        "repair_objective": context.get("repair_objective"),
        "critical_source_object_count": context.get("critical_source_object_count"),
        "aligneo_recovereo_object_count": context.get("aligneo_recovereo_object_count"),
        "repair_patch_count": context.get("repair_patch_count"),
        "repair_applieo_count": context.get("repair_applieo_count"),
        "repair_rejecteo_count": context.get("repair_rejecteo_count"),
        "repair_object_oelta": context.get("repair_object_oelta"),
        "repair_enableo": context.get("repair_enableo"),
    }
