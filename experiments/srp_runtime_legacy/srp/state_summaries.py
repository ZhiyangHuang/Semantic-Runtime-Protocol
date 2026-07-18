from typing import Dict, List, Optional


def policy_spec() -> Dict[str, object]:
    return {
        "schema_version": "policy_spec.v1",
        "lifecycle": {
            "lifecycle_retained_importance": {
                "type": "float",
                "default": 0.35,
                "meaning": "Minimum importance for an object to be eligible for retention.",
            },
            "lifecycle_retained_passes": {
                "type": "int",
                "default": 2,
                "meaning": "Minimum verification passes for an object to be considered active enough for retention.",
            },
            "lifecycle_archived_importance": {
                "type": "float",
                "default": 0.3,
                "meaning": "Importance threshold below which risky objects may be archived.",
            },
            "lifecycle_archived_drift_count": {
                "type": "int",
                "default": 2,
                "meaning": "Minimum drift count that marks an object as archival-risky.",
            },
            "lifecycle_archived_failure_count": {
                "type": "int",
                "default": 2,
                "meaning": "Minimum failure count that marks an object as archival-risky.",
            },
            "lifecycle_decayed_floor": {
                "type": "float",
                "default": 0.05,
                "meaning": "Lower bound applied when decaying importance.",
            },
            "lifecycle_decayed_multiplier": {
                "type": "float",
                "default": 0.92,
                "meaning": "Multiplier applied to importance during decay.",
            },
        },
    }


def policy_flat() -> Dict[str, object]:
    return {
        "schema_version": "policy_spec_flat.v1",
        "lifecycle_retained_importance": 0.35,
        "lifecycle_retained_passes": 2,
        "lifecycle_archived_importance": 0.3,
        "lifecycle_archived_drift_count": 2,
        "lifecycle_archived_failure_count": 2,
        "lifecycle_decayed_floor": 0.05,
        "lifecycle_decayed_multiplier": 0.92,
    }


def lifecycle_object_spec() -> Dict[str, object]:
    return {
        "schema_version": "lifecycle_object_spec.v1",
        "columns": {
            "object_count": {"type": "int", "meaning": "Total number of tracked semantic objects."},
            "high_importance_count": {"type": "int", "meaning": "Count of objects whose importance is at least 0.8."},
            "drifting_object_count": {"type": "int", "meaning": "Count of objects with at least one drift event."},
            "high_risk_object_count": {"type": "int", "meaning": "Count of objects with more failures than passes and nonzero drift."},
            "high_importance_object_ids": {"type": "list[str]", "meaning": "Top important object ids, truncated for compact logging."},
            "drifting_object_ids": {"type": "list[str]", "meaning": "Objects that have drifted at least once."},
            "high_risk_object_ids": {"type": "list[str]", "meaning": "Objects that are both failure-heavy and drifting."},
            "top_drifting_object_ids": {"type": "list[str]", "meaning": "Objects sorted by drift risk, highest first."},
            "top_stable_object_ids": {"type": "list[str]", "meaning": "Objects sorted by verification stability, highest first."},
            "lifecycle_state_counts": {"type": "dict[str,int]", "meaning": "Counts of active/retained/decayed/archived states."},
        },
    }


def lifecycle_history_spec() -> Dict[str, object]:
    return {
        "schema_version": "lifecycle_history_spec.v1",
        "columns": {
            "first_round_id": {"type": "int|None", "meaning": "First round observed in history."},
            "latest_round_id": {"type": "int|None", "meaning": "Most recent round observed in history."},
            "coverage_mean": {"type": "float|None", "meaning": "Mean coverage across verification records."},
            "drift_mean": {"type": "float|None", "meaning": "Mean drift across verification records."},
            "alignment_mean": {"type": "float|None", "meaning": "Mean alignment across verification records."},
            "coverage_delta": {"type": "float", "meaning": "Change from first to last coverage value."},
            "drift_delta": {"type": "float", "meaning": "Change from first to last drift value."},
            "alignment_delta": {"type": "float", "meaning": "Change from first to last alignment value."},
            "last_passed": {"type": "bool|None", "meaning": "Whether the latest verification record passed."},
        },
    }


