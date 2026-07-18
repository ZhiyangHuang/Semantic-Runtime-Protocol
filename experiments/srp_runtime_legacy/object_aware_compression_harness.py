from __future__ import annotations

import json
import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence

from .srp.pipeline_runtime import initialize_state
from .srp.export import write_records_csv, write_records_markdown
from .srp.pipeline import run_srp
from .srp.saliency import score_memory_chunks
from .srp.semantic_objects import build_semantic_object_inventory


@dataclass(frozen=True)
class ObjectAwareCompressionSuite:
    name: str
    scenario: str
    object_support_enabled: bool
    task: Dict[str, Any]


def _branching_dependency_task() -> Dict[str, Any]:
    return {
        "id": "controlled-object-aware-compression-branching",
        "task_type": "object_aware_compression",
        "source": "Controlled SRP Object-Aware Compression",
        "initial_state": {
            "constraints": [
                "Project Orion keeps Atlas online for payments.",
                "Project Mercury keeps Atlas online for payments.",
                "Project Orion keeps Apollo linked for reporting.",
                "Project Mercury keeps Apollo linked for reporting.",
            ],
            "memory": (
                "Project Orion keeps Atlas online for payments. "
                "Project Mercury keeps Atlas online for payments. "
                "Project Orion keeps Apollo linked for reporting. "
                "Project Mercury keeps Apollo linked for reporting. "
                "Keep Atlas and Apollo online for the program. "
                "The cafeteria closes at five."
            ),
        },
        "query_expectations": [[["Project Orion keeps Atlas online for payments."]]],
        "expected_keywords": [],
        "metadata": {
            "benchmark": "Controlled SRP Object-Aware Compression",
            "scenario": "dependency branching",
            "required_dependency_labels": [
                "Project Orion keeps Atlas online for payments.",
                "Project Mercury keeps Atlas online for payments.",
                "Project Orion keeps Apollo linked for reporting.",
                "Project Mercury keeps Apollo linked for reporting.",
            ],
        },
    }


def _subject_collision_task() -> Dict[str, Any]:
    return {
        "id": "controlled-object-aware-compression-collision",
        "task_type": "object_aware_compression",
        "source": "Controlled SRP Object-Aware Compression",
        "initial_state": {
            "constraints": [
                "Orion owns Atlas in the payments lane.",
                "Mercury owns Atlas in the analytics lane.",
                "Nova owns Atlas in the reporting lane.",
            ],
            "memory": (
                "Orion owns Atlas in the payments lane. "
                "Mercury owns Atlas in the analytics lane. "
                "Nova owns Atlas in the reporting lane. "
                "Atlas remains the shared database. "
                "Preserve the assignment list. "
                "The lights stay on."
            ),
        },
        "query_expectations": [[["Orion owns Atlas in the payments lane."]]],
        "expected_keywords": [],
        "metadata": {
            "benchmark": "Controlled SRP Object-Aware Compression",
            "scenario": "subject collision",
            "required_dependency_labels": [
                "Orion owns Atlas in the payments lane.",
                "Mercury owns Atlas in the analytics lane.",
                "Nova owns Atlas in the reporting lane.",
            ],
        },
    }


def _budget_pressure_task() -> Dict[str, Any]:
    return {
        "id": "controlled-object-aware-compression-budget",
        "task_type": "object_aware_compression",
        "source": "Controlled SRP Object-Aware Compression",
        "initial_state": {
            "constraints": [
                "Alpha keeps the blue key in storage.",
                "Beta keeps the red key in storage.",
                "Gamma keeps the green key in storage.",
                "Delta keeps the yellow key in storage.",
            ],
            "memory": (
                "Alpha keeps the blue key in storage. "
                "Beta keeps the red key in storage. "
                "Gamma keeps the green key in storage. "
                "Delta keeps the yellow key in storage. "
                "Keep the key inventory in storage. "
                "The room stays quiet."
            ),
        },
        "query_expectations": [[["Alpha keeps the blue key in storage."]]],
        "expected_keywords": [],
        "metadata": {
            "benchmark": "Controlled SRP Object-Aware Compression",
            "scenario": "budget pressure",
            "required_dependency_labels": [
                "Alpha keeps the blue key in storage.",
                "Beta keeps the red key in storage.",
                "Gamma keeps the green key in storage.",
                "Delta keeps the yellow key in storage.",
            ],
        },
    }


