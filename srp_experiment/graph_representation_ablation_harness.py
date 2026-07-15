from __future__ import annotations

import copy
import json
import os
import random
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence

from .graph_recovery_harness import (
    _build_recovery_package,
    _build_tasks,
    _build_validation_runtime_metadata,
    _delta,
    _fmt,
    _metric_average,
    _temporary_env,
)
from .srp.export import write_records_csv, write_records_markdown
from .srp.recover import recover_state
from .srp.semantic_graph import build_semantic_runtime_graph_by_version
from .srp.validate import validate_state
from .srp.validation_targets import build_validation_targets


@dataclass(frozen=True)
class GraphRepresentationSuite:
    name: str
    scenario: str
    group: str
    representation_version: str
    recovery_mode: str
    graph_schema_version: str
    task: Dict[str, Any]


def _scenario_tasks() -> List[Dict[str, Any]]:
    return _build_tasks()


def build_graph_representation_suites() -> List[GraphRepresentationSuite]:
    suites: List[GraphRepresentationSuite] = []
    for task in _scenario_tasks():
        scenario = str(task.get("metadata", {}).get("scenario") or task.get("id") or "scenario")
        suites.extend(
            [
                GraphRepresentationSuite(
                    name=f"{scenario}_A_text",
                    scenario=scenario,
                    group="A",
                    representation_version="text",
                    recovery_mode="text",
                    graph_schema_version="semantic_runtime_graph.v1",
                    task=copy.deepcopy(task),
                ),
                GraphRepresentationSuite(
                    name=f"{scenario}_B_structured",
                    scenario=scenario,
                    group="B",
                    representation_version="structured",
                    recovery_mode="structured",
                    graph_schema_version="semantic_runtime_graph.v1",
                    task=copy.deepcopy(task),
                ),
                GraphRepresentationSuite(
                    name=f"{scenario}_C_graph_v1",
                    scenario=scenario,
                    group="C",
                    representation_version="v1",
                    recovery_mode="graph",
                    graph_schema_version="semantic_runtime_graph.v1",
                    task=copy.deepcopy(task),
                ),
                GraphRepresentationSuite(
                    name=f"{scenario}_D_graph_v1_5",
                    scenario=scenario,
                    group="D",
                    representation_version="v1.5",
                    recovery_mode="graph",
                    graph_schema_version="semantic_runtime_graph.v1.5",
                    task=copy.deepcopy(task),
                ),
            ]
        )
    return suites


def available_suite_names() -> List[str]:
    return [suite.name for suite in build_graph_representation_suites()]


def select_graph_representation_suites(names: Sequence[str] | None = None) -> List[GraphRepresentationSuite]:
    suites = build_graph_representation_suites()
    if not names:
        return suites
    requested = {str(name).strip() for name in names if str(name).strip()}
    if not requested or "all" in requested:
        return suites
    selected = [suite for suite in suites if suite.name in requested]
    missing = requested - {suite.name for suite in selected}
    if missing:
        raise ValueError(f"Unknown graph representation suite(s): {', '.join(sorted(missing))}")
    return selected


def _graph_version_for_suite(suite: GraphRepresentationSuite) -> str:
    if suite.graph_schema_version.endswith("v1.5"):
        return "v1.5"
    return "v1"


