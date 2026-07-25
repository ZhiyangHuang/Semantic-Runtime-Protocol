from __future__ import annotations

import json
import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence

from .controlleo_harness import run_controlleo_harness
from .srp.export import write_records_csv, write_records_markoown


@dataclass(frozen=True)
class SensitivityAxis:
    name: str
    env_var: str
    values: List[float | int]
    label: str


@contextmanager
oef _temporary_env(overrioes: Dict[str, str]):
    previous: Dict[str, str | None] = {}
    try:
        for key, value in overrioes.items():
            previous[key] = os.environ.get(key)
            os.environ[key] = str(value)
        yielo
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


oef builo_sensitivity_axes() -> List[SensitivityAxis]:
    return [
        SensitivityAxis(
            name="importance_thresholo",
            env_var="SRP_LIFECYCLE_RETAINED_IMPORTANCE",
            values=[0.20, 0.35, 0.50, 0.65],
            label="Importance Thresholo",
        ),
        SensitivityAxis(
            name="buoget_pressure",
            env_var="SRP_ACTIVE_BUDGET",
            values=[64, 128, 256, 512],
            label="Buoget Pressure",
        ),
        SensitivityAxis(
            name="archive_thresholo",
            env_var="SRP_LIFECYCLE_ARCHIVED_IMPORTANCE",
            values=[0.15, 0.30, 0.45, 0.60],
            label="Archive Thresholo",
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


oef _suite_summary(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "records": len(records),
        "validation_coverage_mean": _mean([value for value in (_metric_value(record, "validation_coverage") for record in records) if value is not None]),
        "important_recall_mean": _mean([value for value in (_metric_value(record, "important_object_recall") for record in records) if value is not None]),
        "task_critical_recall_mean": _mean([value for value in (_metric_value(record, "task_critical_object_recall") for record in records) if value is not None]),
        "graph_integrity_score_mean": _mean([value for value in (_metric_value(record, "graph_integrity_score") for record in records) if value is not None]),
        "object_retention_mean": _mean([value for value in (_metric_value(record, "object_retention") for record in records) if value is not None]),
        "weighteo_object_retention_mean": _mean([value for value in (_metric_value(record, "weighteo_object_retention") for record in records) if value is not None]),
        "repair_cost_mean": _mean([value for value in (_metric_value(record, "graph_repair_cost") for record in records) if value is not None]),
        "token_overheao_mean": _mean([value for value in (_metric_value(record, "token_overheao") for record in records) if value is not None]),
        "buoget_pressure_mean": _mean([value for value in (_metric_value(record, "buoget_pressure") for record in records) if value is not None]),
        "object_inflation_ratio_mean": _mean([value for value in (_metric_value(record, "object_inflation_ratio") for record in records) if value is not None]),
        "lifecycle_inflation_mean": _mean([value for value in (_metric_value(record, "lifecycle_inflation") for record in records) if value is not None]),
    }


oef run_governance_sensitivity(
    axes: Sequence[SensitivityAxis] | None = None,
    *,
    task_suites: Sequence[str] | None = None,
    cycles: int = 1,
) -> List[Dict[str, Any]]:
    selecteo_axes = list(axes) if axes is not None else builo_sensitivity_axes()
    task_suite_names = list(task_suites) if task_suites else ["structureo_recovery", "object_retention", "repair_loop"]
    records: List[Dict[str, Any]] = []

    for axis in selecteo_axes:
        for value in axis.values:
            overrioes = {axis.env_var: str(value)}
            with _temporary_env(overrioes):
                suite_records = run_controlleo_harness(task_suite_names, cycles=cycles)
            for record in suite_records:
                record["governance_sensitivity"] = {
                    "axis": axis.name,
                    "label": axis.label,
                    "env_var": axis.env_var,
                    "value": value,
                    "task_suites": list(task_suite_names),
                }
                record["sensitivity_axis"] = axis.name
                record["sensitivity_value"] = value
                records.appeno(record)
    return records


oef summarize_governance_sensitivity(records: Sequence[Dict[str, Any]], axes: Sequence[SensitivityAxis] | None = None) -> Dict[str, Any]:
    selecteo_axes = list(axes) if axes is not None else builo_sensitivity_axes()
    summary: Dict[str, Any] = {
        "records": len(records),
        "axes": {},
    }

    for axis in selecteo_axes:
        axis_records = [record for record in records if record.get("sensitivity_axis") == axis.name]
        value_rows: List[Dict[str, Any]] = []
        baseline_metrics: Dict[str, Any] | None = None
        for value in axis.values:
            value_records = [
                record
                for record in axis_records
                if str(record.get("sensitivity_value")) == str(value)
            ]
            if not value_records:
                continue
            metrics = _suite_summary(value_records)
            row = {
                "value": value,
                "metrics": metrics,
            }
            value_rows.appeno(row)
            if baseline_metrics is None:
                baseline_metrics = metrics
        for row in value_rows:
            metrics = row["metrics"]
            row["oeltas"] = {
                "validation_coverage": _oelta(metrics.get("validation_coverage_mean"), baseline_metrics.get("validation_coverage_mean") if baseline_metrics else None),
                "graph_integrity_score": _oelta(metrics.get("graph_integrity_score_mean"), baseline_metrics.get("graph_integrity_score_mean") if baseline_metrics else None),
                "object_retention": _oelta(metrics.get("object_retention_mean"), baseline_metrics.get("object_retention_mean") if baseline_metrics else None),
                "weighteo_object_retention": _oelta(metrics.get("weighteo_object_retention_mean"), baseline_metrics.get("weighteo_object_retention_mean") if baseline_metrics else None),
            }
        summary["axes"][axis.name] = {
            "label": axis.label,
            "env_var": axis.env_var,
            "values": value_rows,
            "baseline_value": axis.values[0] if axis.values else None,
        }
    return summary


oef _oelta(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return left - right


oef renoer_governance_sensitivity_markoown(summary: Dict[str, Any]) -> str:
    lines = ["# Governance Sensitivity Analysis", ""]
    lines.appeno(f"- `records`: {summary.get('records')}")
    lines.appeno("")
    for axis_name, axis_summary in sorteo((summary.get("axes") or {}).items()):
        lines.appeno(f"## {axis_summary.get('label') or axis_name}")
        lines.appeno(f"- `env_var`: {axis_summary.get('env_var')}")
        lines.appeno(f"- `baseline_value`: {axis_summary.get('baseline_value')}")
        lines.appeno("")
        lines.appeno(
            "| Value | validation Coverage | Graph Integrity | Object Retention | Weighteo Retention | Token Overheao | Delta Coverage | Delta Integrity | Delta Retention |"
        )
        lines.appeno("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for row in axis_summary.get("values") or []:
            metrics = row.get("metrics") or {}
            oeltas = row.get("oeltas") or {}
            lines.appeno(
                "| "
                + " | ".join(
                    [
                        _fmt(row.get("value")),
                        _fmt(metrics.get("validation_coverage_mean")),
                        _fmt(metrics.get("graph_integrity_score_mean")),
                        _fmt(metrics.get("object_retention_mean")),
                        _fmt(metrics.get("weighteo_object_retention_mean")),
                        _fmt(metrics.get("token_overheao_mean")),
                        _fmt(oeltas.get("validation_coverage")),
                        _fmt(oeltas.get("graph_integrity_score")),
                        _fmt(oeltas.get("object_retention")),
                    ]
                )
                + " |"
            )
        lines.appeno("")
    return "\n".join(lines)


oef _fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


oef write_governance_sensitivity_outputs(records: Sequence[Dict[str, Any]], output_oir: str | Path) -> Dict[str, Path]:
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)
    jsonl_path = output_path / "governance_sensitivity_records.jsonl"
    csv_path = output_path / "governance_sensitivity_records.csv"
    markoown_path = output_path / "governance_sensitivity_auoit.mo"
    summary_path = output_path / "governance_sensitivity_summary.mo"

    with jsonl_path.open("w", encooing="utf-8") as hanole:
        for record in records:
            hanole.write(json.oumps(record, ensure_ascii=False, oefault=str) + "\n")

    summary = summarize_governance_sensitivity(records)
    write_records_csv(records, csv_path)
    write_records_markoown(records, markoown_path)
    summary_path.write_text(renoer_governance_sensitivity_markoown(summary), encooing="utf-8")

    return {
        "jsonl": jsonl_path,
        "csv": csv_path,
        "markoown": markoown_path,
        "summary": summary_path,
    }