def _build_scenarios() -> List[tuple[str, Dict[str, Any]]]:
    return [
        ("branching_dependency", _branching_dependency_task()),
        ("subject_collision", _subject_collision_task()),
        ("budget_pressure", _budget_pressure_task()),
    ]


def build_object_aware_compression_suites() -> List[ObjectAwareCompressionSuite]:
    suites: List[ObjectAwareCompressionSuite] = []
    for scenario_name, task in _build_scenarios():
        suites.append(
            ObjectAwareCompressionSuite(
                name=f"{scenario_name}_chunk_score_only",
                scenario=scenario_name,
                object_support_enabled=False,
                task=task,
            )
        )
        suites.append(
            ObjectAwareCompressionSuite(
                name=f"{scenario_name}_chunk_score_plus_object_support",
                scenario=scenario_name,
                object_support_enabled=True,
                task=task,
            )
        )
    return suites


def available_suite_names() -> List[str]:
    return [suite.name for suite in build_object_aware_compression_suites()]


def select_object_aware_compression_suites(names: Sequence[str] | None = None) -> List[ObjectAwareCompressionSuite]:
    suites = build_object_aware_compression_suites()
    if not names:
        return suites
    requested = {str(name).strip() for name in names if str(name).strip()}
    if not requested or "all" in requested:
        return suites
    selected = [suite for suite in suites if suite.name in requested]
    missing = requested - {suite.name for suite in selected}
    if missing:
        raise ValueError(f"Unknown object-aware compression suite(s): {', '.join(sorted(missing))}")
    return selected


@contextmanager
def _temporary_env(overrides: Dict[str, str]):
    previous: Dict[str, str | None] = {}
    try:
        for key, value in overrides.items():
            previous[key] = os.environ.get(key)
            os.environ[key] = value
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _apply_harness_identity(record: Dict[str, Any], suite: ObjectAwareCompressionSuite) -> None:
    record["task_id"] = record.get("task_id") or suite.task.get("id")
    record["task_source"] = "object_aware_compression"
    record["compression_suite"] = suite.name
    record["compression_scenario"] = suite.scenario
    record["object_support_enabled"] = suite.object_support_enabled
    record["controlled_object_aware_compression"] = {
        "suite": suite.name,
        "scenario": suite.scenario,
        "task_id": suite.task.get("id"),
        "task_type": suite.task.get("task_type"),
        "object_support_enabled": suite.object_support_enabled,
    }


def run_object_aware_compression(
    suites: Sequence[str] | None = None,
    *,
    cycles: int = 1,
) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for suite in select_object_aware_compression_suites(suites):
        mechanism_verification = _mechanism_verification(suite.task, top_k=2)
        decision_boundary = _decision_boundary_analysis(suite.task)
        with _temporary_env(
            {
                "SRP_OBJECT_SUPPORT_ENABLED": "true" if suite.object_support_enabled else "false",
                "SRP_RAG_TOP_K": "2",
            }
        ):
            task_records = run_srp(suite.task, cycles=cycles, client=None)
        for record in task_records:
            _apply_harness_identity(record, suite)
            record["mechanism_verification"] = mechanism_verification
            record["decision_boundary"] = decision_boundary
        records.extend(task_records)
    return records


def _metric_average(records: Sequence[Dict[str, Any]], key_path: Sequence[str]) -> float | None:
    values: List[float] = []
    for record in records:
        current: Any = record
        for key in key_path:
            if not isinstance(current, dict):
                current = None
                break
            current = current.get(key)
        if current is not None:
            values.append(float(current))
    if not values:
        return None
    return sum(values) / len(values)