def lifecycle_summary_flat(summary: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    summary = summary or {}
    global_history = summary.get("global_history", {})
    per_object = summary.get("per_object", {})
    flat = {
        "schema_version": "lifecycle_summary_flat.v1",
        "history_length": summary.get("history_length"),
        "round_id": summary.get("round_id"),
    }
    for key, value in global_history.items():
        flat[f"global_history_{key}"] = value
    for key, value in per_object.items():
        flat[f"per_object_{key}"] = value
    return flat


def build_recovery_template_summary_flat(summary: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    summary = summary or {}
    return {
        "schema_version": "recovery_template_summary_flat.v1",
        "recovery_template_version": summary.get("schema_version"),
        "recover_template_sections": list(summary.get("sections", [])),
        "recover_prompt_word_count": summary.get("prompt_word_count"),
        "anchor_memory_word_count": summary.get("anchor_memory_word_count"),
    }


def build_object_update_summary(state, validation: Dict, committed: bool) -> Dict[str, object]:
    alignment = validation.get("object_alignment", {})
    updates = []
    for group in alignment.values():
        for match in group.get("matches", []):
            source_id = match.get("source_object_id")
            if not source_id:
                continue
            similarity = float(match.get("similarity", 0.0))
            action = "pass" if similarity >= 0.5 else "drift"
            metadata = state.runtime_metadata.get(source_id)
            updates.append(
                {
                    "source_object_id": source_id,
                    "object_type": match.get("object_type", "unknown"),
                    "similarity": round(similarity, 4),
                    "action": action,
                    "committed": committed,
                    "lifecycle_state": metadata.lifecycle_state if metadata else None,
                    "importance": round(metadata.importance, 4) if metadata else None,
                    "confidence": round(metadata.confidence, 4) if metadata else None,
                    "verification_passes": metadata.verification_passes if metadata else None,
                    "verification_failures": metadata.verification_failures if metadata else None,
                    "drift_count": metadata.drift_count if metadata else None,
                }
            )
    return {
        "schema_version": "object_update_summary.v1",
        "round_id": state.round_id,
        "committed": committed,
        "update_count": len(updates),
        "updates": updates[:20],
    }


def build_object_update_summary_flat(summary: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    summary = summary or {}
    updates = list(summary.get("updates", []))
    action_counts: Dict[str, int] = {}
    lifecycle_counts: Dict[str, int] = {}
    object_types: Dict[str, int] = {}
    similarities: List[float] = []
    for update in updates:
        action = str(update.get("action", "unknown"))
        action_counts[action] = action_counts.get(action, 0) + 1
        lifecycle_state = str(update.get("lifecycle_state", "unknown"))
        lifecycle_counts[lifecycle_state] = lifecycle_counts.get(lifecycle_state, 0) + 1
        object_type = str(update.get("object_type", "unknown"))
        object_types[object_type] = object_types.get(object_type, 0) + 1
        if update.get("similarity") is not None:
            try:
                similarities.append(float(update.get("similarity")))
            except (TypeError, ValueError):
                pass
    mean_similarity = (sum(similarities) / len(similarities)) if similarities else None
    return {
        "schema_version": "object_update_summary_flat.v1",
        "round_id": summary.get("round_id"),
        "committed": summary.get("committed"),
        "update_count": summary.get("update_count"),
        "update_count_pass": action_counts.get("pass", 0),
        "update_count_drift": action_counts.get("drift", 0),
        "update_count_unknown": action_counts.get("unknown", 0),
        "update_action_counts": action_counts,
        "update_lifecycle_counts": lifecycle_counts,
        "update_object_type_counts": object_types,
        "update_mean_similarity": round(mean_similarity, 4) if mean_similarity is not None else None,
        "updates_joined": "|".join(
            f"{str(item.get('source_object_id'))}:{str(item.get('action', 'unknown'))}:{item.get('similarity', '')}"
            for item in updates
            if item.get("source_object_id")
        ),
    }


def runtime_summary(state) -> Dict[str, Optional[float]]:
    object_count = len(state.ensure_typed_representation().objects)
    high_importance_count = sum(1 for metadata in state.runtime_metadata.values() if metadata.importance >= 0.8)
    importance_values = [metadata.importance for metadata in state.runtime_metadata.values()]
    mean_importance = (sum(importance_values) / len(importance_values)) if importance_values else None
    return {
        "object_count": object_count,
        "high_importance_count": high_importance_count,
        "mean_importance": round(mean_importance, 4) if mean_importance is not None else None,
        "history_length": len(state.history),
    }


def build_lifecycle_summary(state) -> Dict[str, object]:
    object_items = list(state.runtime_metadata.items())
    lifecycle_state_counts = {
        "active": sum(1 for _, metadata in object_items if metadata.lifecycle_state == "active"),
        "retained": sum(1 for _, metadata in object_items if metadata.lifecycle_state == "retained"),
        "decayed": sum(1 for _, metadata in object_items if metadata.lifecycle_state == "decayed"),
        "archived": sum(1 for _, metadata in object_items if metadata.lifecycle_state == "archived"),
    }
    high_importance_objects = [object_id for object_id, metadata in object_items if metadata.importance >= 0.8]
    drifting_objects = [object_id for object_id, metadata in object_items if metadata.drift_count > 0]
    high_risk_objects = [
        object_id
        for object_id, metadata in object_items
        if metadata.verification_failures > metadata.verification_passes and metadata.drift_count > 0
    ]
    top_drifting_objects = [
        object_id
        for object_id, metadata in sorted(
            object_items,
            key=lambda item: (
                item[1].drift_count,
                item[1].verification_failures,
                item[1].importance,
                item[0],
            ),
            reverse=True,
        )
        if metadata.drift_count > 0
    ][:5]
    top_stable_objects = [
        object_id
        for object_id, _ in sorted(
            object_items,
            key=lambda item: (
                item[1].verification_passes,
                item[1].importance,
                -item[1].drift_count,
                item[0],
            ),
            reverse=True,
        )
    ][:5]
    coverage_values = [record.coverage for record in state.history]
    drift_values = [record.drift for record in state.history]
    alignment_values = [record.alignment_score for record in state.history]
    summary = {
        "schema_version": "lifecycle_summary.v1",
        "global_history": {
            "first_round_id": state.history[0].round_id if state.history else None,
            "latest_round_id": state.history[-1].round_id if state.history else state.round_id,
            "coverage_mean": round(sum(coverage_values) / len(coverage_values), 4) if coverage_values else None,
            "drift_mean": round(sum(drift_values) / len(drift_values), 4) if drift_values else None,
            "alignment_mean": round(sum(alignment_values) / len(alignment_values), 4) if alignment_values else None,
            "coverage_delta": round(coverage_values[-1] - coverage_values[0], 4) if len(coverage_values) >= 2 else 0.0,
            "drift_delta": round(drift_values[-1] - drift_values[0], 4) if len(drift_values) >= 2 else 0.0,
            "alignment_delta": round(alignment_values[-1] - alignment_values[0], 4) if len(alignment_values) >= 2 else 0.0,
            "last_passed": state.history[-1].passed if state.history else None,
        },
        "global_history_spec": lifecycle_history_spec(),
        "per_object": {
            "object_count": len(object_items),
            "high_importance_count": len(high_importance_objects),
            "drifting_object_count": len(drifting_objects),
            "high_risk_object_count": len(high_risk_objects),
            "high_importance_object_ids": high_importance_objects[:5],
            "drifting_object_ids": drifting_objects[:5],
            "high_risk_object_ids": high_risk_objects[:5],
            "top_drifting_object_ids": top_drifting_objects,
            "top_stable_object_ids": top_stable_objects,
            "lifecycle_state_counts": lifecycle_state_counts,
        },
        "per_object_spec": lifecycle_object_spec(),
        "policy_spec": policy_spec(),
        "policy_flat": policy_flat(),
        "history_length": len(state.history),
        "round_id": state.round_id,
    }
    return summary


def build_recovery_summary(state, source_package: Dict, anchor_memory: str = "") -> Dict[str, object]:
    source_constraints = [str(item).strip() for item in source_package.get("constraints", []) if str(item).strip()]
    source_global_vocab = [str(item).strip() for item in source_package.get("global_vocab", []) if str(item).strip()]
    source_local_vocab = [str(item).strip() for item in source_package.get("local_vocab", []) if str(item).strip()]
    source_memory = str(source_package.get("memory", "")).strip()
    source_runtime_summary = (
        source_package.get("runtime_summary", {})
        if isinstance(source_package.get("runtime_summary", {}), dict)
        else {}
    )
    source_selection = source_package.get("selected_chunk_ids", [])
    current_summary = runtime_summary(state)
    source_constraint_set = {item.lower() for item in source_constraints}
    recovered_constraint_set = {item.lower() for item in state.constraints if str(item).strip()}
    source_vocab_set = {item.lower() for item in source_global_vocab + source_local_vocab}
    recovered_vocab_set = {
        item.lower() for item in state.global_vocabulary + state.local_vocabulary if str(item).strip()
    }
    constraint_union = source_constraint_set | recovered_constraint_set
    vocab_union = source_vocab_set | recovered_vocab_set
    constraint_overlap_rate = (
        len(source_constraint_set & recovered_constraint_set) / len(constraint_union)
        if constraint_union
        else 1.0
    )
    vocab_overlap_rate = (
        len(source_vocab_set & recovered_vocab_set) / len(vocab_union) if vocab_union else 1.0
    )
    return {
        "schema_version": "recovery_summary.v1",
        "source_memory_length": len(source_memory.split()),
        "recovered_memory_length": len(state.memory.split()),
        "source_constraint_count": len(source_constraints),
        "recovered_constraint_count": len(state.constraints),
        "source_global_vocab_count": len(source_global_vocab),
        "recovered_global_vocab_count": len(state.global_vocabulary),
        "source_local_vocab_count": len(source_local_vocab),
        "recovered_local_vocab_count": len(state.local_vocabulary),
        "source_selected_chunk_ids": list(source_selection) if isinstance(source_selection, list) else [],
        "recovered_round_id": state.round_id,
        "recovered_history_length": len(state.history),
        "recovered_runtime_summary": current_summary,
        "source_runtime_summary": source_runtime_summary,
        "anchor_memory_length": len(str(anchor_memory).split()) if anchor_memory else 0,
        "memory_delta": len(state.memory.split()) - len(source_memory.split()),
        "constraint_overlap_rate": round(constraint_overlap_rate, 4),
        "vocab_overlap_rate": round(vocab_overlap_rate, 4),
        "history_continuity_ok": len(state.history) >= source_runtime_summary.get("history_length", 0),
    }


def build_state_continuity_summary(state, source_package: Dict, anchor_memory: str = "") -> Dict[str, object]:
    state_recovery_summary = build_recovery_summary(state, source_package, anchor_memory=anchor_memory)
    return {
        "schema_version": "state_continuity_summary.v1",
        "runtime": runtime_summary(state),
        "recovery": state_recovery_summary,
        "round_id": state.round_id,
        "history_length": len(state.history),
        "history_continuity_ok": state_recovery_summary.get("history_continuity_ok", False),
        "constraint_overlap_rate": state_recovery_summary.get("constraint_overlap_rate"),
        "vocab_overlap_rate": state_recovery_summary.get("vocab_overlap_rate"),
        "memory_delta": state_recovery_summary.get("memory_delta"),
    }
