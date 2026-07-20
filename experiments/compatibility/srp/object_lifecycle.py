from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .semantic_parser import stable_semantic_object_id
from .validation_targets import SemanticContractGraph


def _index_objects(objects: List[Dict[str, object]]) -> Dict[str, Dict[str, object]]:
    indexed: Dict[str, Dict[str, object]] = {}
    for item in objects:
        if not isinstance(item, dict):
            continue
        object_type = str(item.get("type", "fact")).strip() or "fact"
        value = str(item.get("value", "")).strip()
        if not value:
            continue
        object_id = str(item.get("object_id") or item.get("id") or "").strip() or stable_semantic_object_id(object_type, value)
        indexed[object_id] = {
            "object_id": object_id,
            "type": object_type,
            "value": value,
            "confidence": item.get("confidence"),
            "evidence_pointer": item.get("evidence_pointer"),
        }
    return indexed


def _count_delta(source_map: Dict[str, Dict[str, object]], target_map: Dict[str, Dict[str, object]]) -> Dict[str, object]:
    retained = [item for object_id, item in source_map.items() if object_id in target_map]
    missing = [item for object_id, item in source_map.items() if object_id not in target_map]
    hallucinated = [item for object_id, item in target_map.items() if object_id not in source_map]
    source_count = len(source_map)
    target_count = len(target_map)
    return {
        "retained": retained,
        "missing": missing,
        "hallucinated": hallucinated,
        "object_count": target_count,
        "retained_count": len(retained),
        "missing_count": len(missing),
        "hallucinated_count": len(hallucinated),
        "source_count": source_count,
        "recall": (len(retained) / source_count) if source_count else None,
        "precision": (len(retained) / target_count) if target_count else None,
    }


def _empty_transition(source_stage: str, target_stage: str) -> Dict[str, object]:
    return {
        "source_stage": source_stage,
        "target_stage": target_stage,
        "present": False,
        "source_count": 0,
        "target_count": 0,
        "retained_count": 0,
        "missing_count": 0,
        "hallucinated_count": 0,
        "recall": None,
        "precision": None,
    }


def _empty_delta() -> Dict[str, object]:
    return {
        "retained": [],
        "missing": [],
        "hallucinated": [],
        "source_count": 0,
        "object_count": 0,
        "retained_count": 0,
        "missing_count": 0,
        "hallucinated_count": 0,
        "recall": None,
        "precision": None,
    }


def _build_transition(
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
        **_count_delta(source_map, target_map),
    }


def _build_stage_counts(
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
        "retained": [],
        "missing": [],
        "hallucinated": [],
        "object_count": len(stage_map) if present else 0,
        "raw_object_count": raw_object_count if raw_object_count is not None else (len(stage_map) if present else 0),
        "important_count": important_count,
        "task_critical_count": task_critical_count,
    }


def _extract_stage_objects(stage_payload: Dict[str, object] | None) -> List[Dict[str, object]]:
    stage_payload = stage_payload or {}
    candidates = [
        stage_payload.get("active_objects"),
        stage_payload.get("objects"),
        ((stage_payload.get("typed_representation") or {}).get("objects") if isinstance(stage_payload, dict) else None),
        (((stage_payload.get("structured_state_package") or {}).get("typed_representation") or {}).get("objects") if isinstance(stage_payload, dict) else None),
        (((stage_payload.get("recovered_state_package") or {}).get("typed_representation") or {}).get("objects") if isinstance(stage_payload, dict) else None),
        ((stage_payload.get("semantic_object_inventory") or {}).get("objects") if isinstance(stage_payload, dict) else None),
        stage_payload.get("semantic_objects"),
    ]
    for candidate in candidates:
        if isinstance(candidate, list):
            return [item for item in candidate if isinstance(item, dict)]
    return []