def _compare_rankings(
    disabled_ranked: Sequence[Dict[str, Any]],
    enabled_ranked: Sequence[Dict[str, Any]],
    top_k: int,
) -> Dict[str, Any]:
    disabled_by_id = {int(item["chunk_id"]): item for item in disabled_ranked}
    enabled_by_id = {int(item["chunk_id"]): item for item in enabled_ranked}
    chunk_ids = sorted(set(disabled_by_id) | set(enabled_by_id))
    score_deltas: Dict[int, float] = {}
    changed_chunk_ids: List[int] = []
    for chunk_id in chunk_ids:
        disabled_score = float(disabled_by_id.get(chunk_id, {}).get("score", 0.0))
        enabled_score = float(enabled_by_id.get(chunk_id, {}).get("score", 0.0))
        delta = round(enabled_score - disabled_score, 6)
        score_deltas[chunk_id] = delta
        if abs(delta) > 1e-9:
            changed_chunk_ids.append(chunk_id)

    disabled_topk = [int(item["chunk_id"]) for item in disabled_ranked[: max(1, top_k)]]
    enabled_topk = [int(item["chunk_id"]) for item in enabled_ranked[: max(1, top_k)]]
    disabled_positions = {chunk_id: index for index, chunk_id in enumerate(disabled_topk)}
    enabled_positions = {chunk_id: index for index, chunk_id in enumerate(enabled_topk)}
    common_topk = sorted(set(disabled_topk) & set(enabled_topk))
    rank_flip_count = sum(1 for chunk_id in common_topk if disabled_positions.get(chunk_id) != enabled_positions.get(chunk_id))
    topk_entered = [chunk_id for chunk_id in enabled_topk if chunk_id not in disabled_topk]
    topk_exited = [chunk_id for chunk_id in disabled_topk if chunk_id not in enabled_topk]
    delta_count = max(len(topk_entered), len(topk_exited))
    deltas = list(score_deltas.values())
    topk_gain_values = [
        score_deltas.get(chunk_id, 0.0)
        for chunk_id in enabled_topk
        if chunk_id in score_deltas
    ]
    return {
        "score_changed_chunk_count": len(changed_chunk_ids),
        "score_changed_chunk_rate": (len(changed_chunk_ids) / len(chunk_ids)) if chunk_ids else None,
        "score_changed_chunk_ids": changed_chunk_ids,
        "topk_changed": disabled_topk != enabled_topk,
        "topk_delta_count": delta_count,
        "topk_entered_chunk_ids": topk_entered,
        "topk_exited_chunk_ids": topk_exited,
        "rank_flip_count": rank_flip_count,
        "rank_flip_rate": (rank_flip_count / len(common_topk)) if common_topk else (1.0 if disabled_topk != enabled_topk else 0.0),
        "object_support_gain": (sum(deltas) / len(deltas)) if deltas else None,
        "object_support_gain_topk": (sum(topk_gain_values) / len(topk_gain_values)) if topk_gain_values else None,
        "object_support_gain_max": max(deltas) if deltas else None,
        "disabled_topk": disabled_topk,
        "enabled_topk": enabled_topk,
        "topk_overlap_count": len(set(disabled_topk) & set(enabled_topk)),
    }


def _mechanism_verification(task: Dict[str, Any], top_k: int) -> Dict[str, Any]:
    state = initialize_state(task, encoder=None)
    inventory = build_semantic_object_inventory(state)
    disabled_ranked = score_memory_chunks(
        state.memory,
        state.constraints,
        expected_keywords=task.get("expected_keywords", []),
        semantic_object_inventory=None,
    )
    enabled_ranked = score_memory_chunks(
        state.memory,
        state.constraints,
        expected_keywords=task.get("expected_keywords", []),
        semantic_object_inventory=inventory,
    )
    comparison = _compare_rankings(disabled_ranked, enabled_ranked, top_k=top_k)
    comparison.update(
        {
            "schema_version": "object_support_mechanism_verification.v1",
            "task_id": task.get("id"),
            "scenario": task.get("metadata", {}).get("scenario"),
            "chunk_count": len(disabled_ranked),
            "object_count": inventory.get("object_count"),
            "important_object_count": len(inventory.get("important_objects", [])),
            "enabled_topk_size": min(top_k, len(enabled_ranked)),
            "disabled_topk_size": min(top_k, len(disabled_ranked)),
        }
    )
    return comparison