def _build_graph_validation_record(
    task: Dict[str, Any],
    source_package: Dict[str, Any],
    recovered_package: Dict[str, Any],
    *,
    graph_version: str,
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    graph = build_semantic_runtime_graph_by_version(
        source_package,
        recovered_package,
        build_validation_targets(task),
        version=graph_version,
    )
    summary = graph.summary.get("validation_v1_5" if graph_version == "v1.5" else "validation") or {}
    return graph.as_v1_5_dict() if graph_version == "v1.5" else graph.as_dict(), summary


def _group_average(records: Sequence[Dict[str, Any]], key: str) -> float | None:
    return _metric_average(records, [key])


def _group_summary(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    attribute_retention = _group_average(records, "attribute_retention")
    state_retention = _group_average(records, "state_retention")
    lifecycle_accuracy = _group_average(records, "lifecycle_accuracy")
    return {
        "records": len(records),
        "validation_passed": sum(1 for record in records if record.get("validation_passed")),
        "validation_coverage": _group_average(records, "validation_coverage"),
        "dependency_coverage": _group_average(records, "dependency_coverage"),
        "dependency_precision": _group_average(records, "dependency_precision"),
        "dependency_f1": _group_average(records, "dependency_f1"),
        "object_survival_rate": _group_average(records, "object_survival_rate"),
        "dependency_recall": _group_average(records, "dependency_recall"),
        "constraint_accuracy": _group_average(records, "constraint_accuracy"),
        "attribute_retention": 0.0 if attribute_retention is None else attribute_retention,
        "state_retention": 0.0 if state_retention is None else state_retention,
        "lifecycle_accuracy": 0.0 if lifecycle_accuracy is None else lifecycle_accuracy,
        "hallucinated_count": _group_average(records, "hallucinated_count"),
        "graph_integrity_score": _group_average(records, "graph_integrity_score"),
        "graph_repair_cost": _group_average(records, "graph_repair_cost"),
    }


def run_graph_representation_ablation(
    suites: Sequence[str] | None = None,
    *,
    cycles: int = 1,
    seeds: int = 5,
) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for suite in select_graph_representation_suites(suites):
        for seed in range(1, seeds + 1):
            random.seed(seed)
            for cycle in range(1, cycles + 1):
                package, state = _build_recovery_package(suite.task)
                with _temporary_env(
                    {
                        "SRP_RECOVERY_MODE": suite.recovery_mode,
                        "SRP_SEMANTIC_GRAPH_VERSION": _graph_version_for_suite(suite),
                        "SRP_RANDOM_ALLOCATION_SEED": str(seed),
                    }
                ):
                    recovered = recover_state(package, client=None, anchor_memory=suite.task["initial_state"]["memory"])
                recovered_state = recovered.as_dict()
                recovered_package = dict(recovered_state.get("recovered_state_package") or {})
                validation_targets = build_validation_targets(suite.task)
                validation = validate_state(
                    suite.task["initial_state"]["memory"],
                    recovered.memory,
                    validation_targets,
                    runtime_metadata=_build_validation_runtime_metadata(state, package),
                    recovered_state_package=recovered_package,
                    dependency_labels=suite.task.get("metadata", {}).get("required_dependency_labels"),
                    dependency_objects=suite.task.get("semantic_dependencies", {}).get("required_dependency_objects"),
                )
                graph_version = _graph_version_for_suite(suite)
                semantic_runtime_graph, graph_validation = _build_graph_validation_record(
                    suite.task,
                    package,
                    recovered_package,
                    graph_version=graph_version,
                )
                graph_result = dict(recovered_package.get("graph_recovery_result") or {})
                graph_nodes = semantic_runtime_graph.get("nodes", []) if isinstance(semantic_runtime_graph, dict) else []
                graph_edges = semantic_runtime_graph.get("edges", []) if isinstance(semantic_runtime_graph, dict) else []
                record: Dict[str, Any] = {
                    "cycle": cycle,
                    "seed": seed,
                    "task_id": suite.task.get("id"),
                    "task_type": suite.task.get("task_type"),
                    "task_source": "graph_representation_ablation",
                    "graph_representation_group": suite.group,
                    "graph_representation_version": suite.representation_version,
                    "graph_schema_version": suite.graph_schema_version,
                    "graph_recovery_mode": suite.recovery_mode,
                    "graph_recovery_scenario": suite.scenario,
                    "graph_representation_ablation": {
                        "schema_version": "graph_representation_ablation.v1",
                        "suite": suite.name,
                        "group": suite.group,
                        "representation_version": suite.representation_version,
                        "recovery_mode": suite.recovery_mode,
                        "graph_schema_version": suite.graph_schema_version,
                        "scenario": suite.scenario,
                        "task_id": suite.task.get("id"),
                        "cycle": cycle,
                        "seed": seed,
                    },
                    "source_package": package,
                    "recovered_text": recovered.memory,
                    "recovered_state_package": recovered_package,
                    "reconstruction_result": recovered_state.get("reconstruction_result"),
                    "graph_recovery_result": graph_result or None,
                    "semantic_runtime_graph": semantic_runtime_graph,
                    "semantic_graph_validation": graph_validation,
                    "validation": validation,
                    "validation_passed": validation.get("passed"),
                    "validation_coverage": validation.get("coverage_score"),
                    "dependency_coverage": validation.get("dependency_coverage"),
                    "dependency_precision": validation.get("dependency_precision"),
                    "dependency_f1": validation.get("dependency_f1"),
                    "critical_failures": validation.get("critical_failures"),
                    "critical_failures_count": len(validation.get("critical_failures") or []),
                    "object_survival_rate": graph_validation.get("object_survival_rate"),
                    "dependency_recall": graph_validation.get("dependency_recall"),
                    "constraint_accuracy": graph_validation.get("constraint_accuracy"),
                    "attribute_retention": graph_validation.get("attribute_retention"),
                    "state_retention": graph_validation.get("state_retention"),
                    "lifecycle_accuracy": graph_validation.get("lifecycle_accuracy"),
                    "hallucinated_count": graph_validation.get("hallucinated_node_count"),
                    "hallucination_rate": graph_validation.get("hallucination_rate"),
                    "graph_integrity_score": graph_validation.get("graph_integrity_score"),
                    "graph_node_count": len(graph_nodes),
                    "graph_edge_count": len(graph_edges),
                    "graph_dependency_closure_rate": graph_result.get("dependency_closure_rate"),
                    "graph_recovery_precision": graph_result.get("graph_recovery_precision"),
                    "graph_repair_cost": graph_result.get("repair_cost")
                    if graph_result
                    else int(
                        (graph_validation.get("missing_dependency_count") or 0)
                        + (graph_validation.get("hallucinated_node_count") or 0)
                    ),
                    "graph_dependency_edge_count": graph_result.get("dependency_edge_count"),
                    "graph_blocked_count": graph_result.get("blocked_count"),
                }
                records.append(record)
    return records


def summarize_graph_representation_ablation(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "records": len(records),
        "groups": {},
        "scenarios": {},
    }
    grouped_by_group: Dict[str, List[Dict[str, Any]]] = {}
    grouped_by_scenario: Dict[str, List[Dict[str, Any]]] = {}
    for record in records:
        group = str(record.get("graph_representation_group") or "unknown")
        scenario = str(record.get("graph_recovery_scenario") or "unknown")
        grouped_by_group.setdefault(group, []).append(record)
        grouped_by_scenario.setdefault(scenario, []).append(record)

    for group, group_records in grouped_by_group.items():
        summary["groups"][group] = _group_summary(group_records)

    for scenario, scenario_records in grouped_by_scenario.items():
        scenario_summary = {
            "records": len(scenario_records),
            "validation_passed": sum(1 for record in scenario_records if record.get("validation_passed")),
            "groups": {},
        }
        for group in ["A", "B", "C", "D"]:
            group_records = [record for record in scenario_records if record.get("graph_representation_group") == group]
            if not group_records:
                continue
            scenario_summary["groups"][group] = _group_summary(group_records)
        if "C" in scenario_summary["groups"] and "D" in scenario_summary["groups"]:
                scenario_summary["delta"] = {
                    "D_minus_C": {
                    "validation_coverage": _delta(
                        scenario_summary["groups"]["D"].get("validation_coverage"),
                        scenario_summary["groups"]["C"].get("validation_coverage"),
                    ),
                    "object_survival_rate": _delta(
                        scenario_summary["groups"]["D"].get("object_survival_rate"),
                        scenario_summary["groups"]["C"].get("object_survival_rate"),
                    ),
                    "dependency_recall": _delta(
                        scenario_summary["groups"]["D"].get("dependency_recall"),
                        scenario_summary["groups"]["C"].get("dependency_recall"),
                    ),
                    "constraint_accuracy": _delta(
                        scenario_summary["groups"]["D"].get("constraint_accuracy"),
                        scenario_summary["groups"]["C"].get("constraint_accuracy"),
                    ),
                    "attribute_retention": _delta(
                        scenario_summary["groups"]["D"].get("attribute_retention"),
                        scenario_summary["groups"]["C"].get("attribute_retention"),
                    ),
                    "state_retention": _delta(
                        scenario_summary["groups"]["D"].get("state_retention"),
                        scenario_summary["groups"]["C"].get("state_retention"),
                    ),
                    "lifecycle_accuracy": _delta(
                        scenario_summary["groups"]["D"].get("lifecycle_accuracy"),
                        scenario_summary["groups"]["C"].get("lifecycle_accuracy"),
                    ),
                    "hallucinated_count": _delta(
                        scenario_summary["groups"]["D"].get("hallucinated_count"),
                        scenario_summary["groups"]["C"].get("hallucinated_count"),
                    ),
                    "graph_integrity_score": _delta(
                        scenario_summary["groups"]["D"].get("graph_integrity_score"),
                        scenario_summary["groups"]["C"].get("graph_integrity_score"),
                    ),
                    "graph_repair_cost": _delta(
                        scenario_summary["groups"]["D"].get("graph_repair_cost"),
                        scenario_summary["groups"]["C"].get("graph_repair_cost"),
                    ),
                }
            }
        summary["scenarios"][scenario] = scenario_summary

    summary["comparison"] = {
        "graph_v1_5_minus_graph_v1": {
            "validation_coverage": _comparison_delta(summary, "D", "C", "validation_coverage"),
            "object_survival_rate": _comparison_delta(summary, "D", "C", "object_survival_rate"),
            "dependency_recall": _comparison_delta(summary, "D", "C", "dependency_recall"),
            "constraint_accuracy": _comparison_delta(summary, "D", "C", "constraint_accuracy"),
            "attribute_retention": _comparison_delta(summary, "D", "C", "attribute_retention"),
            "state_retention": _comparison_delta(summary, "D", "C", "state_retention"),
            "lifecycle_accuracy": _comparison_delta(summary, "D", "C", "lifecycle_accuracy"),
            "hallucinated_count": _comparison_delta(summary, "D", "C", "hallucinated_count"),
            "graph_integrity_score": _comparison_delta(summary, "D", "C", "graph_integrity_score"),
            "graph_repair_cost": _comparison_delta(summary, "D", "C", "graph_repair_cost"),
        }
    }
    return summary


def _comparison_delta(summary: Dict[str, Any], left_group: str, right_group: str, key: str) -> float | None:
    left = (summary.get("groups") or {}).get(left_group, {}).get(key)
    right = (summary.get("groups") or {}).get(right_group, {}).get(key)
    if key in {"attribute_retention", "state_retention", "lifecycle_accuracy"}:
        left = 0.0 if left is None else left
        right = 0.0 if right is None else right
    return _delta(left, right)


def render_graph_representation_ablation_markdown(summary: Dict[str, Any]) -> str:
    lines = ["# Graph Representation Ablation", ""]
    lines.extend(
        [
            "| Group | Representation | Recovery Mode | Records | Validation Passed | Validation Coverage | Object Survival Rate | Dependency Recall | Constraint Accuracy | Attribute Retention | State Retention | Lifecycle Accuracy | Hallucinated Count | Graph Integrity Score | Graph Repair Cost |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    group_labels = {
        "A": "text",
        "B": "structured",
        "C": "graph v1",
        "D": "graph v1.5",
    }
    recovery_modes = {
        "A": "text",
        "B": "structured",
        "C": "graph",
        "D": "graph",
    }
    for group, group_summary in sorted((summary.get("groups") or {}).items()):
        lines.append(
            "| "
            + " | ".join(
                [
                    str(group),
                    group_labels.get(group, ""),
                    recovery_modes.get(group, ""),
                    _fmt(group_summary.get("records")),
                    _fmt(group_summary.get("validation_passed")),
                    _fmt(group_summary.get("validation_coverage")),
                    _fmt(group_summary.get("object_survival_rate")),
                    _fmt(group_summary.get("dependency_recall")),
                    _fmt(group_summary.get("constraint_accuracy")),
                    _fmt(group_summary.get("attribute_retention")),
                    _fmt(group_summary.get("state_retention")),
                    _fmt(group_summary.get("lifecycle_accuracy")),
                    _fmt(group_summary.get("hallucinated_count")),
                    _fmt(group_summary.get("graph_integrity_score")),
                    _fmt(group_summary.get("graph_repair_cost")),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Scenario Summary", ""])
    lines.extend(
        [
            "| Scenario | Group | Validation Coverage | Object Survival Rate | Dependency Recall | Constraint Accuracy | Attribute Retention | State Retention | Lifecycle Accuracy | Hallucinated Count | Graph Integrity Score | Graph Repair Cost |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for scenario, scenario_summary in sorted((summary.get("scenarios") or {}).items()):
        for group, group_summary in sorted((scenario_summary.get("groups") or {}).items()):
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(scenario),
                        str(group),
                        _fmt(group_summary.get("validation_coverage")),
                        _fmt(group_summary.get("object_survival_rate")),
                        _fmt(group_summary.get("dependency_recall")),
                        _fmt(group_summary.get("constraint_accuracy")),
                        _fmt(group_summary.get("attribute_retention")),
                        _fmt(group_summary.get("state_retention")),
                        _fmt(group_summary.get("lifecycle_accuracy")),
                        _fmt(group_summary.get("hallucinated_count")),
                        _fmt(group_summary.get("graph_integrity_score")),
                        _fmt(group_summary.get("graph_repair_cost")),
                    ]
                )
                + " |"
            )

    lines.extend(["", "## Representation Deltas", ""])
    lines.extend(
        [
            "| Comparison | Validation Coverage | Object Survival Rate | Dependency Recall | Constraint Accuracy | Attribute Retention | State Retention | Lifecycle Accuracy | Hallucinated Count | Graph Integrity Score | Graph Repair Cost |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for comparison_name, comparison_summary in sorted((summary.get("comparison") or {}).items()):
        lines.append(
            "| "
            + " | ".join(
                [
                    str(comparison_name),
                    _fmt(comparison_summary.get("validation_coverage")),
                    _fmt(comparison_summary.get("object_survival_rate")),
                    _fmt(comparison_summary.get("dependency_recall")),
                    _fmt(comparison_summary.get("constraint_accuracy")),
                    _fmt(comparison_summary.get("attribute_retention")),
                    _fmt(comparison_summary.get("state_retention")),
                    _fmt(comparison_summary.get("lifecycle_accuracy")),
                    _fmt(comparison_summary.get("hallucinated_count")),
                    _fmt(comparison_summary.get("graph_integrity_score")),
                    _fmt(comparison_summary.get("graph_repair_cost")),
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def write_graph_representation_ablation_outputs(
    records: Sequence[Dict[str, Any]],
    output_dir: str | Path,
) -> Dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_path / "graph_representation_ablation_records.jsonl"
    csv_path = output_path / "graph_representation_ablation_records.csv"
    markdown_path = output_path / "graph_representation_ablation_audit.md"
    summary_path = output_path / "graph_representation_ablation_summary.md"
    json_path = output_path / "graph_representation_ablation.json"

    with jsonl_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    summary = summarize_graph_representation_ablation(records)
    write_records_csv(records, csv_path)
    write_records_markdown(records, markdown_path)
    summary_path.write_text(render_graph_representation_ablation_markdown(summary), encoding="utf-8")
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return {
        "jsonl": jsonl_path,
        "csv": csv_path,
        "markdown": markdown_path,
        "summary": summary_path,
        "json": json_path,
    }
