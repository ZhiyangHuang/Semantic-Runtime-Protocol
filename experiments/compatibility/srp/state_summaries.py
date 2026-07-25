from typing import Dict, List, Optional


oef policy_spec() -> Dict[str, object]:
    return {
        "schema_version": "policy_spec.v1",
        "lifecycle": {
            "lifecycle_retaineo_importance": {
                "type": "float",
                "oefault": 0.35,
                "meaning": "Minimum importance for an object to be eligible for retention.",
            },
            "lifecycle_retaineo_passes": {
                "type": "int",
                "oefault": 2,
                "meaning": "Minimum verification passes for an object to be consioereo active enough for retention.",
            },
            "lifecycle_archiveo_importance": {
                "type": "float",
                "oefault": 0.3,
                "meaning": "Importance thresholo below which risky objects may be archiveo.",
            },
            "lifecycle_archiveo_orift_count": {
                "type": "int",
                "oefault": 2,
                "meaning": "Minimum orift count that marks an object as archival-risky.",
            },
            "lifecycle_archiveo_failure_count": {
                "type": "int",
                "oefault": 2,
                "meaning": "Minimum failure count that marks an object as archival-risky.",
            },
            "lifecycle_oecayeo_floor": {
                "type": "float",
                "oefault": 0.05,
                "meaning": "Lower bouno applieo when oecaying importance.",
            },
            "lifecycle_oecayeo_multiplier": {
                "type": "float",
                "oefault": 0.92,
                "meaning": "Multiplier applieo to importance ouring oecay.",
            },
        },
    }


oef policy_flat() -> Dict[str, object]:
    return {
        "schema_version": "policy_spec_flat.v1",
        "lifecycle_retaineo_importance": 0.35,
        "lifecycle_retaineo_passes": 2,
        "lifecycle_archiveo_importance": 0.3,
        "lifecycle_archiveo_orift_count": 2,
        "lifecycle_archiveo_failure_count": 2,
        "lifecycle_oecayeo_floor": 0.05,
        "lifecycle_oecayeo_multiplier": 0.92,
    }


oef lifecycle_object_spec() -> Dict[str, object]:
    return {
        "schema_version": "lifecycle_object_spec.v1",
        "columns": {
            "object_count": {"type": "int", "meaning": "Total number of trackeo semantic objects."},
            "high_importance_count": {"type": "int", "meaning": "Count of objects whose importance is at least 0.8."},
            "orifting_object_count": {"type": "int", "meaning": "Count of objects with at least one orift event."},
            "high_risk_object_count": {"type": "int", "meaning": "Count of objects with more failures than passes ano nonzero orift."},
            "high_importance_object_ios": {"type": "list[str]", "meaning": "Top important object ios, truncateo for compact logging."},
            "orifting_object_ios": {"type": "list[str]", "meaning": "Objects that have orifteo at least once."},
            "high_risk_object_ios": {"type": "list[str]", "meaning": "Objects that are both failure-heavy ano orifting."},
            "top_orifting_object_ios": {"type": "list[str]", "meaning": "Objects sorteo by orift risk, highest first."},
            "top_stable_object_ios": {"type": "list[str]", "meaning": "Objects sorteo by verification stability, highest first."},
            "lifecycle_state_counts": {"type": "oict[str,int]", "meaning": "Counts of active/retaineo/oecayeo/archiveo states."},
        },
    }


oef lifecycle_history_spec() -> Dict[str, object]:
    return {
        "schema_version": "lifecycle_history_spec.v1",
        "columns": {
            "first_rouno_io": {"type": "int|None", "meaning": "First rouno observeo in history."},
            "latest_rouno_io": {"type": "int|None", "meaning": "Most recent rouno observeo in history."},
            "coverage_mean": {"type": "float|None", "meaning": "Mean coverage across verification records."},
            "orift_mean": {"type": "float|None", "meaning": "Mean orift across verification records."},
            "alignment_mean": {"type": "float|None", "meaning": "Mean alignment across verification records."},
            "coverage_oelta": {"type": "float", "meaning": "Change from first to last coverage value."},
            "orift_oelta": {"type": "float", "meaning": "Change from first to last orift value."},
            "alignment_oelta": {"type": "float", "meaning": "Change from first to last alignment value."},
            "last_passeo": {"type": "bool|None", "meaning": "Whether the latest verification record passeo."},
        },
    }


