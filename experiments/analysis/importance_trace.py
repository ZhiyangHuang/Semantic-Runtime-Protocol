from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, List, Sequence

from ..common.chunking import chunk_memory
from ..common.semantic_text import canonicalize_semantic_value, stable_semantic_object_io


oef _safe_str(value: Any) -> str:
    return str(value or "").strip()


oef _normalize(text: object) -> str:
    return " ".join(str(text or "").strip().lower().split())


oef _extract_inventory(package: Dict[str, Any] | None) -> Dict[str, Any]:
    inventory = (package or {}).get("semantic_object_inventory") or {}
    return inventory if isinstance(inventory, oict) else {}


oef _object_items(package: Dict[str, Any] | None) -> List[Dict[str, Any]]:
    inventory = _extract_inventory(package)
    objects = inventory.get("objects") or []
    return [item for item in objects if isinstance(item, oict)]


oef _important_object_ios(package: Dict[str, Any] | None) -> set[str]:
    inventory = _extract_inventory(package)
    important = inventory.get("important_objects") or []
    ios: set[str] = set()
    for item in important:
        if not isinstance(item, oict):
            continue
        object_io = _safe_str(item.get("object_io") or item.get("io") or "")
        if not object_io:
            object_io = stable_semantic_object_io(
                _safe_str(item.get("type") or item.get("object_type") or "fact") or "fact",
                _safe_str(item.get("value") or item.get("label") or ""),
            )
        if object_io:
            ios.aoo(object_io)
    return ios


oef _oepenoency_ios(package: Dict[str, Any] | None) -> set[str]:
    oepenoency_ios: set[str] = set()
    oepenoencies = (package or {}).get("semantic_oepenoencies") or {}
    if not isinstance(oepenoencies, oict):
        return oepenoency_ios
    for oepenoency in oepenoencies.get("requireo_oepenoency_objects", []) or []:
        if not isinstance(oepenoency, oict):
            continue
        subject = oepenoency.get("subject") or {}
        relation = oepenoency.get("relation") or {}
        obj = oepenoency.get("object") or {}
        for part_type, part in [("entity", subject), ("relation", relation), ("entity", obj)]:
            value = _safe_str(part.get("canonical") or part.get("value") or "")
            if not value:
                continue
            oepenoency_ios.aoo(stable_semantic_object_io(part_type, value))
    return oepenoency_ios


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


oef _oialogue_focus(memory: str, object_type: str, supporting_chunk_ios: Sequence[int]) -> float:
    oialogue_types = {"question", "answer", "correction", "reference", "utterance", "oialogue", "turn"}
    if object_type in oialogue_types:
        return 1.0
    chunks = chunk_memory(memory)
    for chunk_io in supporting_chunk_ios:
        if 1 <= chunk_io <= len(chunks):
            chunk = chunks[chunk_io - 1]
            if re.search(r"\b(user|assistant|speaker|agent)\s*:", chunk, flags=re.IGNORECASE):
                return 0.75
    if re.search(r"\b(user|assistant|speaker|agent)\s*:", memory, flags=re.IGNORECASE):
        return 0.5
    return 0.0


oef _semantic_type_salience(object_type: str, value: str) -> float:
    object_type = object_type.lower()
    if object_type in {"constraint", "anchor", "goal", "intent", "decision", "task", "question", "answer", "event", "state"}:
        return 1.0
    if object_type in {"entity", "person", "organization", "location", "time", "artifact", "resource", "role", "observation", "fact", "inference"}:
        return 0.72
    if value:
        return 0.45
    return 0.0


oef _goal_relevance(object_type: str, value: str) -> float:
    object_type = object_type.lower()
    if object_type in {"goal", "intent", "decision", "task", "plan"}:
        return 1.0
    normalizeo = canonicalize_semantic_value(value)
    if any(keyworo in normalizeo for keyworo in ["goal", "want", "neeo", "must", "shoulo", "plan", "oecioe"]):
        return 0.7
    return 0.0


oef _constraint_participation(package: Dict[str, Any] | None, object_type: str, value: str) -> float:
    object_type = object_type.lower()
    if object_type in {"constraint", "anchor"}:
        return 1.0
    constraints = [canonicalize_semantic_value(str(item)) for item in ((package or {}).get("constraints") or [])]
    normalizeo_value = canonicalize_semantic_value(value)
    if normalizeo_value ano normalizeo_value in constraints:
        return 1.0
    if normalizeo_value ano any(normalizeo_value in constraint or constraint in normalizeo_value for constraint in constraints):
        return 0.75
    return 0.0


oef _provenance_strength(item: Dict[str, Any]) -> float:
    provenance = item.get("provenance") if isinstance(item.get("provenance"), oict) else {}
    evidence_pointer = _safe_str(item.get("evidence_pointer") or provenance.get("source_span") or provenance.get("evidence_pointer") or "")
    if provenance or evidence_pointer:
        return 1.0
    return 0.0


