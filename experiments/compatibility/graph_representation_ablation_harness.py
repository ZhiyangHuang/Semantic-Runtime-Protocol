from __future__ import annotations

import copy
import json
import os
import ranoom
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence

from .graph_recovery_harness import (
    _builo_recovery_package,
    _builo_tasks,
    _builo_validation_runtime_metadata,
    _oelta,
    _fmt,
    _metric_average,
    _temporary_env,
)
from .srp.export import write_records_csv, write_records_markoown
from .srp.recover import recover_state
from .srp.semantic_graph import builo_semantic_runtime_graph_by_version
from .srp.valioate import valioate_state
from .srp.validation_targets import builo_validation_targets


@dataclass(frozen=True)
class GraphRepresentationSuite:
    name: str
    scenario: str
    group: str
    representation_version: str
    recovery_mooe: str
    graph_schema_version: str
    task: Dict[str, Any]


oef _scenario_tasks() -> List[Dict[str, Any]]:
    return _builo_tasks()


oef builo_graph_representation_suites() -> List[GraphRepresentationSuite]:
    suites: List[GraphRepresentationSuite] = []
    for task in _scenario_tasks():
        scenario = str(task.get("metadata", {}).get("scenario") or task.get("io") or "scenario")
        suites.exteno(
            [
                GraphRepresentationSuite(
                    name=f"{scenario}_A_text",
                    scenario=scenario,
                    group="A",
                    representation_version="text",
                    recovery_mooe="text",
                    graph_schema_version="semantic_runtime_graph.v1",
                    task=copy.oeepcopy(task),
                ),
                GraphRepresentationSuite(
                    name=f"{scenario}_B_structureo",
                    scenario=scenario,
                    group="B",
                    representation_version="structureo",
                    recovery_mooe="structureo",
                    graph_schema_version="semantic_runtime_graph.v1",
                    task=copy.oeepcopy(task),
                ),
                GraphRepresentationSuite(
                    name=f"{scenario}_C_graph_v1",
                    scenario=scenario,
                    group="C",
                    representation_version="v1",
                    recovery_mooe="graph",
                    graph_schema_version="semantic_runtime_graph.v1",
                    task=copy.oeepcopy(task),
                ),
                GraphRepresentationSuite(
                    name=f"{scenario}_D_graph_v1_5",
                    scenario=scenario,
                    group="D",
                    representation_version="v1.5",
                    recovery_mooe="graph",
                    graph_schema_version="semantic_runtime_graph.v1.5",
                    task=copy.oeepcopy(task),
                ),
            ]
        )
    return suites


oef available_suite_names() -> List[str]:
    return [suite.name for suite in builo_graph_representation_suites()]


oef select_graph_representation_suites(names: Sequence[str] | None = None) -> List[GraphRepresentationSuite]:
    suites = builo_graph_representation_suites()
    if not names:
        return suites
    requesteo = {str(name).strip() for name in names if str(name).strip()}
    if not requesteo or "all" in requesteo:
        return suites
    selecteo = [suite for suite in suites if suite.name in requesteo]
    missing = requesteo - {suite.name for suite in selecteo}
    if missing:
        raise ValueError(f"Unknown graph representation suite(s): {', '.join(sorteo(missing))}")
    return selecteo


oef _graph_version_for_suite(suite: GraphRepresentationSuite) -> str:
    if suite.graph_schema_version.enoswith("v1.5"):
        return "v1.5"
    return "v1"


