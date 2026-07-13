from __future__ import annotations

import copy
import json
import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence

from .srp.compress import compress_state
from .srp.export import write_records_csv, write_records_markdown
from .srp.pipeline_runtime import initialize_state
from .srp.recover import recover_state
from .srp.semantic_graph import build_semantic_runtime_graph
from .srp.semantic_parser import stable_semantic_object_id
from .srp.state import SemanticObjectMetadata
from .srp.validate import validate_state
from .srp.validation_targets import build_validation_targets


@dataclass(frozen=True)
class GraphRecoverySuite:
    name: str
    scenario: str
    recovery_mode: str
    task: Dict[str, Any]


def _dependency_object(
    dependency_id: str,
    subject_value: str,
    relation_value: str,
    object_value: str,
    *,
    subject_type: str = "entity",
    relation_type: str = "relation",
    object_type: str = "entity",
) -> Dict[str, Any]:
    return {
        "dependency_id": dependency_id,
        "subject": {
            "type": subject_type,
            "canonical": subject_value,
            "object_id": stable_semantic_object_id(subject_type, subject_value),
        },
        "relation": {
            "type": relation_type,
            "canonical": relation_value,
            "object_id": stable_semantic_object_id(relation_type, relation_value),
        },
        "object": {
            "type": object_type,
            "canonical": object_value,
            "object_id": stable_semantic_object_id(object_type, object_value),
        },
    }


def _task(
    *,
    task_id: str,
    scenario: str,
    memory: str,
    constraints: Sequence[str],
    query_expectation: str,
    dependency_objects: Sequence[Dict[str, Any]],
    expected_keywords: Sequence[str],
) -> Dict[str, Any]:
    dependency_labels = [
        " ".join(
            value
            for value in [
                str(item.get("subject", {}).get("canonical", "")).strip(),
                str(item.get("relation", {}).get("canonical", "")).strip(),
                str(item.get("object", {}).get("canonical", "")).strip(),
            ]
            if value
        )
        for item in dependency_objects
    ]
    return {
        "id": task_id,
        "task_type": "graph_recovery_evaluation",
        "source": "SRP Graph Recovery Evaluation Harness",
        "initial_state": {
            "constraints": list(constraints),
            "memory": memory,
        },
        "query_expectations": [[[query_expectation]]],
        "expected_keywords": list(expected_keywords),
        "semantic_dependencies": {
            "required_dependency_objects": list(dependency_objects),
        },
        "metadata": {
            "benchmark": "SRP Graph Recovery Evaluation",
            "round": "1",
            "scenario": scenario,
            "required_dependency_labels": dependency_labels,
            "required_dependency_objects": list(dependency_objects),
        },
    }


def _dependency_chain_task() -> Dict[str, Any]:
    return _task(
        task_id="graph-recovery-dependency-chain",
        scenario="dependency_chain",
        memory=(
            "John owns the blue key. "
            "The blue key opens Room A. "
            "John cannot enter Room A. "
            "Keep the key ownership chain intact."
        ),
        constraints=[
            "John owns the blue key.",
            "The blue key opens Room A.",
            "John cannot enter Room A.",
        ],
        query_expectation="John owns the blue key.",
        dependency_objects=[
            _dependency_object("dep-1", "John", "owns", "blue key"),
            _dependency_object("dep-2", "blue key", "opens", "Room A"),
            _dependency_object("dep-3", "John", "cannot enter", "Room A", relation_type="constraint"),
        ],
        expected_keywords=["john", "blue", "key", "room", "intact"],
    )


def _identity_collision_task() -> Dict[str, Any]:
    return _task(
        task_id="graph-recovery-identity-collision",
        scenario="identity_collision",
        memory=(
            "Orion owns Atlas in the payments lane. "
            "Mercury owns Atlas in the analytics lane. "
            "Nova owns Atlas in the reporting lane. "
            "Preserve the lane assignments."
        ),
        constraints=[
            "Orion owns Atlas in the payments lane.",
            "Mercury owns Atlas in the analytics lane.",
            "Nova owns Atlas in the reporting lane.",
        ],
        query_expectation="Orion owns Atlas in the payments lane.",
        dependency_objects=[
            _dependency_object("dep-1", "Orion", "owns", "Atlas in the payments lane"),
            _dependency_object("dep-2", "Mercury", "owns", "Atlas in the analytics lane"),
            _dependency_object("dep-3", "Nova", "owns", "Atlas in the reporting lane"),
        ],
        expected_keywords=["orion", "mercury", "nova", "atlas", "lane"],
    )


