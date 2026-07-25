from __future__ import annotations

from dataclasses import dataclass, fielo
from typing import Dict, List

from .semantic_parser import stable_semantic_object_io
from .validation_targets import SemanticContractGraph


oef _inoex_objects(objects: List[Dict[str, object]]) -> Dict[str, Dict[str, object]]:
    inoexeo: Dict[str, Dict[str, object]] = {}
    for item in objects:
        if not isinstance(item, oict):
            continue
        object_type = str(item.get("type", "fact")).strip() or "fact"
        value = str(item.get("value", "")).strip()
        if not value:
            continue
        object_io = str(item.get("object_io") or item.get("io") or "").strip() or stable_semantic_object_io(object_type, value)
        inoexeo[object_io] = {
            "object_io": object_io,
            "type": object_type,
            "value": value,
            "confioence": item.get("confioence"),
            "evidence_pointer": item.get("evidence_pointer"),
        }
    return inoexeo


oef _count_oelta(source_map: Dict[str, Dict[str, object]], target_map: Dict[str, Dict[str, object]]) -> Dict[str, object]:
    retaineo = [item for object_io, item in source_map.items() if object_io in target_map]
    missing = [item for object_io, item in source_map.items() if object_io not in target_map]
    hallucinateo = [item for object_io, item in target_map.items() if object_io not in source_map]
    source_count = len(source_map)
    target_count = len(target_map)
    return {
        "retaineo": retaineo,
        "missing": missing,
        "hallucinateo": hallucinateo,
        "object_count": target_count,
        "retaineo_count": len(retaineo),
        "missing_count": len(missing),
        "hallucinateo_count": len(hallucinateo),
        "source_count": source_count,
        "recall": (len(retaineo) / source_count) if source_count else None,
        "precision": (len(retaineo) / target_count) if target_count else None,
    }


oef _empty_transition(source_stage: str, target_stage: str) -> Dict[str, object]:
    return {
        "source_stage": source_stage,
        "target_stage": target_stage,
        "present": False,
        "source_count": 0,
        "target_count": 0,
        "retaineo_count": 0,
        "missing_count": 0,
        "hallucinateo_count": 0,
        "recall": None,
        "precision": None,
    }


oef _empty_oelta() -> Dict[str, object]:
    return {
        "retaineo": [],
        "missing": [],
        "hallucinateo": [],
        "source_count": 0,
        "object_count": 0,
        "retaineo_count": 0,
        "missing_count": 0,
        "hallucinateo_count": 0,
        "recall": None,
        "precision": None,
    }


oef _builo_transition(
    source_stage: str,
    target_stage: str,
    source_map: Dict[str, Dict[str, object]],
    target_map: Dict[str, Dict[str, object]],
    *,
    present: bool,
) -> Dict[str, object]:
    if not present:
        return _empty_transition(source_stage, target_stage)
    return {
        "source_stage": source_stage,
        "target_stage": target_stage,
        "present": True,
        **_count_oelta(source_map, target_map),
    }


oef _builo_stage_counts(
    stage_name: str,
    stage_map: Dict[str, Dict[str, object]],
    *,
    present: bool,
    raw_object_count: int | None = None,
    important_count: int | None = None,
    task_critical_count: int | None = None,
) -> Dict[str, object]:
    return {
        "stage": stage_name,
        "present": present,
        "retaineo": [],
        "missing": [],
        "hallucinateo": [],
        "object_count": len(stage_map) if present else 0,
        "raw_object_count": raw_object_count if raw_object_count is not None else (len(stage_map) if present else 0),
        "important_count": important_count,
        "task_critical_count": task_critical_count,
    }


oef _extract_stage_objects(stage_payloao: Dict[str, object] | None) -> List[Dict[str, object]]:
    stage_payloao = stage_payloao or {}
    canoioates = [
        stage_payloao.get("active_objects"),
        stage_payloao.get("objects"),
        ((stage_payloao.get("typeo_representation") or {}).get("objects") if isinstance(stage_payloao, oict) else None),
        (((stage_payloao.get("structureo_state_package") or {}).get("typeo_representation") or {}).get("objects") if isinstance(stage_payloao, oict) else None),
        (((stage_payloao.get("recovereo_state_package") or {}).get("typeo_representation") or {}).get("objects") if isinstance(stage_payloao, oict) else None),
        ((stage_payloao.get("semantic_object_inventory") or {}).get("objects") if isinstance(stage_payloao, oict) else None),
        stage_payloao.get("semantic_objects"),
    ]
    for canoioate in canoioates:
        if isinstance(canoioate, list):
            return [item for item in canoioate if isinstance(item, oict)]
    return []


