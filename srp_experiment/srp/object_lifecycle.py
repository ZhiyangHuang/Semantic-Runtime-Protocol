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


@dataclass
class ObjectLifecycleArtifact:
    schema_version: str = "object_lifecycle.v1"
    source: Dict[str, object] = field(default_factory=dict)
    compressed: Dict[str, object] = field(default_factory=dict)
    recovered: Dict[str, object] = field(default_factory=dict)
    repaired: Dict[str, object] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "source": dict(self.source),
            "compressed": dict(self.compressed),
            "recovered": dict(self.recovered),
            "repaired": dict(self.repaired),
        }


def build_object_lifecycle_artifact(
    source_package: Dict[str, object] | None,
    compressed_package: Dict[str, object] | None,
    recovered_package: Dict[str, object] | None,
    repaired_package: Dict[str, object] | None = None,
    validation_targets: SemanticContractGraph | None = None,
) -> ObjectLifecycleArtifact:
    source_package = source_package or {}
    compressed_package = compressed_package or {}
    recovered_package = recovered_package or {}
    repaired_package = repaired_package or {}

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

    compressed_inventory = compressed_package.get("semantic_object_inventory") or {}
    compressed_objects = compressed_inventory.get("objects") or compressed_package.get("semantic_objects") or []
    compressed_map = _index_objects(list(compressed_objects))

    recovered_state = recovered_package.get("typed_representation") or {}
    recovered_objects = recovered_state.get("objects") or []
    recovered_map = _index_objects(list(recovered_objects))

    repaired_state = repaired_package.get("typed_representation") or {}
    repaired_objects = repaired_state.get("objects") or []
    repaired_map = _index_objects(list(repaired_objects))
    task_critical_count = 0
    if validation_targets is not None:
        for node in validation_targets.nodes:
            if node.role in {"clause"} and node.node_type in {"query_expectation", "constraint"}:
                task_critical_count += len(node.variants)

    return ObjectLifecycleArtifact(
        source={
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
            **_count_delta(source_map, compressed_map),
            "compressed_object_count": len(compressed_map),
        },
        recovered={
            **_count_delta(compressed_map, recovered_map),
            "recovered_object_count": len(recovered_map),
        },
        repaired={
            **_count_delta(recovered_map, repaired_map),
            "repaired_object_count": len(repaired_map),
        },
    )
