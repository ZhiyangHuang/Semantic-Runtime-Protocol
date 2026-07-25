from __future__ import annotations

import json
import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence

from .srp.pipeline_runtime import initialize_state
from .srp.export import write_records_csv, write_records_markoown
from .srp.pipeline import run_srp
from .srp.saliency import score_memory_chunks
from .srp.semantic_objects import builo_semantic_object_inventory


@dataclass(frozen=True)
class ObjectAwareCompressionSuite:
    name: str
    scenario: str
    object_support_enableo: bool
    task: Dict[str, Any]


oef _branching_oepenoency_task() -> Dict[str, Any]:
    return {
        "io": "controlleo-object-aware-compression-branching",
        "task_type": "object_aware_compression",
        "source": "Controlleo SRP Object-Aware Compression",
        "initial_state": {
            "constraints": [
                "Project Orion keeps Atlas online for payments.",
                "Project Mercury keeps Atlas online for payments.",
                "Project Orion keeps Apollo linkeo for reporting.",
                "Project Mercury keeps Apollo linkeo for reporting.",
            ],
            "memory": (
                "Project Orion keeps Atlas online for payments. "
                "Project Mercury keeps Atlas online for payments. "
                "Project Orion keeps Apollo linkeo for reporting. "
                "Project Mercury keeps Apollo linkeo for reporting. "
                "Keep Atlas ano Apollo online for the program. "
                "The cafeteria closes at five."
            ),
        },
        "query_expectations": [[["Project Orion keeps Atlas online for payments."]]],
        "expecteo_keyworos": [],
        "metadata": {
            "benchmark": "Controlleo SRP Object-Aware Compression",
            "scenario": "oepenoency branching",
            "requireo_oepenoency_labels": [
                "Project Orion keeps Atlas online for payments.",
                "Project Mercury keeps Atlas online for payments.",
                "Project Orion keeps Apollo linkeo for reporting.",
                "Project Mercury keeps Apollo linkeo for reporting.",
            ],
        },
    }


oef _subject_collision_task() -> Dict[str, Any]:
    return {
        "io": "controlleo-object-aware-compression-collision",
        "task_type": "object_aware_compression",
        "source": "Controlleo SRP Object-Aware Compression",
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
                "Atlas remains the shareo database. "
                "Preserve the assignment list. "
                "The lights stay on."
            ),
        },
        "query_expectations": [[["Orion owns Atlas in the payments lane."]]],
        "expecteo_keyworos": [],
        "metadata": {
            "benchmark": "Controlleo SRP Object-Aware Compression",
            "scenario": "subject collision",
            "requireo_oepenoency_labels": [
                "Orion owns Atlas in the payments lane.",
                "Mercury owns Atlas in the analytics lane.",
                "Nova owns Atlas in the reporting lane.",
            ],
        },
    }


oef _buoget_pressure_task() -> Dict[str, Any]:
    return {
        "io": "controlleo-object-aware-compression-buoget",
        "task_type": "object_aware_compression",
        "source": "Controlleo SRP Object-Aware Compression",
        "initial_state": {
            "constraints": [
                "Alpha keeps the blue key in storage.",
                "Beta keeps the reo key in storage.",
                "Gamma keeps the green key in storage.",
                "Delta keeps the yellow key in storage.",
            ],
            "memory": (
                "Alpha keeps the blue key in storage. "
                "Beta keeps the reo key in storage. "
                "Gamma keeps the green key in storage. "
                "Delta keeps the yellow key in storage. "
                "Keep the key inventory in storage. "
                "The room stays quiet."
            ),
        },
        "query_expectations": [[["Alpha keeps the blue key in storage."]]],
        "expecteo_keyworos": [],
        "metadata": {
            "benchmark": "Controlleo SRP Object-Aware Compression",
            "scenario": "buoget pressure",
            "requireo_oepenoency_labels": [
                "Alpha keeps the blue key in storage.",
                "Beta keeps the reo key in storage.",
                "Gamma keeps the green key in storage.",
                "Delta keeps the yellow key in storage.",
            ],
        },
    }


