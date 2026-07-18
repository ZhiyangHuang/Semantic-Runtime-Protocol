from __future__ import annotations

import json
import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence

from .srp.export import write_records_csv, write_records_markdown
from .srp.pipeline import run_srp


@dataclass(frozen=True)
class PolicyBoundaryTask:
    name: str
    task: Dict[str, Any]
    semantic_unit_count: int


@dataclass(frozen=True)
class PolicyBoundarySweep:
    benchmark: str
    budget: int
    seed: int
    task: Dict[str, Any]
    semantic_unit_count: int


@contextmanager
def _temporary_env(overrides: Dict[str, str]):
    previous: Dict[str, str | None] = {}
    try:
        for key, value in overrides.items():
            previous[key] = os.environ.get(key)
            os.environ[key] = str(value)
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _dependency_object(dependency_id: str, subject_value: str, relation_value: str, object_value: str) -> Dict[str, Any]:
    return {
        "dependency_id": dependency_id,
        "subject": {
            "type": "entity",
            "canonical": subject_value,
        },
        "relation": {
            "type": "relation",
            "canonical": relation_value,
        },
        "object": {
            "type": "entity",
            "canonical": object_value,
        },
    }


def _validation_dependency_object(dependency_id: str, surface: str) -> Dict[str, Any]:
    return {
        "dependency_id": dependency_id,
        "concept": "fact",
        "normalized_value": surface,
        "surface": surface,
    }


def _pressure_task() -> PolicyBoundaryTask:
    critical_clauses = [
        ("Aster", "keeps", "reactor alpha stable"),
        ("Boreal", "keeps", "coolant beta stable"),
        ("Cinder", "keeps", "sensor gamma aligned"),
        ("Dune", "keeps", "access delta sealed"),
        ("Ember", "keeps", "power epsilon routed"),
        ("Fjord", "keeps", "backup zeta primed"),
    ]
    decoy_clauses = [
        ("Gale", "keeps", "alarms eta routed"),
        ("Harbor", "keeps", "logbook theta sealed"),
        ("Ion", "keeps", "tokens iota rotated"),
        ("Jade", "keeps", "maintenance kappa closed"),
        ("Kite", "keeps", "shuttle lambda scheduled"),
        ("Lumen", "keeps", "gate mu sealed"),
        ("Mosaic", "keeps", "reports nu archived"),
        ("Nexus", "keeps", "override xi blocked"),
        ("Orbit", "keeps", "telemetry omicron stable"),
        ("Pulse", "keeps", "fallback pi ready"),
        ("Quill", "keeps", "auxiliary rails rho aligned"),
        ("Ridge", "keeps", "secondary valves sigma closed"),
        ("Sol", "keeps", "sideband tau quiet"),
        ("Tundra", "keeps", "buffer upsilon primed"),
        ("Umber", "keeps", "shadow links phi dormant"),
        ("Vega", "keeps", "spare relays chi ready"),
        ("Wisp", "keeps", "satellite nodes psi parked"),
        ("Xeno", "keeps", "fallback channels omega sealed"),
        ("Yarrow", "keeps", "auxiliary mesh eta calm"),
        ("Zephyr", "keeps", "backup trace lambda silent"),
    ]
    clauses = critical_clauses + decoy_clauses
    memory = ". ".join(f"{subject} {relation} {obj}" for subject, relation, obj in clauses) + "."
    constraints = [f"{subject} {relation} {obj}." for subject, relation, obj in critical_clauses]
    dependency_objects = [
        _dependency_object(f"dep-{index}", subject, relation, obj)
        for index, (subject, relation, obj) in enumerate(clauses, start=1)
    ]
    expected_keywords = [
        "aster",
        "boreal",
        "cinder",
        "dune",
        "ember",
        "fjord",
        "gale",
        "harbor",
        "ion",
        "jade",
        "kite",
        "lumen",
        "mosaic",
        "nexus",
        "orbit",
        "pulse",
        "quill",
        "ridge",
        "sol",
        "tundra",
        "umber",
        "vega",
        "wisp",
        "xeno",
        "yarrow",
        "zephyr",
        "reactor",
        "coolant",
        "sensor",
        "access",
        "power",
        "backup",
        "alarms",
        "logbook",
        "tokens",
        "maintenance",
        "shuttle",
        "gate",
        "reports",
        "override",
        "telemetry",
        "fallback",
    ]
    important_objects = [
        {
            "object_id": f"boundary:{index}",
            "type": "constraint",
            "value": f"{subject} {relation} {obj}.",
            "confidence": 1.0,
            "evidence_pointer": f"memory:{index}",
        }
        for index, (subject, relation, obj) in enumerate(clauses, start=1)
    ]
    task = {
        "id": "policy-boundary-memory-saturation",
        "task_type": "policy_boundary_analysis",
        "source": "SRP Policy Boundary Analysis",
        "initial_state": {
            "constraints": constraints,
            "memory": memory,
        },
        "queries": [
            "Preserve the full reactor map and keep the module assignments stable.",
        ],
        "query_expectations": [[[constraint] for constraint in constraints]],
        "expected_keywords": expected_keywords,
        "semantic_dependencies": {
            "required_dependency_objects": dependency_objects,
        },
        "metadata": {
            "benchmark": "SRP Policy Boundary Analysis",
            "scenario": "memory_saturation",
            "pressure_mode": "memory_saturation",
            "semantic_unit_count": len(constraints) + len(clauses) + len(expected_keywords),
            "required_dependency_labels": constraints,
            "required_dependency_objects": dependency_objects,
            "important_objects": important_objects,
        },
    }
    return PolicyBoundaryTask(
        name="memory_saturation",
        task=task,
        semantic_unit_count=int(task["metadata"]["semantic_unit_count"]),
    )