@dataclass
class ObjectLifecycleArtifact:
    schema_version: str = "object_lifecycle.v1"
    source: Dict[str, object] = field(default_factory=dict)
    compressed: Dict[str, object] = field(default_factory=dict)
    recovered: Dict[str, object] = field(default_factory=dict)
    repaired: Dict[str, object] = field(default_factory=dict)
    allocated: Dict[str, object] = field(default_factory=dict)
    executed: Dict[str, object] = field(default_factory=dict)
    transitions: Dict[str, object] = field(default_factory=dict)
    source_object_count: int = 0
    compressed_object_count: int = 0
    recovered_object_count: int = 0
    repaired_object_count: int = 0
    allocated_object_count: int = 0
    executed_object_count: int = 0
    lifecycle_inflation: float | None = None

    def as_dict(self) -> Dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "source": dict(self.source),
            "compressed": dict(self.compressed),
            "recovered": dict(self.recovered),
            "repaired": dict(self.repaired),
            "allocated": dict(self.allocated),
            "executed": dict(self.executed),
            "transitions": dict(self.transitions),
            "source_object_count": self.source_object_count,
            "compressed_object_count": self.compressed_object_count,
            "recovered_object_count": self.recovered_object_count,
            "repaired_object_count": self.repaired_object_count,
            "allocated_object_count": self.allocated_object_count,
            "executed_object_count": self.executed_object_count,
            "lifecycle_inflation": self.lifecycle_inflation,
        }