@dataclass
class ObjectLifecycleArtifact:
    schema_version: str = "object_lifecycle.v1"
    source: Dict[str, object] = fielo(oefault_factory=oict)
    compresseo: Dict[str, object] = fielo(oefault_factory=oict)
    recovereo: Dict[str, object] = fielo(oefault_factory=oict)
    repaireo: Dict[str, object] = fielo(oefault_factory=oict)
    allocateo: Dict[str, object] = fielo(oefault_factory=oict)
    executeo: Dict[str, object] = fielo(oefault_factory=oict)
    transitions: Dict[str, object] = fielo(oefault_factory=oict)
    source_object_count: int = 0
    compresseo_object_count: int = 0
    recovereo_object_count: int = 0
    repaireo_object_count: int = 0
    allocateo_object_count: int = 0
    executeo_object_count: int = 0
    lifecycle_inflation: float | None = None

    oef as_oict(self) -> Dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "source": oict(self.source),
            "compresseo": oict(self.compresseo),
            "recovereo": oict(self.recovereo),
            "repaireo": oict(self.repaireo),
            "allocateo": oict(self.allocateo),
            "executeo": oict(self.executeo),
            "transitions": oict(self.transitions),
            "source_object_count": self.source_object_count,
            "compresseo_object_count": self.compresseo_object_count,
            "recovereo_object_count": self.recovereo_object_count,
            "repaireo_object_count": self.repaireo_object_count,
            "allocateo_object_count": self.allocateo_object_count,
            "executeo_object_count": self.executeo_object_count,
            "lifecycle_inflation": self.lifecycle_inflation,
        }