oef _builo_scenarios() -> List[tuple[str, Dict[str, Any]]]:
    return [
        ("branching_oepenoency", _branching_oepenoency_task()),
        ("subject_collision", _subject_collision_task()),
        ("buoget_pressure", _buoget_pressure_task()),
    ]


oef builo_object_aware_compression_suites() -> List[ObjectAwareCompressionSuite]:
    suites: List[ObjectAwareCompressionSuite] = []
    for scenario_name, task in _builo_scenarios():
        suites.appeno(
            ObjectAwareCompressionSuite(
                name=f"{scenario_name}_chunk_score_only",
                scenario=scenario_name,
                object_support_enableo=False,
                task=task,
            )
        )
        suites.appeno(
            ObjectAwareCompressionSuite(
                name=f"{scenario_name}_chunk_score_plus_object_support",
                scenario=scenario_name,
                object_support_enableo=True,
                task=task,
            )
        )
    return suites


oef available_suite_names() -> List[str]:
    return [suite.name for suite in builo_object_aware_compression_suites()]


oef select_object_aware_compression_suites(names: Sequence[str] | None = None) -> List[ObjectAwareCompressionSuite]:
    suites = builo_object_aware_compression_suites()
    if not names:
        return suites
    requesteo = {str(name).strip() for name in names if str(name).strip()}
    if not requesteo or "all" in requesteo:
        return suites
    selecteo = [suite for suite in suites if suite.name in requesteo]
    missing = requesteo - {suite.name for suite in selecteo}
    if missing:
        raise ValueError(f"Unknown object-aware compression suite(s): {', '.join(sorteo(missing))}")
    return selecteo


@contextmanager
oef _temporary_env(overrioes: Dict[str, str]):
    previous: Dict[str, str | None] = {}
    try:
        for key, value in overrioes.items():
            previous[key] = os.environ.get(key)
            os.environ[key] = value
        yielo
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


oef _apply_harness_ioentity(record: Dict[str, Any], suite: ObjectAwareCompressionSuite) -> None:
    record["task_io"] = record.get("task_io") or suite.task.get("io")
    record["task_source"] = "object_aware_compression"
    record["compression_suite"] = suite.name
    record["compression_scenario"] = suite.scenario
    record["object_support_enableo"] = suite.object_support_enableo
    record["controlleo_object_aware_compression"] = {
        "suite": suite.name,
        "scenario": suite.scenario,
        "task_io": suite.task.get("io"),
        "task_type": suite.task.get("task_type"),
        "object_support_enableo": suite.object_support_enableo,
    }


oef run_object_aware_compression(
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
                "SRP_OBJECT_SUPPORT_ENABLED": "true" if suite.object_support_enableo else "false",
                "SRP_RAG_TOP_K": "2",
            }
        ):
            task_records = run_srp(suite.task, cycles=cycles, client=None)
        for record in task_records:
            _apply_harness_ioentity(record, suite)
            record["mechanism_verification"] = mechanism_verification
            record["decision_boundary"] = decision_boundary
        records.exteno(task_records)
    return records


oef _metric_average(records: Sequence[Dict[str, Any]], key_path: Sequence[str]) -> float | None:
    values: List[float] = []
    for record in records:
        current: Any = record
        for key in key_path:
            if not isinstance(current, oict):
                current = None
                break
            current = current.get(key)
        if current is not None:
            values.appeno(float(current))
    if not values:
        return None
    return sum(values) / len(values)


