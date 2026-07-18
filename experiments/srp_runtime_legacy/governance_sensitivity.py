from __future__ import annotations

import json
import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence

from .controlled_harness import run_controlled_harness
from .srp.export import write_records_csv, write_records_markdown


@dataclass(frozen=True)
class SensitivityAxis:
    name: str
    env_var: str
    values: List[float | int]
    label: str


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


def build_sensitivity_axes() -> List[SensitivityAxis]:
    return [
        SensitivityAxis(
            name="importance_threshold",
            env_var="SRP_LIFECYCLE_RETAINED_IMPORTANCE",
            values=[0.20, 0.35, 0.50, 0.65],
            label="Importance Threshold",
        ),
        SensitivityAxis(
            name="budget_pressure",
            env_var="SRP_ACTIVE_BUDGET",
            values=[64, 128, 256, 512],
            label="Budget Pressure",
        ),
        SensitivityAxis(
            name="archive_threshold",
            env_var="SRP_LIFECYCLE_ARCHIVED_IMPORTANCE",
            values=[0.15, 0.30, 0.45, 0.60],
            label="Archive Threshold",
        ),
    ]


def _metric_value(record: Dict[str, Any], key: str) -> float | None:
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


def _mean(values: Sequence[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _suite_summary(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "records": len(records),
        "validation_coverage_mean": _mean([value for value in (_metric_value(record, "validation_coverage") for record in records) if value is not None]),
        "important_recall_mean": _mean([value for value in (_metric_value(record, "important_object_recall") for record in records) if value is not None]),
        "task_critical_recall_mean": _mean([value for value in (_metric_value(record, "task_critical_object_recall") for record in records) if value is not None]),
        "graph_integrity_score_mean": _mean([value for value in (_metric_value(record, "graph_integrity_score") for record in records) if value is not None]),
        "object_retention_mean": _mean([value for value in (_metric_value(record, "object_retention") for record in records) if value is not None]),
        "weighted_object_retention_mean": _mean([value for value in (_metric_value(record, "weighted_object_retention") for record in records) if value is not None]),
        "repair_cost_mean": _mean([value for value in (_metric_value(record, "graph_repair_cost") for record in records) if value is not None]),
        "token_overhead_mean": _mean([value for value in (_metric_value(record, "token_overhead") for record in records) if value is not None]),
        "budget_pressure_mean": _mean([value for value in (_metric_value(record, "budget_pressure") for record in records) if value is not None]),
        "object_inflation_ratio_mean": _mean([value for value in (_metric_value(record, "object_inflation_ratio") for record in records) if value is not None]),
        "lifecycle_inflation_mean": _mean([value for value in (_metric_value(record, "lifecycle_inflation") for record in records) if value is not None]),
    }


def run_governance_sensitivity(
    axes: Sequence[SensitivityAxis] | None = None,
    *,
    task_suites: Sequence[str] | None = None,
    cycles: int = 1,
) -> List[Dict[str, Any]]:
    selected_axes = list(axes) if axes is not None else build_sensitivity_axes()
    task_suite_names = list(task_suites) if task_suites else ["structured_recovery", "object_retention", "repair_loop"]
    records: List[Dict[str, Any]] = []

    for axis in selected_axes:
        for value in axis.values:
            overrides = {axis.env_var: str(value)}
            with _temporary_env(overrides):
                suite_records = run_controlled_harness(task_suite_names, cycles=cycles)
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
                records.append(record)
    return records


def summarize_governance_sensitivity(records: Sequence[Dict[str, Any]], axes: Sequence[SensitivityAxis] | None = None) -> Dict[str, Any]:
    selected_axes = list(axes) if axes is not None else build_sensitivity_axes()
    summary: Dict[str, Any] = {
        "records": len(records),
        "axes": {},
    }

    for axis in selected_axes:
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
            value_rows.append(row)
            if baseline_metrics is None:
                baseline_metrics = metrics
        for row in value_rows:
            metrics = row["metrics"]
            row["deltas"] = {
                "validation_coverage": _delta(metrics.get("validation_coverage_mean"), baseline_metrics.get("validation_coverage_mean") if baseline_metrics else None),
                "graph_integrity_score": _delta(metrics.get("graph_integrity_score_mean"), baseline_metrics.get("graph_integrity_score_mean") if baseline_metrics else None),
                "object_retention": _delta(metrics.get("object_retention_mean"), baseline_metrics.get("object_retention_mean") if baseline_metrics else None),
                "weighted_object_retention": _delta(metrics.get("weighted_object_retention_mean"), baseline_metrics.get("weighted_object_retention_mean") if baseline_metrics else None),
            }
        summary["axes"][axis.name] = {
            "label": axis.label,
            "env_var": axis.env_var,
            "values": value_rows,
            "baseline_value": axis.values[0] if axis.values else None,
        }
    return summary


def _delta(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return left - right


def render_governance_sensitivity_markdown(summary: Dict[str, Any]) -> str:
    lines = ["# Governance Sensitivity Analysis", ""]
    lines.append(f"- `records`: {summary.get('records')}")
    lines.append("")
    for axis_name, axis_summary in sorted((summary.get("axes") or {}).items()):
        lines.append(f"## {axis_summary.get('label') or axis_name}")
        lines.append(f"- `env_var`: {axis_summary.get('env_var')}")
        lines.append(f"- `baseline_value`: {axis_summary.get('baseline_value')}")
        lines.append("")
        lines.append(
            "| Value | Validation Coverage | Graph Integrity | Object Retention | Weighted Retention | Token Overhead | Delta Coverage | Delta Integrity | Delta Retention |"
        )
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for row in axis_summary.get("values") or []:
            metrics = row.get("metrics") or {}
            deltas = row.get("deltas") or {}
            lines.append(
                "| "
                + " | ".join(
                    [
                        _fmt(row.get("value")),
                        _fmt(metrics.get("validation_coverage_mean")),
                        _fmt(metrics.get("graph_integrity_score_mean")),
                        _fmt(metrics.get("object_retention_mean")),
                        _fmt(metrics.get("weighted_object_retention_mean")),
                        _fmt(metrics.get("token_overhead_mean")),
                        _fmt(deltas.get("validation_coverage")),
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
        return f"{value:.6f}"
    return str(value)


def write_governance_sensitivity_outputs(records: Sequence[Dict[str, Any]], output_dir: str | Path) -> Dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_path / "governance_sensitivity_records.jsonl"
    csv_path = output_path / "governance_sensitivity_records.csv"
    markdown_path = output_path / "governance_sensitivity_audit.md"
    summary_path = output_path / "governance_sensitivity_summary.md"

    with jsonl_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    summary = summarize_governance_sensitivity(records)
    write_records_csv(records, csv_path)
    write_records_markdown(records, markdown_path)
    summary_path.write_text(render_governance_sensitivity_markdown(summary), encoding="utf-8")

    return {
        "jsonl": jsonl_path,
        "csv": csv_path,
        "markdown": markdown_path,
        "summary": summary_path,
    }
