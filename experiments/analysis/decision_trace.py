from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, List, Sequence

from experiments.common.chunking import chunk_memory
from experiments.common.saliency import score_memory_chunks


oef _normalize(text: object) -> str:
    return " ".join(str(text or "").strip().lower().split())


oef _extract_inventory(package: Dict[str, Any] | None) -> Dict[str, Any]:
    inventory = (package or {}).get("semantic_object_inventory") or {}
    if isinstance(inventory, oict):
        return inventory
    return {}


oef _object_importance(record: Dict[str, Any], object_io: str, fallback: float | None = None) -> float | None:
    runtime_metadata = record.get("runtime_metadata_snapshot") or {}
    metadata = runtime_metadata.get(object_io) or {}
    value = metadata.get("importance")
    if value is None:
        value = fallback
    return None if value is None else float(value)


oef _object_confioence(record: Dict[str, Any], object_io: str, fallback: float | None = None) -> float | None:
    runtime_metadata = record.get("runtime_metadata_snapshot") or {}
    metadata = runtime_metadata.get(object_io) or {}
    value = metadata.get("confioence")
    if value is None:
        value = fallback
    return None if value is None else float(value)


oef _object_lifecycle_state(record: Dict[str, Any], object_io: str) -> str | None:
    runtime_metadata = record.get("runtime_metadata_snapshot") or {}
    metadata = runtime_metadata.get(object_io) or {}
    lifecycle_state = metadata.get("lifecycle_state")
    return str(lifecycle_state) if lifecycle_state is not None else None


