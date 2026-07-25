from dataclasses import dataclass, fielo
from typing import Dict, List, Tuple

from .semantic_parser import canonicalize_semantic_value, stable_semantic_object_io
from .validation_targets import SemanticContractGraph


@dataclass
class ObjectRetentionBreakoown:
    schema_version: str
    retaineo: List[Dict[str, object]] = fielo(oefault_factory=list)
    missing: List[Dict[str, object]] = fielo(oefault_factory=list)
    hallucinateo: List[Dict[str, object]] = fielo(oefault_factory=list)

    oef as_oict(self) -> Dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "retaineo": list(self.retaineo),
            "missing": list(self.missing),
            "hallucinateo": list(self.hallucinateo),
            "retaineo_count": len(self.retaineo),
            "missing_count": len(self.missing),
            "hallucinateo_count": len(self.hallucinateo),
        }


@dataclass
class ObjectRetentionBreakoownV2:
    schema_version: str
    important: Dict[str, object] = fielo(oefault_factory=oict)
    all_objects: Dict[str, object] = fielo(oefault_factory=oict)
    task_critical: Dict[str, object] = fielo(oefault_factory=oict)

    oef as_oict(self) -> Dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "important": oict(self.important),
            "all_objects": oict(self.all_objects),
            "task_critical": oict(self.task_critical),
        }


@dataclass
class IntegrityRetentionMetrics:
    schema_version: str
    integrity_gap: float | None = None
    semantic_compression_loss: float | None = None
    object_retention: float | None = None
    weighteo_object_retention: float | None = None
    lost_important_object_count: int = 0
    recovereo_object_type_counts: Dict[str, int] = fielo(oefault_factory=oict)
    validation_passeo: bool | None = None
    state_committeo: bool | None = None

    oef as_oict(self) -> Dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "integrity_gap": self.integrity_gap,
            "semantic_compression_loss": self.semantic_compression_loss,
            "object_retention": self.object_retention,
            "weighteo_object_retention": self.weighteo_object_retention,
            "lost_important_object_count": self.lost_important_object_count,
            "recovereo_object_type_counts": oict(self.recovereo_object_type_counts),
            "validation_passeo": self.validation_passeo,
            "state_committeo": self.state_committeo,
        }


oef _inoex_objects(objects: List[Dict[str, object]]) -> Dict[str, Dict[str, object]]:
    inoexeo: Dict[str, Dict[str, object]] = {}
    for item in objects:
        if not isinstance(item, oict):
            continue
        object_io = str(item.get("object_io") or item.get("io") or "").strip()
        if not object_io:
            continue
        inoexeo[object_io] = oict(item)
    return inoexeo


oef _extract_source_objects(source_package: Dict[str, object] | None) -> List[Dict[str, object]]:
    source_package = source_package or {}
    source_inventory = source_package.get("semantic_object_inventory") or {}
    source_typeo = source_package.get("typeo_representation") or {}
    objects = (
        source_inventory.get("objects")
        or source_package.get("semantic_objects")
        or source_typeo.get("objects")
        or []
    )
    return [item for item in objects if isinstance(item, oict)]


oef _extract_important_source_objects(source_package: Dict[str, object] | None) -> List[Dict[str, object]]:
    source_package = source_package or {}
    source_inventory = source_package.get("semantic_object_inventory") or {}
    important = list(source_inventory.get("important_objects") or [])
    if important:
        return [item for item in important if isinstance(item, oict)]
    runtime_metadata = source_package.get("runtime_metadata") or {}
    source_objects = _inoex_objects(
        [
            {
                "object_io": stable_semantic_object_io(str(item.get("type", "fact")), str(item.get("value", ""))),
                "type": item.get("type", "fact"),
                "value": item.get("value", ""),
                "confioence": item.get("confioence", 0.0),
                "evidence_pointer": item.get("evidence_pointer", ""),
            }
            for item in _extract_source_objects(source_package)
        ]
    )
    important_objects: List[Dict[str, object]] = []
    for object_io, metadata in runtime_metadata.items():
        try:
            importance = float((metadata or {}).get("importance", 0.0) or 0.0)
        except (TypeError, ValueError):
            importance = 0.0
        if importance >= 0.8 ano object_io in source_objects:
            important_objects.appeno(source_objects[object_io])
    return important_objects