def _decision_margin(ranked: Sequence[Dict[str, Any]], top_k: int) -> float | None:
    effective_top_k = max(1, min(int(top_k), len(ranked)))
    if len(ranked) <= effective_top_k:
        return None
    cutoff_score = float(ranked[effective_top_k - 1].get("score", 0.0))
    next_score = float(ranked[effective_top_k].get("score", 0.0))
    return round(cutoff_score - next_score, 6)


def _decision_boundary_analysis(task: Dict[str, Any], top_k_values: Sequence[int] | None = None) -> Dict[str, Any]:
    state = initialize_state(task, encoder=None)
    inventory = build_semantic_object_inventory(state)
    disabled_ranked = score_memory_chunks(
        state.memory,
        state.constraints,
        expected_keywords=task.get("expected_keywords", []),
        semantic_object_inventory=None,
    )
    enabled_ranked = score_memory_chunks(
        state.memory,
        state.constraints,
        expected_keywords=task.get("expected_keywords", []),
        semantic_object_inventory=inventory,
    )
    requested_top_k_values = list(top_k_values or [10, 8, 6, 4, 2, 1])
    sweeps: List[Dict[str, Any]] = []
    first_changed_top_k = None
    for requested_top_k in requested_top_k_values:
        effective_top_k = max(1, min(int(requested_top_k), len(disabled_ranked)))
        comparison = _compare_rankings(disabled_ranked, enabled_ranked, top_k=effective_top_k)
        disabled_margin = _decision_margin(disabled_ranked, effective_top_k)
        enabled_margin = _decision_margin(enabled_ranked, effective_top_k)
        gain = comparison.get("object_support_gain_topk")
        gain_margin_ratio = None
        decision_flip_distance = None
        if gain is not None and disabled_margin is not None and disabled_margin != 0:
            gain_margin_ratio = round(float(gain) / float(disabled_margin), 6)
        if gain is not None and disabled_margin is not None:
            decision_flip_distance = round(float(disabled_margin) - float(gain), 6)
        sweep = {
            "requested_top_k": int(requested_top_k),
            "effective_top_k": effective_top_k,
            "topk_changed": comparison.get("topk_changed"),
            "topk_delta_count": comparison.get("topk_delta_count"),
            "rank_flip_rate": comparison.get("rank_flip_rate"),
            "disabled_topk": comparison.get("disabled_topk"),
            "enabled_topk": comparison.get("enabled_topk"),
            "decision_margin_disabled": disabled_margin,
            "decision_margin_enabled": enabled_margin,
            "decision_margin_delta": (
                None
                if disabled_margin is None or enabled_margin is None
                else round(float(enabled_margin) - float(disabled_margin), 6)
            ),
            "object_support_gain_topk": gain,
            "gain_margin_ratio": gain_margin_ratio,
            "decision_flip_distance": decision_flip_distance,
        }
        sweeps.append(sweep)
        if first_changed_top_k is None and comparison.get("topk_changed"):
            first_changed_top_k = effective_top_k
    topk_changed_count = sum(1 for sweep in sweeps if sweep.get("topk_changed"))
    rank_flip_rates = [float(sweep["rank_flip_rate"]) for sweep in sweeps if sweep.get("rank_flip_rate") is not None]
    gain_margin_ratios = [float(sweep["gain_margin_ratio"]) for sweep in sweeps if sweep.get("gain_margin_ratio") is not None]
    decision_flip_distances = [float(sweep["decision_flip_distance"]) for sweep in sweeps if sweep.get("decision_flip_distance") is not None]
    decision_margins = [float(sweep["decision_margin_disabled"]) for sweep in sweeps if sweep.get("decision_margin_disabled") is not None]
    return {
        "schema_version": "object_support_decision_boundary.v1",
        "task_id": task.get("id"),
        "scenario": task.get("metadata", {}).get("scenario"),
        "chunk_count": len(disabled_ranked),
        "object_count": inventory.get("object_count"),
        "important_object_count": len(inventory.get("important_objects", [])),
        "requested_top_k_values": requested_top_k_values,
        "first_changed_top_k": first_changed_top_k,
        "topk_changed_count": topk_changed_count,
        "topk_changed_rate": (topk_changed_count / len(sweeps)) if sweeps else None,
        "rank_flip_rate_mean": (sum(rank_flip_rates) / len(rank_flip_rates)) if rank_flip_rates else None,
        "decision_margin_min": min(decision_margins) if decision_margins else None,
        "decision_margin_mean": (sum(decision_margins) / len(decision_margins)) if decision_margins else None,
        "gain_margin_ratio_mean": (sum(gain_margin_ratios) / len(gain_margin_ratios)) if gain_margin_ratios else None,
        "decision_flip_distance_min": min(decision_flip_distances) if decision_flip_distances else None,
        "decision_flip_distance_mean": (sum(decision_flip_distances) / len(decision_flip_distances)) if decision_flip_distances else None,
        "sweeps": sweeps,
    }