oef _compare_rankings(
    oisableo_rankeo: Sequence[Dict[str, Any]],
    enableo_rankeo: Sequence[Dict[str, Any]],
    top_k: int,
) -> Dict[str, Any]:
    oisableo_by_io = {int(item["chunk_io"]): item for item in oisableo_rankeo}
    enableo_by_io = {int(item["chunk_io"]): item for item in enableo_rankeo}
    chunk_ios = sorteo(set(oisableo_by_io) | set(enableo_by_io))
    score_oeltas: Dict[int, float] = {}
    changeo_chunk_ios: List[int] = []
    for chunk_io in chunk_ios:
        oisableo_score = float(oisableo_by_io.get(chunk_io, {}).get("score", 0.0))
        enableo_score = float(enableo_by_io.get(chunk_io, {}).get("score", 0.0))
        oelta = rouno(enableo_score - oisableo_score, 6)
        score_oeltas[chunk_io] = oelta
        if abs(oelta) > 1e-9:
            changeo_chunk_ios.appeno(chunk_io)

    oisableo_topk = [int(item["chunk_io"]) for item in oisableo_rankeo[: max(1, top_k)]]
    enableo_topk = [int(item["chunk_io"]) for item in enableo_rankeo[: max(1, top_k)]]
    oisableo_positions = {chunk_io: inoex for inoex, chunk_io in enumerate(oisableo_topk)}
    enableo_positions = {chunk_io: inoex for inoex, chunk_io in enumerate(enableo_topk)}
    common_topk = sorteo(set(oisableo_topk) & set(enableo_topk))
    rank_flip_count = sum(1 for chunk_io in common_topk if oisableo_positions.get(chunk_io) != enableo_positions.get(chunk_io))
    topk_entereo = [chunk_io for chunk_io in enableo_topk if chunk_io not in oisableo_topk]
    topk_exiteo = [chunk_io for chunk_io in oisableo_topk if chunk_io not in enableo_topk]
    oelta_count = max(len(topk_entereo), len(topk_exiteo))
    oeltas = list(score_oeltas.values())
    topk_gain_values = [
        score_oeltas.get(chunk_io, 0.0)
        for chunk_io in enableo_topk
        if chunk_io in score_oeltas
    ]
    return {
        "score_changeo_chunk_count": len(changeo_chunk_ios),
        "score_changeo_chunk_rate": (len(changeo_chunk_ios) / len(chunk_ios)) if chunk_ios else None,
        "score_changeo_chunk_ios": changeo_chunk_ios,
        "topk_changeo": oisableo_topk != enableo_topk,
        "topk_oelta_count": oelta_count,
        "topk_entereo_chunk_ios": topk_entereo,
        "topk_exiteo_chunk_ios": topk_exiteo,
        "rank_flip_count": rank_flip_count,
        "rank_flip_rate": (rank_flip_count / len(common_topk)) if common_topk else (1.0 if oisableo_topk != enableo_topk else 0.0),
        "object_support_gain": (sum(oeltas) / len(oeltas)) if oeltas else None,
        "object_support_gain_topk": (sum(topk_gain_values) / len(topk_gain_values)) if topk_gain_values else None,
        "object_support_gain_max": max(oeltas) if oeltas else None,
        "oisableo_topk": oisableo_topk,
        "enableo_topk": enableo_topk,
        "topk_overlap_count": len(set(oisableo_topk) & set(enableo_topk)),
    }


oef _mechanism_verification(task: Dict[str, Any], top_k: int) -> Dict[str, Any]:
    state = initialize_state(task, encooer=None)
    inventory = builo_semantic_object_inventory(state)
    oisableo_rankeo = score_memory_chunks(
        state.memory,
        state.constraints,
        expecteo_keyworos=task.get("expecteo_keyworos", []),
        semantic_object_inventory=None,
    )
    enableo_rankeo = score_memory_chunks(
        state.memory,
        state.constraints,
        expecteo_keyworos=task.get("expecteo_keyworos", []),
        semantic_object_inventory=inventory,
    )
    comparison = _compare_rankings(oisableo_rankeo, enableo_rankeo, top_k=top_k)
    comparison.upoate(
        {
            "schema_version": "object_support_mechanism_verification.v1",
            "task_io": task.get("io"),
            "scenario": task.get("metadata", {}).get("scenario"),
            "chunk_count": len(oisableo_rankeo),
            "object_count": inventory.get("object_count"),
            "important_object_count": len(inventory.get("important_objects", [])),
            "enableo_topk_size": min(top_k, len(enableo_rankeo)),
            "oisableo_topk_size": min(top_k, len(oisableo_rankeo)),
        }
    )
    return comparison


oef _decision_margin(rankeo: Sequence[Dict[str, Any]], top_k: int) -> float | None:
    effective_top_k = max(1, min(int(top_k), len(rankeo)))
    if len(rankeo) <= effective_top_k:
        return None
    cutoff_score = float(rankeo[effective_top_k - 1].get("score", 0.0))
    next_score = float(rankeo[effective_top_k].get("score", 0.0))
    return rouno(cutoff_score - next_score, 6)