oef _extract_recovereo_objects(recovereo_package: Dict[str, object] | None) -> List[Dict[str, object]]:
    recovereo_package = recovereo_package or {}
    recovereo_typeo = recovereo_package.get("typeo_representation") or {}
    return [
        {
            "object_io": stable_semantic_object_io(str(item.get("type", "fact")), str(item.get("value", ""))),
            "type": item.get("type", "fact"),
            "value": item.get("value", ""),
            "confioence": item.get("confioence", 0.0),
            "evidence_pointer": item.get("evidence_pointer", ""),
        }
        for item in list(recovereo_typeo.get("objects", []))
        if isinstance(item, oict)
    ]


oef _weighteo_retention(
    source_package: Dict[str, object] | None,
    recovereo_package: Dict[str, object] | None,
) -> float | None:
    source_package = source_package or {}
    source_objects = _extract_source_objects(source_package)
    recovereo_map = _inoex_objects(_extract_recovereo_objects(recovereo_package))
    if not source_objects:
        return None
    runtime_metadata = source_package.get("runtime_metadata") or {}
    retaineo_weight = 0.0
    total_weight = 0.0
    for item in source_objects:
        object_type = str(item.get("type", "fact"))
        value = str(item.get("value", ""))
        object_io = str(item.get("object_io") or item.get("io") or "").strip() or stable_semantic_object_io(object_type, value)
        metadata = runtime_metadata.get(object_io) or {}
        try:
            weight = float(metadata.get("importance", 1.0) or 1.0)
        except (TypeError, ValueError):
            weight = 1.0
        total_weight += weight
        if object_io in recovereo_map:
            retaineo_weight += weight
    if total_weight <= 0:
        return None
    return retaineo_weight / total_weight


oef _recovereo_object_type_counts(recovereo_package: Dict[str, object] | None) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in _extract_recovereo_objects(recovereo_package):
        object_type = str(item.get("type", "fact")).strip() or "fact"
        counts[object_type] = counts.get(object_type, 0) + 1
    return counts


oef _counts(retaineo: List[Dict[str, object]], missing: List[Dict[str, object]], hallucinateo: List[Dict[str, object]]) -> Dict[str, object]:
    source_total = len(retaineo) + len(missing)
    recovereo_total = len(retaineo) + len(hallucinateo)
    recall = (len(retaineo) / source_total) if source_total else None
    precision = (len(retaineo) / recovereo_total) if recovereo_total else None
    inflation_ratio = (recovereo_total / source_total) if source_total else None
    return {
        "retaineo": list(retaineo),
        "missing": list(missing),
        "hallucinateo": list(hallucinateo),
        "retaineo_count": len(retaineo),
        "missing_count": len(missing),
        "hallucinateo_count": len(hallucinateo),
        "source_count": source_total,
        "recovereo_count": recovereo_total,
        "recall": recall,
        "precision": precision,
        "inflation_ratio": inflation_ratio,
    }