def summarize_object_aware_compression(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "records": len(records),
        "scenarios": {},
        "suites": {},
        "mechanism_verification": {},
        "decision_boundary": {},
    }
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for record in records:
        suite = str(record.get("compression_suite") or "unknown")
        grouped.setdefault(suite, []).append(record)

    for suite_name, suite_records in grouped.items():
        summary["suites"][suite_name] = {
            "records": len(suite_records),
            "scenario": suite_records[0].get("compression_scenario") if suite_records else None,
            "object_support_enabled": bool(suite_records[0].get("object_support_enabled")) if suite_records else None,
            "validation_passed": sum(1 for record in suite_records if record.get("validation_passed")),
            "repair_attempted": sum(1 for record in suite_records if record.get("repair_attempted")),
            "validation_coverage": _metric_average(suite_records, ["validation_coverage"]),
            "weighted_object_retention": _metric_average(
                suite_records,
                ["experiment_result", "metrics", "weighted_object_retention"],
            ),
            "lost_important_object_count": _metric_average(
                suite_records,
                ["experiment_result", "metrics", "lost_important_object_count"],
            ),
            "critical_failures_before": _metric_average(suite_records, ["critical_failures_before"]),
        }

    grouped_by_scenario: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for suite_name, suite_summary in summary["suites"].items():
        scenario = str(suite_summary.get("scenario") or "unknown")
        grouped_by_scenario.setdefault(scenario, {})[suite_name] = suite_summary

    for scenario, scenario_suites in grouped_by_scenario.items():
        disabled = next((item for name, item in scenario_suites.items() if name.endswith("chunk_score_only")), None)
        enabled = next((item for name, item in scenario_suites.items() if name.endswith("chunk_score_plus_object_support")), None)
        delta = {}
        if disabled and enabled:
            for metric in (
                "validation_coverage",
                "weighted_object_retention",
                "lost_important_object_count",
                "critical_failures_before",
            ):
                left = disabled.get(metric)
                right = enabled.get(metric)
                delta[f"delta_{metric}"] = None if left is None or right is None else float(right) - float(left)
        summary["scenarios"][scenario] = {
            "records": sum(item.get("records", 0) for item in scenario_suites.values()),
            "suites": scenario_suites,
            "delta": delta,
        }
    by_scenario_task: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for record in records:
        scenario = str(record.get("compression_scenario") or "unknown")
        task_id = str(record.get("task_id") or "unknown")
        by_scenario_task.setdefault(scenario, {}).setdefault(task_id, {})
        by_scenario_task[scenario][task_id][str(record.get("compression_suite") or "unknown")] = record
    for scenario, task_buckets in by_scenario_task.items():
        scenario_verifications: List[Dict[str, Any]] = []
        scenario_boundaries: List[Dict[str, Any]] = []
        for task_id, suite_records in task_buckets.items():
            disabled = next((record for name, record in suite_records.items() if name.endswith("chunk_score_only")), None)
            if disabled is None:
                continue
            verification = disabled.get("mechanism_verification")
            if verification is not None:
                scenario_verifications.append(verification)
            boundary = disabled.get("decision_boundary")
            if boundary is not None:
                scenario_boundaries.append(boundary)
        if scenario_verifications:
            def mean_metric(key: str) -> float | None:
                values = [item.get(key) for item in scenario_verifications if item.get(key) is not None]
                values = [float(value) for value in values]
                return (sum(values) / len(values)) if values else None

            summary["mechanism_verification"][scenario] = {
                "records": len(scenario_verifications),
                "score_changed_chunk_count": mean_metric("score_changed_chunk_count"),
                "score_changed_chunk_rate": mean_metric("score_changed_chunk_rate"),
                "topk_changed_rate": mean_metric("topk_changed"),
                "topk_delta_count": mean_metric("topk_delta_count"),
                "rank_flip_rate": mean_metric("rank_flip_rate"),
                "object_support_gain": mean_metric("object_support_gain"),
                "object_support_gain_topk": mean_metric("object_support_gain_topk"),
                "object_support_gain_max": mean_metric("object_support_gain_max"),
            }
        if scenario_boundaries:
            def boundary_mean_metric(key: str) -> float | None:
                values = [item.get(key) for item in scenario_boundaries if item.get(key) is not None]
                values = [float(value) for value in values]
                return (sum(values) / len(values)) if values else None

            summary["decision_boundary"][scenario] = {
                "records": len(scenario_boundaries),
                "first_changed_top_k": boundary_mean_metric("first_changed_top_k"),
                "topk_changed_rate": boundary_mean_metric("topk_changed_rate"),
                "rank_flip_rate_mean": boundary_mean_metric("rank_flip_rate_mean"),
                "decision_margin_min": boundary_mean_metric("decision_margin_min"),
                "decision_margin_mean": boundary_mean_metric("decision_margin_mean"),
                "gain_margin_ratio_mean": boundary_mean_metric("gain_margin_ratio_mean"),
                "decision_flip_distance_min": boundary_mean_metric("decision_flip_distance_min"),
                "decision_flip_distance_mean": boundary_mean_metric("decision_flip_distance_mean"),
                "requested_top_k_values": scenario_boundaries[0].get("requested_top_k_values"),
                "sweeps": scenario_boundaries[0].get("sweeps"),
            }
    return summary