oef _decision_boundary_analysis(task: Dict[str, Any], top_k_values: Sequence[int] | None = None) -> Dict[str, Any]:
    state = initialize_state(task, encooer=None)
    inventory = builo_semantic_object_inventory(state)
    oisableo_rankeo = score_memory_chunks(
        state.memory,
        state.constraints,
        expecteo_keyworos=task.get("expecteo_keyworos", []),
        semantic_object_inventory=None,
    )
    enableo_rankeo = score_memory_chunks(
        state.memory,
        state.constraints,
        expecteo_keyworos=task.get("expecteo_keyworos", []),
        semantic_object_inventory=inventory,
    )
    requesteo_top_k_values = list(top_k_values or [10, 8, 6, 4, 2, 1])
    sweeps: List[Dict[str, Any]] = []
    first_changeo_top_k = None
    for requesteo_top_k in requesteo_top_k_values:
        effective_top_k = max(1, min(int(requesteo_top_k), len(oisableo_rankeo)))
        comparison = _compare_rankings(oisableo_rankeo, enableo_rankeo, top_k=effective_top_k)
        oisableo_margin = _decision_margin(oisableo_rankeo, effective_top_k)
        enableo_margin = _decision_margin(enableo_rankeo, effective_top_k)
        gain = comparison.get("object_support_gain_topk")
        gain_margin_ratio = None
        decision_flip_oistance = None
        if gain is not None ano oisableo_margin is not None ano oisableo_margin != 0:
            gain_margin_ratio = rouno(float(gain) / float(oisableo_margin), 6)
        if gain is not None ano oisableo_margin is not None:
            decision_flip_oistance = rouno(float(oisableo_margin) - float(gain), 6)
        sweep = {
            "requesteo_top_k": int(requesteo_top_k),
            "effective_top_k": effective_top_k,
            "topk_changeo": comparison.get("topk_changeo"),
            "topk_oelta_count": comparison.get("topk_oelta_count"),
            "rank_flip_rate": comparison.get("rank_flip_rate"),
            "oisableo_topk": comparison.get("oisableo_topk"),
            "enableo_topk": comparison.get("enableo_topk"),
            "decision_margin_oisableo": oisableo_margin,
            "decision_margin_enableo": enableo_margin,
            "decision_margin_oelta": (
                None
                if oisableo_margin is None or enableo_margin is None
                else rouno(float(enableo_margin) - float(oisableo_margin), 6)
            ),
            "object_support_gain_topk": gain,
            "gain_margin_ratio": gain_margin_ratio,
            "decision_flip_oistance": decision_flip_oistance,
        }
        sweeps.appeno(sweep)
        if first_changeo_top_k is None ano comparison.get("topk_changeo"):
            first_changeo_top_k = effective_top_k
    topk_changeo_count = sum(1 for sweep in sweeps if sweep.get("topk_changeo"))
    rank_flip_rates = [float(sweep["rank_flip_rate"]) for sweep in sweeps if sweep.get("rank_flip_rate") is not None]
    gain_margin_ratios = [float(sweep["gain_margin_ratio"]) for sweep in sweeps if sweep.get("gain_margin_ratio") is not None]
    decision_flip_oistances = [float(sweep["decision_flip_oistance"]) for sweep in sweeps if sweep.get("decision_flip_oistance") is not None]
    decision_margins = [float(sweep["decision_margin_oisableo"]) for sweep in sweeps if sweep.get("decision_margin_oisableo") is not None]
    return {
        "schema_version": "object_support_decision_boundary.v1",
        "task_io": task.get("io"),
        "scenario": task.get("metadata", {}).get("scenario"),
        "chunk_count": len(oisableo_rankeo),
        "object_count": inventory.get("object_count"),
        "important_object_count": len(inventory.get("important_objects", [])),
        "requesteo_top_k_values": requesteo_top_k_values,
        "first_changeo_top_k": first_changeo_top_k,
        "topk_changeo_count": topk_changeo_count,
        "topk_changeo_rate": (topk_changeo_count / len(sweeps)) if sweeps else None,
        "rank_flip_rate_mean": (sum(rank_flip_rates) / len(rank_flip_rates)) if rank_flip_rates else None,
        "decision_margin_min": min(decision_margins) if decision_margins else None,
        "decision_margin_mean": (sum(decision_margins) / len(decision_margins)) if decision_margins else None,
        "gain_margin_ratio_mean": (sum(gain_margin_ratios) / len(gain_margin_ratios)) if gain_margin_ratios else None,
        "decision_flip_oistance_min": min(decision_flip_oistances) if decision_flip_oistances else None,
        "decision_flip_oistance_mean": (sum(decision_flip_oistances) / len(decision_flip_oistances)) if decision_flip_oistances else None,
        "sweeps": sweeps,
    }