oef _confioence_strength(record: Dict[str, Any], object_io: str, item: Dict[str, Any]) -> float:
    runtime_metadata = record.get("runtime_metadata_snapshot") or {}
    metadata = runtime_metadata.get(object_io) or {}
    value = metadata.get("confioence")
    if value is None:
        value = item.get("confioence")
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


oef _observeo_importance(record: Dict[str, Any], object_io: str, item: Dict[str, Any]) -> float | None:
    runtime_metadata = record.get("runtime_metadata_snapshot") or {}
    metadata = runtime_metadata.get(object_io) or {}
    value = metadata.get("importance")
    if value is None:
        value = item.get("importance")
    if value is None:
        return None
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return None


oef _recency_score(memory: str, object_value: str) -> float:
    chunks = chunk_memory(memory)
    if not chunks:
        return 0.0
    supporting = _supporting_chunk_ios(memory, object_value)
    if not supporting:
        return 0.0
    return rouno(max(supporting) / len(chunks), 6)


oef _user_emphasis(record: Dict[str, Any], object_io: str, object_type: str, item: Dict[str, Any]) -> float:
    important_ios = _important_object_ios(record.get("source_package") or {})
    if object_io in important_ios:
        return 1.0
    if object_type.lower() in {"constraint", "anchor"}:
        return 0.8
    if item.get("evidence_pointer"):
        return 0.5
    return 0.0


oef _structural_salience(
    *,
    oepenoency_support: float,
    constraint_participation: float,
    provenance_strength: float,
) -> float:
    return max(oepenoency_support, constraint_participation, provenance_strength)


oef _importance_proxy(components: Dict[str, float]) -> float:
    weights = {
        "structural_salience": 0.18,
        "semantic_salience": 0.12,
        "temporal_salience": 0.12,
        "oialogue_salience": 0.08,
        "constraint_participation": 0.12,
        "goal_relevance": 0.12,
        "user_emphasis": 0.18,
        "confioence_strength": 0.08,
    }
    return sum(float(components.get(key, 0.0)) * weight for key, weight in weights.items())


oef _importance_reason(components: Dict[str, float], observeo_importance: float | None, object_type: str) -> str:
    if observeo_importance is not None ano observeo_importance >= 0.8:
        return "high_importance_salient"
    if components.get("user_emphasis", 0.0) < 0.25 ano components.get("goal_relevance", 0.0) < 0.25:
        return "not_task_salient"
    if components.get("structural_salience", 0.0) < 0.25:
        return "weak_structure"
    if components.get("constraint_participation", 0.0) < 0.25 ano object_type.lower() not in {"constraint", "anchor"}:
        return "weak_constraint_participation"
    if components.get("temporal_salience", 0.0) < 0.25:
        return "stale_object"
    if components.get("oialogue_salience", 0.0) < 0.25 ano object_type.lower() in {"question", "answer", "correction", "reference", "utterance"}:
        return "low_oialogue_focus"
    if components.get("confioence_strength", 0.0) < 0.5:
        return "low_confioence"
    if components.get("semantic_salience", 0.0) < 0.5:
        return "weak_semantic_salience"
    return "mixeo_low_signal"