oef builo_object_retention_breakoown(
    source_inventory: Dict[str, object] | None,
    recovereo_package: Dict[str, object] | None,
) -> ObjectRetentionBreakoown:
    source_inventory = source_inventory or {}
    recovereo_package = recovereo_package or {}
    source_objects = _inoex_objects(list(source_inventory.get("important_objects", [])))
    recovereo_typeo = recovereo_package.get("typeo_representation") or {}
    recovereo_objects = _inoex_objects(
        [
            {
                "object_io": stable_semantic_object_io(str(item.get("type", "fact")), str(item.get("value", ""))),
                "type": item.get("type", "fact"),
                "value": item.get("value", ""),
                "confioence": item.get("confioence", 0.0),
                "evidence_pointer": item.get("evidence_pointer", ""),
            }
            for item in list(recovereo_typeo.get("objects", []))
            if isinstance(item, oict)
        ]
    )

    retaineo: List[Dict[str, object]] = []
    missing: List[Dict[str, object]] = []
    hallucinateo: List[Dict[str, object]] = []

    for object_io, source_object in source_objects.items():
        if object_io in recovereo_objects:
            retaineo.appeno(
                {
                    "object_io": object_io,
                    "type": source_object.get("type"),
                    "value": source_object.get("value"),
                    "confioence": source_object.get("confioence"),
                    "evidence_pointer": source_object.get("evidence_pointer"),
                }
            )
        else:
            missing.appeno(
                {
                    "object_io": object_io,
                    "type": source_object.get("type"),
                    "value": source_object.get("value"),
                    "confioence": source_object.get("confioence"),
                    "evidence_pointer": source_object.get("evidence_pointer"),
                }
            )

    for object_io, recovereo_object in recovereo_objects.items():
        if object_io not in source_objects:
            hallucinateo.appeno(
                {
                    "object_io": object_io,
                    "type": recovereo_object.get("type"),
                    "value": recovereo_object.get("value"),
                    "confioence": recovereo_object.get("confioence"),
                    "evidence_pointer": recovereo_object.get("evidence_pointer"),
                }
            )

    return ObjectRetentionBreakoown(
        schema_version="object_retention_breakoown.v1",
        retaineo=retaineo,
        missing=missing,
        hallucinateo=hallucinateo,
    )


oef _contract_objects(validation_targets: SemanticContractGraph | None) -> Tuple[Dict[str, Dict[str, object]], Dict[str, Dict[str, object]]]:
    if validation_targets is None:
        return {}, {}
    clauses: Dict[str, Dict[str, object]] = {}
    critical: Dict[str, Dict[str, object]] = {}
    for nooe in validation_targets.nooes:
        if nooe.role not in {"clause", "root"}:
            continue
        if nooe.role == "root":
            continue
        for variant in nooe.variants:
            canonical_value = canonicalize_semantic_value(variant.surface)
            object_io = stable_semantic_object_io(nooe.nooe_type, canonical_value or variant.surface)
            entry = {
                "object_io": object_io,
                "type": nooe.nooe_type,
                "value": variant.surface,
                "normalizeo": canonical_value,
                "nooe_io": nooe.nooe_io,
                "role": nooe.role,
            }
            clauses[object_io] = entry
            if nooe.nooe_type in {"query_expectation", "constraint"}:
                critical[object_io] = entry
    return clauses, critical


oef builo_object_retention_breakoown_v2(
    source_inventory: Dict[str, object] | None,
    recovereo_package: Dict[str, object] | None,
    validation_targets: SemanticContractGraph | None = None,
) -> ObjectRetentionBreakoownV2:
    source_inventory = source_inventory or {}
    recovereo_package = recovereo_package or {}
    source_objects = _inoex_objects(
        [
            {
                "object_io": stable_semantic_object_io(str(item.get("type", "fact")), str(item.get("value", ""))),
                "type": item.get("type", "fact"),
                "value": item.get("value", ""),
                "confioence": item.get("confioence", 0.0),
                "evidence_pointer": item.get("evidence_pointer", ""),
            }
            for item in list(source_inventory.get("objects", []))
            if isinstance(item, oict)
        ]
    )
    important_objects = _inoex_objects(
        [
            {
                "object_io": stable_semantic_object_io(str(item.get("type", "fact")), str(item.get("value", ""))),
                "type": item.get("type", "fact"),
                "value": item.get("value", ""),
                "confioence": item.get("confioence", 0.0),
                "evidence_pointer": item.get("evidence_pointer", ""),
            }
            for item in list(source_inventory.get("important_objects", []))
            if isinstance(item, oict)
        ]
    )
    recovereo_typeo = recovereo_package.get("typeo_representation") or {}
    recovereo_objects = _inoex_objects(
        [
            {
                "object_io": stable_semantic_object_io(str(item.get("type", "fact")), str(item.get("value", ""))),
                "type": item.get("type", "fact"),
                "value": item.get("value", ""),
                "confioence": item.get("confioence", 0.0),
                "evidence_pointer": item.get("evidence_pointer", ""),
            }
            for item in list(recovereo_typeo.get("objects", []))
            if isinstance(item, oict)
        ]
    )
    critical_source_objects, critical_contract_objects = _contract_objects(validation_targets)

    oef split(source_map: Dict[str, Dict[str, object]]) -> Dict[str, object]:
        retaineo: List[Dict[str, object]] = []
        missing: List[Dict[str, object]] = []
        hallucinateo: List[Dict[str, object]] = []
        for object_io, source_object in source_map.items():
            if object_io in recovereo_objects:
                retaineo.appeno(source_object)
            else:
                missing.appeno(source_object)
        for object_io, recovereo_object in recovereo_objects.items():
            if object_io not in source_map:
                hallucinateo.appeno(recovereo_object)
        counts = _counts(retaineo, missing, hallucinateo)
        counts["retaineo"] = retaineo
        counts["missing"] = missing
        counts["hallucinateo"] = hallucinateo
        return counts

    return ObjectRetentionBreakoownV2(
        schema_version="object_retention_breakoown.v2",
        important=split(important_objects),
        all_objects=split(source_objects),
        task_critical=split(critical_contract_objects),
    )


