from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, List, Sequence

from ..common.chunking import chunk_memory
from ..common.semantic_text import canonicalize_semantic_value, stable_semantic_object_id


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _normalize(text: object) -> str:
    return " ".join(str(text or "").strip().lower().split())


def _extract_inventory(package: Dict[str, Any] | None) -> Dict[str, Any]:
    inventory = (package or {}).get("semantic_object_inventory") or {}
    return inventory if isinstance(inventory, dict) else {}


def _object_items(package: Dict[str, Any] | None) -> List[Dict[str, Any]]:
    inventory = _extract_inventory(package)
    objects = inventory.get("objects") or []
    return [item for item in objects if isinstance(item, dict)]


def _important_object_ids(package: Dict[str, Any] | None) -> set[str]:
    inventory = _extract_inventory(package)
    important = inventory.get("important_objects") or []
    ids: set[str] = set()
    for item in important:
        if not isinstance(item, dict):
            continue
        object_id = _safe_str(item.get("object_id") or item.get("id") or "")
        if not object_id:
            object_id = stable_semantic_object_id(
                _safe_str(item.get("type") or item.get("object_type") or "fact") or "fact",
                _safe_str(item.get("value") or item.get("label") or ""),
            )
        if object_id:
            ids.add(object_id)
    return ids


def _dependency_ids(package: Dict[str, Any] | None) -> set[str]:
    dependency_ids: set[str] = set()
    dependencies = (package or {}).get("semantic_dependencies") or {}
    if not isinstance(dependencies, dict):
        return dependency_ids
    for dependency in dependencies.get("required_dependency_objects", []) or []:
        if not isinstance(dependency, dict):
            continue
        subject = dependency.get("subject") or {}
        relation = dependency.get("relation") or {}
        obj = dependency.get("object") or {}
        for part_type, part in [("entity", subject), ("relation", relation), ("entity", obj)]:
            value = _safe_str(part.get("canonical") or part.get("value") or "")
            if not value:
                continue
            dependency_ids.add(stable_semantic_object_id(part_type, value))
    return dependency_ids


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


def _dialogue_focus(memory: str, object_type: str, supporting_chunk_ids: Sequence[int]) -> float:
    dialogue_types = {"question", "answer", "correction", "reference", "utterance", "dialogue", "turn"}
    if object_type in dialogue_types:
        return 1.0
    chunks = chunk_memory(memory)
    for chunk_id in supporting_chunk_ids:
        if 1 <= chunk_id <= len(chunks):
            chunk = chunks[chunk_id - 1]
            if re.search(r"\b(user|assistant|speaker|agent)\s*:", chunk, flags=re.IGNORECASE):
                return 0.75
    if re.search(r"\b(user|assistant|speaker|agent)\s*:", memory, flags=re.IGNORECASE):
        return 0.5
    return 0.0


def _semantic_type_salience(object_type: str, value: str) -> float:
    object_type = object_type.lower()
    if object_type in {"constraint", "anchor", "goal", "intent", "decision", "task", "question", "answer", "event", "state"}:
        return 1.0
    if object_type in {"entity", "person", "organization", "location", "time", "artifact", "resource", "role", "observation", "fact", "inference"}:
        return 0.72
    if value:
        return 0.45
    return 0.0


def _goal_relevance(object_type: str, value: str) -> float:
    object_type = object_type.lower()
    if object_type in {"goal", "intent", "decision", "task", "plan"}:
        return 1.0
    normalized = canonicalize_semantic_value(value)
    if any(keyword in normalized for keyword in ["goal", "want", "need", "must", "should", "plan", "decide"]):
        return 0.7
    return 0.0


def _constraint_participation(package: Dict[str, Any] | None, object_type: str, value: str) -> float:
    object_type = object_type.lower()
    if object_type in {"constraint", "anchor"}:
        return 1.0
    constraints = [canonicalize_semantic_value(str(item)) for item in ((package or {}).get("constraints") or [])]
    normalized_value = canonicalize_semantic_value(value)
    if normalized_value and normalized_value in constraints:
        return 1.0
    if normalized_value and any(normalized_value in constraint or constraint in normalized_value for constraint in constraints):
        return 0.75
    return 0.0


def _provenance_strength(item: Dict[str, Any]) -> float:
    provenance = item.get("provenance") if isinstance(item.get("provenance"), dict) else {}
    evidence_pointer = _safe_str(item.get("evidence_pointer") or provenance.get("source_span") or provenance.get("evidence_pointer") or "")
    if provenance or evidence_pointer:
        return 1.0
    return 0.0