def _validation_pressure_task() -> PolicyBoundaryTask:
    bridge_facts = [
        "Bridge alpha keeps the blue key aligned with the archive gate.",
        "Archive gate stays open only after bridge alpha is confirmed.",
        "Bridge beta keeps the red key aligned with the transit rail.",
        "Transit rail stays open only after bridge beta is confirmed.",
        "Bridge gamma keeps the green key aligned with the relay shelf.",
        "Relay shelf stays open only after bridge gamma is confirmed.",
        "Bridge delta keeps the orange key aligned with the access lock.",
        "Access lock stays open only after bridge delta is confirmed.",
    ]
    decoy_facts = [
        "Harbor keeps the logbook quiet.",
        "Ion keeps the telemetry stable.",
        "Jade keeps the maintenance buffer closed.",
        "Kite keeps the shuttle schedule clean.",
        "Lumen keeps the fallback lane silent.",
        "Mosaic keeps the report stack archived.",
        "Nexus keeps the override channel blocked.",
        "Orbit keeps the telemetry channel aligned.",
        "Pulse keeps the backup mirror ready.",
        "Quill keeps the sidecar notes concise.",
        "Ridge keeps the auxiliary valves closed.",
        "Sol keeps the sideband quiet.",
        "Tundra keeps the buffer primed.",
        "Umber keeps the shadow links dormant.",
        "Vega keeps the spare relays ready.",
        "Wisp keeps the satellite nodes parked.",
        "Xeno keeps the trace channels sealed.",
        "Yarrow keeps the auxiliary mesh calm.",
        "Zephyr keeps the backup trace silent.",
        "Atlas keeps the calibration deck clean.",
    ]
    clauses = bridge_facts + decoy_facts
    memory = ". ".join(clauses) + "."
    constraints = [
        "Bridge alpha keeps the blue key aligned with the archive gate.",
        "Bridge beta keeps the red key aligned with the transit rail.",
    ]
    dependency_objects = [
        _validation_dependency_object(f"dep-{index}", surface)
        for index, surface in enumerate(bridge_facts, start=1)
    ]
    expected_keywords = [
        "bridge",
        "alpha",
        "beta",
        "gamma",
        "delta",
        "blue",
        "red",
        "green",
        "orange",
        "archive",
        "transit",
        "relay",
        "lock",
        "confirmed",
    ]
    important_objects = [
        {
            "object_id": "bridge-alpha",
            "type": "fact",
            "value": bridge_facts[0],
            "confidence": 1.0,
            "evidence_pointer": "memory:1",
        },
        {
            "object_id": "bridge-beta",
            "type": "fact",
            "value": bridge_facts[2],
            "confidence": 1.0,
            "evidence_pointer": "memory:3",
        },
    ]
    task = {
        "id": "policy-boundary-validation-pressure",
        "task_type": "policy_boundary_analysis",
        "source": "SRP Policy Boundary Analysis",
        "initial_state": {
            "constraints": constraints,
            "memory": memory,
        },
        "queries": [
            "Preserve the bridge dependencies that keep the archive, transit, relay, and access paths valid.",
        ],
        "query_expectations": [[[fact] for fact in bridge_facts]],
        "expected_keywords": expected_keywords,
        "semantic_dependencies": {
            "required_dependency_objects": dependency_objects,
        },
        "metadata": {
            "benchmark": "SRP Policy Boundary Analysis",
            "scenario": "validation_pressure",
            "pressure_mode": "validation_pressure",
            "semantic_unit_count": len(constraints) + len(clauses) + len(expected_keywords),
            "required_dependency_labels": bridge_facts,
            "required_dependency_objects": dependency_objects,
            "important_objects": important_objects,
        },
    }
    return PolicyBoundaryTask(
        name="validation_pressure",
        task=task,
        semantic_unit_count=int(task["metadata"]["semantic_unit_count"]),
    )