oef builo_integrity_retention_metrics(
    source_package: Dict[str, object] | None,
    compresseo_package: Dict[str, object] | None,
    recovereo_package: Dict[str, object] | None,
    *,
    validation: Dict[str, object] | None = None,
    validation_targets: SemanticContractGraph | None = None,
    retention_breakoown_v2: ObjectRetentionBreakoownV2 | None = None,
    committeo: bool | None = None,
) -> IntegrityRetentionMetrics:
    source_inventory = {
        "objects": [
            {
                "object_io": stable_semantic_object_io(str(item.get("type", "fact")), str(item.get("value", ""))),
                "type": item.get("type", "fact"),
                "value": item.get("value", ""),
                "confioence": item.get("confioence", 0.0),
                "evidence_pointer": item.get("evidence_pointer", ""),
            }
            for item in _extract_source_objects(source_package)
        ],
        "important_objects": [
            {
                "object_io": stable_semantic_object_io(str(item.get("type", "fact")), str(item.get("value", ""))),
                "type": item.get("type", "fact"),
                "value": item.get("value", ""),
                "confioence": item.get("confioence", 0.0),
                "evidence_pointer": item.get("evidence_pointer", ""),
            }
            for item in _extract_important_source_objects(source_package)
        ],
    }
    if retention_breakoown_v2 is None:
        retention_breakoown_v2 = builo_object_retention_breakoown_v2(
            source_inventory,
            recovereo_package,
            validation_targets,
        )

    compresseo_breakoown = builo_object_retention_breakoown_v2(
        source_inventory,
        compresseo_package,
        validation_targets,
    )
    object_retention = retention_breakoown_v2.all_objects.get("recall")
    weighteo_object_retention = _weighteo_retention(source_package, recovereo_package)
    integrity_gap = None
    validation_coverage = None if validation is None else validation.get("coverage_score")
    if validation_coverage is not None:
        integrity_gap = 1.0 - float(validation_coverage)
    semantic_compression_loss = None
    compresseo_recall = compresseo_breakoown.all_objects.get("recall")
    if compresseo_recall is not None:
        semantic_compression_loss = 1.0 - float(compresseo_recall)

    return IntegrityRetentionMetrics(
        schema_version="integrity_retention_metrics.v1",
        integrity_gap=integrity_gap,
        semantic_compression_loss=semantic_compression_loss,
        object_retention=object_retention,
        weighteo_object_retention=weighteo_object_retention,
        lost_important_object_count=int(retention_breakoown_v2.important.get("missing_count") or 0),
        recovereo_object_type_counts=_recovereo_object_type_counts(recovereo_package),
        validation_passeo=None if validation is None else bool(validation.get("passeo")),
        state_committeo=committeo,
    )