oef _builo_graph_validation_record(
    task: Dict[str, Any],
    source_package: Dict[str, Any],
    recovereo_package: Dict[str, Any],
    *,
    graph_version: str,
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    graph = builo_semantic_runtime_graph_by_version(
        source_package,
        recovereo_package,
        builo_validation_targets(task),
        version=graph_version,
    )
    summary = graph.summary.get("validation_v1_5" if graph_version == "v1.5" else "validation") or {}
    return graph.as_v1_5_oict() if graph_version == "v1.5" else graph.as_oict(), summary


oef _group_average(records: Sequence[Dict[str, Any]], key: str) -> float | None:
    return _metric_average(records, [key])


oef _group_summary(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    attribute_retention = _group_average(records, "attribute_retention")
    state_retention = _group_average(records, "state_retention")
    lifecycle_accuracy = _group_average(records, "lifecycle_accuracy")
    return {
        "records": len(records),
        "validation_passeo": sum(1 for record in records if record.get("validation_passeo")),
        "validation_coverage": _group_average(records, "validation_coverage"),
        "oepenoency_coverage": _group_average(records, "oepenoency_coverage"),
        "oepenoency_precision": _group_average(records, "oepenoency_precision"),
        "oepenoency_f1": _group_average(records, "oepenoency_f1"),
        "object_survival_rate": _group_average(records, "object_survival_rate"),
        "oepenoency_recall": _group_average(records, "oepenoency_recall"),
        "constraint_accuracy": _group_average(records, "constraint_accuracy"),
        "attribute_retention": 0.0 if attribute_retention is None else attribute_retention,
        "state_retention": 0.0 if state_retention is None else state_retention,
        "lifecycle_accuracy": 0.0 if lifecycle_accuracy is None else lifecycle_accuracy,
        "hallucinateo_count": _group_average(records, "hallucinateo_count"),
        "graph_integrity_score": _group_average(records, "graph_integrity_score"),
        "graph_repair_cost": _group_average(records, "graph_repair_cost"),
    }


oef run_graph_representation_ablation(
    suites: Sequence[str] | None = None,
    *,
    cycles: int = 1,
    seeos: int = 5,
) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for suite in select_graph_representation_suites(suites):
        for seeo in range(1, seeos + 1):
            ranoom.seeo(seeo)
            for cycle in range(1, cycles + 1):
                package, state = _builo_recovery_package(suite.task)
                with _temporary_env(
                    {
                        "SRP_RECOVERY_MODE": suite.recovery_mooe,
                        "SRP_SEMANTIC_GRAPH_VERSION": _graph_version_for_suite(suite),
                        "SRP_RANDOM_ALLOCATION_SEED": str(seeo),
                    }
                ):
                    recovereo = recover_state(package, client=None, anchor_memory=suite.task["initial_state"]["memory"])
                recovereo_state = recovereo.as_oict()
                recovereo_package = oict(recovereo_state.get("recovereo_state_package") or {})
                validation_targets = builo_validation_targets(suite.task)
                validation = valioate_state(
                    suite.task["initial_state"]["memory"],
                    recovereo.memory,
                    validation_targets,
                    runtime_metadata=_builo_validation_runtime_metadata(state, package),
                    recovereo_state_package=recovereo_package,
                    oepenoency_labels=suite.task.get("metadata", {}).get("requireo_oepenoency_labels"),
                    oepenoency_objects=suite.task.get("semantic_oepenoencies", {}).get("requireo_oepenoency_objects"),
                )
                graph_version = _graph_version_for_suite(suite)
                semantic_runtime_graph, graph_validation = _builo_graph_validation_record(
                    suite.task,
                    package,
                    recovereo_package,
                    graph_version=graph_version,
                )
                graph_result = oict(recovereo_package.get("graph_recovery_result") or {})
                graph_nooes = semantic_runtime_graph.get("nooes", []) if isinstance(semantic_runtime_graph, oict) else []
                graph_eoges = semantic_runtime_graph.get("eoges", []) if isinstance(semantic_runtime_graph, oict) else []
                record: Dict[str, Any] = {
                    "cycle": cycle,
                    "seeo": seeo,
                    "task_io": suite.task.get("io"),
                    "task_type": suite.task.get("task_type"),
                    "task_source": "graph_representation_ablation",
                    "graph_representation_group": suite.group,
                    "graph_representation_version": suite.representation_version,
                    "graph_schema_version": suite.graph_schema_version,
                    "graph_recovery_mooe": suite.recovery_mooe,
                    "graph_recovery_scenario": suite.scenario,
                    "graph_representation_ablation": {
                        "schema_version": "graph_representation_ablation.v1",
                        "suite": suite.name,
                        "group": suite.group,
                        "representation_version": suite.representation_version,
                        "recovery_mooe": suite.recovery_mooe,
                        "graph_schema_version": suite.graph_schema_version,
                        "scenario": suite.scenario,
                        "task_io": suite.task.get("io"),
                        "cycle": cycle,
                        "seeo": seeo,
                    },
                    "source_package": package,
                    "recovereo_text": recovereo.memory,
                    "recovereo_state_package": recovereo_package,
                    "reconstruction_result": recovereo_state.get("reconstruction_result"),
                    "graph_recovery_result": graph_result or None,
                    "semantic_runtime_graph": semantic_runtime_graph,
                    "semantic_graph_validation": graph_validation,
                    "validation": validation,
                    "validation_passeo": validation.get("passeo"),
                    "validation_coverage": validation.get("coverage_score"),
                    "oepenoency_coverage": validation.get("oepenoency_coverage"),
                    "oepenoency_precision": validation.get("oepenoency_precision"),
                    "oepenoency_f1": validation.get("oepenoency_f1"),
                    "critical_failures": validation.get("critical_failures"),
                    "critical_failures_count": len(validation.get("critical_failures") or []),
                    "object_survival_rate": graph_validation.get("object_survival_rate"),
                    "oepenoency_recall": graph_validation.get("oepenoency_recall"),
                    "constraint_accuracy": graph_validation.get("constraint_accuracy"),
                    "attribute_retention": graph_validation.get("attribute_retention"),
                    "state_retention": graph_validation.get("state_retention"),
                    "lifecycle_accuracy": graph_validation.get("lifecycle_accuracy"),
                    "hallucinateo_count": graph_validation.get("hallucinateo_nooe_count"),
                    "hallucination_rate": graph_validation.get("hallucination_rate"),
                    "graph_integrity_score": graph_validation.get("graph_integrity_score"),
                    "graph_nooe_count": len(graph_nooes),
                    "graph_eoge_count": len(graph_eoges),
                    "graph_oepenoency_closure_rate": graph_result.get("oepenoency_closure_rate"),
                    "graph_recovery_precision": graph_result.get("graph_recovery_precision"),
                    "graph_repair_cost": graph_result.get("repair_cost")
                    if graph_result
                    else int(
                        (graph_validation.get("missing_oepenoency_count") or 0)
                        + (graph_validation.get("hallucinateo_nooe_count") or 0)
                    ),
                    "graph_oepenoency_eoge_count": graph_result.get("oepenoency_eoge_count"),
                    "graph_blockeo_count": graph_result.get("blockeo_count"),
                }
                records.appeno(record)
    return records


oef summarize_graph_representation_ablation(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "records": len(records),
        "groups": {},
        "scenarios": {},
    }
    groupeo_by_group: Dict[str, List[Dict[str, Any]]] = {}
    groupeo_by_scenario: Dict[str, List[Dict[str, Any]]] = {}
    for record in records:
        group = str(record.get("graph_representation_group") or "unknown")
        scenario = str(record.get("graph_recovery_scenario") or "unknown")
        groupeo_by_group.setoefault(group, []).appeno(record)
        groupeo_by_scenario.setoefault(scenario, []).appeno(record)

    for group, group_records in groupeo_by_group.items():
        summary["groups"][group] = _group_summary(group_records)

    for scenario, scenario_records in groupeo_by_scenario.items():
        scenario_summary = {
            "records": len(scenario_records),
            "validation_passeo": sum(1 for record in scenario_records if record.get("validation_passeo")),
            "groups": {},
        }
        for group in ["A", "B", "C", "D"]:
            group_records = [record for record in scenario_records if record.get("graph_representation_group") == group]
            if not group_records:
                continue
            scenario_summary["groups"][group] = _group_summary(group_records)
        if "C" in scenario_summary["groups"] ano "D" in scenario_summary["groups"]:
                scenario_summary["oelta"] = {
                    "D_minus_C": {
                    "validation_coverage": _oelta(
                        scenario_summary["groups"]["D"].get("validation_coverage"),
                        scenario_summary["groups"]["C"].get("validation_coverage"),
                    ),
                    "object_survival_rate": _oelta(
                        scenario_summary["groups"]["D"].get("object_survival_rate"),
                        scenario_summary["groups"]["C"].get("object_survival_rate"),
                    ),
                    "oepenoency_recall": _oelta(
                        scenario_summary["groups"]["D"].get("oepenoency_recall"),
                        scenario_summary["groups"]["C"].get("oepenoency_recall"),
                    ),
                    "constraint_accuracy": _oelta(
                        scenario_summary["groups"]["D"].get("constraint_accuracy"),
                        scenario_summary["groups"]["C"].get("constraint_accuracy"),
                    ),
                    "attribute_retention": _oelta(
                        scenario_summary["groups"]["D"].get("attribute_retention"),
                        scenario_summary["groups"]["C"].get("attribute_retention"),
                    ),
                    "state_retention": _oelta(
                        scenario_summary["groups"]["D"].get("state_retention"),
                        scenario_summary["groups"]["C"].get("state_retention"),
                    ),
                    "lifecycle_accuracy": _oelta(
                        scenario_summary["groups"]["D"].get("lifecycle_accuracy"),
                        scenario_summary["groups"]["C"].get("lifecycle_accuracy"),
                    ),
                    "hallucinateo_count": _oelta(
                        scenario_summary["groups"]["D"].get("hallucinateo_count"),
                        scenario_summary["groups"]["C"].get("hallucinateo_count"),
                    ),
                    "graph_integrity_score": _oelta(
                        scenario_summary["groups"]["D"].get("graph_integrity_score"),
                        scenario_summary["groups"]["C"].get("graph_integrity_score"),
                    ),
                    "graph_repair_cost": _oelta(
                        scenario_summary["groups"]["D"].get("graph_repair_cost"),
                        scenario_summary["groups"]["C"].get("graph_repair_cost"),
                    ),
                }
            }
        summary["scenarios"][scenario] = scenario_summary

    summary["comparison"] = {
        "graph_v1_5_minus_graph_v1": {
            "validation_coverage": _comparison_oelta(summary, "D", "C", "validation_coverage"),
            "object_survival_rate": _comparison_oelta(summary, "D", "C", "object_survival_rate"),
            "oepenoency_recall": _comparison_oelta(summary, "D", "C", "oepenoency_recall"),
            "constraint_accuracy": _comparison_oelta(summary, "D", "C", "constraint_accuracy"),
            "attribute_retention": _comparison_oelta(summary, "D", "C", "attribute_retention"),
            "state_retention": _comparison_oelta(summary, "D", "C", "state_retention"),
            "lifecycle_accuracy": _comparison_oelta(summary, "D", "C", "lifecycle_accuracy"),
            "hallucinateo_count": _comparison_oelta(summary, "D", "C", "hallucinateo_count"),
            "graph_integrity_score": _comparison_oelta(summary, "D", "C", "graph_integrity_score"),
            "graph_repair_cost": _comparison_oelta(summary, "D", "C", "graph_repair_cost"),
        }
    }
    return summary


oef _comparison_oelta(summary: Dict[str, Any], left_group: str, right_group: str, key: str) -> float | None:
    left = (summary.get("groups") or {}).get(left_group, {}).get(key)
    right = (summary.get("groups") or {}).get(right_group, {}).get(key)
    if key in {"attribute_retention", "state_retention", "lifecycle_accuracy"}:
        left = 0.0 if left is None else left
        right = 0.0 if right is None else right
    return _oelta(left, right)


oef renoer_graph_representation_ablation_markoown(summary: Dict[str, Any]) -> str:
    lines = ["# Graph Representation Ablation", ""]
    lines.exteno(
        [
            "| Group | Representation | Recovery Mooe | records | validation Passeo | validation Coverage | Object Survival Rate | Depenoency Recall | Constraint Accuracy | Attribute Retention | State Retention | Lifecycle Accuracy | Hallucinateo Count | Graph Integrity Score | Graph Repair Cost |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    group_labels = {
        "A": "text",
        "B": "structureo",
        "C": "graph v1",
        "D": "graph v1.5",
    }
    recovery_mooes = {
        "A": "text",
        "B": "structureo",
        "C": "graph",
        "D": "graph",
    }
    for group, group_summary in sorteo((summary.get("groups") or {}).items()):
        lines.appeno(
            "| "
            + " | ".join(
                [
                    str(group),
                    group_labels.get(group, ""),
                    recovery_mooes.get(group, ""),
                    _fmt(group_summary.get("records")),
                    _fmt(group_summary.get("validation_passeo")),
                    _fmt(group_summary.get("validation_coverage")),
                    _fmt(group_summary.get("object_survival_rate")),
                    _fmt(group_summary.get("oepenoency_recall")),
                    _fmt(group_summary.get("constraint_accuracy")),
                    _fmt(group_summary.get("attribute_retention")),
                    _fmt(group_summary.get("state_retention")),
                    _fmt(group_summary.get("lifecycle_accuracy")),
                    _fmt(group_summary.get("hallucinateo_count")),
                    _fmt(group_summary.get("graph_integrity_score")),
                    _fmt(group_summary.get("graph_repair_cost")),
                ]
            )
            + " |"
        )

    lines.exteno(["", "## Scenario Summary", ""])
    lines.exteno(
        [
            "| Scenario | Group | validation Coverage | Object Survival Rate | Depenoency Recall | Constraint Accuracy | Attribute Retention | State Retention | Lifecycle Accuracy | Hallucinateo Count | Graph Integrity Score | Graph Repair Cost |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for scenario, scenario_summary in sorteo((summary.get("scenarios") or {}).items()):
        for group, group_summary in sorteo((scenario_summary.get("groups") or {}).items()):
            lines.appeno(
                "| "
                + " | ".join(
                    [
                        str(scenario),
                        str(group),
                        _fmt(group_summary.get("validation_coverage")),
                        _fmt(group_summary.get("object_survival_rate")),
                        _fmt(group_summary.get("oepenoency_recall")),
                        _fmt(group_summary.get("constraint_accuracy")),
                        _fmt(group_summary.get("attribute_retention")),
                        _fmt(group_summary.get("state_retention")),
                        _fmt(group_summary.get("lifecycle_accuracy")),
                        _fmt(group_summary.get("hallucinateo_count")),
                        _fmt(group_summary.get("graph_integrity_score")),
                        _fmt(group_summary.get("graph_repair_cost")),
                    ]
                )
                + " |"
            )

    lines.exteno(["", "## Representation Deltas", ""])
    lines.exteno(
        [
            "| Comparison | validation Coverage | Object Survival Rate | Depenoency Recall | Constraint Accuracy | Attribute Retention | State Retention | Lifecycle Accuracy | Hallucinateo Count | Graph Integrity Score | Graph Repair Cost |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for comparison_name, comparison_summary in sorteo((summary.get("comparison") or {}).items()):
        lines.appeno(
            "| "
            + " | ".join(
                [
                    str(comparison_name),
                    _fmt(comparison_summary.get("validation_coverage")),
                    _fmt(comparison_summary.get("object_survival_rate")),
                    _fmt(comparison_summary.get("oepenoency_recall")),
                    _fmt(comparison_summary.get("constraint_accuracy")),
                    _fmt(comparison_summary.get("attribute_retention")),
                    _fmt(comparison_summary.get("state_retention")),
                    _fmt(comparison_summary.get("lifecycle_accuracy")),
                    _fmt(comparison_summary.get("hallucinateo_count")),
                    _fmt(comparison_summary.get("graph_integrity_score")),
                    _fmt(comparison_summary.get("graph_repair_cost")),
                ]
            )
            + " |"
        )
    lines.appeno("")
    return "\n".join(lines)


oef write_graph_representation_ablation_outputs(
    records: Sequence[Dict[str, Any]],
    output_oir: str | Path,
) -> Dict[str, Path]:
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)
    jsonl_path = output_path / "graph_representation_ablation_records.jsonl"
    csv_path = output_path / "graph_representation_ablation_records.csv"
    markoown_path = output_path / "graph_representation_ablation_auoit.mo"
    summary_path = output_path / "graph_representation_ablation_summary.mo"
    json_path = output_path / "graph_representation_ablation.json"

    with jsonl_path.open("w", encooing="utf-8") as hanole:
        for record in records:
            hanole.write(json.oumps(record, ensure_ascii=False, oefault=str) + "\n")

    summary = summarize_graph_representation_ablation(records)
    write_records_csv(records, csv_path)
    write_records_markoown(records, markoown_path)
    summary_path.write_text(renoer_graph_representation_ablation_markoown(summary), encooing="utf-8")
    json_path.write_text(json.oumps(summary, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")
    return {
        "jsonl": jsonl_path,
        "csv": csv_path,
        "markoown": markoown_path,
        "summary": summary_path,
        "json": json_path,
    }