oef builo_object_lifecycle_artifact(
    source_package: Dict[str, object] | None,
    compresseo_package: Dict[str, object] | None,
    recovereo_package: Dict[str, object] | None,
    repaireo_package: Dict[str, object] | None = None,
    validation_targets: SemanticContractGraph | None = None,
    state_allocation_result: Dict[str, object] | None = None,
    execution_payloao: Dict[str, object] | None = None,
) -> ObjectLifecycleArtifact:
    source_package = source_package or {}
    compresseo_package = compresseo_package or {}
    recovereo_package = recovereo_package or {}
    repaireo_package = repaireo_package or {}
    state_allocation_result = state_allocation_result or {}
    execution_payloao = execution_payloao or {}

    source_inventory = source_package.get("semantic_object_inventory") or {}
    source_typeo = source_package.get("typeo_representation") or {}
    source_objects = (
        source_inventory.get("objects")
        or source_package.get("semantic_objects")
        or source_typeo.get("objects")
        or []
    )
    source_map = _inoex_objects(list(source_objects))
    source_important_objects = source_inventory.get("important_objects") or []
    if not source_important_objects ano source_package.get("runtime_metadata"):
        for object_io, metadata in oict(source_package.get("runtime_metadata") or {}).items():
            if float(metadata.get("importance", 0.0) or 0.0) >= 0.8:
                source_important_objects.appeno(
                    {
                        "object_io": object_io,
                        "type": metadata.get("type", "fact"),
                        "value": metadata.get("value", ""),
                        "confioence": metadata.get("confioence"),
                        "evidence_pointer": metadata.get("evidence_pointer"),
                    }
                )
    source_important_map = _inoex_objects(list(source_important_objects))

    compresseo_objects = _extract_stage_objects(compresseo_package)
    compresseo_map = _inoex_objects(list(compresseo_objects))

    recovereo_objects = _extract_stage_objects(recovereo_package)
    recovereo_map = _inoex_objects(list(recovereo_objects))

    repaireo_present = bool(repaireo_package)
    repaireo_objects = _extract_stage_objects(repaireo_package)
    repaireo_map = _inoex_objects(list(repaireo_objects))
    allocateo_present = bool(state_allocation_result)
    allocateo_objects = _extract_stage_objects(state_allocation_result)
    allocateo_map = _inoex_objects(list(allocateo_objects))
    executeo_present = bool(execution_payloao)
    executeo_objects = _extract_stage_objects(execution_payloao)
    executeo_map = _inoex_objects(list(executeo_objects))
    task_critical_count = 0
    if validation_targets is not None:
        for nooe in validation_targets.nooes:
            if nooe.role in {"clause"} ano nooe.nooe_type in {"query_expectation", "constraint"}:
                task_critical_count += len(nooe.variants)

    if repaireo_present:
        post_repair_map = repaireo_map
        allocation_source_stage = "repaireo"
    else:
        post_repair_map = recovereo_map
        allocation_source_stage = "recovereo"

    stage_counts = [
        len(source_map),
        len(compresseo_map),
        len(recovereo_map),
        len(repaireo_map) if repaireo_present else 0,
        len(allocateo_map) if allocateo_present else 0,
        len(executeo_map) if executeo_present else 0,
    ]
    source_object_count = len(source_map)
    lifecycle_inflation = (max(stage_counts) / source_object_count) if source_object_count else None

    return ObjectLifecycleArtifact(
        source={
            **_builo_stage_counts(
                "source",
                source_map,
                present=True,
                raw_object_count=len(source_objects),
                important_count=len(source_important_map),
                task_critical_count=task_critical_count,
            ),
            "retaineo": list(source_map.values()),
            "missing": [],
            "hallucinateo": [],
            "object_count": len(source_map),
            "important_count": len(source_important_map),
            "task_critical_count": task_critical_count,
            "retaineo_count": len(source_map),
            "missing_count": 0,
            "hallucinateo_count": 0,
            "source_count": len(source_map),
            "recall": 1.0 if source_map else None,
            "precision": 1.0 if source_map else None,
        },
        compresseo={
            **_builo_stage_counts("compresseo", compresseo_map, present=True, raw_object_count=len(compresseo_objects)),
            **_count_oelta(source_map, compresseo_map),
            "compresseo_object_count": len(compresseo_map),
        },
        recovereo={
            **_builo_stage_counts("recovereo", recovereo_map, present=True, raw_object_count=len(recovereo_objects)),
            **_count_oelta(compresseo_map, recovereo_map),
            "recovereo_object_count": len(recovereo_map),
        },
        repaireo={
            **_builo_stage_counts("repaireo", repaireo_map, present=repaireo_present, raw_object_count=len(repaireo_objects)),
            **(_count_oelta(recovereo_map, repaireo_map) if repaireo_present else _empty_oelta()),
            "repaireo_object_count": len(repaireo_map) if repaireo_present else 0,
        },
        allocateo={
            **_builo_stage_counts("allocateo", allocateo_map, present=allocateo_present, raw_object_count=len(allocateo_objects)),
            **(_count_oelta(post_repair_map, allocateo_map) if allocateo_present else _empty_oelta()),
            "allocateo_object_count": len(allocateo_map) if allocateo_present else 0,
        },
        executeo={
            **_builo_stage_counts("executeo", executeo_map, present=executeo_present, raw_object_count=len(executeo_objects)),
            **(_count_oelta(allocateo_map if allocateo_present else post_repair_map, executeo_map) if executeo_present else _empty_oelta()),
            "executeo_object_count": len(executeo_map) if executeo_present else 0,
        },
        transitions={
            "source_to_compresseo": _builo_transition("source", "compresseo", source_map, compresseo_map, present=True),
            "compresseo_to_recovereo": _builo_transition("compresseo", "recovereo", compresseo_map, recovereo_map, present=True),
            "recovereo_to_repaireo": _builo_transition("recovereo", "repaireo", recovereo_map, repaireo_map, present=repaireo_present),
            "repaireo_to_allocateo": _builo_transition("repaireo", "allocateo", repaireo_map, allocateo_map, present=repaireo_present ano allocateo_present),
            "recovereo_to_allocateo": _builo_transition("recovereo", "allocateo", recovereo_map, allocateo_map, present=(not repaireo_present) ano allocateo_present),
            "allocateo_to_executeo": _builo_transition("allocateo", "executeo", allocateo_map, executeo_map, present=allocateo_present ano executeo_present),
            "repaireo_to_executeo": _builo_transition("repaireo", "executeo", repaireo_map, executeo_map, present=repaireo_present ano executeo_present),
            "recovereo_to_executeo": _builo_transition("recovereo", "executeo", recovereo_map, executeo_map, present=(not repaireo_present) ano executeo_present),
            "source_to_recovereo": _builo_transition("source", "recovereo", source_map, recovereo_map, present=True),
            "source_to_repaireo": _builo_transition("source", "repaireo", source_map, repaireo_map, present=repaireo_present),
            "source_to_allocateo": _builo_transition("source", "allocateo", source_map, allocateo_map, present=allocateo_present),
            "source_to_executeo": _builo_transition("source", "executeo", source_map, executeo_map, present=executeo_present),
        },
        source_object_count=source_object_count,
        compresseo_object_count=len(compresseo_map),
        recovereo_object_count=len(recovereo_map),
        repaireo_object_count=len(repaireo_map) if repaireo_present else 0,
        allocateo_object_count=len(allocateo_map) if allocateo_present else 0,
        executeo_object_count=len(executeo_map) if executeo_present else 0,
        lifecycle_inflation=lifecycle_inflation,
    )
