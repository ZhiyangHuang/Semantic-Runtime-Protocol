from typing import Dict, Optional

from .experiment_result import build_experiment_result
from .object_lifecycle import build_object_lifecycle_artifact
from .object_retention import build_object_retention_breakdown
from .object_retention import build_object_retention_breakdown_v2
from .object_retention import build_integrity_retention_metrics
from .runtime_representation import build_runtime_representation_v2
from .semantic_graph import build_semantic_runtime_graph


def _word_count(value: object) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return 0
    return len(text.split())


def _compression_ratio(source_size: int | None, compressed_size: int | None) -> float | None:
    if source_size is None or compressed_size is None or source_size <= 0:
        return None
    return compressed_size / source_size


def _runtime_metadata_snapshot(state) -> Dict[str, Dict[str, object]]:
    snapshot: Dict[str, Dict[str, object]] = {}
    runtime_metadata = getattr(state, "runtime_metadata", {}) or {}
    for object_id, metadata in runtime_metadata.items():
        if hasattr(metadata, "as_dict"):
            snapshot[object_id] = metadata.as_dict()
        elif isinstance(metadata, dict):
            snapshot[object_id] = dict(metadata)
        else:
            snapshot[object_id] = {
                "importance": getattr(metadata, "importance", None),
                "confidence": getattr(metadata, "confidence", None),
                "lifecycle_state": getattr(metadata, "lifecycle_state", None),
            }
    return snapshot


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
    repair_diagnostics: Dict | None = None,
    allocation_forensic_trace: Dict | None = None,
) -> Dict:
    lifecycle_artifact = build_object_lifecycle_artifact(
        source_package,
        compressed_package or package,
        recovered_package or getattr(recovered, "recovered_state_package", None),
        repaired_package,
        validation_targets=validation_targets,
        state_allocation_result=state_allocation_result,
        execution_payload=execution_payload,
    )
    lifecycle_artifact_dict = lifecycle_artifact.as_dict()
    retention_breakdown_v2 = build_object_retention_breakdown_v2(
        (source_package or {}).get("semantic_object_inventory") or package.get("semantic_object_inventory"),
        getattr(recovered, "recovered_state_package", None),
        validation_targets=validation_targets,
    )
    integrity_metrics = build_integrity_retention_metrics(
        source_package,
        compressed_package or package,
        getattr(recovered, "recovered_state_package", None),
        validation=validation,
        validation_targets=validation_targets,
        retention_breakdown_v2=retention_breakdown_v2,
        committed=committed,
    )
    semantic_runtime_graph = build_semantic_runtime_graph(
        source_package or package,
        getattr(recovered, "recovered_state_package", None),
        validation_targets=validation_targets,
    )
    runtime_representation_v2 = build_runtime_representation_v2(
        state,
        anchor_memory=(source_package or package).get("memory") or committed_memory,
    )
    semantic_graph_validation = semantic_runtime_graph.summary.get("validation") or {}
    source_size = _word_count((source_package or {}).get("memory") or committed_memory)
    compressed_size = _word_count((compressed_package or package).get("memory"))
    compression_ratio = _compression_ratio(source_size, compressed_size)
    structured_state_package_present = bool(getattr(recovered, "recovered_state_package", None))
    transitions = lifecycle_artifact_dict.get("transitions") or {}
    task_precision = retention_breakdown_v2.task_critical.get("precision")
    task_recall = retention_breakdown_v2.task_critical.get("recall")
    task_f1 = (
        None
        if task_precision is None or task_recall is None or (task_precision + task_recall) == 0
        else 2 * task_precision * task_recall / (task_precision + task_recall)
    )
    record = {
        "cycle": cycle,
        "source_package": source_package,
        "compressed_package": compressed_package or package,
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
        "source_size": source_size,
        "compressed_size": compressed_size,
        "compression_ratio": compression_ratio,
        "semantic_object_inventory": package.get("semantic_object_inventory"),
        "semantic_objects": package.get("semantic_objects", []),
        "structured_state_package": package.get("structured_state_package"),
        "recovered_package": recovered_package,
        "recovered_state_package": getattr(recovered, "recovered_state_package", None),
        "structured_state_package_present": structured_state_package_present,
        "reconstruction_result": getattr(recovered, "reconstruction_result", None),
        "graph_recovery_result": getattr(recovered, "graph_recovery_result", None),
        "semantic_runtime_graph": getattr(recovered, "semantic_runtime_graph", None),
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
            (source_package or {}).get("semantic_object_inventory") or package.get("semantic_object_inventory"),
            getattr(recovered, "recovered_state_package", None),
        ).as_dict(),
        "object_retention_breakdown_v2": retention_breakdown_v2.as_dict(),
        "integrity_retention_metrics": integrity_metrics.as_dict(),
        "object_lifecycle": lifecycle_artifact_dict,
        "semantic_runtime_graph": semantic_runtime_graph.as_dict(),
        "runtime_representation_v2": runtime_representation_v2.as_dict(),
        "runtime_representation_v2_projection": runtime_representation_v2.project_graph(),
        "runtime_representation_v2_summary": runtime_representation_v2.summary,
        "runtime_metadata_snapshot": _runtime_metadata_snapshot(state),
        "semantic_graph_validation": semantic_graph_validation,
        "source_object_count": lifecycle_artifact_dict.get("source_object_count"),
        "compressed_object_count": lifecycle_artifact_dict.get("compressed_object_count"),
        "recovered_object_count": lifecycle_artifact_dict.get("recovered_object_count"),
        "repaired_object_count": lifecycle_artifact_dict.get("repaired_object_count"),
        "allocated_object_count": lifecycle_artifact_dict.get("allocated_object_count"),
        "executed_object_count": lifecycle_artifact_dict.get("executed_object_count"),
        "source_to_compressed_recall": (transitions.get("source_to_compressed") or {}).get("recall"),
        "compressed_to_recovered_recall": (transitions.get("compressed_to_recovered") or {}).get("recall"),
        "recovered_to_repaired_recall": (transitions.get("recovered_to_repaired") or {}).get("recall"),
        "lifecycle_inflation": lifecycle_artifact_dict.get("lifecycle_inflation"),
        "important_object_recall": retention_breakdown_v2.important.get("recall"),
        "task_critical_object_recall": task_recall,
        "task_critical_object_precision": task_precision,
        "task_critical_object_f1": task_f1,
        "object_inflation_ratio": retention_breakdown_v2.all_objects.get("inflation_ratio"),
        "integrity_gap": integrity_metrics.integrity_gap,
        "semantic_compression_loss": integrity_metrics.semantic_compression_loss,
        "object_retention": integrity_metrics.object_retention,
        "weighted_object_retention": integrity_metrics.weighted_object_retention,
        "lost_important_object_count": integrity_metrics.lost_important_object_count,
        "recovered_object_type_counts": integrity_metrics.recovered_object_type_counts,
        "graph_node_count": semantic_runtime_graph.summary.get("node_count"),
        "graph_edge_count": semantic_runtime_graph.summary.get("edge_count"),
        "graph_object_survival_rate": semantic_graph_validation.get("object_survival_rate"),
        "graph_dependency_recall": semantic_graph_validation.get("dependency_recall"),
        "graph_constraint_accuracy": semantic_graph_validation.get("constraint_accuracy"),
        "graph_hallucination_rate": semantic_graph_validation.get("hallucination_rate"),
        "graph_integrity_score": semantic_graph_validation.get("graph_integrity_score"),
        "graph_dependency_closure_rate": (
            (getattr(recovered, "graph_recovery_result", None) or {}).get("dependency_closure_rate")
            if getattr(recovered, "graph_recovery_result", None) is not None
            else None
        ),
        "graph_recovery_precision": (
            (getattr(recovered, "graph_recovery_result", None) or {}).get("graph_recovery_precision")
            if getattr(recovered, "graph_recovery_result", None) is not None
            else None
        ),
        "graph_repair_cost": (
            (getattr(recovered, "graph_recovery_result", None) or {}).get("repair_cost")
            if getattr(recovered, "graph_recovery_result", None) is not None
            else None
        ),
        "repair_context": package.get("repair_context"),
        "repair_context_flat": package.get("repair_context_flat"),
        "repair_diagnostics": repair_diagnostics,
        "repair_attempted": (repair_diagnostics or {}).get("repair_attempted"),
        "coverage_before_repair": (repair_diagnostics or {}).get("coverage_before_repair"),
        "coverage_after_repair": (repair_diagnostics or {}).get("coverage_after_repair"),
        "repair_gain": (repair_diagnostics or {}).get("repair_gain"),
        "critical_failures_before": (repair_diagnostics or {}).get("critical_failures_before"),
        "critical_failures_after": (repair_diagnostics or {}).get("critical_failures_after"),
        "token_overhead": (repair_diagnostics or {}).get("token_overhead"),
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
    record["experiment_result"] = build_experiment_result(record)
    return record