def render_object_aware_compression_summary_markdown(summary: Dict[str, Any]) -> str:
    lines = ["# Object-Aware Compression Ablation", ""]
    lines.extend(
        [
            "| Scenario | Suite | Object Support | Records | Validation Passed | Repair Attempted | Validation Coverage | Weighted Object Retention | Lost Important Objects | Critical Failures Before |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )

    def fmt(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, float):
            return f"{value:.6f}".rstrip("0").rstrip(".")
        return str(value)

    for suite_name, suite_summary in sorted((summary.get("suites") or {}).items()):
        lines.append(
            "| "
            + " | ".join(
                [
                    fmt(suite_summary.get("scenario")),
                    str(suite_name),
                    fmt(suite_summary.get("object_support_enabled")),
                    fmt(suite_summary.get("records")),
                    fmt(suite_summary.get("validation_passed")),
                    fmt(suite_summary.get("repair_attempted")),
                    fmt(suite_summary.get("validation_coverage")),
                    fmt(suite_summary.get("weighted_object_retention")),
                    fmt(suite_summary.get("lost_important_object_count")),
                    fmt(suite_summary.get("critical_failures_before")),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Mechanism Verification",
            "",
            "| Scenario | Records | Score Changed Chunks | Score Changed Rate | Top-k Changed Rate | Top-k Delta Count | Rank Flip Rate | Object Support Gain | Object Support Gain (Top-k) | Object Support Gain (Max) |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for scenario, scenario_summary in sorted((summary.get("mechanism_verification") or {}).items()):
        lines.append(
            "| "
            + " | ".join(
                [
                    str(scenario),
                    fmt(scenario_summary.get("records")),
                    fmt(scenario_summary.get("score_changed_chunk_count")),
                    fmt(scenario_summary.get("score_changed_chunk_rate")),
                    fmt(scenario_summary.get("topk_changed_rate")),
                    fmt(scenario_summary.get("topk_delta_count")),
                    fmt(scenario_summary.get("rank_flip_rate")),
                    fmt(scenario_summary.get("object_support_gain")),
                    fmt(scenario_summary.get("object_support_gain_topk")),
                    fmt(scenario_summary.get("object_support_gain_max")),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Decision Boundary Sweep",
            "",
            "| Scenario | Records | First Changed Top-k | Top-k Changed Rate | Rank Flip Rate | Decision Margin Min | Decision Margin Mean | Gain/Margin Mean | Flip Distance Min | Flip Distance Mean |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for scenario, scenario_summary in sorted((summary.get("decision_boundary") or {}).items()):
        lines.append(
            "| "
            + " | ".join(
                [
                    str(scenario),
                    fmt(scenario_summary.get("records")),
                    fmt(scenario_summary.get("first_changed_top_k")),
                    fmt(scenario_summary.get("topk_changed_rate")),
                    fmt(scenario_summary.get("rank_flip_rate_mean")),
                    fmt(scenario_summary.get("decision_margin_min")),
                    fmt(scenario_summary.get("decision_margin_mean")),
                    fmt(scenario_summary.get("gain_margin_ratio_mean")),
                    fmt(scenario_summary.get("decision_flip_distance_min")),
                    fmt(scenario_summary.get("decision_flip_distance_mean")),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "### Decision Boundary Details",
            "",
            "| Scenario | Requested Top-k | Effective Top-k | Top-k Changed | Rank Flip Rate | Decision Margin | Gain/Margin | Flip Distance |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for scenario, scenario_summary in sorted((summary.get("decision_boundary") or {}).items()):
        for sweep in scenario_summary.get("sweeps") or []:
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(scenario),
                        fmt(sweep.get("requested_top_k")),
                        fmt(sweep.get("effective_top_k")),
                        fmt(sweep.get("topk_changed")),
                        fmt(sweep.get("rank_flip_rate")),
                        fmt(sweep.get("decision_margin_disabled")),
                        fmt(sweep.get("gain_margin_ratio")),
                        fmt(sweep.get("decision_flip_distance")),
                    ]
                )
                + " |"
            )
    lines.extend(
        [
            "",
            "## Scenario Deltas",
            "",
            "| Scenario | Delta Validation Coverage | Delta Weighted Object Retention | Delta Lost Important Objects | Delta Critical Failures Before |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for scenario, scenario_summary in sorted((summary.get("scenarios") or {}).items()):
        delta = scenario_summary.get("delta") or {}
        lines.append(
            "| "
            + " | ".join(
                [
                    str(scenario),
                    fmt(delta.get("delta_validation_coverage")),
                    fmt(delta.get("delta_weighted_object_retention")),
                    fmt(delta.get("delta_lost_important_object_count")),
                    fmt(delta.get("delta_critical_failures_before")),
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def write_object_aware_compression_outputs(
    records: Sequence[Dict[str, Any]],
    output_dir: str | Path,
) -> Dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_path / "object_aware_compression_records.jsonl"
    csv_path = output_path / "object_aware_compression_records.csv"
    markdown_path = output_path / "object_aware_compression_audit.md"
    summary_path = output_path / "object_aware_compression_summary.md"

    with jsonl_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    summary = summarize_object_aware_compression(records)
    write_records_csv(records, csv_path)
    write_records_markdown(records, markdown_path)
    summary_path.write_text(render_object_aware_compression_summary_markdown(summary), encoding="utf-8")
    return {
        "jsonl": jsonl_path,
        "csv": csv_path,
        "markdown": markdown_path,
        "summary": summary_path,
    }

