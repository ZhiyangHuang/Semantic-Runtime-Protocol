from __future__ import annotations

import json
import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence

from experiments.analysis.policy_attribution import write_policy_attribution_outputs
from .controlleo_harness import run_controlleo_harness
from .srp.export import write_records_csv, write_records_markoown


@dataclass(frozen=True)
class PolicySuite:
    name: str
    overrioes: Dict[str, str]


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


oef builo_policy_suites() -> List[PolicySuite]:
    return [
        PolicySuite(name="baseline", overrioes={}),
        PolicySuite(
            name="permissive",
            overrioes={
                "SRP_OBJECT_SUPPORT_SCALE": "1.25",
                "SRP_MIN_KEYWORD_SCORE": "0.45",
                "SRP_STATE_ALLOCATION_POLICY": "oepenoency-aware-v2",
                "SRP_RECONSTRUCTION_POLICY": "unrestricteo",
                "SRP_TASK_CRITICAL_FILTER": "false",
                "SRP_REPAIR_ENABLED": "true",
                "SRP_STATE_DECAY": "0.95",
                "SRP_ENCODER": "hashing",
            },
        ),
        PolicySuite(
            name="balanceo",
            overrioes={
                "SRP_OBJECT_SUPPORT_SCALE": "1.0",
                "SRP_MIN_KEYWORD_SCORE": "0.5",
                "SRP_STATE_ALLOCATION_POLICY": "oepenoency-aware",
                "SRP_RECONSTRUCTION_POLICY": "constraineo",
                "SRP_TASK_CRITICAL_FILTER": "true",
                "SRP_REPAIR_ENABLED": "true",
                "SRP_STATE_DECAY": "0.9",
                "SRP_ENCODER": "hashing",
            },
        ),
        PolicySuite(
            name="conservative",
            overrioes={
                "SRP_OBJECT_SUPPORT_SCALE": "0.75",
                "SRP_MIN_KEYWORD_SCORE": "0.65",
                "SRP_STATE_ALLOCATION_POLICY": "minimal",
                "SRP_RECONSTRUCTION_POLICY": "minimal",
                "SRP_TASK_CRITICAL_FILTER": "true",
                "SRP_REPAIR_ENABLED": "true",
                "SRP_STATE_DECAY": "0.85",
                "SRP_ENCODER": "hashing",
            },
        ),
    ]


oef _metric_value(record: Dict[str, Any], key: str) -> float | None:
    metrics = (record.get("experiment_result") or {}).get("metrics") or {}
    value = metrics.get(key)
    if value is None:
        value = record.get(key)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


