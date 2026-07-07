import os
from time import perf_counter
from typing import Dict, List

from .encoder import build_encoder, cosine_similarity, serialize_state_for_encoding
from .compress import compress_state
from .recover import recover_state
from .state import SemanticState
from .validate import validate_state
from .validation_targets import build_validation_targets


def _extract_vocab(text: str) -> List[str]:
    words = [word.strip(".,").lower() for word in text.split()]
    unique = []
    for word in words:
        if len(word) > 4 and word not in unique:
            unique.append(word)
    return unique[:12]


def _merge_vocab(existing: List[str], additions: List[str], limit: int = 12) -> List[str]:
    merged = list(existing)
    for item in additions:
        cleaned = str(item).strip().lower()
        if cleaned and cleaned not in merged:
            merged.append(cleaned)
    return merged[:limit]


def run_srp(
    task: Dict,
    cycles: int,
    client=None,
    max_cycle_drift: float = 0.35,
    min_keyword_score: float = 0.5,
) -> List[Dict]:
    constraint_state = list(task["initial_state"].get("constraints", []))
    anchor_memory = task["initial_state"]["memory"]
    effective_max_cycle_drift = float(os.getenv("SRP_MAX_CYCLE_DRIFT", str(max_cycle_drift)))
    effective_min_keyword_score = float(os.getenv("SRP_MIN_KEYWORD_SCORE", str(min_keyword_score)))
    encoder = build_encoder()
    state = SemanticState(
        memory=anchor_memory,
        constraints=constraint_state,
        global_vocabulary=_extract_vocab(anchor_memory),
        local_vocabulary=_extract_vocab(" ".join(constraint_state)),
        term_map={},
        loss_notes=[],
        policy={
            "compression_goal": "preserve task memory under bounded drift",
            "anti_leakage": "do not introduce query verbs or protocol terms unless they are already in memory",
            "recovery_goal": "recover the original task memory as directly as possible by aligning to a stable semantic anchor",
            "lifecycle_retained_importance": 0.35,
            "lifecycle_retained_passes": 2,
            "lifecycle_archived_importance": 0.3,
            "lifecycle_archived_drift_count": 2,
            "lifecycle_archived_failure_count": 2,
            "lifecycle_decayed_floor": 0.05,
            "lifecycle_decayed_multiplier": 0.92,
        },
    )
    state.ensure_runtime_metadata(anchor_memory=anchor_memory)
    state.ensure_state_vector(encoder=encoder)
    records = []
    previous_semantic_drift = None
    initial_semantic_drift = None
    for cycle in range(1, cycles + 1):
        started_at = perf_counter()
        pre_cycle_state_text = serialize_state_for_encoding(state)
        pre_cycle_vector = list(state.state_vector) if state.state_vector is not None else None
        pre_cycle_memory = state.memory
        pre_cycle_constraints = list(state.constraints)
        pre_cycle_global_vocabulary = list(state.global_vocabulary)
        pre_cycle_local_vocabulary = list(state.local_vocabulary)
        pre_cycle_term_map = dict(state.term_map)
        pre_cycle_loss_notes = list(state.loss_notes)
        package = compress_state(state, client=client)
        recovered = recover_state(package, client=client, anchor_memory=anchor_memory)
        validation_targets = build_validation_targets(task)
        validation = validate_state(
            pre_cycle_memory,
            recovered.memory,
            validation_targets,
            max_drift=effective_max_cycle_drift,
            min_keyword_score=effective_min_keyword_score,
            runtime_metadata=state.runtime_metadata,
        )
        committed = validation["passed"]
        state.observe_verification(validation, committed=committed)
        committed_memory = recovered.memory if committed else pre_cycle_memory
        committed_constraints = recovered.constraints if committed else pre_cycle_constraints
        committed_term_map = recovered.term_map if committed else pre_cycle_term_map
        committed_loss_notes = recovered.loss_notes if committed else pre_cycle_loss_notes
        committed_global_vocabulary = (
            _merge_vocab(pre_cycle_global_vocabulary, package.get("global_vocab", []) + _extract_vocab(pre_cycle_memory))
            if committed
            else pre_cycle_global_vocabulary
        )
        committed_local_vocabulary = (
            _merge_vocab(pre_cycle_local_vocabulary, pre_cycle_constraints + _extract_vocab(" ".join(pre_cycle_memory.split()[:12])), limit=12)
            if committed
            else pre_cycle_local_vocabulary
        )
        package_usage = package.get("usage") or {}
        recovered_usage = getattr(recovered, "usage", None) or {}
        if encoder is not None:
            recovered.ensure_runtime_metadata(anchor_memory=anchor_memory)
            recovered.ensure_state_vector(encoder=encoder)
            source_vector = encoder.encode_passage(pre_cycle_state_text)
            recovered_vector = encoder.encode_passage(serialize_state_for_encoding(recovered))
            semantic_similarity = cosine_similarity(source_vector, recovered_vector)
            semantic_drift = 1.0 - semantic_similarity
            if initial_semantic_drift is None:
                initial_semantic_drift = semantic_drift
            semantic_drift_rate = (
                None if previous_semantic_drift is None else round(semantic_drift - previous_semantic_drift, 6)
            )
            semantic_drift_from_initial = round(semantic_drift - initial_semantic_drift, 6) if initial_semantic_drift is not None else None
            semantic_stability = round(max(0.0, 1.0 - semantic_drift), 6)
            previous_semantic_drift = semantic_drift
        else:
            semantic_similarity = None
            semantic_drift = None
            semantic_drift_rate = None
            semantic_drift_from_initial = None
            semantic_stability = None
        usage = {
            "prompt_tokens": sum(value for value in [package_usage.get("prompt_tokens"), recovered_usage.get("prompt_tokens")] if value is not None) or None,
            "completion_tokens": sum(value for value in [package_usage.get("completion_tokens"), recovered_usage.get("completion_tokens")] if value is not None) or None,
            "total_tokens": sum(value for value in [package_usage.get("total_tokens"), recovered_usage.get("total_tokens")] if value is not None) or None,
        }
        records.append(
            {
                "cycle": cycle,
                "representation": package["memory"],
                "compression_parse_status": package.get("parse_status"),
                "compression_parse_error": package.get("parse_error"),
                "compression_stripped_thinking": package.get("stripped_thinking"),
                "chunk_selection_method": package.get("chunk_selection_method"),
                "selected_chunk_ids": package.get("selected_chunk_ids", []),
                "chunk_selection": package.get("chunk_selection", []),
                "chunk_selection_scores": package.get("chunk_selection_scores", []),
                "chunk_selection_reasons": package.get("chunk_selection_reasons", []),
                "chunk_selection_factors": package.get("chunk_selection_factors", []),
                "recovered_text": recovered.memory,
                "state_continuity_summary": recovered.state_continuity_summary,
                "recovery_template_summary": recovered.recovery_template_summary,
                "recovery_template_summary_flat": recovered.recovery_template_summary_flat,
                "lifecycle_summary": recovered.lifecycle_summary,
                "object_update_summary": recovered.object_update_summary,
                "object_update_summary_flat": recovered.object_update_summary_flat,
                "lifecycle_summary_flat": recovered.lifecycle_summary.get("flat") if recovered.lifecycle_summary else None,
                "policy_flat": recovered.lifecycle_summary.get("policy_flat") if recovered.lifecycle_summary else None,
                "committed_memory": committed_memory,
                "tokens": len(package["memory"].split()) + len(package["global_vocab"]) + 8,
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens"),
                "latency_seconds": round(perf_counter() - started_at, 4),
                "validation_score": validation["score"],
                "validation_contract_satisfaction": validation["contract_satisfaction"],
                "validation_drift": validation["drift"],
                "validation_drift_risk": validation["drift_risk"],
                "validation_drift_blocks_commit": validation["drift_blocks_commit"],
                "validation_coverage": validation["coverage_score"],
                "validation_alignment": validation["alignment_score"],
                "validation_leakage_detected": validation["leakage_detected"],
                "critical_failures": validation.get("critical_failures", []),
                "failure_summary": validation.get("failure_summary"),
                "failure_summary_flat": validation.get("failure_summary_flat"),
                "max_cycle_drift": validation["max_drift"],
                "blocking_drift": validation["blocking_drift"],
                "min_keyword_score": validation["min_keyword_score"],
                "min_coverage_score": validation["min_coverage_score"],
                "runtime_round": state.round_id,
                "runtime_history_length": len(state.history),
                "mean_object_importance": (
                    sum(meta.importance for meta in state.runtime_metadata.values()) / len(state.runtime_metadata)
                    if state.runtime_metadata
                    else None
                ),
                "encoder_name": encoder.name if encoder is not None else None,
                "semantic_similarity": round(semantic_similarity, 6) if semantic_similarity is not None else None,
                "semantic_drift": round(semantic_drift, 6) if semantic_drift is not None else None,
                "semantic_drift_rate": semantic_drift_rate,
                "semantic_drift_from_initial": semantic_drift_from_initial,
                "semantic_drift_baseline": round(initial_semantic_drift, 6) if initial_semantic_drift is not None else None,
                "semantic_stability": semantic_stability,
                "state_vector_dim": len(state.state_vector) if state.state_vector is not None else None,
                "state_vector_present": state.state_vector is not None,
                "validation_passed": validation["passed"],
                "state_committed": committed,
                "notes": "semantic runtime protocol" if committed else "semantic runtime protocol (rollback to pre-compression memory)",
            }
        )
        state = SemanticState(
            memory=committed_memory,
            constraints=committed_constraints,
            global_vocabulary=committed_global_vocabulary,
            local_vocabulary=committed_local_vocabulary,
            term_map=committed_term_map,
            loss_notes=committed_loss_notes,
            policy=state.policy,
            runtime_metadata=state.runtime_metadata,
            history=state.history,
            round_id=state.round_id,
            state_vector=state.state_vector,
            state_vector_encoder=state.state_vector_encoder,
            lifecycle_summary=state.lifecycle_summary,
            object_update_summary=state.object_update_summary,
            recovery_template_summary_flat=state.recovery_template_summary_flat,
            object_update_summary_flat=state.object_update_summary_flat,
        )
    return records