def _dependency_f1_pressure_task() -> PolicyBoundaryTask:
    bridge_facts = [
        "Bridge alpha keeps the blue key aligned with the archive gate.",
        "Bridge beta keeps the red key aligned with the transit rail.",
        "Bridge gamma keeps the green key aligned with the relay shelf.",
        "Bridge delta keeps the orange key aligned with the access lock.",
        "Bridge epsilon keeps the silver key aligned with the signal vault.",
        "Bridge zeta keeps the amber key aligned with the vault latch.",
        "Bridge eta keeps the violet key aligned with the control hinge.",
        "Bridge theta keeps the white key aligned with the timing lock.",
    ]
    near_duplicate_decoys = [
        "Bridge alpha keeps the archive key aligned with the blue gate.",
        "Bridge beta keeps the transit key aligned with the red rail.",
        "Bridge gamma keeps the relay key aligned with the green shelf.",
        "Bridge delta keeps the access key aligned with the orange lock.",
        "Bridge epsilon keeps the signal key aligned with the silver vault.",
        "Bridge zeta keeps the vault key aligned with the amber latch.",
        "Bridge eta keeps the control key aligned with the violet hinge.",
        "Bridge theta keeps the timing key aligned with the white lock.",
    ]
    decoy_facts = [
        "Harbor keeps the logbook quiet.",
        "Ion keeps the telemetry stable.",
        "Jade keeps the maintenance buffer closed.",
        "Kite keeps the shuttle schedule clean.",
        "Lumen keeps the fallback lane silent.",
        "Mosaic keeps the report stack archived.",
        "Nexus keeps the override channel blocked.",
        "Orbit keeps the telemetry channel aligned.",
        "Pulse keeps the backup mirror ready.",
        "Quill keeps the sidecar notes concise.",
        "Ridge keeps the auxiliary valves closed.",
        "Sol keeps the sideband quiet.",
        "Tundra keeps the buffer primed.",
        "Umber keeps the shadow links dormant.",
        "Vega keeps the spare relays ready.",
        "Wisp keeps the satellite nodes parked.",
    ]
    clauses = bridge_facts + near_duplicate_decoys + decoy_facts
    memory = ". ".join(clauses) + "."
    constraints = [
        "Bridge alpha keeps the blue key aligned with the archive gate.",
        "Bridge beta keeps the red key aligned with the transit rail.",
        "Bridge gamma keeps the green key aligned with the relay shelf.",
        "Bridge delta keeps the orange key aligned with the access lock.",
        "Bridge epsilon keeps the silver key aligned with the signal vault.",
        "Bridge zeta keeps the amber key aligned with the vault latch.",
        "Bridge eta keeps the violet key aligned with the control hinge.",
        "Bridge theta keeps the white key aligned with the timing lock.",
    ]
    dependency_objects = [
        _validation_dependency_object(f"dep-{index}", surface)
        for index, surface in enumerate(bridge_facts, start=1)
    ]
    expected_keywords = [
        "bridge",
        "alpha",
        "beta",
        "gamma",
        "delta",
        "blue",
        "red",
        "green",
        "orange",
        "archive",
        "transit",
        "relay",
        "lock",
        "confirmed",
        "silver",
        "amber",
        "violet",
        "white",
        "vault",
        "hinge",
        "signal",
        "timing",
    ]
    important_confidences = [1.0, 0.95, 0.92, 0.88, 0.83, 0.78, 0.73, 0.68]
    important_objects = [
        {
            "object_id": f"bridge:{index}",
            "type": "fact",
            "value": surface,
            "confidence": important_confidences[index - 1],
            "evidence_pointer": f"memory:{index}",
        }
        for index, surface in enumerate(bridge_facts, start=1)
    ]
    important_objects.extend(
        [
            {
                "object_id": f"bridge:decoy:{index}",
                "type": "fact",
                "value": surface,
                "confidence": confidence,
                "evidence_pointer": f"memory:{index + len(bridge_facts)}",
            }
            for index, (surface, confidence) in enumerate(
                zip(near_duplicate_decoys, [0.66, 0.62, 0.58, 0.54, 0.5, 0.46, 0.42, 0.38]),
                start=1,
            )
        ]
    )
    task = {
        "id": "policy-boundary-dependency-f1-pressure",
        "task_type": "policy_boundary_analysis",
        "source": "SRP Policy Boundary Analysis",
        "initial_state": {
            "constraints": constraints,
            "memory": memory,
        },
        "queries": [
            "Preserve the bridge dependencies that keep the archive, transit, relay, and access paths valid.",
        ],
        "query_expectations": [[[fact] for fact in bridge_facts]],
        "expected_keywords": expected_keywords,
        "semantic_dependencies": {
            "required_dependency_objects": dependency_objects,
        },
        "metadata": {
            "benchmark": "SRP Policy Boundary Analysis",
            "scenario": "dependency_f1_pressure",
            "pressure_mode": "dependency_f1_pressure",
            "semantic_unit_count": len(constraints) + len(clauses) + len(expected_keywords),
            "required_dependency_labels": bridge_facts,
            "required_dependency_objects": dependency_objects,
            "important_objects": important_objects,
        },
    }
    return PolicyBoundaryTask(
        name="dependency_f1_pressure",
        task=task,
        semantic_unit_count=int(task["metadata"]["semantic_unit_count"]),
    )