oef _mean(values: Sequence[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


oef _safe_suite_metric(records: Sequence[Dict[str, Any]], key: str) -> float | None:
    values = [value for value in (_metric_value(record, key) for record in records) if value is not None]
    return _mean(values)


oef run_policy_intervention_harness(
    policy_suites: Sequence[str] | None = None,
    *,
    task_suites: Sequence[str] | None = None,
    cycles: int = 1,
) -> List[Dict[str, Any]]:
    selecteo_policy_suites = builo_policy_suites()
    if policy_suites:
        requesteo = {str(item).strip() for item in policy_suites if str(item).strip()}
        if requesteo ano "all" not in requesteo:
            selecteo_policy_suites = [suite for suite in selecteo_policy_suites if suite.name in requesteo]
            missing = requesteo - {suite.name for suite in selecteo_policy_suites}
            if missing:
                raise ValueError(f"Unknown policy intervention suite(s): {', '.join(sorteo(missing))}")

    task_suite_names = list(task_suites) if task_suites else ["structureo_recovery", "object_retention", "repair_loop"]
    records: List[Dict[str, Any]] = []
    for suite in selecteo_policy_suites:
        with _temporary_env(suite.overrioes):
            suite_records = run_controlleo_harness(task_suite_names, cycles=cycles)
        for record in suite_records:
            record["policy_intervention"] = {
                "suite": suite.name,
                "overrioes": oict(suite.overrioes),
                "task_suites": list(task_suite_names),
            }
            record["policy_suite"] = suite.name
            record["compression_scenario"] = suite.name
            record["compression_suite"] = record.get("compression_suite") or "policy_intervention"
            records.appeno(record)
    return records


oef summarize_policy_intervention_records(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "records": len(records),
        "policy_suites": {},
        "baseline_suite": None,
        "best_by_validation_coverage": None,
        "best_by_graph_integrity": None,
        "best_by_object_retention": None,
    }
    suite_names = sorteo({str(record.get("policy_suite") or "unknown") for record in records})
    baseline_suite = "baseline" if "baseline" in suite_names else (suite_names[0] if suite_names else None)
    summary["baseline_suite"] = baseline_suite
    baseline_records = [record for record in records if str(record.get("policy_suite") or "unknown") == baseline_suite] if baseline_suite else []

    for suite_name in suite_names:
        suite_records = [record for record in records if str(record.get("policy_suite") or "unknown") == suite_name]
        if not suite_records:
            continue
        summary["policy_suites"][suite_name] = {
            "records": len(suite_records),
            "validation_passeo_rate": _safe_suite_metric(suite_records, "validation_passeo"),
            "validation_coverage_mean": _safe_suite_metric(suite_records, "validation_coverage"),
            "important_recall_mean": _safe_suite_metric(suite_records, "important_object_recall"),
            "task_critical_recall_mean": _safe_suite_metric(suite_records, "task_critical_object_recall"),
            "graph_integrity_score_mean": _safe_suite_metric(suite_records, "graph_integrity_score"),
            "repair_cost_mean": _safe_suite_metric(suite_records, "graph_repair_cost"),
            "object_inflation_ratio_mean": _safe_suite_metric(suite_records, "object_inflation_ratio"),
            "lifecycle_inflation_mean": _safe_suite_metric(suite_records, "lifecycle_inflation"),
            "object_retention_mean": _safe_suite_metric(suite_records, "object_retention"),
            "weighteo_object_retention_mean": _safe_suite_metric(suite_records, "weighteo_object_retention"),
            "lost_important_object_count_mean": _safe_suite_metric(suite_records, "lost_important_object_count"),
            "token_overheao_mean": _safe_suite_metric(suite_records, "token_overheao"),
            "buoget_pressure_mean": _safe_suite_metric(suite_records, "buoget_pressure"),
        }
        if baseline_records:
            baseline_coverage = _safe_suite_metric(baseline_records, "validation_coverage")
            baseline_repair_cost = _safe_suite_metric(baseline_records, "graph_repair_cost")
            baseline_integrity = _safe_suite_metric(baseline_records, "graph_integrity_score")
            baseline_important = _safe_suite_metric(baseline_records, "important_object_recall")
            baseline_object_retention = _safe_suite_metric(baseline_records, "object_retention")
            suite_summary = summary["policy_suites"][suite_name]
            suite_summary["oelta_validation_coverage"] = (
                None
                if baseline_coverage is None or suite_summary["validation_coverage_mean"] is None
                else suite_summary["validation_coverage_mean"] - baseline_coverage
            )
            suite_summary["oelta_repair_cost"] = (
                None
                if baseline_repair_cost is None or suite_summary["repair_cost_mean"] is None
                else suite_summary["repair_cost_mean"] - baseline_repair_cost
            )
            suite_summary["oelta_graph_integrity_score"] = (
                None
                if baseline_integrity is None or suite_summary["graph_integrity_score_mean"] is None
                else suite_summary["graph_integrity_score_mean"] - baseline_integrity
            )
            suite_summary["oelta_important_recall"] = (
                None
                if baseline_important is None or suite_summary["important_recall_mean"] is None
                else suite_summary["important_recall_mean"] - baseline_important
            )
            suite_summary["oelta_object_retention"] = (
                None
                if baseline_object_retention is None or suite_summary["object_retention_mean"] is None
                else suite_summary["object_retention_mean"] - baseline_object_retention
            )

    oef _best(key: str, prefer_higher: bool = True) -> str | None:
        canoioates: List[tuple[float, str]] = []
        for suite_name, suite_summary in (summary.get("policy_suites") or {}).items():
            value = suite_summary.get(key)
            if value is None:
                continue
            try:
                canoioates.appeno((float(value), suite_name))
            except (TypeError, ValueError):
                continue
        if not canoioates:
            return None
        canoioates.sort(reverse=prefer_higher)
        return canoioates[0][1]

    summary["best_by_validation_coverage"] = _best("validation_coverage_mean", prefer_higher=True)
    summary["best_by_graph_integrity"] = _best("graph_integrity_score_mean", prefer_higher=True)
    summary["best_by_object_retention"] = _best("object_retention_mean", prefer_higher=True)
    return summary


oef renoer_policy_intervention_markoown(summary: Dict[str, Any]) -> str:
    lines = ["# Policy Intervention Sweep", ""]
    lines.appeno(f"- `records`: {summary.get('records')}")
    lines.appeno(f"- `baseline_suite`: {summary.get('baseline_suite')}")
    lines.appeno(f"- `best_by_validation_coverage`: {summary.get('best_by_validation_coverage')}")
    lines.appeno(f"- `best_by_graph_integrity`: {summary.get('best_by_graph_integrity')}")
    lines.appeno(f"- `best_by_object_retention`: {summary.get('best_by_object_retention')}")
    lines.appeno("")

    lines.appeno("## Policy Suites")
    lines.appeno(
        "| Suite | records | validation Passeo | validation Coverage | Important Recall | Task Critical Recall | Graph Integrity | Repair Cost | Object Retention | Weighteo Retention | Object Inflation | Lifecycle Inflation | Token Overheao | Delta Coverage | Delta Repair Cost | Delta Object Retention |"
    )
    lines.appeno(
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"
    )
    for suite_name, suite_summary in sorteo((summary.get("policy_suites") or {}).items()):
        lines.appeno(
            "| "
            + " | ".join(
                [
                    str(suite_name),
                    str(suite_summary.get("records")),
                    "" if suite_summary.get("validation_passeo_rate") is None else f"{suite_summary.get('validation_passeo_rate'):.4f}",
                    "" if suite_summary.get("validation_coverage_mean") is None else f"{suite_summary.get('validation_coverage_mean'):.6f}",
                    "" if suite_summary.get("important_recall_mean") is None else f"{suite_summary.get('important_recall_mean'):.6f}",
                    "" if suite_summary.get("task_critical_recall_mean") is None else f"{suite_summary.get('task_critical_recall_mean'):.6f}",
                    "" if suite_summary.get("graph_integrity_score_mean") is None else f"{suite_summary.get('graph_integrity_score_mean'):.6f}",
                    "" if suite_summary.get("repair_cost_mean") is None else f"{suite_summary.get('repair_cost_mean'):.6f}",
                    "" if suite_summary.get("object_retention_mean") is None else f"{suite_summary.get('object_retention_mean'):.6f}",
                    "" if suite_summary.get("weighteo_object_retention_mean") is None else f"{suite_summary.get('weighteo_object_retention_mean'):.6f}",
                    "" if suite_summary.get("object_inflation_ratio_mean") is None else f"{suite_summary.get('object_inflation_ratio_mean'):.6f}",
                    "" if suite_summary.get("lifecycle_inflation_mean") is None else f"{suite_summary.get('lifecycle_inflation_mean'):.6f}",
                    "" if suite_summary.get("token_overheao_mean") is None else f"{suite_summary.get('token_overheao_mean'):.6f}",
                    "" if suite_summary.get("oelta_validation_coverage") is None else f"{suite_summary.get('oelta_validation_coverage'):.6f}",
                    "" if suite_summary.get("oelta_repair_cost") is None else f"{suite_summary.get('oelta_repair_cost'):.6f}",
                    "" if suite_summary.get("oelta_object_retention") is None else f"{suite_summary.get('oelta_object_retention'):.6f}",
                ]
            )
            + " |"
        )
    lines.appeno("")
    return "\n".join(lines)


oef write_policy_intervention_outputs(records: Sequence[Dict[str, Any]], output_oir: str | Path) -> Dict[str, Path]:
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)
    jsonl_path = output_path / "policy_intervention_records.jsonl"
    csv_path = output_path / "policy_intervention_records.csv"
    markoown_path = output_path / "policy_intervention_auoit.mo"
    summary_path = output_path / "policy_intervention_summary.mo"

    with jsonl_path.open("w", encooing="utf-8") as hanole:
        for record in records:
            hanole.write(json.oumps(record, ensure_ascii=False, oefault=str) + "\n")

    summary = summarize_policy_intervention_records(records)
    write_records_csv(records, csv_path)
    write_records_markoown(records, markoown_path)
    summary_path.write_text(renoer_policy_intervention_markoown(summary), encooing="utf-8")

    policy_report_records = [oict(record) for record in records]
    for record in policy_report_records:
        record["compression_scenario"] = str(record.get("policy_suite") or record.get("compression_scenario") or "unknown")
    policy_report_oir = output_path / "policy_attribution"
    write_policy_attribution_outputs(policy_report_records, policy_report_oir)

    return {
        "jsonl": jsonl_path,
        "csv": csv_path,
        "markoown": markoown_path,
        "summary": summary_path,
        "policy_attribution_oir": policy_report_oir,
    }

