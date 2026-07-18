from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, List, Sequence

from ..common.chunking import chunk_memory
from ..common.semantic_text import stable_semantic_object_id


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _extract_inventory(package: Dict[str, Any] | None) -> Dict[str, Any]:
    inventory = (package or {}).get("semantic_object_inventory") or {}
    return inventory if isinstance(inventory, dict) else {}


def _object_items(package: Dict[str, Any] | None) -> List[Dict[str, Any]]:
    inventory = _extract_inventory(package)
    objects = inventory.get("objects") or []
    return [item for item in objects if isinstance(item, dict)]


def _policy_dict(record: Dict[str, Any]) -> Dict[str, Any]:
    candidates = [
        record.get("policy_flat"),
        (record.get("source_package") or {}).get("policy_flat"),
        (record.get("source_package") or {}).get("policy"),
        record.get("policy"),
        (record.get("compressed_package") or {}).get("policy"),
    ]
    for candidate in candidates:
        if isinstance(candidate, dict) and candidate:
            return dict(candidate)
    return {
        "lifecycle_retained_importance": 0.35,
        "lifecycle_retained_passes": 2,
        "lifecycle_archived_importance": 0.3,
        "lifecycle_archived_drift_count": 2,
        "lifecycle_archived_failure_count": 2,
        "lifecycle_decayed_floor": 0.05,
        "lifecycle_decayed_multiplier": 0.92,
    }


def _compression_ratio(record: Dict[str, Any]) -> float | None:
    value = record.get("compression_ratio")
    if value is None:
        source_size = record.get("source_size")
        compressed_size = record.get("compressed_size")
        try:
            if source_size and compressed_size:
                source_size = float(source_size)
                compressed_size = float(compressed_size)
                if source_size > 0:
                    value = compressed_size / source_size
        except (TypeError, ValueError):
            value = None
    if value is None:
        return None
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return None


