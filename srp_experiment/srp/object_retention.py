from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .semantic_parser import canonicalize_semantic_value, stable_semantic_object_id
from .validation_targets import SemanticContractGraph


@dataclass
class ObjectRetentionBreakdown:
    schema_version: str
    retained: List[Dict[str, object]] = field(default_factory=list)
    missing: List[Dict[str, object]] = field(default_factory=list)
    hallucinated: List[Dict[str, object]] = field(default_factory=list)

    def as_dict(self) -> Dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "retained": list(self.retained),
            "missing": list(self.missing),
            "hallucinated": list(self.hallucinated),
            "retained_count": len(self.retained),
            "missing_count": len(self.missing),
            "hallucinated_count": len(self.hallucinated),
        }


@dataclass
class ObjectRetentionBreakdownV2:
    schema_version: str
    important: Dict[str, object] = field(default_factory=dict)
    all_objects: Dict[str, object] = field(default_factory=dict)
    task_critical: Dict[str, object] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "important": dict(self.important),
            "all_objects": dict(self.all_objects),
            "task_critical": dict(self.task_critical),
        }


def _index_objects(objects: List[Dict[str, object]]) -> Dict[str, Dict[str, object]]:
    indexed: Dict[str, Dict[str, object]] = {}
    for item in objects:
        if not isinstance(item, dict):
            continue
        object_id = str(item.get("object_id") or item.get("id") or "").strip()
        if not object_id:
            continue
        indexed[object_id] = dict(item)
    return indexed


def _counts(retained: List[Dict[str, object]], missing: List[Dict[str, object]], hallucinated: List[Dict[str, object]]) -> Dict[str, object]:
    source_total = len(retained) + len(missing)
    recovered_total = len(retained) + len(hallucinated)
    recall = (len(retained) / source_total) if source_total else None
    precision = (len(retained) / recovered_total) if recovered_total else None
    inflation_ratio = (recovered_total / source_total) if source_total else None
    return {
        "retained": list(retained),
        "missing": list(missing),
        "hallucinated": list(hallucinated),
        "retained_count": len(retained),
        "missing_count": len(missing),
        "hallucinated_count": len(hallucinated),
        "source_count": source_total,
        "recovered_count": recovered_total,
        "recall": recall,
        "precision": precision,
        "inflation_ratio": inflation_ratio,
    }


def build_object_retention_breakdown(
    source_inventory: Dict[str, object] | None,
    recovered_package: Dict[str, object] | None,
) -> ObjectRetentionBreakdown:
    source_inventory = source_inventory or {}
    recovered_package = recovered_package or {}
    source_objects = _index_objects(list(source_inventory.get("important_objects", [])))
    recovered_typed = recovered_package.get("typed_representation") or {}
    recovered_objects = _index_objects(
        [
            {
                "object_id": stable_semantic_object_id(str(item.get("type", "fact")), str(item.get("value", ""))),
                "type": item.get("type", "fact"),
                "value": item.get("value", ""),
                "confidence": item.get("confidence", 0.0),
                "evidence_pointer": item.get("evidence_pointer", ""),
            }
            for item in list(recovered_typed.get("objects", []))
            if isinstance(item, dict)
        ]
    )

    retained: List[Dict[str, object]] = []
    missing: List[Dict[str, object]] = []
    hallucinated: List[Dict[str, object]] = []

    for object_id, source_object in source_objects.items():
        if object_id in recovered_objects:
            retained.append(
                {
                    "object_id": object_id,
                    "type": source_object.get("type"),
                    "value": source_object.get("value"),
                    "confidence": source_object.get("confidence"),
                    "evidence_pointer": source_object.get("evidence_pointer"),
                }
            )
        else:
            missing.append(
                {
                    "object_id": object_id,
                    "type": source_object.get("type"),
                    "value": source_object.get("value"),
                    "confidence": source_object.get("confidence"),
                    "evidence_pointer": source_object.get("evidence_pointer"),
                }
            )

    for object_id, recovered_object in recovered_objects.items():
        if object_id not in source_objects:
            hallucinated.append(
                {
                    "object_id": object_id,
                    "type": recovered_object.get("type"),
                    "value": recovered_object.get("value"),
                    "confidence": recovered_object.get("confidence"),
                    "evidence_pointer": recovered_object.get("evidence_pointer"),
                }
            )

    return ObjectRetentionBreakdown(
        schema_version="object_retention_breakdown.v1",
        retained=retained,
        missing=missing,
        hallucinated=hallucinated,
    )