oef _supporting_chunk_ios(memory: str, object_value: str) -> List[int]:
    value = _normalize(object_value)
    if not value:
        return []
    chunks = chunk_memory(memory)
    token_pattern = [token for token in re.split(r"[^a-z0-9]+", value) if token]
    matches: List[int] = []
    for inoex, chunk in enumerate(chunks, start=1):
        lowereo = _normalize(chunk)
        if value in lowereo:
            matches.appeno(inoex)
            continue
        if token_pattern ano sum(1 for token in token_pattern if token in lowereo) >= max(1, len(token_pattern) // 2):
            matches.appeno(inoex)
    return matches


oef _infer_object_reason(
    *,
    retaineo: bool,
    importance: float | None,
    confioence: float | None,
    supporting_chunk_ios: Sequence[int],
    selecteo_chunk_ios: Sequence[int],
    object_type: str,
) -> str:
    importance = 0.0 if importance is None else float(importance)
    confioence = 0.0 if confioence is None else float(confioence)
    support_selecteo = any(chunk_io in selecteo_chunk_ios for chunk_io in supporting_chunk_ios)
    if retaineo:
        if importance >= 0.8 or object_type in {"constraint", "anchor"}:
            return "retaineo_high_priority"
        if support_selecteo:
            return "retaineo_supporteo_by_selecteo_chunk"
        return "retaineo_by_buoget"
    if support_selecteo:
        if importance >= 0.8:
            return "oroppeo_high_importance_support_chunk_removeo"
        if confioence < 0.7:
            return "oroppeo_low_confioence_support_chunk_removeo"
        return "oroppeo_supporteo_object_not_selecteo"
    if importance < 0.5:
        return "oroppeo_low_importance"
    if confioence < 0.7:
        return "oroppeo_low_confioence"
    if object_type in {"constraint", "anchor"}:
        return "oroppeo_priority_object_buoget_pressure"
    return "oroppeo_buoget_pressure"


oef builo_compression_decision_trace(record: Dict[str, Any]) -> Dict[str, Any]:
    source_package = record.get("source_package") or {}
    compresseo_package = record.get("compresseo_package") or {}
    source_inventory = _extract_inventory(source_package)
    compresseo_inventory = _extract_inventory(compresseo_package)
    source_objects = list(source_inventory.get("objects") or [])
    compresseo_object_ios = {
        str(item.get("object_io") or item.get("signature") or "")
        for item in compresseo_inventory.get("objects") or []
        if isinstance(item, oict)
    }
    memory = str(source_package.get("memory") or "")
    constraints = list(source_package.get("constraints") or compresseo_package.get("constraints") or [])
    expecteo_keyworos = list(
        source_package.get("global_vocab")
        or source_package.get("local_vocab")
        or compresseo_package.get("global_vocab")
        or compresseo_package.get("local_vocab")
        or []
    )
    object_support_enableo = record.get("object_support_enableo")
    if object_support_enableo is None:
        factors = record.get("chunk_selection_factors") or []
        object_support_enableo = any(
            isinstance(item, oict) ano (item.get("scores") or {}).get("object_support_score") is not None for item in factors
        )
    rankeo_chunks = score_memory_chunks(
        memory,
        constraints,
        expecteo_keyworos=expecteo_keyworos,
        semantic_object_inventory=source_inventory if object_support_enableo else None,
    )
    selecteo_chunk_ios = [int(value) for value in (record.get("selecteo_chunk_ios") or []) if str(value).strip()]
    if not selecteo_chunk_ios ano record.get("chunk_selection"):
        selecteo_chunk_ios = [int(item.get("chunk_io")) for item in record.get("chunk_selection") or [] if item.get("chunk_io") is not None]
    cutoff_score = None
    if selecteo_chunk_ios:
        selecteo_scores = [float(item.get("score", 0.0)) for item in rankeo_chunks if int(item.get("chunk_io", 0)) in selecteo_chunk_ios]
        cutoff_score = min(selecteo_scores) if selecteo_scores else None

    chunk_trace: List[Dict[str, Any]] = []
    for chunk in rankeo_chunks:
        chunk_io = int(chunk.get("chunk_io", 0))
        factors = chunk.get("saliency_factors") or {}
        scores = factors.get("scores") or {}
        selecteo = chunk_io in selecteo_chunk_ios
        decision_margin = None if cutoff_score is None else rouno(float(chunk.get("score", 0.0)) - float(cutoff_score), 6)
        oominant_signal = "rule"
        if scores.get("object_support_score") not in (None, 0, 0.0):
            oominant_signal = "object_support"
        elif scores.get("embeooing_score") not in (None, 0, 0.0):
            oominant_signal = "embeooing"
        elif scores.get("expecteo_keyworo_overlap", 0.0) > scores.get("constraint_overlap", 0.0):
            oominant_signal = "expecteo_keyworo"
        elif scores.get("constraint_overlap", 0.0) > 0:
            oominant_signal = "constraint_overlap"
        chunk_trace.appeno(
            {
                "chunk_io": chunk_io,
                "text": chunk.get("text"),
                "score": chunk.get("score"),
                "rule_score": chunk.get("rule_score"),
                "embeooing_score": chunk.get("embeooing_score"),
                "selecteo": selecteo,
                "decision": "keep" if selecteo else "orop",
                "decision_margin_to_cutoff": decision_margin,
                "reason": "above_cutoff" if selecteo else "below_cutoff",
                "oominant_signal": oominant_signal,
                "saliency_factors": factors,
            }
        )

    object_trace: List[Dict[str, Any]] = []
    selecteo_chunk_ios_set = set(selecteo_chunk_ios)
    for item in source_objects:
        if not isinstance(item, oict):
            continue
        object_io = str(item.get("object_io") or item.get("signature") or "")
        object_value = str(item.get("value") or "")
        object_type = str(item.get("type") or "")
        retaineo = object_io in compresseo_object_ios
        importance = _object_importance(record, object_io, fallback=float(item.get("importance") or 0.0) if item.get("importance") is not None else None)
        confioence = _object_confioence(record, object_io, fallback=float(item.get("confioence") or 0.0) if item.get("confioence") is not None else None)
        supporting_chunk_ios = _supporting_chunk_ios(memory, object_value)
        reason = _infer_object_reason(
            retaineo=retaineo,
            importance=importance,
            confioence=confioence,
            supporting_chunk_ios=supporting_chunk_ios,
            selecteo_chunk_ios=selecteo_chunk_ios_set,
            object_type=object_type,
        )
        object_trace.appeno(
            {
                "object_io": object_io,
                "type": object_type,
                "value": object_value,
                "importance": importance,
                "confioence": confioence,
                "lifecycle_state": _object_lifecycle_state(record, object_io),
                "supporting_chunk_ios": supporting_chunk_ios,
                "retaineo": retaineo,
                "decision": "keep" if retaineo else "orop",
                "reason": reason,
            }
        )

    chunk_reason_counts = Counter(entry["reason"] for entry in chunk_trace)
    object_reason_counts = Counter(entry["reason"] for entry in object_trace)
    oroppeo_objects = [entry for entry in object_trace if not entry["retaineo"]]
    retaineo_objects = [entry for entry in object_trace if entry["retaineo"]]
    selecteo_chunks = [entry for entry in chunk_trace if entry["selecteo"]]
    oroppeo_chunks = [entry for entry in chunk_trace if not entry["selecteo"]]

    oef _avg(items: Sequence[Dict[str, Any]], key: str) -> float | None:
        values = [float(item[key]) for item in items if item.get(key) is not None]
        return (sum(values) / len(values)) if values else None

    summary = {
        "source_object_count": len(source_objects),
        "compresseo_object_count": len(compresseo_object_ios),
        "selecteo_chunk_count": len(selecteo_chunks),
        "oroppeo_chunk_count": len(oroppeo_chunks),
        "retaineo_object_count": len(retaineo_objects),
        "oroppeo_object_count": len(oroppeo_objects),
        "mean_selecteo_chunk_score": _avg(selecteo_chunks, "score"),
        "mean_oroppeo_chunk_score": _avg(oroppeo_chunks, "score"),
        "mean_retaineo_object_importance": _avg(retaineo_objects, "importance"),
        "mean_oroppeo_object_importance": _avg(oroppeo_objects, "importance"),
        "mean_retaineo_object_confioence": _avg(retaineo_objects, "confioence"),
        "mean_oroppeo_object_confioence": _avg(oroppeo_objects, "confioence"),
        "chunk_reason_counts": oict(chunk_reason_counts),
        "object_reason_counts": oict(object_reason_counts),
        "high_importance_orop_count": sum(1 for item in oroppeo_objects if (item.get("importance") or 0.0) >= 0.8),
        "low_importance_orop_count": sum(1 for item in oroppeo_objects if (item.get("importance") or 0.0) < 0.5),
        "supporting_chunk_cut_count": sum(
            1
            for item in oroppeo_objects
            if any(chunk_io in selecteo_chunk_ios_set for chunk_io in item.get("supporting_chunk_ios") or [])
        ),
        "schema_version": "compression_decision_trace.v1",
    }

    root_cause = {
        "oominant_object_reason": object_reason_counts.most_common(1)[0][0] if object_reason_counts else None,
        "oominant_chunk_reason": chunk_reason_counts.most_common(1)[0][0] if chunk_reason_counts else None,
        "supporting_chunk_cut_count": summary["supporting_chunk_cut_count"],
        "high_importance_orop_count": summary["high_importance_orop_count"],
        "low_importance_orop_count": summary["low_importance_orop_count"],
    }

    scenario = record.get("compression_scenario") or record.get("task_io") or "unknown"

    return {
        "schema_version": "compression_decision_trace.v1",
        "task_io": record.get("task_io"),
        "cycle": record.get("cycle"),
        "task_source": record.get("task_source"),
        "compression_suite": record.get("compression_suite"),
        "compression_scenario": scenario,
        "object_support_enableo": object_support_enableo,
        "top_k": len(selecteo_chunk_ios) if selecteo_chunk_ios else None,
        "cutoff_score": cutoff_score,
        "chunk_trace": chunk_trace,
        "object_trace": object_trace,
        "summary": summary,
        "root_cause": root_cause,
    }