def _supporting_chunk_ids(memory: str, object_value: str) -> List[int]:
    value = " ".join(str(object_value or "").strip().lower().split())
    if not value:
        return []
    chunks = chunk_memory(memory)
    tokens = [token for token in re.split(r"[^a-z0-9]+", value) if token]
    matches: List[int] = []
    for index, chunk in enumerate(chunks, start=1):
        lowered = " ".join(str(chunk or "").strip().lower().split())
        if value in lowered:
            matches.append(index)
            continue
        if tokens and sum(1 for token in tokens if token in lowered) >= max(1, len(tokens) // 2):
            matches.append(index)
    return matches


def _runtime_metadata(record: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    runtime_metadata = (record.get("source_package") or {}).get("runtime_metadata")
    if not isinstance(runtime_metadata, dict):
        runtime_metadata = record.get("runtime_metadata_snapshot") or {}
    if not isinstance(runtime_metadata, dict):
        return {}
    output: Dict[str, Dict[str, Any]] = {}
    for key, value in runtime_metadata.items():
        if isinstance(value, dict):
            output[str(key)] = dict(value)
        elif hasattr(value, "as_dict"):
            output[str(key)] = value.as_dict()
        else:
            output[str(key)] = {
                "importance": getattr(value, "importance", None),
                "confidence": getattr(value, "confidence", None),
                "verification_passes": getattr(value, "verification_passes", None),
                "verification_failures": getattr(value, "verification_failures", None),
                "drift_count": getattr(value, "drift_count", None),
                "lifecycle_state": getattr(value, "lifecycle_state", None),
            }
    return output


def _object_id(item: Dict[str, Any]) -> str:
    object_type = _safe_str(item.get("type") or item.get("object_type") or "fact") or "fact"
    value = _safe_str(item.get("value") or item.get("label") or "")
    return _safe_str(item.get("object_id") or item.get("id") or "") or stable_semantic_object_id(object_type, value)


def _importance_score(record: Dict[str, Any], object_id: str, item: Dict[str, Any]) -> float:
    metadata = _runtime_metadata(record).get(object_id) or {}
    value = metadata.get("importance")
    if value is None:
        value = item.get("importance")
    if value is None:
        value = item.get("confidence")
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def _verification_passes(record: Dict[str, Any], object_id: str, item: Dict[str, Any]) -> int:
    metadata = _runtime_metadata(record).get(object_id) or {}
    value = metadata.get("verification_passes")
    if value is None:
        value = item.get("verification_passes")
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _verification_failures(record: Dict[str, Any], object_id: str, item: Dict[str, Any]) -> int:
    metadata = _runtime_metadata(record).get(object_id) or {}
    value = metadata.get("verification_failures")
    if value is None:
        value = item.get("verification_failures")
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _drift_count(record: Dict[str, Any], object_id: str, item: Dict[str, Any]) -> int:
    metadata = _runtime_metadata(record).get(object_id) or {}
    value = metadata.get("drift_count")
    if value is None:
        value = item.get("drift_count")
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _lifecycle_state(record: Dict[str, Any], object_id: str, item: Dict[str, Any]) -> str:
    metadata = _runtime_metadata(record).get(object_id) or {}
    value = metadata.get("lifecycle_state")
    if value is None:
        value = item.get("lifecycle_state")
    return _safe_str(value) or "unknown"


def _policy_reason(
    *,
    retained: bool,
    importance_score: float,
    retained_importance: float,
    retained_passes: int,
    verification_passes: int,
    archived_importance: float,
    archived_drift_count: int,
    archived_failure_count: int,
    drift_count: int,
    failure_count: int,
    lifecycle_state: str,
    compression_ratio: float | None,
    supported_by_selected_chunk: bool,
) -> str:
    if lifecycle_state in {"archived", "decayed"}:
        return f"lifecycle_{lifecycle_state}"
    if retained:
        if importance_score >= retained_importance and verification_passes >= retained_passes:
            return "retained_above_policy_threshold"
        if verification_passes < retained_passes:
            return "retained_but_insufficient_verification"
        return "retained_by_policy_floor"
    if not supported_by_selected_chunk:
        return "chunk_budget_pressure"
    if importance_score < retained_importance:
        return "below_retention_threshold"
    if drift_count >= archived_drift_count or failure_count >= archived_failure_count:
        return "archival_risk"
    if importance_score < archived_importance:
        return "below_archive_threshold"
    if compression_ratio is not None and compression_ratio < 0.5:
        return "budget_pressure"
    return "policy_default_drop"


def _budget_pressure(record: Dict[str, Any]) -> float:
    compression_ratio = _compression_ratio(record)
    if compression_ratio is None:
        return 0.0
    return round(max(0.0, min(1.0, 1.0 - compression_ratio)), 6)


def build_policy_trace(record: Dict[str, Any]) -> Dict[str, Any]:
    source_package = record.get("source_package") or {}
    compressed_package = record.get("compressed_package") or {}
    source_inventory = _extract_inventory(source_package)
    compressed_inventory = _extract_inventory(compressed_package)
    policy = _policy_dict(record)
    retained_importance = float(policy.get("lifecycle_retained_importance", 0.35) or 0.35)
    retained_passes = int(float(policy.get("lifecycle_retained_passes", 2) or 2))
    archived_importance = float(policy.get("lifecycle_archived_importance", 0.3) or 0.3)
    archived_drift_count = int(float(policy.get("lifecycle_archived_drift_count", 2) or 2))
    archived_failure_count = int(float(policy.get("lifecycle_archived_failure_count", 2) or 2))
    decayed_floor = float(policy.get("lifecycle_decayed_floor", 0.05) or 0.05)
    decayed_multiplier = float(policy.get("lifecycle_decayed_multiplier", 0.92) or 0.92)
    compression_ratio = _compression_ratio(record)
    budget_pressure = _budget_pressure(record)

    source_objects = _object_items(source_package)
    compressed_object_ids = {
        str(item.get("object_id") or item.get("signature") or "")
        for item in compressed_inventory.get("objects") or []
        if isinstance(item, dict)
    }
    source_memory = _safe_str(source_package.get("memory") or record.get("committed_memory") or record.get("representation") or "")
    selected_chunk_ids = [int(value) for value in (record.get("selected_chunk_ids") or []) if str(value).strip()]

    traces: List[Dict[str, Any]] = []
    for item in source_objects:
        object_id = _object_id(item)
        object_type = _safe_str(item.get("type") or item.get("object_type") or "fact") or "fact"
        value = _safe_str(item.get("value") or item.get("label") or "")
        supporting_chunk_ids = _supporting_chunk_ids(source_memory, value)
        supported_by_selected_chunk = any(chunk_id in selected_chunk_ids for chunk_id in supporting_chunk_ids)
        importance_score = _importance_score(record, object_id, item)
        verification_passes = _verification_passes(record, object_id, item)
        verification_failures = _verification_failures(record, object_id, item)
        drift_count = _drift_count(record, object_id, item)
        lifecycle_state = _lifecycle_state(record, object_id, item)
        retained = object_id in compressed_object_ids
        reason = _policy_reason(
            retained=retained,
            importance_score=importance_score,
            retained_importance=retained_importance,
            retained_passes=retained_passes,
            verification_passes=verification_passes,
            archived_importance=archived_importance,
            archived_drift_count=archived_drift_count,
            archived_failure_count=archived_failure_count,
            drift_count=drift_count,
            failure_count=verification_failures,
            lifecycle_state=lifecycle_state,
            compression_ratio=compression_ratio,
            supported_by_selected_chunk=supported_by_selected_chunk,
        )
        retention_margin = round(importance_score - retained_importance, 6)
        archive_margin = round(archived_importance - importance_score, 6)
        verification_margin = verification_passes - retained_passes
        traces.append(
            {
                "object_id": object_id,
                "type": object_type,
                "value": value,
                "importance_score": round(importance_score, 6),
                "retained": retained,
                "reason": reason,
                "supported_by_selected_chunk": supported_by_selected_chunk,
                "supporting_chunk_ids": supporting_chunk_ids,
                "selected_chunk_ids": selected_chunk_ids,
                "policy": {
                    "lifecycle_retained_importance": retained_importance,
                    "lifecycle_retained_passes": retained_passes,
                    "lifecycle_archived_importance": archived_importance,
                    "lifecycle_archived_drift_count": archived_drift_count,
                    "lifecycle_archived_failure_count": archived_failure_count,
                    "lifecycle_decayed_floor": decayed_floor,
                    "lifecycle_decayed_multiplier": decayed_multiplier,
                },
                "policy_signals": {
                    "compression_ratio": compression_ratio,
                    "budget_pressure": budget_pressure,
                    "verification_passes": verification_passes,
                    "verification_failures": verification_failures,
                    "drift_count": drift_count,
                    "lifecycle_state": lifecycle_state,
                },
                "margins": {
                    "retention_margin": retention_margin,
                    "archive_margin": archive_margin,
                    "verification_margin": verification_margin,
                },
            }
        )

    return {
        "schema_version": "policy_attribution.v1",
        "task_id": record.get("task_id"),
        "cycle": record.get("cycle"),
        "compression_suite": record.get("compression_suite"),
        "compression_scenario": record.get("compression_scenario") or record.get("task_id") or "unknown",
        "policy": policy,
        "traces": traces,
        "summary": {
            "object_count": len(traces),
            "retained_object_count": sum(1 for entry in traces if entry.get("retained")),
            "dropped_object_count": sum(1 for entry in traces if not entry.get("retained")),
            "budget_pressure": budget_pressure,
            "compression_ratio": compression_ratio,
            "mean_importance_score": (
                sum(float(entry.get("importance_score") or 0.0) for entry in traces) / len(traces) if traces else None
            ),
            "mean_retention_margin": (
                sum(float(entry.get("margins", {}).get("retention_margin") or 0.0) for entry in traces) / len(traces)
                if traces
                else None
            ),
            "mean_archive_margin": (
                sum(float(entry.get("margins", {}).get("archive_margin") or 0.0) for entry in traces) / len(traces)
                if traces
                else None
            ),
            "mean_verification_margin": (
                sum(float(entry.get("margins", {}).get("verification_margin") or 0.0) for entry in traces) / len(traces)
                if traces
                else None
            ),
            "reason_counts": dict(Counter(entry.get("reason") for entry in traces)),
        },
        "root_cause": {
            "dominant_policy_reason": Counter(entry.get("reason") for entry in traces).most_common(1)[0][0] if traces else None,
            "budget_pressure": budget_pressure,
            "compression_ratio": compression_ratio,
            "retained_importance": retained_importance,
            "retained_passes": retained_passes,
            "archived_importance": archived_importance,
            "archived_drift_count": archived_drift_count,
            "archived_failure_count": archived_failure_count,
            "decayed_floor": decayed_floor,
            "decayed_multiplier": decayed_multiplier,
        },
    }