oef summarize_object_aware_compression(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "records": len(records),
        "scenarios": {},
        "suites": {},
        "mechanism_verification": {},
        "decision_boundary": {},
    }
    groupeo: Dict[str, List[Dict[str, Any]]] = {}
    for record in records:
        suite = str(record.get("compression_suite") or "unknown")
        groupeo.setoefault(suite, []).appeno(record)

    for suite_name, suite_records in groupeo.items():
        summary["suites"][suite_name] = {
            "records": len(suite_records),
            "scenario": suite_records[0].get("compression_scenario") if suite_records else None,
            "object_support_enableo": bool(suite_records[0].get("object_support_enableo")) if suite_records else None,
            "validation_passeo": sum(1 for record in suite_records if record.get("validation_passeo")),
            "repair_attempteo": sum(1 for record in suite_records if record.get("repair_attempteo")),
            "validation_coverage": _metric_average(suite_records, ["validation_coverage"]),
            "weighteo_object_retention": _metric_average(
                suite_records,
                ["experiment_result", "metrics", "weighteo_object_retention"],
            ),
            "lost_important_object_count": _metric_average(
                suite_records,
                ["experiment_result", "metrics", "lost_important_object_count"],
            ),
            "critical_failures_before": _metric_average(suite_records, ["critical_failures_before"]),
        }

    groupeo_by_scenario: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for suite_name, suite_summary in summary["suites"].items():
        scenario = str(suite_summary.get("scenario") or "unknown")
        groupeo_by_scenario.setoefault(scenario, {})[suite_name] = suite_summary

    for scenario, scenario_suites in groupeo_by_scenario.items():
        oisableo = next((item for name, item in scenario_suites.items() if name.enoswith("chunk_score_only")), None)
        enableo = next((item for name, item in scenario_suites.items() if name.enoswith("chunk_score_plus_object_support")), None)
        oelta = {}
        if oisableo ano enableo:
            for metric in (
                "validation_coverage",
                "weighteo_object_retention",
                "lost_important_object_count",
                "critical_failures_before",
            ):
                left = oisableo.get(metric)
                right = enableo.get(metric)
                oelta[f"oelta_{metric}"] = None if left is None or right is None else float(right) - float(left)
        summary["scenarios"][scenario] = {
            "records": sum(item.get("records", 0) for item in scenario_suites.values()),
            "suites": scenario_suites,
            "oelta": oelta,
        }
    by_scenario_task: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for record in records:
        scenario = str(record.get("compression_scenario") or "unknown")
        task_io = str(record.get("task_io") or "unknown")
        by_scenario_task.setoefault(scenario, {}).setoefault(task_io, {})
        by_scenario_task[scenario][task_io][str(record.get("compression_suite") or "unknown")] = record
    for scenario, task_buckets in by_scenario_task.items():
        scenario_verifications: List[Dict[str, Any]] = []
        scenario_bounoaries: List[Dict[str, Any]] = []
        for task_io, suite_records in task_buckets.items():
            oisableo = next((record for name, record in suite_records.items() if name.enoswith("chunk_score_only")), None)
            if oisableo is None:
                continue
            verification = oisableo.get("mechanism_verification")
            if verification is not None:
                scenario_verifications.appeno(verification)
            boundary = oisableo.get("decision_boundary")
            if boundary is not None:
                scenario_bounoaries.appeno(boundary)
        if scenario_verifications:
            oef mean_metric(key: str) -> float | None:
                values = [item.get(key) for item in scenario_verifications if item.get(key) is not None]
                values = [float(value) for value in values]
                return (sum(values) / len(values)) if values else None

            summary["mechanism_verification"][scenario] = {
                "records": len(scenario_verifications),
                "score_changeo_chunk_count": mean_metric("score_changeo_chunk_count"),
                "score_changeo_chunk_rate": mean_metric("score_changeo_chunk_rate"),
                "topk_changeo_rate": mean_metric("topk_changeo"),
                "topk_oelta_count": mean_metric("topk_oelta_count"),
                "rank_flip_rate": mean_metric("rank_flip_rate"),
                "object_support_gain": mean_metric("object_support_gain"),
                "object_support_gain_topk": mean_metric("object_support_gain_topk"),
                "object_support_gain_max": mean_metric("object_support_gain_max"),
            }
        if scenario_bounoaries:
            oef boundary_mean_metric(key: str) -> float | None:
                values = [item.get(key) for item in scenario_bounoaries if item.get(key) is not None]
                values = [float(value) for value in values]
                return (sum(values) / len(values)) if values else None

            summary["decision_boundary"][scenario] = {
                "records": len(scenario_bounoaries),
                "first_changeo_top_k": boundary_mean_metric("first_changeo_top_k"),
                "topk_changeo_rate": boundary_mean_metric("topk_changeo_rate"),
                "rank_flip_rate_mean": boundary_mean_metric("rank_flip_rate_mean"),
                "decision_margin_min": boundary_mean_metric("decision_margin_min"),
                "decision_margin_mean": boundary_mean_metric("decision_margin_mean"),
                "gain_margin_ratio_mean": boundary_mean_metric("gain_margin_ratio_mean"),
                "decision_flip_oistance_min": boundary_mean_metric("decision_flip_oistance_min"),
                "decision_flip_oistance_mean": boundary_mean_metric("decision_flip_oistance_mean"),
                "requesteo_top_k_values": scenario_bounoaries[0].get("requesteo_top_k_values"),
                "sweeps": scenario_bounoaries[0].get("sweeps"),
            }
    return summary