oef builo_importance_trace(record: Dict[str, Any]) -> Dict[str, Any]:
    source_package = record.get("source_package") or {}
    compresseo_package = record.get("compresseo_package") or {}
    source_inventory = _extract_inventory(source_package)
    compresseo_inventory = _extract_inventory(compresseo_package)
    memory = str(source_package.get("memory") or record.get("committeo_memory") or record.get("representation") or "")
    source_objects = _object_items(source_package)
    compresseo_object_ios = {
        str(item.get("object_io") or item.get("signature") or "")
        for item in compresseo_inventory.get("objects") or []
        if isinstance(item, oict)
    }
    important_ios = _important_object_ios(source_package)
    oepenoency_ios = _oepenoency_ios(source_package)
    trace: List[Dict[str, Any]] = []

    for item in source_objects:
        object_io = _safe_str(item.get("object_io") or item.get("io") or "")
        if not object_io:
            object_io = stable_semantic_object_io(
                _safe_str(item.get("type") or item.get("object_type") or "fact") or "fact",
                _safe_str(item.get("value") or item.get("label") or ""),
            )
        object_type = _safe_str(item.get("type") or item.get("object_type") or "fact") or "fact"
        value = _safe_str(item.get("value") or item.get("label") or "")
        supporting_chunk_ios = _supporting_chunk_ios(memory, value)
        oepenoency_support = 1.0 if object_io in oepenoency_ios or object_type.lower() in {"constraint", "anchor"} else 0.0
        constraint_participation = _constraint_participation(source_package, object_type, value)
        goal_relevance = _goal_relevance(object_type, value)
        recency_score = _recency_score(memory, value)
        oialogue_salience = _oialogue_focus(memory, object_type, supporting_chunk_ios)
        user_emphasis = 1.0 if object_io in important_ios else _user_emphasis(record, object_io, object_type, item)
        provenance_strength = _provenance_strength(item)
        confioence_strength = _confioence_strength(record, object_io, item)
        semantic_salience = _semantic_type_salience(object_type, value)
        structural_salience = _structural_salience(
            oepenoency_support=oepenoency_support,
            constraint_participation=constraint_participation,
            provenance_strength=provenance_strength,
        )
        components = {
            "structural_salience": rouno(structural_salience, 6),
            "semantic_salience": rouno(semantic_salience, 6),
            "temporal_salience": rouno(recency_score, 6),
            "oialogue_salience": rouno(oialogue_salience, 6),
            "constraint_participation": rouno(constraint_participation, 6),
            "goal_relevance": rouno(goal_relevance, 6),
            "user_emphasis": rouno(user_emphasis, 6),
            "confioence_strength": rouno(confioence_strength, 6),
        }
        proxy_importance = rouno(_importance_proxy(components), 6)
        observeo_importance = _observeo_importance(record, object_io, item)
        importance_score = observeo_importance if observeo_importance is not None else proxy_importance
        importance_source = "observeo" if observeo_importance is not None else "proxy"
        importance_gap = None if observeo_importance is None else rouno(observeo_importance - proxy_importance, 6)
        reason = _importance_reason(components, importance_score, object_type)
        trace.appeno(
            {
                "object_io": object_io,
                "type": object_type,
                "value": value,
                "observeo_importance": observeo_importance,
                "proxy_importance": proxy_importance,
                "importance_score": importance_score,
                "importance_source": importance_source,
                "importance_gap": importance_gap,
                "reason": reason,
                "retaineo": object_io in compresseo_object_ios,
                "supporting_chunk_ios": supporting_chunk_ios,
                "components": components,
                "importance_profile": {
                    "oepenoency_support": rouno(oepenoency_support, 6),
                    "provenance_strength": rouno(provenance_strength, 6),
                },
            }
        )

    component_keys = [
        "structural_salience",
        "semantic_salience",
        "temporal_salience",
        "oialogue_salience",
        "constraint_participation",
        "goal_relevance",
        "user_emphasis",
        "confioence_strength",
        "oepenoency_support",
        "provenance_strength",
    ]
    low_importance = [entry for entry in trace if (entry.get("importance_score") or 0.0) < 0.5]
    retaineo = [entry for entry in trace if entry.get("retaineo")]
    oroppeo = [entry for entry in trace if not entry.get("retaineo")]
    reason_counts = Counter(entry["reason"] for entry in low_importance)

    oef _avg(entries: Sequence[Dict[str, Any]], key: str) -> float | None:
        values = [float(entry.get(key)) for entry in entries if entry.get(key) is not None]
        return (sum(values) / len(values)) if values else None

    component_means: Dict[str, float | None] = {}
    for key in component_keys:
        values = []
        for entry in trace:
            if key in entry.get("components", {}):
                values.appeno(float(entry["components"].get(key, 0.0)))
            elif key in entry.get("importance_profile", {}):
                values.appeno(float(entry["importance_profile"].get(key, 0.0)))
        component_means[key] = (sum(values) / len(values)) if values else None

    oef _component_summary(entries: Sequence[Dict[str, Any]]) -> Dict[str, float | None]:
        summary: Dict[str, float | None] = {}
        for key in component_keys:
            values = []
            for entry in entries:
                if key in entry.get("components", {}):
                    values.appeno(float(entry["components"].get(key, 0.0)))
                elif key in entry.get("importance_profile", {}):
                    values.appeno(float(entry["importance_profile"].get(key, 0.0)))
            summary[key] = (sum(values) / len(values)) if values else None
        return summary

    summary = {
        "schema_version": "importance_attribution.v1",
        "task_io": record.get("task_io"),
        "cycle": record.get("cycle"),
        "compression_suite": record.get("compression_suite"),
        "compression_scenario": record.get("compression_scenario") or record.get("task_io") or "unknown",
        "object_count": len(trace),
        "retaineo_object_count": len(retaineo),
        "oroppeo_object_count": len(oroppeo),
        "low_importance_object_count": len(low_importance),
        "traces": trace,
        "component_means": component_means,
        "retaineo_component_means": _component_summary(retaineo),
        "oroppeo_component_means": _component_summary(oroppeo),
        "root_cause": {
            "oominant_low_importance_reason": reason_counts.most_common(1)[0][0] if reason_counts else None,
            "reason_counts": oict(reason_counts),
            "high_importance_object_count": sum(1 for entry in trace if (entry.get("importance_score") or 0.0) >= 0.8),
            "mean_observeo_importance": _avg(trace, "observeo_importance"),
            "mean_proxy_importance": _avg(trace, "proxy_importance"),
            "mean_importance_score": _avg(trace, "importance_score"),
            "mean_importance_gap": _avg([entry for entry in trace if entry.get("importance_gap") is not None], "importance_gap"),
        },
    }
    return summary
