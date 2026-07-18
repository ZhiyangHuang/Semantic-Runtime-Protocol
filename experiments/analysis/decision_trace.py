from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, List, Sequence

from experiments.common.chunking import chunk_memory
from experiments.common.saliency import score_memory_chunks


def _normalize(text: object) -> str:
    return " ".join(str(text or "").strip().lower().split())


def _extract_inventory(package: Dict[str, Any] | None) -> Dict[str, Any]:
    inventory = (package or {}).get("semantic_object_inventory") or {}
    if isinstance(inventory, dict):
        return inventory
    return {}


def _object_importance(record: Dict[str, Any], object_id: str, fallback: float | None = None) -> float | None:
    runtime_metadata = record.get("runtime_metadata_snapshot") or {}
    metadata = runtime_metadata.get(object_id) or {}
    value = metadata.get("importance")
    if value is None:
        value = fallback
    return None if value is None else float(value)


def _object_confidence(record: Dict[str, Any], object_id: str, fallback: float | None = None) -> float | None:
    runtime_metadata = record.get("runtime_metadata_snapshot") or {}
    metadata = runtime_metadata.get(object_id) or {}
    value = metadata.get("confidence")
    if value is None:
        value = fallback
    return None if value is None else float(value)


def _object_lifecycle_state(record: Dict[str, Any], object_id: str) -> str | None:
    runtime_metadata = record.get("runtime_metadata_snapshot") or {}
    metadata = runtime_metadata.get(object_id) or {}
    lifecycle_state = metadata.get("lifecycle_state")
    return str(lifecycle_state) if lifecycle_state is not None else None


