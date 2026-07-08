from typing import Dict, Optional

from .object_lifecycle import build_object_lifecycle_artifact
from .object_retention import build_object_retention_breakdown
from .object_retention import build_object_retention_breakdown_v2


def build_cycle_record(
    cycle: int,
    state,
    package: Dict,
    recovered,
    validation: Dict,
    validation_targets,
    usage: Dict[str, Optional[int]],
    metrics,
    committed_memory: str,
    latency_seconds: float,
    encoder_name: Optional[str],
    committed: bool,
    source_package: Dict | None = None,
    compressed_package: Dict | None = None,
    recovered_package: Dict | None = None,
    repaired_package: Dict | None = None,
    state_allocation_result: Dict | None = None,
    execution_state_source: str | None = None,
    execution_payload: Dict | None = None,
    execution_state_object_count: int | None = None,
    execution_result: Dict | None = None,
    execution_answer: str | None = None,
    execution_answer_evaluation: Dict | None = None,
    execution_mode: str | None = None,
    allocation_forensic_trace: Dict | None = None,
) -> Dict:
    lifecycle_artifact = build_object_lifecycle_artifact(
        source_package,
        compressed_package or package,
        recovered_package or getattr(recovered, "recovered_state_package", None),
        repaired_package,
        validation_targets=validation_targets,
    )
    retention_breakdown_v2 = build_object_retention_breakdown_v2(
        package.get("semantic_object_inventory"),
        getattr(recovered, "recovered_state_package", None),
        validation_targets=validation_targets,
    )
    task_precision = retention_breakdown_v2.task_critical.get("precision")
    task_recall = retention_breakdown_v2.task_critical.get("recall")
    task_f1 = (
        None
        if task_precision is None or task_recall is None or (task_precision + task_recall) == 0
        else 2 * task_precision * task_recall / (task_precision + task_recall)
    )
    return {
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
        "semantic_object_inventory": package.get("semantic_object_inventory"),
        "semantic_objects": package.get("semantic_objects", []),
        "structured_state_package": package.get("structured_state_package"),
        "recovered_state_package": getattr(recovered, "recovered_state_package", None),
        "reconstruction_result": getattr(recovered, "reconstruction_result", None),
        "state_allocation_result": state_allocation_result,
        "allocation_forensic_trace": allocation_forensic_trace,
        "execution_state_source": execution_state_source,
        "execution_payload": execution_payload,
        "execution_state_object_count": execution_state_object_count,
        "execution_prompt_tokens": (
            len(str(execution_payload.get("context", "")).split())
            if isinstance(execution_payload, dict) and execution_payload.get("context") is not None
            else None
        ),
        "execution_result": execution_result,
        "execution_answer": execution_answer,
        "execution_answer_evaluation": execution_answer_evaluation,
        "execution_mode": execution_mode,
        "object_retention_breakdown": build_object_retention_breakdown(
            package.get("semantic_object_inventory"),
            getattr(recovered, "recovered_state_package", None),
        ).as_dict(),
        "object_retention_breakdown_v2": retention_breakdown_v2.as_dict(),
        "object_lifecycle": lifecycle_artifact.as_dict(),
        "important_object_recall": retention_breakdown_v2.important.get("recall"),
        "task_critical_object_recall": task_recall,
        "task_critical_object_precision": task_precision,
        "task_critical_object_f1": task_f1,
        "object_inflation_ratio": retention_breakdown_v2.all_objects.get("inflation_ratio"),
        "repair_context": package.get("repair_context"),
        "repair_context_flat": package.get("repair_context_flat"),
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
        "latency_seconds": round(latency_seconds, 4),
        "validation_score": validation["score"],
        "validation_contract_satisfaction": validation["contract_satisfaction"],
        "validation_drift": validation["drift"],
        "validation_drift_risk": validation["drift_risk"],
        "validation_drift_blocks_commit": validation["drift_blocks_commit"],
        "validation_coverage": validation["coverage_score"],
        "validation_alignment": validation["alignment_score"],
        "dependency_coverage": validation.get("dependency_coverage"),
        "dependency_precision": validation.get("dependency_precision"),
        "dependency_f1": validation.get("dependency_f1"),
        "dependency_audit": validation.get("dependency_audit"),
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
        "encoder_name": encoder_name,
        "semantic_similarity": metrics.similarity,
        "semantic_drift": metrics.drift,
        "semantic_drift_rate": metrics.drift_rate,
        "semantic_drift_from_initial": metrics.drift_from_initial,
        "semantic_drift_baseline": metrics.drift_baseline,
        "semantic_stability": metrics.stability,
        "state_vector_dim": len(state.state_vector) if state.state_vector is not None else None,
        "state_vector_present": state.state_vector is not None,
        "validation_passed": validation["passed"],
        "state_committed": committed,
        "notes": "semantic runtime protocol" if committed else "semantic runtime protocol (rollback to pre-compression memory)",
    }