def build_policy_boundary_tasks() -> List[PolicyBoundaryTask]:
    return [_pressure_task(), _validation_pressure_task(), _dependency_f1_pressure_task()]


def _mean(values: Sequence[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _metric_value(record: Dict[str, Any], key: str) -> float | None:
    value = record.get(key)
    if value is None:
        value = (record.get("experiment_result") or {}).get("metrics", {}).get(key)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _allocation_metric_value(record: Dict[str, Any], key: str) -> float | None:
    value = ((record.get("state_allocation_result") or {}).get("metrics") or {}).get(key)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _boundary_metric_names() -> List[str]:
    return [
        "active_retention_ratio",
        "active_state_efficiency",
        "active_object_count",
        "validation_coverage",
        "dependency_coverage",
        "dependency_f1",
        "validation_score",
        "graph_integrity_score",
        "object_retention",
        "weighted_object_retention",
    ]


def _derive_boundary_from_rows(
    rows: Sequence[Dict[str, Any]],
    threshold: float = 0.05,
    metric_names: Sequence[str] | None = None,
    mode: str = "baseline",
) -> Dict[str, Any]:
    sorted_rows = sorted(rows, key=lambda row: float(row["budget"]), reverse=True)
    if not sorted_rows:
        return {
            "transition_detected": False,
            "dominant_metric": None,
            "boundary_upper_budget": None,
            "boundary_lower_budget": None,
            "boundary_pressure_index_upper": None,
            "boundary_pressure_index_lower": None,
            "threshold": threshold,
        }

    baseline = sorted_rows[0]
    metric_boundaries: Dict[str, Dict[str, Any]] = {}
    selected_metric_names = list(metric_names) if metric_names is not None else _boundary_metric_names()

    for metric_name in selected_metric_names:
        baseline_value = baseline["metrics"].get(metric_name)
        if baseline_value is None:
            continue
        if mode == "adjacent":
            previous_row = baseline
            previous_value = baseline_value
            for row in sorted_rows[1:]:
                current_value = row["metrics"].get(metric_name)
                if current_value is None:
                    continue
                drop = float(previous_value) - float(current_value)
                if drop >= threshold:
                    metric_boundaries[metric_name] = {
                        "boundary_upper_budget": int(previous_row["budget"]),
                        "boundary_lower_budget": int(row["budget"]),
                        "drop": round(drop, 6),
                    }
                    break
                previous_row = row
                previous_value = current_value
        else:
            previous_row = baseline
            for row in sorted_rows[1:]:
                current_value = row["metrics"].get(metric_name)
                if current_value is None:
                    continue
                drop = float(baseline_value) - float(current_value)
                if drop >= threshold:
                    metric_boundaries[metric_name] = {
                        "boundary_upper_budget": int(previous_row["budget"]),
                        "boundary_lower_budget": int(row["budget"]),
                        "drop": round(drop, 6),
                    }
                    break
                previous_row = row

    dominant_metric = None
    dominant_drop = 0.0
    for metric_name in selected_metric_names:
        boundary_info = metric_boundaries.get(metric_name)
        if boundary_info is None:
            continue
        dominant_metric = metric_name
        dominant_drop = float(boundary_info.get("drop") or 0.0)
        break

    if dominant_metric is None:
        for metric_name in selected_metric_names:
            baseline_value = baseline["metrics"].get(metric_name)
            if baseline_value is None:
                continue
            for row in sorted_rows[1:]:
                current_value = row["metrics"].get(metric_name)
                if current_value is None:
                    continue
                drop = float(baseline_value) - float(current_value)
                if drop > dominant_drop:
                    dominant_drop = drop
                    dominant_metric = metric_name
        if dominant_metric is None:
            dominant_metric = "validation_coverage"

    boundary_upper_budget = None
    boundary_lower_budget = None
    if dominant_metric in metric_boundaries:
        boundary_upper_budget = metric_boundaries[dominant_metric]["boundary_upper_budget"]
        boundary_lower_budget = metric_boundaries[dominant_metric]["boundary_lower_budget"]

    transition_detected = boundary_upper_budget is not None and boundary_lower_budget is not None
    return {
        "transition_detected": transition_detected,
        "dominant_metric": dominant_metric,
        "dominant_drop": round(dominant_drop, 6),
        "boundary_upper_budget": boundary_upper_budget,
        "boundary_lower_budget": boundary_lower_budget,
        "boundary_pressure_index_upper": None if boundary_upper_budget is None else round(float(baseline["semantic_unit_count"]) / float(boundary_upper_budget), 6),
        "boundary_pressure_index_lower": None if boundary_lower_budget is None else round(float(baseline["semantic_unit_count"]) / float(boundary_lower_budget), 6),
        "baseline_budget": int(baseline["budget"]),
        "baseline_pressure_index": round(float(baseline["semantic_unit_count"]) / float(baseline["budget"]), 6) if baseline.get("budget") else None,
        "threshold": threshold,
        "mode": mode,
    }


def run_policy_boundary_analysis(
    *,
    budgets: Sequence[int] | None = None,
    seeds: Sequence[int] | None = None,
    tasks: Sequence[PolicyBoundaryTask] | None = None,
    cycles: int = 1,
) -> List[Dict[str, Any]]:
    selected_tasks = list(tasks) if tasks is not None else build_policy_boundary_tasks()
    selected_budgets = [int(value) for value in (budgets if budgets is not None else [4, 8, 12, 16, 24, 32])]
    selected_seeds = [int(value) for value in (seeds if seeds is not None else [0, 1, 2, 3, 4])]
    records: List[Dict[str, Any]] = []

    for task_spec in selected_tasks:
        for budget in selected_budgets:
            for seed in selected_seeds:
                overrides = {
                    "SRP_STATE_ALLOCATION_POLICY": "random",
                    "SRP_EXECUTION_STATE_SOURCE": "active",
                    "SRP_ACTIVE_BUDGET": str(budget),
                    "SRP_RANDOM_ALLOCATION_SEED": str(seed),
                }
                with _temporary_env(overrides):
                    task_records = run_srp(task_spec.task, cycles=cycles, client=None)
                for record in task_records:
                    record["policy_boundary"] = {
                        "benchmark": task_spec.name,
                        "budget": budget,
                        "seed": seed,
                        "cycles": cycles,
                        "execution_state_source": "active",
                        "state_allocation_policy": "random",
                        "semantic_unit_count": task_spec.semantic_unit_count,
                        "semantic_pressure_index": round(task_spec.semantic_unit_count / float(budget), 6) if budget else None,
                    }
                    record["policy_boundary_suite"] = task_spec.name
                    record["policy_boundary_budget"] = budget
                    record["policy_boundary_seed"] = seed
                    record["policy_boundary_pressure_index"] = (
                        round(task_spec.semantic_unit_count / float(budget), 6) if budget else None
                    )
                    records.append(record)
    return records


def summarize_policy_boundary_records(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "records": len(records),
        "benchmarks": {},
    }
    benchmark_names = sorted({str(record.get("policy_boundary_suite") or "unknown") for record in records})
    for benchmark_name in benchmark_names:
        benchmark_records = [record for record in records if str(record.get("policy_boundary_suite") or "unknown") == benchmark_name]
        if not benchmark_records:
            continue
        pressure_indices = [record.get("policy_boundary_pressure_index") for record in benchmark_records if record.get("policy_boundary_pressure_index") is not None]
        semantic_unit_count = next(
            (int((record.get("policy_boundary") or {}).get("semantic_unit_count")) for record in benchmark_records if (record.get("policy_boundary") or {}).get("semantic_unit_count") is not None),
            None,
        )
        by_budget: Dict[int, List[Dict[str, Any]]] = {}
        for record in benchmark_records:
            budget = int(record.get("policy_boundary_budget") or 0)
            by_budget.setdefault(budget, []).append(record)

        budget_rows: List[Dict[str, Any]] = []
        for budget in sorted(by_budget):
            budget_records = by_budget[budget]
            allocation_metrics = {
                "active_object_count": _mean([value for value in (_allocation_metric_value(record, "active_object_count") for record in budget_records) if value is not None]),
                "active_state_efficiency": _mean([value for value in (_allocation_metric_value(record, "active_state_efficiency") for record in budget_records) if value is not None]),
                "active_retention_ratio": _mean([value for value in (_allocation_metric_value(record, "active_retention_ratio") for record in budget_records) if value is not None]),
                "latent_preservation": _mean([value for value in (_allocation_metric_value(record, "latent_preservation") for record in budget_records) if value is not None]),
                "hallucination_isolation": _mean([value for value in (_allocation_metric_value(record, "hallucination_isolation") for record in budget_records) if value is not None]),
            }
            metrics = {
                "validation_coverage": _mean([value for value in (_metric_value(record, "validation_coverage") for record in budget_records) if value is not None]),
                "dependency_coverage": _mean([value for value in (_metric_value(record, "dependency_coverage") for record in budget_records) if value is not None]),
                "dependency_precision": _mean([value for value in (_metric_value(record, "dependency_precision") for record in budget_records) if value is not None]),
                "dependency_f1": _mean([value for value in (_metric_value(record, "dependency_f1") for record in budget_records) if value is not None]),
                "validation_score": _mean([value for value in (_metric_value(record, "validation_score") for record in budget_records) if value is not None]),
                "graph_integrity_score": _mean([value for value in (_metric_value(record, "graph_integrity_score") for record in budget_records) if value is not None]),
                "object_retention": _mean([value for value in (_metric_value(record, "object_retention") for record in budget_records) if value is not None]),
                "weighted_object_retention": _mean([value for value in (_metric_value(record, "weighted_object_retention") for record in budget_records) if value is not None]),
                "token_overhead": _mean([value for value in (_metric_value(record, "token_overhead") for record in budget_records) if value is not None]),
                "budget_pressure": _mean([value for value in (_metric_value(record, "budget_pressure") for record in budget_records) if value is not None]),
            }
            metrics.update(allocation_metrics)
            row = {
                "budget": budget,
                "records": len(budget_records),
                "semantic_unit_count": semantic_unit_count,
                "semantic_pressure_index": _mean([float((record.get("policy_boundary") or {}).get("semantic_pressure_index")) for record in budget_records if (record.get("policy_boundary") or {}).get("semantic_pressure_index") is not None]),
                "allocation_metrics": allocation_metrics,
                "metrics": metrics,
            }
            budget_rows.append(row)

        for row in budget_rows:
            metrics = row["metrics"]
            row["deltas"] = {
                "validation_coverage": None,
                "graph_integrity_score": None,
                "object_retention": None,
                "weighted_object_retention": None,
            }
        baseline_metrics = budget_rows[-1]["metrics"] if budget_rows else {}
        for row in budget_rows:
            metrics = row["metrics"]
            row["deltas"] = {
                "validation_coverage": _delta(metrics.get("validation_coverage"), baseline_metrics.get("validation_coverage")),
                "dependency_coverage": _delta(metrics.get("dependency_coverage"), baseline_metrics.get("dependency_coverage")),
                "graph_integrity_score": _delta(metrics.get("graph_integrity_score"), baseline_metrics.get("graph_integrity_score")),
                "object_retention": _delta(metrics.get("object_retention"), baseline_metrics.get("object_retention")),
                "weighted_object_retention": _delta(metrics.get("weighted_object_retention"), baseline_metrics.get("weighted_object_retention")),
            }

        allocation_boundary = _derive_boundary_from_rows(
            budget_rows,
            metric_names=["active_retention_ratio", "active_state_efficiency", "active_object_count", "latent_preservation", "hallucination_isolation"],
        )
        dependency_boundary = _derive_boundary_from_rows(
            budget_rows,
            metric_names=["dependency_coverage", "dependency_precision", "dependency_f1"],
        )
        dependency_f1_boundary = _derive_boundary_from_rows(
            budget_rows,
            metric_names=["dependency_f1"],
            mode="adjacent",
        )
        validation_boundary = _derive_boundary_from_rows(
            budget_rows,
            metric_names=[
                "validation_score",
                "validation_coverage",
                "graph_integrity_score",
                "object_retention",
                "weighted_object_retention",
            ],
        )
        boundary_gap = {
            "allocation_to_dependency": _boundary_gap(allocation_boundary, dependency_boundary),
            "dependency_to_dependency_f1": _boundary_gap(dependency_boundary, dependency_f1_boundary),
            "dependency_f1_to_validation": _boundary_gap(dependency_f1_boundary, validation_boundary),
            "allocation_to_validation": _boundary_gap(allocation_boundary, validation_boundary),
        }
        summary["benchmarks"][benchmark_name] = {
            "records": len(benchmark_records),
            "semantic_unit_count": semantic_unit_count,
            "semantic_pressure_index_mean": _mean([float(value) for value in pressure_indices if value is not None]) if pressure_indices else None,
            "budgets": budget_rows,
            "allocation_boundary": allocation_boundary,
            "dependency_boundary": dependency_boundary,
            "dependency_f1_boundary": dependency_f1_boundary,
            "validation_boundary": validation_boundary,
            "boundary_gap": boundary_gap,
            "boundary": allocation_boundary,
            "baseline_budget": allocation_boundary.get("baseline_budget"),
        }
    return summary


def _delta(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return left - right


def _boundary_midpoint(boundary: Dict[str, Any] | None) -> float | None:
    if not boundary:
        return None
    upper = boundary.get("boundary_upper_budget")
    lower = boundary.get("boundary_lower_budget")
    if upper is None or lower is None:
        return None
    return (float(upper) + float(lower)) / 2.0


def _boundary_gap(left_boundary: Dict[str, Any] | None, right_boundary: Dict[str, Any] | None) -> Dict[str, Any]:
    left_midpoint = _boundary_midpoint(left_boundary)
    right_midpoint = _boundary_midpoint(right_boundary)
    left_pressure = None
    right_pressure = None
    if left_boundary:
        left_pressure = left_boundary.get("boundary_pressure_index_lower") or left_boundary.get("boundary_pressure_index_upper")
    if right_boundary:
        right_pressure = right_boundary.get("boundary_pressure_index_lower") or right_boundary.get("boundary_pressure_index_upper")
    return {
        "left_midpoint_budget": left_midpoint,
        "right_midpoint_budget": right_midpoint,
        "budget_gap": None if left_midpoint is None or right_midpoint is None else round(float(right_midpoint) - float(left_midpoint), 6),
        "left_pressure_index": left_pressure,
        "right_pressure_index": right_pressure,
        "pressure_gap": None if left_pressure is None or right_pressure is None else round(float(right_pressure) - float(left_pressure), 6),
    }


def render_policy_boundary_markdown(summary: Dict[str, Any]) -> str:
    lines = ["# Policy Boundary Analysis", ""]
    lines.append(f"- `records`: {summary.get('records')}")
    lines.append("")
    for benchmark_name, benchmark_summary in sorted((summary.get("benchmarks") or {}).items()):
        allocation_boundary = benchmark_summary.get("allocation_boundary") or {}
        dependency_boundary = benchmark_summary.get("dependency_boundary") or {}
        dependency_f1_boundary = benchmark_summary.get("dependency_f1_boundary") or {}
        validation_boundary = benchmark_summary.get("validation_boundary") or {}
        boundary_gap = benchmark_summary.get("boundary_gap") or {}
        lines.append(f"## {benchmark_name}")
        lines.append(f"- `semantic_unit_count`: {benchmark_summary.get('semantic_unit_count')}")
        lines.append(f"- `baseline_budget`: {benchmark_summary.get('baseline_budget')}")
        lines.append(f"- `allocation_dominant_metric`: {allocation_boundary.get('dominant_metric')}")
        lines.append(f"- `allocation_transition_detected`: {allocation_boundary.get('transition_detected')}")
        lines.append(f"- `allocation_boundary_upper_budget`: {allocation_boundary.get('boundary_upper_budget')}")
        lines.append(f"- `allocation_boundary_lower_budget`: {allocation_boundary.get('boundary_lower_budget')}")
        lines.append(f"- `allocation_boundary_pressure_index_upper`: {allocation_boundary.get('boundary_pressure_index_upper')}")
        lines.append(f"- `allocation_boundary_pressure_index_lower`: {allocation_boundary.get('boundary_pressure_index_lower')}")
        lines.append(f"- `dependency_transition_detected`: {dependency_boundary.get('transition_detected')}")
        lines.append(f"- `dependency_dominant_metric`: {dependency_boundary.get('dominant_metric')}")
        lines.append(f"- `dependency_boundary_upper_budget`: {dependency_boundary.get('boundary_upper_budget')}")
        lines.append(f"- `dependency_boundary_lower_budget`: {dependency_boundary.get('boundary_lower_budget')}")
        lines.append(f"- `dependency_f1_transition_detected`: {dependency_f1_boundary.get('transition_detected')}")
        lines.append(f"- `dependency_f1_boundary_upper_budget`: {dependency_f1_boundary.get('boundary_upper_budget')}")
        lines.append(f"- `dependency_f1_boundary_lower_budget`: {dependency_f1_boundary.get('boundary_lower_budget')}")
        lines.append(f"- `validation_transition_detected`: {validation_boundary.get('transition_detected')}")
        lines.append(f"- `validation_dominant_metric`: {validation_boundary.get('dominant_metric')}")
        lines.append(f"- `validation_boundary_upper_budget`: {validation_boundary.get('boundary_upper_budget')}")
        lines.append(f"- `validation_boundary_lower_budget`: {validation_boundary.get('boundary_lower_budget')}")
        if boundary_gap:
            lines.append("- `boundary_gap`:")
            for gap_name in [
                "allocation_to_dependency",
                "dependency_to_dependency_f1",
                "dependency_f1_to_validation",
                "allocation_to_validation",
            ]:
                gap = boundary_gap.get(gap_name) or {}
                lines.append(f"  - `{gap_name}_budget_gap`: {gap.get('budget_gap')}")
                lines.append(f"  - `{gap_name}_pressure_gap`: {gap.get('pressure_gap')}")
        lines.append("")
        lines.append(
            "| Budget | Pressure Index | Active Count | Active Retention | Active Efficiency | Validation Coverage | Dependency Coverage | Dependency F1 | Validation Score | Graph Integrity | Object Retention | Weighted Retention | Delta Coverage | Delta Dependency | Delta Integrity | Delta Retention |"
        )
        lines.append(
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"
        )
        for row in benchmark_summary.get("budgets") or []:
            metrics = row.get("metrics") or {}
            allocation_metrics = row.get("allocation_metrics") or {}
            deltas = row.get("deltas") or {}
            dependency_audit = row.get("dependency_audit") or {}
            lines.append(
                "| "
                + " | ".join(
                    [
                        _fmt(row.get("budget")),
                        _fmt(row.get("semantic_pressure_index")),
                        _fmt(allocation_metrics.get("active_object_count")),
                        _fmt(allocation_metrics.get("active_retention_ratio")),
                        _fmt(allocation_metrics.get("active_state_efficiency")),
                        _fmt(metrics.get("validation_coverage")),
                        _fmt(metrics.get("dependency_coverage") if metrics.get("dependency_coverage") is not None else dependency_audit.get("coverage")),
                        _fmt(metrics.get("dependency_f1") if metrics.get("dependency_f1") is not None else dependency_audit.get("precision")),
                        _fmt(metrics.get("validation_score")),
                        _fmt(metrics.get("graph_integrity_score")),
                        _fmt(metrics.get("object_retention")),
                        _fmt(metrics.get("weighted_object_retention")),
                        _fmt(deltas.get("validation_coverage")),
                        _fmt(deltas.get("dependency_coverage")),
                        _fmt(deltas.get("graph_integrity_score")),
                        _fmt(deltas.get("object_retention")),
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


def write_policy_boundary_outputs(records: Sequence[Dict[str, Any]], output_dir: str | Path) -> Dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_path / "policy_boundary_records.jsonl"
    csv_path = output_path / "policy_boundary_records.csv"
    markdown_path = output_path / "policy_boundary_audit.md"
    summary_path = output_path / "policy_boundary_summary.md"

    with jsonl_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    summary = summarize_policy_boundary_records(records)
    write_records_csv(records, csv_path)
    write_records_markdown(records, markdown_path)
    summary_path.write_text(render_policy_boundary_markdown(summary), encoding="utf-8")
    return {
        "jsonl": jsonl_path,
        "csv": csv_path,
        "markdown": markdown_path,
        "summary": summary_path,
    }