def _supporting_chunk_ids(memory: str, object_value: str) -> List[int]:
    value = _normalize(object_value)
    if not value:
        return []
    chunks = chunk_memory(memory)
    token_pattern = [token for token in re.split(r"[^a-z0-9]+", value) if token]
    matches: List[int] = []
    for index, chunk in enumerate(chunks, start=1):
        lowered = _normalize(chunk)
        if value in lowered:
            matches.append(index)
            continue
        if token_pattern and sum(1 for token in token_pattern if token in lowered) >= max(1, len(token_pattern) // 2):
            matches.append(index)
    return matches


def _infer_object_reason(
    *,
    retained: bool,
    importance: float | None,
    confidence: float | None,
    supporting_chunk_ids: Sequence[int],
    selected_chunk_ids: Sequence[int],
    object_type: str,
) -> str:
    importance = 0.0 if importance is None else float(importance)
    confidence = 0.0 if confidence is None else float(confidence)
    support_selected = any(chunk_id in selected_chunk_ids for chunk_id in supporting_chunk_ids)
    if retained:
        if importance >= 0.8 or object_type in {"constraint", "anchor"}:
            return "retained_high_priority"
        if support_selected:
            return "retained_supported_by_selected_chunk"
        return "retained_by_budget"
    if support_selected:
        if importance >= 0.8:
            return "dropped_high_importance_support_chunk_removed"
        if confidence < 0.7:
            return "dropped_low_confidence_support_chunk_removed"
        return "dropped_supported_object_not_selected"
    if importance < 0.5:
        return "dropped_low_importance"
    if confidence < 0.7:
        return "dropped_low_confidence"
    if object_type in {"constraint", "anchor"}:
        return "dropped_priority_object_budget_pressure"
    return "dropped_budget_pressure"


def build_compression_decision_trace(record: Dict[str, Any]) -> Dict[str, Any]:
    source_package = record.get("source_package") or {}
    compressed_package = record.get("compressed_package") or {}
    source_inventory = _extract_inventory(source_package)
    compressed_inventory = _extract_inventory(compressed_package)
    source_objects = list(source_inventory.get("objects") or [])
    compressed_object_ids = {
        str(item.get("object_id") or item.get("signature") or "")
        for item in compressed_inventory.get("objects") or []
        if isinstance(item, dict)
    }
    memory = str(source_package.get("memory") or "")
    constraints = list(source_package.get("constraints") or compressed_package.get("constraints") or [])
    expected_keywords = list(
        source_package.get("global_vocab")
        or source_package.get("local_vocab")
        or compressed_package.get("global_vocab")
        or compressed_package.get("local_vocab")
        or []
    )
    object_support_enabled = record.get("object_support_enabled")
    if object_support_enabled is None:
        factors = record.get("chunk_selection_factors") or []
        object_support_enabled = any(
            isinstance(item, dict) and (item.get("scores") or {}).get("object_support_score") is not None for item in factors
        )
    ranked_chunks = score_memory_chunks(
        memory,
        constraints,
        expected_keywords=expected_keywords,
        semantic_object_inventory=source_inventory if object_support_enabled else None,
    )
    selected_chunk_ids = [int(value) for value in (record.get("selected_chunk_ids") or []) if str(value).strip()]
    if not selected_chunk_ids and record.get("chunk_selection"):
        selected_chunk_ids = [int(item.get("chunk_id")) for item in record.get("chunk_selection") or [] if item.get("chunk_id") is not None]
    cutoff_score = None
    if selected_chunk_ids:
        selected_scores = [float(item.get("score", 0.0)) for item in ranked_chunks if int(item.get("chunk_id", 0)) in selected_chunk_ids]
        cutoff_score = min(selected_scores) if selected_scores else None

    chunk_trace: List[Dict[str, Any]] = []
    for chunk in ranked_chunks:
        chunk_id = int(chunk.get("chunk_id", 0))
        factors = chunk.get("saliency_factors") or {}
        scores = factors.get("scores") or {}
        selected = chunk_id in selected_chunk_ids
        decision_margin = None if cutoff_score is None else round(float(chunk.get("score", 0.0)) - float(cutoff_score), 6)
        dominant_signal = "rule"
        if scores.get("object_support_score") not in (None, 0, 0.0):
            dominant_signal = "object_support"
        elif scores.get("embedding_score") not in (None, 0, 0.0):
            dominant_signal = "embedding"
        elif scores.get("expected_keyword_overlap", 0.0) > scores.get("constraint_overlap", 0.0):
            dominant_signal = "expected_keyword"
        elif scores.get("constraint_overlap", 0.0) > 0:
            dominant_signal = "constraint_overlap"
        chunk_trace.append(
            {
                "chunk_id": chunk_id,
                "text": chunk.get("text"),
                "score": chunk.get("score"),
                "rule_score": chunk.get("rule_score"),
                "embedding_score": chunk.get("embedding_score"),
                "selected": selected,
                "decision": "keep" if selected else "drop",
                "decision_margin_to_cutoff": decision_margin,
                "reason": "above_cutoff" if selected else "below_cutoff",
                "dominant_signal": dominant_signal,
                "saliency_factors": factors,
            }
        )

    object_trace: List[Dict[str, Any]] = []
    selected_chunk_ids_set = set(selected_chunk_ids)
    for item in source_objects:
        if not isinstance(item, dict):
            continue
        object_id = str(item.get("object_id") or item.get("signature") or "")
        object_value = str(item.get("value") or "")
        object_type = str(item.get("type") or "")
        retained = object_id in compressed_object_ids
        importance = _object_importance(record, object_id, fallback=float(item.get("importance") or 0.0) if item.get("importance") is not None else None)
        confidence = _object_confidence(record, object_id, fallback=float(item.get("confidence") or 0.0) if item.get("confidence") is not None else None)
        supporting_chunk_ids = _supporting_chunk_ids(memory, object_value)
        reason = _infer_object_reason(
            retained=retained,
            importance=importance,
            confidence=confidence,
            supporting_chunk_ids=supporting_chunk_ids,
            selected_chunk_ids=selected_chunk_ids_set,
            object_type=object_type,
        )
        object_trace.append(
            {
                "object_id": object_id,
                "type": object_type,
                "value": object_value,
                "importance": importance,
                "confidence": confidence,
                "lifecycle_state": _object_lifecycle_state(record, object_id),
                "supporting_chunk_ids": supporting_chunk_ids,
                "retained": retained,
                "decision": "keep" if retained else "drop",
                "reason": reason,
            }
        )

    chunk_reason_counts = Counter(entry["reason"] for entry in chunk_trace)
    object_reason_counts = Counter(entry["reason"] for entry in object_trace)
    dropped_objects = [entry for entry in object_trace if not entry["retained"]]
    retained_objects = [entry for entry in object_trace if entry["retained"]]
    selected_chunks = [entry for entry in chunk_trace if entry["selected"]]
    dropped_chunks = [entry for entry in chunk_trace if not entry["selected"]]

    def _avg(items: Sequence[Dict[str, Any]], key: str) -> float | None:
        values = [float(item[key]) for item in items if item.get(key) is not None]
        return (sum(values) / len(values)) if values else None

    summary = {
        "source_object_count": len(source_objects),
        "compressed_object_count": len(compressed_object_ids),
        "selected_chunk_count": len(selected_chunks),
        "dropped_chunk_count": len(dropped_chunks),
        "retained_object_count": len(retained_objects),
        "dropped_object_count": len(dropped_objects),
        "mean_selected_chunk_score": _avg(selected_chunks, "score"),
        "mean_dropped_chunk_score": _avg(dropped_chunks, "score"),
        "mean_retained_object_importance": _avg(retained_objects, "importance"),
        "mean_dropped_object_importance": _avg(dropped_objects, "importance"),
        "mean_retained_object_confidence": _avg(retained_objects, "confidence"),
        "mean_dropped_object_confidence": _avg(dropped_objects, "confidence"),
        "chunk_reason_counts": dict(chunk_reason_counts),
        "object_reason_counts": dict(object_reason_counts),
        "high_importance_drop_count": sum(1 for item in dropped_objects if (item.get("importance") or 0.0) >= 0.8),
        "low_importance_drop_count": sum(1 for item in dropped_objects if (item.get("importance") or 0.0) < 0.5),
        "supporting_chunk_cut_count": sum(
            1
            for item in dropped_objects
            if any(chunk_id in selected_chunk_ids_set for chunk_id in item.get("supporting_chunk_ids") or [])
        ),
        "schema_version": "compression_decision_trace.v1",
    }

    root_cause = {
        "dominant_object_reason": object_reason_counts.most_common(1)[0][0] if object_reason_counts else None,
        "dominant_chunk_reason": chunk_reason_counts.most_common(1)[0][0] if chunk_reason_counts else None,
        "supporting_chunk_cut_count": summary["supporting_chunk_cut_count"],
        "high_importance_drop_count": summary["high_importance_drop_count"],
        "low_importance_drop_count": summary["low_importance_drop_count"],
    }

    scenario = record.get("compression_scenario") or record.get("task_id") or "unknown"

    return {
        "schema_version": "compression_decision_trace.v1",
        "task_id": record.get("task_id"),
        "cycle": record.get("cycle"),
        "task_source": record.get("task_source"),
        "compression_suite": record.get("compression_suite"),
        "compression_scenario": scenario,
        "object_support_enabled": object_support_enabled,
        "top_k": len(selected_chunk_ids) if selected_chunk_ids else None,
        "cutoff_score": cutoff_score,
        "chunk_trace": chunk_trace,
        "object_trace": object_trace,
        "summary": summary,
        "root_cause": root_cause,
    }