def _contract_objects(validation_targets: SemanticContractGraph | None) -> Tuple[Dict[str, Dict[str, object]], Dict[str, Dict[str, object]]]:
    if validation_targets is None:
        return {}, {}
    clauses: Dict[str, Dict[str, object]] = {}
    critical: Dict[str, Dict[str, object]] = {}
    for node in validation_targets.nodes:
        if node.role not in {"clause", "root"}:
            continue
        if node.role == "root":
            continue
        for variant in node.variants:
            canonical_value = canonicalize_semantic_value(variant.surface)
            object_id = stable_semantic_object_id(node.node_type, canonical_value or variant.surface)
            entry = {
                "object_id": object_id,
                "type": node.node_type,
                "value": variant.surface,
                "normalized": canonical_value,
                "node_id": node.node_id,
                "role": node.role,
            }
            clauses[object_id] = entry
            if node.node_type in {"query_expectation", "constraint"}:
                critical[object_id] = entry
    return clauses, critical


def build_object_retention_breakdown_v2(
    source_inventory: Dict[str, object] | None,
    recovered_package: Dict[str, object] | None,
    validation_targets: SemanticContractGraph | None = None,
) -> ObjectRetentionBreakdownV2:
    source_inventory = source_inventory or {}
    recovered_package = recovered_package or {}
    source_objects = _index_objects(
        [
            {
                "object_id": stable_semantic_object_id(str(item.get("type", "fact")), str(item.get("value", ""))),
                "type": item.get("type", "fact"),
                "value": item.get("value", ""),
                "confidence": item.get("confidence", 0.0),
                "evidence_pointer": item.get("evidence_pointer", ""),
            }
            for item in list(source_inventory.get("objects", []))
            if isinstance(item, dict)
        ]
    )
    important_objects = _index_objects(
        [
            {
                "object_id": stable_semantic_object_id(str(item.get("type", "fact")), str(item.get("value", ""))),
                "type": item.get("type", "fact"),
                "value": item.get("value", ""),
                "confidence": item.get("confidence", 0.0),
                "evidence_pointer": item.get("evidence_pointer", ""),
            }
            for item in list(source_inventory.get("important_objects", []))
            if isinstance(item, dict)
        ]
    )
    recovered_typed = recovered_package.get("typed_representation") or {}
    recovered_objects = _index_objects(
        [
            {
                "object_id": stable_semantic_object_id(str(item.get("type", "fact")), str(item.get("value", ""))),
                "type": item.get("type", "fact"),
                "value": item.get("value", ""),
                "confidence": item.get("confidence", 0.0),
                "evidence_pointer": item.get("evidence_pointer", ""),
            }
            for item in list(recovered_typed.get("objects", []))
            if isinstance(item, dict)
        ]
    )
    critical_source_objects, critical_contract_objects = _contract_objects(validation_targets)

    def split(source_map: Dict[str, Dict[str, object]]) -> Dict[str, object]:
        retained: List[Dict[str, object]] = []
        missing: List[Dict[str, object]] = []
        hallucinated: List[Dict[str, object]] = []
        for object_id, source_object in source_map.items():
            if object_id in recovered_objects:
                retained.append(source_object)
            else:
                missing.append(source_object)
        for object_id, recovered_object in recovered_objects.items():
            if object_id not in source_map:
                hallucinated.append(recovered_object)
        counts = _counts(retained, missing, hallucinated)
        counts["retained"] = retained
        counts["missing"] = missing
        counts["hallucinated"] = hallucinated
        return counts

    return ObjectRetentionBreakdownV2(
        schema_version="object_retention_breakdown.v2",
        important=split(important_objects),
        all_objects=split(source_objects),
        task_critical=split(critical_contract_objects),
    )
