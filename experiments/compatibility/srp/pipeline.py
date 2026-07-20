import os
from time import perf_counter
from typing import Dict, List

from .compress import compress_state
from .encoder import build_encoder
from .execution import build_selected_execution_payload, execution_state_source, select_execution_state
from .execution_runner import evaluate_execution_answer, execute_task
from .pipeline_record_builder import build_cycle_record
from .pipeline_runtime import (
    CycleSnapshot,
    PipelineConfig,
    compute_semantic_metrics,
    initialize_state,
    merge_usage,
    select_committed_fields,
    transition_state,
)
from .state_allocation import build_state_allocation_policy
from .repair import build_repair_package
from .repair_diagnostics import build_repair_diagnostics
from .recover import recover_state
from .validate import validate_state
from .validation_targets import build_validation_targets


def _source_package_from_state(state):
    return state.as_dict()


def run_srp(
    task: Dict,
    cycles: int,
    client=None,
    max_cycle_drift: float = 0.35,
    min_keyword_score: float = 0.5,
) -> List[Dict]:
    anchor_memory = task["initial_state"]["memory"]
    config = PipelineConfig.from_env(max_cycle_drift, min_keyword_score)
    encoder = build_encoder()
    state = initialize_state(task, encoder=encoder)
    validation_targets = build_validation_targets(task)

    records = []
    previous_semantic_drift = None
    initial_semantic_drift = None

    for cycle in range(1, cycles + 1):
        started_at = perf_counter()
        snapshot = CycleSnapshot.capture(state)
        source_package = _source_package_from_state(state)

        compressed_package = compress_state(state, client=client)
        package = compressed_package
        recovered = recover_state(package, client=client, anchor_memory=anchor_memory)
        recovered_package = recovered.recovered_state_package
        repair_package = None
        state_allocation_result = None
        execution_payload = None
        execution_result = None
        execution_text = recovered.memory
        execution_state_package = recovered.recovered_state_package
        execution_mode = os.getenv("SRP_EXECUTION_MODE", "answer")
        validation_before_repair = None
        usage_before_repair = merge_usage(package, recovered)
        usage_after_repair = usage_before_repair
        repair_diagnostics = build_repair_diagnostics(
            repair_attempted=False,
            validation_before_repair=None,
            validation_after_repair=None,
            total_tokens_before_repair=None,
            total_tokens_after_repair=None,
        )
        if recovered.recovered_state_package is not None:
            allocation_policy = build_state_allocation_policy()
            allocation_result = allocation_policy.allocate(
            recovered.recovered_state_package,
            {
                "task": task,
                    "validation": None,
                    "validation_targets": validation_targets,
                    "recovered_state_package": recovered.recovered_state_package,
                },
            )
            state.state_allocation_result = allocation_result
            state.state_allocation_summary = {
                "schema_version": "state_allocation_summary.v1",
                "policy_name": allocation_result.policy_name,
                "active_object_count": allocation_result.metrics.active_object_count,
                "latent_object_count": allocation_result.metrics.latent_object_count,
                "discard_object_count": allocation_result.metrics.discard_object_count,
                "validation_coverage": allocation_result.metrics.validation_coverage,
                "active_state_efficiency": allocation_result.metrics.active_state_efficiency,
                "latent_preservation": allocation_result.metrics.latent_preservation,
                "hallucination_isolation": allocation_result.metrics.hallucination_isolation,
                "active_retention_ratio": allocation_result.metrics.active_retention_ratio,
            }
            state_allocation_result = {
                "policy_name": allocation_result.policy_name,
                "active_state": allocation_result.active_state,
                "latent_state": allocation_result.latent_state,
                "discard_state": allocation_result.discard_state,
                "active_objects": allocation_result.active_objects,
                "latent_objects": allocation_result.latent_objects,
                "discard_objects": allocation_result.discard_objects,
                "metrics": allocation_result.metrics.__dict__,
                "forensic_trace": allocation_result.forensic_trace,
            }
            execution_state = select_execution_state(
                recovered_package=recovered.recovered_state_package,
                allocation_result=state_allocation_result,
                source=execution_state_source(),
            )
            execution_payload = build_selected_execution_payload(
                recovered_package=recovered.recovered_state_package,
                allocation_result=state_allocation_result,
                source=execution_state_source(),
            )
            execution_text = execution_payload.context
            execution_state_package = execution_state
            execution_result = execute_task(
                client=client,
                context=execution_payload.context,
                query=str(task.get("queries", [""])[0] if task.get("queries") else ""),
                source=execution_state_source(),
                mode=execution_mode,
            )

        validation = validate_state(
            snapshot.memory,
            execution_text,
            validation_targets,
            max_drift=config.max_cycle_drift,
            min_keyword_score=config.min_keyword_score,
            runtime_metadata=state.runtime_metadata,
            recovered_state_package=execution_state_package,
            dependency_labels=task.get("metadata", {}).get("required_dependency_labels"),
            dependency_objects=task.get("metadata", {}).get("required_dependency_objects"),
        )
        validation_before_repair = validation

        repair_enabled = str(os.getenv("SRP_REPAIR_ENABLED", "true")).strip().lower() not in {"0", "false", "no", "off"}
        if repair_enabled and (
            not validation["passed"]
            and recovered.recovered_state_package is not None
        ):
            repair_package = build_repair_package(package, recovered.recovered_state_package, validation, validation_targets)
            repaired_recovered = recover_state(repair_package, client=client, anchor_memory=anchor_memory)
            repaired_state_allocation_result = None
            repaired_execution_payload = None
            repaired_execution_text = repaired_recovered.memory
            repaired_execution_state_package = repaired_recovered.recovered_state_package
            if repaired_recovered.recovered_state_package is not None:
                allocation_policy = build_state_allocation_policy()
                allocation_result = allocation_policy.allocate(
                    repaired_recovered.recovered_state_package,
                    {
                        "task": task,
                        "validation": validation,
                        "validation_targets": validation_targets,
                        "recovered_state_package": repaired_recovered.recovered_state_package,
                    },
                )
                repaired_state_allocation_result = {
                    "policy_name": allocation_result.policy_name,
                    "active_state": allocation_result.active_state,
                    "latent_state": allocation_result.latent_state,
                    "discard_state": allocation_result.discard_state,
                    "active_objects": allocation_result.active_objects,
                    "latent_objects": allocation_result.latent_objects,
                    "discard_objects": allocation_result.discard_objects,
                    "metrics": allocation_result.metrics.__dict__,
                    "forensic_trace": allocation_result.forensic_trace,
                }
                repaired_execution_state = select_execution_state(
                    recovered_package=repaired_recovered.recovered_state_package,
                    allocation_result=repaired_state_allocation_result,
                    source=execution_state_source(),
                )
            repaired_execution_payload = build_selected_execution_payload(
                recovered_package=repaired_recovered.recovered_state_package,
                allocation_result=repaired_state_allocation_result,
                source=execution_state_source(),
            )
            repaired_execution_text = repaired_execution_payload.context
            repaired_execution_state_package = repaired_execution_state
            execution_result = execute_task(
                client=client,
                context=repaired_execution_payload.context,
                query=str(task.get("queries", [""])[0] if task.get("queries") else ""),
                source=execution_state_source(),
                mode=execution_mode,
            )
            repaired_validation = validate_state(
                snapshot.memory,
                repaired_execution_text,
                validation_targets,
                max_drift=config.max_cycle_drift,
                min_keyword_score=config.min_keyword_score,
                runtime_metadata=state.runtime_metadata,
                recovered_state_package=repaired_execution_state_package,
                dependency_labels=task.get("metadata", {}).get("required_dependency_labels"),
                dependency_objects=task.get("metadata", {}).get("required_dependency_objects"),
            )
            validation = repaired_validation
            recovered = repaired_recovered
            package = repair_package
            state_allocation_result = repaired_state_allocation_result
            execution_payload = repaired_execution_payload
            execution_text = repaired_execution_text
            execution_state_package = repaired_execution_state_package
            usage_after_repair = merge_usage(package, recovered)
            repair_diagnostics = build_repair_diagnostics(
                repair_attempted=True,
                validation_before_repair=validation_before_repair,
                validation_after_repair=validation,
                total_tokens_before_repair=usage_before_repair.get("total_tokens"),
                total_tokens_after_repair=usage_after_repair.get("total_tokens"),
            )

        committed = validation["passed"]
        state.observe_verification(validation, committed=committed)

        committed_fields = select_committed_fields(snapshot, recovered, package, committed)
        metrics, previous_semantic_drift, initial_semantic_drift = compute_semantic_metrics(
            state=state,
            recovered=recovered,
            anchor_memory=anchor_memory,
            encoder=encoder,
            previous_semantic_drift=previous_semantic_drift,
            initial_semantic_drift=initial_semantic_drift,
            source_state_text=snapshot.state_text,
        )
        usage = merge_usage(package, recovered)

        records.append(
            build_cycle_record(
                cycle=cycle,
                state=state,
                package=package,
                recovered=recovered,
                validation=validation,
                validation_targets=validation_targets,
                usage=usage,
                metrics=metrics,
                committed_memory=committed_fields["memory"],
                latency_seconds=perf_counter() - started_at,
                encoder_name=encoder.name if encoder is not None else None,
                committed=committed,
                source_package=source_package,
                compressed_package=compressed_package,
                recovered_package=recovered_package,
                repaired_package=(
                    recovered.recovered_state_package
                    if repair_package is not None
                    else None
                ),
                state_allocation_result=state_allocation_result,
                execution_state_source=execution_state_source(),
                execution_payload=execution_payload.as_dict() if execution_payload is not None else None,
                execution_state_object_count=len(execution_payload.objects) if execution_payload is not None else None,
                execution_result=execution_result.as_dict() if execution_result is not None else None,
                execution_answer=execution_result.answer if execution_result is not None else None,
                execution_answer_evaluation=(
                    evaluate_execution_answer(
                        execution_result.answer,
                        str(task.get("expected_output", "")),
                        task.get("expected_keywords", []),
                    )
                    if execution_result is not None
                    else None
                ),
                execution_mode=execution_mode,
                repair_diagnostics=repair_diagnostics.as_dict(),
                allocation_forensic_trace=(
                    state_allocation_result.get("forensic_trace")
                    if isinstance(state_allocation_result, dict)
                    else None
                ),
            )
        )

        state = transition_state(state, committed_fields)

    return records