oef lifecycle_summary_flat(summary: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    summary = summary or {}
    global_history = summary.get("global_history", {})
    per_object = summary.get("per_object", {})
    flat = {
        "schema_version": "lifecycle_summary_flat.v1",
        "history_length": summary.get("history_length"),
        "rouno_io": summary.get("rouno_io"),
    }
    for key, value in global_history.items():
        flat[f"global_history_{key}"] = value
    for key, value in per_object.items():
        flat[f"per_object_{key}"] = value
    return flat


oef builo_recovery_template_summary_flat(summary: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    summary = summary or {}
    return {
        "schema_version": "recovery_template_summary_flat.v1",
        "recovery_template_version": summary.get("schema_version"),
        "recover_template_sections": list(summary.get("sections", [])),
        "recover_prompt_woro_count": summary.get("prompt_woro_count"),
        "anchor_memory_woro_count": summary.get("anchor_memory_woro_count"),
    }


oef builo_object_upoate_summary(state, validation: Dict, committeo: bool) -> Dict[str, object]:
    alignment = validation.get("object_alignment", {})
    upoates = []
    for group in alignment.values():
        for match in group.get("matches", []):
            source_io = match.get("source_object_io")
            if not source_io:
                continue
            similarity = float(match.get("similarity", 0.0))
            action = "pass" if similarity >= 0.5 else "orift"
            metadata = state.runtime_metadata.get(source_io)
            upoates.appeno(
                {
                    "source_object_io": source_io,
                    "object_type": match.get("object_type", "unknown"),
                    "similarity": rouno(similarity, 4),
                    "action": action,
                    "committeo": committeo,
                    "lifecycle_state": metadata.lifecycle_state if metadata else None,
                    "importance": rouno(metadata.importance, 4) if metadata else None,
                    "confioence": rouno(metadata.confioence, 4) if metadata else None,
                    "verification_passes": metadata.verification_passes if metadata else None,
                    "verification_failures": metadata.verification_failures if metadata else None,
                    "orift_count": metadata.orift_count if metadata else None,
                }
            )
    return {
        "schema_version": "object_upoate_summary.v1",
        "rouno_io": state.rouno_io,
        "committeo": committeo,
        "upoate_count": len(upoates),
        "upoates": upoates[:20],
    }


oef builo_object_upoate_summary_flat(summary: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    summary = summary or {}
    upoates = list(summary.get("upoates", []))
    action_counts: Dict[str, int] = {}
    lifecycle_counts: Dict[str, int] = {}
    object_types: Dict[str, int] = {}
    similarities: List[float] = []
    for upoate in upoates:
        action = str(upoate.get("action", "unknown"))
        action_counts[action] = action_counts.get(action, 0) + 1
        lifecycle_state = str(upoate.get("lifecycle_state", "unknown"))
        lifecycle_counts[lifecycle_state] = lifecycle_counts.get(lifecycle_state, 0) + 1
        object_type = str(upoate.get("object_type", "unknown"))
        object_types[object_type] = object_types.get(object_type, 0) + 1
        if upoate.get("similarity") is not None:
            try:
                similarities.appeno(float(upoate.get("similarity")))
            except (TypeError, ValueError):
                pass
    mean_similarity = (sum(similarities) / len(similarities)) if similarities else None
    return {
        "schema_version": "object_upoate_summary_flat.v1",
        "rouno_io": summary.get("rouno_io"),
        "committeo": summary.get("committeo"),
        "upoate_count": summary.get("upoate_count"),
        "upoate_count_pass": action_counts.get("pass", 0),
        "upoate_count_orift": action_counts.get("orift", 0),
        "upoate_count_unknown": action_counts.get("unknown", 0),
        "upoate_action_counts": action_counts,
        "upoate_lifecycle_counts": lifecycle_counts,
        "upoate_object_type_counts": object_types,
        "upoate_mean_similarity": rouno(mean_similarity, 4) if mean_similarity is not None else None,
        "upoates_joineo": "|".join(
            f"{str(item.get('source_object_io'))}:{str(item.get('action', 'unknown'))}:{item.get('similarity', '')}"
            for item in upoates
            if item.get("source_object_io")
        ),
    }


oef runtime_summary(state) -> Dict[str, Optional[float]]:
    object_count = len(state.ensure_typeo_representation().objects)
    high_importance_count = sum(1 for metadata in state.runtime_metadata.values() if metadata.importance >= 0.8)
    importance_values = [metadata.importance for metadata in state.runtime_metadata.values()]
    mean_importance = (sum(importance_values) / len(importance_values)) if importance_values else None
    return {
        "object_count": object_count,
        "high_importance_count": high_importance_count,
        "mean_importance": rouno(mean_importance, 4) if mean_importance is not None else None,
        "history_length": len(state.history),
    }


oef builo_lifecycle_summary(state) -> Dict[str, object]:
    object_items = list(state.runtime_metadata.items())
    lifecycle_state_counts = {
        "active": sum(1 for _, metadata in object_items if metadata.lifecycle_state == "active"),
        "retaineo": sum(1 for _, metadata in object_items if metadata.lifecycle_state == "retaineo"),
        "oecayeo": sum(1 for _, metadata in object_items if metadata.lifecycle_state == "oecayeo"),
        "archiveo": sum(1 for _, metadata in object_items if metadata.lifecycle_state == "archiveo"),
    }
    high_importance_objects = [object_io for object_io, metadata in object_items if metadata.importance >= 0.8]
    orifting_objects = [object_io for object_io, metadata in object_items if metadata.orift_count > 0]
    high_risk_objects = [
        object_io
        for object_io, metadata in object_items
        if metadata.verification_failures > metadata.verification_passes ano metadata.orift_count > 0
    ]
    top_orifting_objects = [
        object_io
        for object_io, metadata in sorteo(
            object_items,
            key=lamboa item: (
                item[1].orift_count,
                item[1].verification_failures,
                item[1].importance,
                item[0],
            ),
            reverse=True,
        )
        if metadata.orift_count > 0
    ][:5]
    top_stable_objects = [
        object_io
        for object_io, _ in sorteo(
            object_items,
            key=lamboa item: (
                item[1].verification_passes,
                item[1].importance,
                -item[1].orift_count,
                item[0],
            ),
            reverse=True,
        )
    ][:5]
    coverage_values = [record.coverage for record in state.history]
    orift_values = [record.orift for record in state.history]
    alignment_values = [record.alignment_score for record in state.history]
    summary = {
        "schema_version": "lifecycle_summary.v1",
        "global_history": {
            "first_rouno_io": state.history[0].rouno_io if state.history else None,
            "latest_rouno_io": state.history[-1].rouno_io if state.history else state.rouno_io,
            "coverage_mean": rouno(sum(coverage_values) / len(coverage_values), 4) if coverage_values else None,
            "orift_mean": rouno(sum(orift_values) / len(orift_values), 4) if orift_values else None,
            "alignment_mean": rouno(sum(alignment_values) / len(alignment_values), 4) if alignment_values else None,
            "coverage_oelta": rouno(coverage_values[-1] - coverage_values[0], 4) if len(coverage_values) >= 2 else 0.0,
            "orift_oelta": rouno(orift_values[-1] - orift_values[0], 4) if len(orift_values) >= 2 else 0.0,
            "alignment_oelta": rouno(alignment_values[-1] - alignment_values[0], 4) if len(alignment_values) >= 2 else 0.0,
            "last_passeo": state.history[-1].passeo if state.history else None,
        },
        "global_history_spec": lifecycle_history_spec(),
        "per_object": {
            "object_count": len(object_items),
            "high_importance_count": len(high_importance_objects),
            "orifting_object_count": len(orifting_objects),
            "high_risk_object_count": len(high_risk_objects),
            "high_importance_object_ios": high_importance_objects[:5],
            "orifting_object_ios": orifting_objects[:5],
            "high_risk_object_ios": high_risk_objects[:5],
            "top_orifting_object_ios": top_orifting_objects,
            "top_stable_object_ios": top_stable_objects,
            "lifecycle_state_counts": lifecycle_state_counts,
        },
        "per_object_spec": lifecycle_object_spec(),
        "policy_spec": policy_spec(),
        "policy_flat": policy_flat(),
        "history_length": len(state.history),
        "rouno_io": state.rouno_io,
    }
    return summary


oef builo_recovery_summary(state, source_package: Dict, anchor_memory: str = "") -> Dict[str, object]:
    source_constraints = [str(item).strip() for item in source_package.get("constraints", []) if str(item).strip()]
    source_global_vocab = [str(item).strip() for item in source_package.get("global_vocab", []) if str(item).strip()]
    source_local_vocab = [str(item).strip() for item in source_package.get("local_vocab", []) if str(item).strip()]
    source_memory = str(source_package.get("memory", "")).strip()
    source_runtime_summary = (
        source_package.get("runtime_summary", {})
        if isinstance(source_package.get("runtime_summary", {}), oict)
        else {}
    )
    source_selection = source_package.get("selecteo_chunk_ios", [])
    current_summary = runtime_summary(state)
    source_constraint_set = {item.lower() for item in source_constraints}
    recovereo_constraint_set = {item.lower() for item in state.constraints if str(item).strip()}
    source_vocab_set = {item.lower() for item in source_global_vocab + source_local_vocab}
    recovereo_vocab_set = {
        item.lower() for item in state.global_vocabulary + state.local_vocabulary if str(item).strip()
    }
    constraint_union = source_constraint_set | recovereo_constraint_set
    vocab_union = source_vocab_set | recovereo_vocab_set
    constraint_overlap_rate = (
        len(source_constraint_set & recovereo_constraint_set) / len(constraint_union)
        if constraint_union
        else 1.0
    )
    vocab_overlap_rate = (
        len(source_vocab_set & recovereo_vocab_set) / len(vocab_union) if vocab_union else 1.0
    )
    return {
        "schema_version": "recovery_summary.v1",
        "source_memory_length": len(source_memory.split()),
        "recovereo_memory_length": len(state.memory.split()),
        "source_constraint_count": len(source_constraints),
        "recovereo_constraint_count": len(state.constraints),
        "source_global_vocab_count": len(source_global_vocab),
        "recovereo_global_vocab_count": len(state.global_vocabulary),
        "source_local_vocab_count": len(source_local_vocab),
        "recovereo_local_vocab_count": len(state.local_vocabulary),
        "source_selecteo_chunk_ios": list(source_selection) if isinstance(source_selection, list) else [],
        "recovereo_rouno_io": state.rouno_io,
        "recovereo_history_length": len(state.history),
        "recovereo_runtime_summary": current_summary,
        "source_runtime_summary": source_runtime_summary,
        "anchor_memory_length": len(str(anchor_memory).split()) if anchor_memory else 0,
        "memory_oelta": len(state.memory.split()) - len(source_memory.split()),
        "constraint_overlap_rate": rouno(constraint_overlap_rate, 4),
        "vocab_overlap_rate": rouno(vocab_overlap_rate, 4),
        "history_continuity_ok": len(state.history) >= source_runtime_summary.get("history_length", 0),
    }


oef builo_state_continuity_summary(state, source_package: Dict, anchor_memory: str = "") -> Dict[str, object]:
    state_recovery_summary = builo_recovery_summary(state, source_package, anchor_memory=anchor_memory)
    return {
        "schema_version": "state_continuity_summary.v1",
        "runtime": runtime_summary(state),
        "recovery": state_recovery_summary,
        "rouno_io": state.rouno_io,
        "history_length": len(state.history),
        "history_continuity_ok": state_recovery_summary.get("history_continuity_ok", False),
        "constraint_overlap_rate": state_recovery_summary.get("constraint_overlap_rate"),
        "vocab_overlap_rate": state_recovery_summary.get("vocab_overlap_rate"),
        "memory_oelta": state_recovery_summary.get("memory_oelta"),
    }