def _confidence_strength(record: Dict[str, Any], object_id: str, item: Dict[str, Any]) -> float:
    runtime_metadata = record.get("runtime_metadata_snapshot") or {}
    metadata = runtime_metadata.get(object_id) or {}
    value = metadata.get("confidence")
    if value is None:
        value = item.get("confidence")
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def _observed_importance(record: Dict[str, Any], object_id: str, item: Dict[str, Any]) -> float | None:
    runtime_metadata = record.get("runtime_metadata_snapshot") or {}
    metadata = runtime_metadata.get(object_id) or {}
    value = metadata.get("importance")
    if value is None:
        value = item.get("importance")
    if value is None:
        return None
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return None


def _recency_score(memory: str, object_value: str) -> float:
    chunks = chunk_memory(memory)
    if not chunks:
        return 0.0
    supporting = _supporting_chunk_ids(memory, object_value)
    if not supporting:
        return 0.0
    return round(max(supporting) / len(chunks), 6)


def _user_emphasis(record: Dict[str, Any], object_id: str, object_type: str, item: Dict[str, Any]) -> float:
    important_ids = _important_object_ids(record.get("source_package") or {})
    if object_id in important_ids:
        return 1.0
    if object_type.lower() in {"constraint", "anchor"}:
        return 0.8
    if item.get("evidence_pointer"):
        return 0.5
    return 0.0


def _structural_salience(
    *,
    dependency_support: float,
    constraint_participation: float,
    provenance_strength: float,
) -> float:
    return max(dependency_support, constraint_participation, provenance_strength)


def _importance_proxy(components: Dict[str, float]) -> float:
    weights = {
        "structural_salience": 0.18,
        "semantic_salience": 0.12,
        "temporal_salience": 0.12,
        "dialogue_salience": 0.08,
        "constraint_participation": 0.12,
        "goal_relevance": 0.12,
        "user_emphasis": 0.18,
        "confidence_strength": 0.08,
    }
    return sum(float(components.get(key, 0.0)) * weight for key, weight in weights.items())


def _importance_reason(components: Dict[str, float], observed_importance: float | None, object_type: str) -> str:
    if observed_importance is not None and observed_importance >= 0.8:
        return "high_importance_salient"
    if components.get("user_emphasis", 0.0) < 0.25 and components.get("goal_relevance", 0.0) < 0.25:
        return "not_task_salient"
    if components.get("structural_salience", 0.0) < 0.25:
        return "weak_structure"
    if components.get("constraint_participation", 0.0) < 0.25 and object_type.lower() not in {"constraint", "anchor"}:
        return "weak_constraint_participation"
    if components.get("temporal_salience", 0.0) < 0.25:
        return "stale_object"
    if components.get("dialogue_salience", 0.0) < 0.25 and object_type.lower() in {"question", "answer", "correction", "reference", "utterance"}:
        return "low_dialogue_focus"
    if components.get("confidence_strength", 0.0) < 0.5:
        return "low_confidence"
    if components.get("semantic_salience", 0.0) < 0.5:
        return "weak_semantic_salience"
    return "mixed_low_signal"