def _constraint_closure_task() -> Dict[str, Any]:
    return _task(
        task_id="graph-recovery-constraint-closure",
        scenario="constraint_closure",
        memory=(
            "Only Alice can access the key. "
            "Bob cannot access the key. "
            "Alice opens Door B. "
            "Keep the access constraint closed."
        ),
        constraints=[
            "Only Alice can access the key.",
            "Bob cannot access the key.",
            "Alice opens Door B.",
        ],
        query_expectation="Only Alice can access the key.",
        dependency_objects=[
            _dependency_object("dep-1", "Alice", "can access", "the key", relation_type="access"),
            _dependency_object("dep-2", "Bob", "cannot access", "the key", relation_type="constraint"),
            _dependency_object("dep-3", "Alice", "opens", "Door B"),
        ],
        expected_keywords=["alice", "bob", "key", "door", "constraint"],
    )


def _build_tasks() -> List[Dict[str, Any]]:
    return [
        _dependency_chain_task(),
        _identity_collision_task(),
        _constraint_closure_task(),
    ]


def build_graph_recovery_suites() -> List[GraphRecoverySuite]:
    suites: List[GraphRecoverySuite] = []
    for task in _build_tasks():
        scenario = str(task.get("metadata", {}).get("scenario") or task.get("id") or "scenario")
        for mode in ["text", "structured", "graph"]:
            suites.append(
                GraphRecoverySuite(
                    name=f"{scenario}_{mode}",
                    scenario=scenario,
                    recovery_mode=mode,
                    task=copy.deepcopy(task),
                )
            )
    return suites


def available_suite_names() -> List[str]:
    return [suite.name for suite in build_graph_recovery_suites()]


def select_graph_recovery_suites(names: Sequence[str] | None = None) -> List[GraphRecoverySuite]:
    suites = build_graph_recovery_suites()
    if not names:
        return suites
    requested = {str(name).strip() for name in names if str(name).strip()}
    if not requested or "all" in requested:
        return suites
    selected = [suite for suite in suites if suite.name in requested]
    missing = requested - {suite.name for suite in selected}
    if missing:
        raise ValueError(f"Unknown graph recovery suite(s): {', '.join(sorted(missing))}")
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