def build_object_lifecycle_artifact(
    source_package: Dict[str, object] | None,
    compressed_package: Dict[str, object] | None,
    recovered_package: Dict[str, object] | None,
    repaired_package: Dict[str, object] | None = None,
    validation_targets: SemanticContractGraph | None = None,
    state_allocation_result: Dict[str, object] | None = None,
    execution_payload: Dict[str, object] | None = None,
) -> ObjectLifecycleArtifact:
    source_package = source_package or {}
    compressed_package = compressed_package or {}
    recovered_package = recovered_package or {}
    repaired_package = repaired_package or {}
    state_allocation_result = state_allocation_result or {}
    execution_payload = execution_payload or {}

    source_inventory = source_package.get("semantic_object_inventory") or {}
    source_typed = source_package.get("typed_representation") or {}
    source_objects = (
        source_inventory.get("objects")
        or source_package.get("semantic_objects")
        or source_typed.get("objects")
        or []
    )
    source_map = _index_objects(list(source_objects))
    source_important_objects = source_inventory.get("important_objects") or []
    if not source_important_objects and source_package.get("runtime_metadata"):
        for object_id, metadata in dict(source_package.get("runtime_metadata") or {}).items():
            if float(metadata.get("importance", 0.0) or 0.0) >= 0.8:
                source_important_objects.append(
                    {
                        "object_id": object_id,
                        "type": metadata.get("type", "fact"),
                        "value": metadata.get("value", ""),
                        "confidence": metadata.get("confidence"),
                        "evidence_pointer": metadata.get("evidence_pointer"),
                    }
                )
    source_important_map = _index_objects(list(source_important_objects))

    compressed_objects = _extract_stage_objects(compressed_package)
    compressed_map = _index_objects(list(compressed_objects))

    recovered_objects = _extract_stage_objects(recovered_package)
    recovered_map = _index_objects(list(recovered_objects))

    repaired_present = bool(repaired_package)
    repaired_objects = _extract_stage_objects(repaired_package)
    repaired_map = _index_objects(list(repaired_objects))
    allocated_present = bool(state_allocation_result)
    allocated_objects = _extract_stage_objects(state_allocation_result)
    allocated_map = _index_objects(list(allocated_objects))
    executed_present = bool(execution_payload)
    executed_objects = _extract_stage_objects(execution_payload)
    executed_map = _index_objects(list(executed_objects))
    task_critical_count = 0
    if validation_targets is not None:
        for node in validation_targets.nodes:
            if node.role in {"clause"} and node.node_type in {"query_expectation", "constraint"}:
                task_critical_count += len(node.variants)

    if repaired_present:
        post_repair_map = repaired_map
        allocation_source_stage = "repaired"
    else:
        post_repair_map = recovered_map
        allocation_source_stage = "recovered"

    stage_counts = [
        len(source_map),
        len(compressed_map),
        len(recovered_map),
        len(repaired_map) if repaired_present else 0,
        len(allocated_map) if allocated_present else 0,
        len(executed_map) if executed_present else 0,
    ]
    source_object_count = len(source_map)
    lifecycle_inflation = (max(stage_counts) / source_object_count) if source_object_count else None

    return ObjectLifecycleArtifact(
        source={
            **_build_stage_counts(
                "source",
                source_map,
                present=True,
                raw_object_count=len(source_objects),
                important_count=len(source_important_map),
                task_critical_count=task_critical_count,
            ),
            "retained": list(source_map.values()),
            "missing": [],
            "hallucinated": [],
            "object_count": len(source_map),
            "important_count": len(source_important_map),
            "task_critical_count": task_critical_count,
            "retained_count": len(source_map),
            "missing_count": 0,
            "hallucinated_count": 0,
            "source_count": len(source_map),
            "recall": 1.0 if source_map else None,
            "precision": 1.0 if source_map else None,
        },
        compressed={
            **_build_stage_counts("compressed", compressed_map, present=True, raw_object_count=len(compressed_objects)),
            **_count_delta(source_map, compressed_map),
            "compressed_object_count": len(compressed_map),
        },
        recovered={
            **_build_stage_counts("recovered", recovered_map, present=True, raw_object_count=len(recovered_objects)),
            **_count_delta(compressed_map, recovered_map),
            "recovered_object_count": len(recovered_map),
        },
        repaired={
            **_build_stage_counts("repaired", repaired_map, present=repaired_present, raw_object_count=len(repaired_objects)),
            **(_count_delta(recovered_map, repaired_map) if repaired_present else _empty_delta()),
            "repaired_object_count": len(repaired_map) if repaired_present else 0,
        },
        allocated={
            **_build_stage_counts("allocated", allocated_map, present=allocated_present, raw_object_count=len(allocated_objects)),
            **(_count_delta(post_repair_map, allocated_map) if allocated_present else _empty_delta()),
            "allocated_object_count": len(allocated_map) if allocated_present else 0,
        },
        executed={
            **_build_stage_counts("executed", executed_map, present=executed_present, raw_object_count=len(executed_objects)),
            **(_count_delta(allocated_map if allocated_present else post_repair_map, executed_map) if executed_present else _empty_delta()),
            "executed_object_count": len(executed_map) if executed_present else 0,
        },
        transitions={
            "source_to_compressed": _build_transition("source", "compressed", source_map, compressed_map, present=True),
            "compressed_to_recovered": _build_transition("compressed", "recovered", compressed_map, recovered_map, present=True),
            "recovered_to_repaired": _build_transition("recovered", "repaired", recovered_map, repaired_map, present=repaired_present),
            "repaired_to_allocated": _build_transition("repaired", "allocated", repaired_map, allocated_map, present=repaired_present and allocated_present),
            "recovered_to_allocated": _build_transition("recovered", "allocated", recovered_map, allocated_map, present=(not repaired_present) and allocated_present),
            "allocated_to_executed": _build_transition("allocated", "executed", allocated_map, executed_map, present=allocated_present and executed_present),
            "repaired_to_executed": _build_transition("repaired", "executed", repaired_map, executed_map, present=repaired_present and executed_present),
            "recovered_to_executed": _build_transition("recovered", "executed", recovered_map, executed_map, present=(not repaired_present) and executed_present),
            "source_to_recovered": _build_transition("source", "recovered", source_map, recovered_map, present=True),
            "source_to_repaired": _build_transition("source", "repaired", source_map, repaired_map, present=repaired_present),
            "source_to_allocated": _build_transition("source", "allocated", source_map, allocated_map, present=allocated_present),
            "source_to_executed": _build_transition("source", "executed", source_map, executed_map, present=executed_present),
        },
        source_object_count=source_object_count,
        compressed_object_count=len(compressed_map),
        recovered_object_count=len(recovered_map),
        repaired_object_count=len(repaired_map) if repaired_present else 0,
        allocated_object_count=len(allocated_map) if allocated_present else 0,
        executed_object_count=len(executed_map) if executed_present else 0,
        lifecycle_inflation=lifecycle_inflation,
    )