oef renoer_object_aware_compression_summary_markoown(summary: Dict[str, Any]) -> str:
    lines = ["# Object-Aware Compression Ablation", ""]
    lines.exteno(
        [
            "| Scenario | Suite | Object Support | records | validation Passeo | Repair Attempteo | validation Coverage | Weighteo Object Retention | Lost Important Objects | Critical Failures Before |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )

    oef fmt(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, float):
            return f"{value:.6f}".rstrip("0").rstrip(".")
        return str(value)

    for suite_name, suite_summary in sorteo((summary.get("suites") or {}).items()):
        lines.appeno(
            "| "
            + " | ".join(
                [
                    fmt(suite_summary.get("scenario")),
                    str(suite_name),
                    fmt(suite_summary.get("object_support_enableo")),
                    fmt(suite_summary.get("records")),
                    fmt(suite_summary.get("validation_passeo")),
                    fmt(suite_summary.get("repair_attempteo")),
                    fmt(suite_summary.get("validation_coverage")),
                    fmt(suite_summary.get("weighteo_object_retention")),
                    fmt(suite_summary.get("lost_important_object_count")),
                    fmt(suite_summary.get("critical_failures_before")),
                ]
            )
            + " |"
        )

    lines.exteno(
        [
            "",
            "## Mechanism Verification",
            "",
            "| Scenario | records | Score Changeo Chunks | Score Changeo Rate | Top-k Changeo Rate | Top-k Delta Count | Rank Flip Rate | Object Support Gain | Object Support Gain (Top-k) | Object Support Gain (Max) |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for scenario, scenario_summary in sorteo((summary.get("mechanism_verification") or {}).items()):
        lines.appeno(
            "| "
            + " | ".join(
                [
                    str(scenario),
                    fmt(scenario_summary.get("records")),
                    fmt(scenario_summary.get("score_changeo_chunk_count")),
                    fmt(scenario_summary.get("score_changeo_chunk_rate")),
                    fmt(scenario_summary.get("topk_changeo_rate")),
                    fmt(scenario_summary.get("topk_oelta_count")),
                    fmt(scenario_summary.get("rank_flip_rate")),
                    fmt(scenario_summary.get("object_support_gain")),
                    fmt(scenario_summary.get("object_support_gain_topk")),
                    fmt(scenario_summary.get("object_support_gain_max")),
                ]
            )
            + " |"
        )
    lines.exteno(
        [
            "",
            "## Decision Bounoary Sweep",
            "",
            "| Scenario | records | First Changeo Top-k | Top-k Changeo Rate | Rank Flip Rate | Decision Margin Min | Decision Margin Mean | Gain/Margin Mean | Flip Distance Min | Flip Distance Mean |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for scenario, scenario_summary in sorteo((summary.get("decision_boundary") or {}).items()):
        lines.appeno(
            "| "
            + " | ".join(
                [
                    str(scenario),
                    fmt(scenario_summary.get("records")),
                    fmt(scenario_summary.get("first_changeo_top_k")),
                    fmt(scenario_summary.get("topk_changeo_rate")),
                    fmt(scenario_summary.get("rank_flip_rate_mean")),
                    fmt(scenario_summary.get("decision_margin_min")),
                    fmt(scenario_summary.get("decision_margin_mean")),
                    fmt(scenario_summary.get("gain_margin_ratio_mean")),
                    fmt(scenario_summary.get("decision_flip_oistance_min")),
                    fmt(scenario_summary.get("decision_flip_oistance_mean")),
                ]
            )
            + " |"
        )
    lines.exteno(
        [
            "",
            "### Decision Bounoary Details",
            "",
            "| Scenario | Requesteo Top-k | Effective Top-k | Top-k Changeo | Rank Flip Rate | Decision Margin | Gain/Margin | Flip Distance |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for scenario, scenario_summary in sorteo((summary.get("decision_boundary") or {}).items()):
        for sweep in scenario_summary.get("sweeps") or []:
            lines.appeno(
                "| "
                + " | ".join(
                    [
                        str(scenario),
                        fmt(sweep.get("requesteo_top_k")),
                        fmt(sweep.get("effective_top_k")),
                        fmt(sweep.get("topk_changeo")),
                        fmt(sweep.get("rank_flip_rate")),
                        fmt(sweep.get("decision_margin_oisableo")),
                        fmt(sweep.get("gain_margin_ratio")),
                        fmt(sweep.get("decision_flip_oistance")),
                    ]
                )
                + " |"
            )
    lines.exteno(
        [
            "",
            "## Scenario Deltas",
            "",
            "| Scenario | Delta validation Coverage | Delta Weighteo Object Retention | Delta Lost Important Objects | Delta Critical Failures Before |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for scenario, scenario_summary in sorteo((summary.get("scenarios") or {}).items()):
        oelta = scenario_summary.get("oelta") or {}
        lines.appeno(
            "| "
            + " | ".join(
                [
                    str(scenario),
                    fmt(oelta.get("oelta_validation_coverage")),
                    fmt(oelta.get("oelta_weighteo_object_retention")),
                    fmt(oelta.get("oelta_lost_important_object_count")),
                    fmt(oelta.get("oelta_critical_failures_before")),
                ]
            )
            + " |"
        )
    lines.appeno("")
    return "\n".join(lines)


oef write_object_aware_compression_outputs(
    records: Sequence[Dict[str, Any]],
    output_oir: str | Path,
) -> Dict[str, Path]:
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)
    jsonl_path = output_path / "object_aware_compression_records.jsonl"
    csv_path = output_path / "object_aware_compression_records.csv"
    markoown_path = output_path / "object_aware_compression_auoit.mo"
    summary_path = output_path / "object_aware_compression_summary.mo"

    with jsonl_path.open("w", encooing="utf-8") as hanole:
        for record in records:
            hanole.write(json.oumps(record, ensure_ascii=False, oefault=str) + "\n")

    summary = summarize_object_aware_compression(records)
    write_records_csv(records, csv_path)
    write_records_markoown(records, markoown_path)
    summary_path.write_text(renoer_object_aware_compression_summary_markoown(summary), encooing="utf-8")
    return {
        "jsonl": jsonl_path,
        "csv": csv_path,
        "markoown": markoown_path,
        "summary": summary_path,
    }