def _augment_package_with_dependency_objects(package: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
    package = copy.deepcopy(package)
    dependency_objects = list((task.get("semantic_dependencies") or {}).get("required_dependency_objects", []))
    if not dependency_objects:
        package["semantic_dependencies"] = copy.deepcopy(task.get("semantic_dependencies") or {})
        return package

    inventory = dict(package.get("semantic_object_inventory") or {})
    typed_representation = dict(package.get("typed_representation") or {})
    inventory_objects = [dict(item) for item in list(inventory.get("objects", [])) if isinstance(item, dict)]
    typed_objects = [dict(item) for item in list(typed_representation.get("objects", [])) if isinstance(item, dict)]
    inventory_index = {
        str(item.get("object_id") or item.get("id") or ""): item
        for item in inventory_objects
        if str(item.get("object_id") or item.get("id") or "").strip()
    }
    typed_index = {
        str(item.get("object_id") or item.get("id") or ""): item
        for item in typed_objects
        if str(item.get("object_id") or item.get("id") or "").strip()
    }
    runtime_metadata = dict(package.get("runtime_metadata") or {})

    for dependency_index, dependency in enumerate(dependency_objects, start=1):
        for part_name, default_type in [("subject", "entity"), ("relation", "relation"), ("object", "entity")]:
            part = dependency.get(part_name) or {}
            value = str(part.get("canonical") or part.get("value") or "").strip()
            if not value:
                continue
            object_type = str(part.get("type") or default_type).strip() or default_type
            object_id = str(part.get("object_id") or stable_semantic_object_id(object_type, value)).strip()
            evidence_pointer = f"dependency:{dependency_index}:{part_name}"
            obj = {
                "object_id": object_id,
                "type": object_type,
                "value": value,
                "confidence": 0.9 if object_type != "constraint" else 1.0,
                "evidence_pointer": evidence_pointer,
                "metadata": {
                    "source": "semantic_dependencies",
                    "dependency_id": str(dependency.get("dependency_id", "")),
                    "role": part_name,
                },
            }
            if object_id not in inventory_index:
                inventory_objects.append(obj)
                inventory_index[object_id] = obj
            if object_id not in typed_index:
                typed_objects.append(obj)
                typed_index[object_id] = obj
            runtime_metadata.setdefault(
                object_id,
                {
                    "importance": 0.9 if object_type != "relation" else 0.85,
                    "confidence": obj["confidence"],
                },
            )

    type_counts: Dict[str, int] = {}
    important_objects: List[Dict[str, Any]] = []
    for item in inventory_objects:
        object_type = str(item.get("type", "fact")).strip() or "fact"
        type_counts[object_type] = type_counts.get(object_type, 0) + 1
        if object_type in {"question", "constraint", "anchor"} or float(item.get("confidence", 0.0) or 0.0) >= 0.8:
            important_objects.append(
                {
                    "object_id": str(item.get("object_id") or item.get("id") or "").strip(),
                    "type": object_type,
                    "value": str(item.get("value", "")),
                    "confidence": round(float(item.get("confidence", 0.0) or 0.0), 4),
                    "evidence_pointer": str(item.get("evidence_pointer", "")),
                }
            )

    object_ids = [
        str(item.get("object_id") or item.get("id") or "").strip()
        for item in inventory_objects
        if str(item.get("object_id") or item.get("id") or "").strip()
    ]
    inventory.update(
        {
            "schema_version": "semantic_object_inventory.v1",
            "object_count": len(inventory_objects),
            "object_ids": object_ids,
            "type_counts": type_counts,
            "important_objects": important_objects[:20],
            "objects": inventory_objects,
        }
    )
    typed_representation["objects"] = typed_objects
    package["semantic_object_inventory"] = inventory
    package["semantic_objects"] = inventory_objects
    package["typed_representation"] = typed_representation
    package["runtime_metadata"] = runtime_metadata
    package["semantic_dependencies"] = copy.deepcopy(task.get("semantic_dependencies") or {})
    return package


def _build_recovery_package(task: Dict[str, Any]) -> tuple[Dict[str, Any], Any]:
    state = initialize_state(task, encoder=None)
    package = compress_state(state, client=None)
    return _augment_package_with_dependency_objects(package, task), state


def _build_validation_runtime_metadata(state, package: Dict[str, Any]) -> Dict[str, SemanticObjectMetadata]:
    runtime_metadata = dict(state.runtime_metadata)
    package_runtime_metadata = package.get("runtime_metadata") or {}
    for object_id, metadata in package_runtime_metadata.items():
        if object_id in runtime_metadata:
            continue
        if not isinstance(metadata, dict):
            continue
        runtime_metadata[object_id] = SemanticObjectMetadata(
            importance=float(metadata.get("importance", 0.0) or 0.0),
            confidence=float(metadata.get("confidence", 0.0) or 0.0),
        )
    return runtime_metadata


def _build_graph_validation_record(
    task: Dict[str, Any],
    source_package: Dict[str, Any],
    recovered_package: Dict[str, Any],
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    graph = build_semantic_runtime_graph(source_package, recovered_package, build_validation_targets(task))
    return graph.as_dict(), graph.summary.get("validation") or {}


def _extract_graph_result(recovered_package: Dict[str, Any]) -> Dict[str, Any]:
    return dict(recovered_package.get("graph_recovery_result") or {})


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


def run_graph_recovery_evaluation(
    suites: Sequence[str] | None = None,
    *,
    cycles: int = 1,
) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for suite in select_graph_recovery_suites(suites):
        for cycle in range(1, cycles + 1):
            package, state = _build_recovery_package(suite.task)
            with _temporary_env({"SRP_RECOVERY_MODE": suite.recovery_mode}):
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
            semantic_runtime_graph, graph_validation = _build_graph_validation_record(suite.task, package, recovered_package)
            graph_result = _extract_graph_result(recovered_package)
            graph_nodes = semantic_runtime_graph.get("nodes", []) if isinstance(semantic_runtime_graph, dict) else []
            graph_edges = semantic_runtime_graph.get("edges", []) if isinstance(semantic_runtime_graph, dict) else []
            record: Dict[str, Any] = {
                "cycle": cycle,
                "task_id": suite.task.get("id"),
                "task_type": suite.task.get("task_type"),
                "task_source": "graph_recovery_evaluation",
                "graph_recovery_suite": suite.name,
                "graph_recovery_mode": suite.recovery_mode,
                "graph_recovery_scenario": suite.scenario,
                "graph_recovery_evaluation": {
                    "schema_version": "graph_recovery_evaluation.v1",
                    "suite": suite.name,
                    "mode": suite.recovery_mode,
                    "scenario": suite.scenario,
                    "task_id": suite.task.get("id"),
                    "cycle": cycle,
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
                "hallucinated_count": graph_validation.get("hallucinated_node_count"),
                "hallucination_rate": graph_validation.get("hallucination_rate"),
                "graph_integrity_score": graph_validation.get("graph_integrity_score"),
                "graph_node_count": len(graph_nodes),
                "graph_edge_count": len(graph_edges),
                "graph_object_survival_rate": graph_validation.get("object_survival_rate"),
                "graph_dependency_recall": graph_validation.get("dependency_recall"),
                "graph_constraint_accuracy": graph_validation.get("constraint_accuracy"),
                "graph_hallucination_rate": graph_validation.get("hallucination_rate"),
                "graph_integrity_score": graph_validation.get("graph_integrity_score"),
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


def summarize_graph_recovery_evaluation(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "records": len(records),
        "modes": {},
        "scenarios": {},
    }
    grouped_by_mode: Dict[str, List[Dict[str, Any]]] = {}
    grouped_by_scenario: Dict[str, List[Dict[str, Any]]] = {}
    for record in records:
        mode = str(record.get("graph_recovery_mode") or "unknown")
        scenario = str(record.get("graph_recovery_scenario") or "unknown")
        grouped_by_mode.setdefault(mode, []).append(record)
        grouped_by_scenario.setdefault(scenario, []).append(record)

    for mode, mode_records in grouped_by_mode.items():
        summary["modes"][mode] = {
            "records": len(mode_records),
            "validation_passed": sum(1 for record in mode_records if record.get("validation_passed")),
            "validation_coverage": _metric_average(mode_records, ["validation_coverage"]),
            "dependency_coverage": _metric_average(mode_records, ["dependency_coverage"]),
            "dependency_precision": _metric_average(mode_records, ["dependency_precision"]),
            "dependency_f1": _metric_average(mode_records, ["dependency_f1"]),
            "object_survival_rate": _metric_average(mode_records, ["object_survival_rate"]),
            "dependency_recall": _metric_average(mode_records, ["dependency_recall"]),
            "constraint_accuracy": _metric_average(mode_records, ["constraint_accuracy"]),
            "hallucinated_count": _metric_average(mode_records, ["hallucinated_count"]),
            "hallucination_rate": _metric_average(mode_records, ["hallucination_rate"]),
            "graph_integrity_score": _metric_average(mode_records, ["graph_integrity_score"]),
            "graph_dependency_closure_rate": _metric_average(mode_records, ["graph_dependency_closure_rate"]),
            "graph_recovery_precision": _metric_average(mode_records, ["graph_recovery_precision"]),
            "graph_repair_cost": _metric_average(mode_records, ["graph_repair_cost"]),
        }

    for scenario, scenario_records in grouped_by_scenario.items():
        scenario_summary = {
            "records": len(scenario_records),
            "validation_passed": sum(1 for record in scenario_records if record.get("validation_passed")),
            "modes": {},
        }
        for mode in ["text", "structured", "graph"]:
            mode_records = [record for record in scenario_records if record.get("graph_recovery_mode") == mode]
            if not mode_records:
                continue
            scenario_summary["modes"][mode] = {
                "records": len(mode_records),
                "validation_coverage": _metric_average(mode_records, ["validation_coverage"]),
                "dependency_coverage": _metric_average(mode_records, ["dependency_coverage"]),
                "dependency_precision": _metric_average(mode_records, ["dependency_precision"]),
                "dependency_f1": _metric_average(mode_records, ["dependency_f1"]),
                "object_survival_rate": _metric_average(mode_records, ["object_survival_rate"]),
                "dependency_recall": _metric_average(mode_records, ["dependency_recall"]),
                "hallucinated_count": _metric_average(mode_records, ["hallucinated_count"]),
                "graph_integrity_score": _metric_average(mode_records, ["graph_integrity_score"]),
                "graph_repair_cost": _metric_average(mode_records, ["graph_repair_cost"]),
            }
        if "graph" in scenario_summary["modes"] and "text" in scenario_summary["modes"]:
            scenario_summary["delta"] = {
                "graph_minus_text": {
                    "validation_coverage": _delta(
                        scenario_summary["modes"]["graph"].get("validation_coverage"),
                        scenario_summary["modes"]["text"].get("validation_coverage"),
                    ),
                    "dependency_coverage": _delta(
                        scenario_summary["modes"]["graph"].get("dependency_coverage"),
                        scenario_summary["modes"]["text"].get("dependency_coverage"),
                    ),
                    "hallucinated_count": _delta(
                        scenario_summary["modes"]["graph"].get("hallucinated_count"),
                        scenario_summary["modes"]["text"].get("hallucinated_count"),
                    ),
                    "graph_integrity_score": _delta(
                        scenario_summary["modes"]["graph"].get("graph_integrity_score"),
                        scenario_summary["modes"]["text"].get("graph_integrity_score"),
                    ),
                }
            }
        if "graph" in scenario_summary["modes"] and "structured" in scenario_summary["modes"]:
            scenario_summary.setdefault("delta", {})["graph_minus_structured"] = {
                "validation_coverage": _delta(
                    scenario_summary["modes"]["graph"].get("validation_coverage"),
                    scenario_summary["modes"]["structured"].get("validation_coverage"),
                ),
                "dependency_coverage": _delta(
                    scenario_summary["modes"]["graph"].get("dependency_coverage"),
                    scenario_summary["modes"]["structured"].get("dependency_coverage"),
                ),
                "hallucinated_count": _delta(
                    scenario_summary["modes"]["graph"].get("hallucinated_count"),
                    scenario_summary["modes"]["structured"].get("hallucinated_count"),
                ),
                "graph_integrity_score": _delta(
                    scenario_summary["modes"]["graph"].get("graph_integrity_score"),
                    scenario_summary["modes"]["structured"].get("graph_integrity_score"),
                ),
            }
        summary["scenarios"][scenario] = scenario_summary

    summary["comparison"] = {
        "graph_vs_text": {
            "validation_coverage": _comparison_delta(summary, "graph", "text", "validation_coverage"),
            "dependency_coverage": _comparison_delta(summary, "graph", "text", "dependency_coverage"),
            "hallucinated_count": _comparison_delta(summary, "graph", "text", "hallucinated_count"),
            "graph_integrity_score": _comparison_delta(summary, "graph", "text", "graph_integrity_score"),
            "graph_repair_cost": _comparison_delta(summary, "graph", "text", "graph_repair_cost"),
        },
        "graph_vs_structured": {
            "validation_coverage": _comparison_delta(summary, "graph", "structured", "validation_coverage"),
            "dependency_coverage": _comparison_delta(summary, "graph", "structured", "dependency_coverage"),
            "hallucinated_count": _comparison_delta(summary, "graph", "structured", "hallucinated_count"),
            "graph_integrity_score": _comparison_delta(summary, "graph", "structured", "graph_integrity_score"),
            "graph_repair_cost": _comparison_delta(summary, "graph", "structured", "graph_repair_cost"),
        },
    }
    return summary


def _delta(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return round(float(left) - float(right), 6)


def _comparison_delta(summary: Dict[str, Any], left_mode: str, right_mode: str, key: str) -> float | None:
    left = (summary.get("modes") or {}).get(left_mode, {}).get(key)
    right = (summary.get("modes") or {}).get(right_mode, {}).get(key)
    return _delta(left, right)


def render_graph_recovery_summary_markdown(summary: Dict[str, Any]) -> str:
    lines = ["# Graph Recovery Evaluation", ""]
    lines.extend(
        [
            "| Mode | Records | Validation Passed | Validation Coverage | Dependency Coverage | Dependency Precision | Dependency F1 | Object Survival Rate | Dependency Recall | Hallucinated Count | Graph Integrity Score | Graph Repair Cost |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for mode, mode_summary in sorted((summary.get("modes") or {}).items()):
        lines.append(
            "| "
            + " | ".join(
                [
                    str(mode),
                    _fmt(mode_summary.get("records")),
                    _fmt(mode_summary.get("validation_passed")),
                    _fmt(mode_summary.get("validation_coverage")),
                    _fmt(mode_summary.get("dependency_coverage")),
                    _fmt(mode_summary.get("dependency_precision")),
                    _fmt(mode_summary.get("dependency_f1")),
                    _fmt(mode_summary.get("object_survival_rate")),
                    _fmt(mode_summary.get("dependency_recall")),
                    _fmt(mode_summary.get("hallucinated_count")),
                    _fmt(mode_summary.get("graph_integrity_score")),
                    _fmt(mode_summary.get("graph_repair_cost")),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Scenario Summary", ""])
    lines.extend(
        [
            "| Scenario | Records | Graph Validation Coverage | Graph Dependency Coverage | Graph Hallucinated Count | Graph Integrity Score | Graph Repair Cost |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for scenario, scenario_summary in sorted((summary.get("scenarios") or {}).items()):
        graph_mode = (scenario_summary.get("modes") or {}).get("graph") or {}
        lines.append(
            "| "
            + " | ".join(
                [
                    str(scenario),
                    _fmt(scenario_summary.get("records")),
                    _fmt(graph_mode.get("validation_coverage")),
                    _fmt(graph_mode.get("dependency_coverage")),
                    _fmt(graph_mode.get("hallucinated_count")),
                    _fmt(graph_mode.get("graph_integrity_score")),
                    _fmt(graph_mode.get("graph_repair_cost")),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Comparison Deltas", ""])
    lines.extend(
        [
            "| Comparison | Validation Coverage | Dependency Coverage | Hallucinated Count | Graph Integrity Score | Graph Repair Cost |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for comparison_name, comparison_summary in sorted((summary.get("comparison") or {}).items()):
        lines.append(
            "| "
            + " | ".join(
                [
                    str(comparison_name),
                    _fmt(comparison_summary.get("validation_coverage")),
                    _fmt(comparison_summary.get("dependency_coverage")),
                    _fmt(comparison_summary.get("hallucinated_count")),
                    _fmt(comparison_summary.get("graph_integrity_score")),
                    _fmt(comparison_summary.get("graph_repair_cost")),
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def _fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}".rstrip("0").rstrip(".")
    return str(value)


def write_graph_recovery_outputs(
    records: Sequence[Dict[str, Any]],
    output_dir: str | Path,
) -> Dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_path / "graph_recovery_ablation_records.jsonl"
    csv_path = output_path / "graph_recovery_ablation_records.csv"
    markdown_path = output_path / "graph_recovery_ablation_audit.md"
    summary_path = output_path / "graph_recovery_ablation_summary.md"
    json_path = output_path / "graph_recovery_ablation.json"

    with jsonl_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    summary = summarize_graph_recovery_evaluation(records)
    write_records_csv(records, csv_path)
    write_records_markdown(records, markdown_path)
    summary_path.write_text(render_graph_recovery_summary_markdown(summary), encoding="utf-8")
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return {
        "jsonl": jsonl_path,
        "csv": csv_path,
        "markdown": markdown_path,
        "summary": summary_path,
        "json": json_path,
    }