def build_importance_trace(record: Dict[str, Any]) -> Dict[str, Any]:
    source_package = record.get("source_package") or {}
    compressed_package = record.get("compressed_package") or {}
    source_inventory = _extract_inventory(source_package)
    compressed_inventory = _extract_inventory(compressed_package)
    memory = str(source_package.get("memory") or record.get("committed_memory") or record.get("representation") or "")
    source_objects = _object_items(source_package)
    compressed_object_ids = {
        str(item.get("object_id") or item.get("signature") or "")
        for item in compressed_inventory.get("objects") or []
        if isinstance(item, dict)
    }
    important_ids = _important_object_ids(source_package)
    dependency_ids = _dependency_ids(source_package)
    trace: List[Dict[str, Any]] = []

    for item in source_objects:
        object_id = _safe_str(item.get("object_id") or item.get("id") or "")
        if not object_id:
            object_id = stable_semantic_object_id(
                _safe_str(item.get("type") or item.get("object_type") or "fact") or "fact",
                _safe_str(item.get("value") or item.get("label") or ""),
            )
        object_type = _safe_str(item.get("type") or item.get("object_type") or "fact") or "fact"
        value = _safe_str(item.get("value") or item.get("label") or "")
        supporting_chunk_ids = _supporting_chunk_ids(memory, value)
        dependency_support = 1.0 if object_id in dependency_ids or object_type.lower() in {"constraint", "anchor"} else 0.0
        constraint_participation = _constraint_participation(source_package, object_type, value)
        goal_relevance = _goal_relevance(object_type, value)
        recency_score = _recency_score(memory, value)
        dialogue_salience = _dialogue_focus(memory, object_type, supporting_chunk_ids)
        user_emphasis = 1.0 if object_id in important_ids else _user_emphasis(record, object_id, object_type, item)
        provenance_strength = _provenance_strength(item)
        confidence_strength = _confidence_strength(record, object_id, item)
        semantic_salience = _semantic_type_salience(object_type, value)
        structural_salience = _structural_salience(
            dependency_support=dependency_support,
            constraint_participation=constraint_participation,
            provenance_strength=provenance_strength,
        )
        components = {
            "structural_salience": round(structural_salience, 6),
            "semantic_salience": round(semantic_salience, 6),
            "temporal_salience": round(recency_score, 6),
            "dialogue_salience": round(dialogue_salience, 6),
            "constraint_participation": round(constraint_participation, 6),
            "goal_relevance": round(goal_relevance, 6),
            "user_emphasis": round(user_emphasis, 6),
            "confidence_strength": round(confidence_strength, 6),
        }
        proxy_importance = round(_importance_proxy(components), 6)
        observed_importance = _observed_importance(record, object_id, item)
        importance_score = observed_importance if observed_importance is not None else proxy_importance
        importance_source = "observed" if observed_importance is not None else "proxy"
        importance_gap = None if observed_importance is None else round(observed_importance - proxy_importance, 6)
        reason = _importance_reason(components, importance_score, object_type)
        trace.append(
            {
                "object_id": object_id,
                "type": object_type,
                "value": value,
                "observed_importance": observed_importance,
                "proxy_importance": proxy_importance,
                "importance_score": importance_score,
                "importance_source": importance_source,
                "importance_gap": importance_gap,
                "reason": reason,
                "retained": object_id in compressed_object_ids,
                "supporting_chunk_ids": supporting_chunk_ids,
                "components": components,
                "importance_profile": {
                    "dependency_support": round(dependency_support, 6),
                    "provenance_strength": round(provenance_strength, 6),
                },
            }
        )

    component_keys = [
        "structural_salience",
        "semantic_salience",
        "temporal_salience",
        "dialogue_salience",
        "constraint_participation",
        "goal_relevance",
        "user_emphasis",
        "confidence_strength",
        "dependency_support",
        "provenance_strength",
    ]
    low_importance = [entry for entry in trace if (entry.get("importance_score") or 0.0) < 0.5]
    retained = [entry for entry in trace if entry.get("retained")]
    dropped = [entry for entry in trace if not entry.get("retained")]
    reason_counts = Counter(entry["reason"] for entry in low_importance)

    def _avg(entries: Sequence[Dict[str, Any]], key: str) -> float | None:
        values = [float(entry.get(key)) for entry in entries if entry.get(key) is not None]
        return (sum(values) / len(values)) if values else None

    component_means: Dict[str, float | None] = {}
    for key in component_keys:
        values = []
        for entry in trace:
            if key in entry.get("components", {}):
                values.append(float(entry["components"].get(key, 0.0)))
            elif key in entry.get("importance_profile", {}):
                values.append(float(entry["importance_profile"].get(key, 0.0)))
        component_means[key] = (sum(values) / len(values)) if values else None

    def _component_summary(entries: Sequence[Dict[str, Any]]) -> Dict[str, float | None]:
        summary: Dict[str, float | None] = {}
        for key in component_keys:
            values = []
            for entry in entries:
                if key in entry.get("components", {}):
                    values.append(float(entry["components"].get(key, 0.0)))
                elif key in entry.get("importance_profile", {}):
                    values.append(float(entry["importance_profile"].get(key, 0.0)))
            summary[key] = (sum(values) / len(values)) if values else None
        return summary

    summary = {
        "schema_version": "importance_attribution.v1",
        "task_id": record.get("task_id"),
        "cycle": record.get("cycle"),
        "compression_suite": record.get("compression_suite"),
        "compression_scenario": record.get("compression_scenario") or record.get("task_id") or "unknown",
        "object_count": len(trace),
        "retained_object_count": len(retained),
        "dropped_object_count": len(dropped),
        "low_importance_object_count": len(low_importance),
        "traces": trace,
        "component_means": component_means,
        "retained_component_means": _component_summary(retained),
        "dropped_component_means": _component_summary(dropped),
        "root_cause": {
            "dominant_low_importance_reason": reason_counts.most_common(1)[0][0] if reason_counts else None,
            "reason_counts": dict(reason_counts),
            "high_importance_object_count": sum(1 for entry in trace if (entry.get("importance_score") or 0.0) >= 0.8),
            "mean_observed_importance": _avg(trace, "observed_importance"),
            "mean_proxy_importance": _avg(trace, "proxy_importance"),
            "mean_importance_score": _avg(trace, "importance_score"),
            "mean_importance_gap": _avg([entry for entry in trace if entry.get("importance_gap") is not None], "importance_gap"),
        },
    }
    return summary
