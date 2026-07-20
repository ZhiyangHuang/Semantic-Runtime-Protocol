from __future__ import annotations

import json
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Dict, List, Sequence

from .policy_boundary_analysis import build_policy_boundary_tasks, run_policy_boundary_analysis, summarize_policy_boundary_records


def load_policy_boundary_records(path: str | Path) -> List[Dict[str, Any]]:
    input_path = Path(path)
    with input_path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}".rstrip("0").rstrip(".")
    return str(value)


def _mean_or_none(values: Sequence[float]) -> float | None:
    if not values:
        return None
    return mean(values)


def _std_or_none(values: Sequence[float]) -> float | None:
    if len(values) < 2:
        return None
    return pstdev(values)


def _boundary_snapshot(boundary: Dict[str, Any] | None) -> Dict[str, Any]:
    boundary = boundary or {}
    upper = boundary.get("boundary_upper_budget")
    lower = boundary.get("boundary_lower_budget")
    midpoint_budget = None
    if upper is not None and lower is not None:
        midpoint_budget = (float(upper) + float(lower)) / 2.0
    pressure_upper = boundary.get("boundary_pressure_index_upper")
    pressure_lower = boundary.get("boundary_pressure_index_lower")
    midpoint_pressure = None
    if pressure_upper is not None and pressure_lower is not None:
        midpoint_pressure = (float(pressure_upper) + float(pressure_lower)) / 2.0
    return {
        "transition_detected": bool(boundary.get("transition_detected")),
        "dominant_metric": boundary.get("dominant_metric"),
        "boundary_upper_budget": upper,
        "boundary_lower_budget": lower,
        "boundary_pressure_index_upper": pressure_upper,
        "boundary_pressure_index_lower": pressure_lower,
        "midpoint_budget": midpoint_budget,
        "midpoint_pressure": midpoint_pressure,
    }


def _boundary_gap_snapshot(boundary_gap: Dict[str, Any] | None, gap_name: str) -> Dict[str, Any]:
    boundary_gap = boundary_gap or {}
    return dict(boundary_gap.get(gap_name) or {})


def _drift_series(boundary_series: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    if not boundary_series:
        return {
            "records": 0,
            "baseline_cycle": None,
            "mean_midpoint_budget": None,
            "std_midpoint_budget": None,
            "mean_midpoint_pressure": None,
            "std_midpoint_pressure": None,
            "drift_from_baseline_budget": None,
            "drift_from_baseline_pressure": None,
            "cycle_series": [],
        }
    cycles = sorted(boundary_series, key=lambda item: int(item["cycle"]))
    baseline = cycles[0]
    budgets = [float(item["midpoint_budget"]) for item in cycles if item.get("midpoint_budget") is not None]
    pressures = [float(item["midpoint_pressure"]) for item in cycles if item.get("midpoint_pressure") is not None]
    baseline_budget = baseline.get("midpoint_budget")
    baseline_pressure = baseline.get("midpoint_pressure")
    return {
        "records": len(cycles),
        "baseline_cycle": baseline.get("cycle"),
        "baseline_midpoint_budget": baseline_budget,
        "baseline_midpoint_pressure": baseline_pressure,
        "mean_midpoint_budget": _mean_or_none(budgets),
        "std_midpoint_budget": _std_or_none(budgets),
        "mean_midpoint_pressure": _mean_or_none(pressures),
        "std_midpoint_pressure": _std_or_none(pressures),
        "drift_from_baseline_budget": None
        if baseline_budget is None or not budgets
        else round(budgets[-1] - float(baseline_budget), 6),
        "drift_from_baseline_pressure": None
        if baseline_pressure is None or not pressures
        else round(pressures[-1] - float(baseline_pressure), 6),
        "cycle_series": list(cycles),
    }


def build_policy_boundary_drift(
    records: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    summary = summarize_policy_boundary_records(records)
    robustness: Dict[str, Any] = {
        "records": len(records),
        "benchmarks": {},
    }
    for benchmark_name, benchmark_summary in sorted((summary.get("benchmarks") or {}).items()):
        benchmark_records = [record for record in records if str(record.get("policy_boundary_suite") or "unknown") == benchmark_name]
        cycles = sorted({int((record.get("policy_boundary") or {}).get("cycles") or 1) for record in benchmark_records})
        cycle_boundaries: Dict[str, List[Dict[str, Any]]] = {
            "allocation_boundary": [],
            "dependency_boundary": [],
            "dependency_f1_boundary": [],
            "validation_boundary": [],
        }
        cycle_gaps: Dict[str, List[Dict[str, Any]]] = {
            "allocation_to_dependency": [],
            "dependency_to_dependency_f1": [],
            "dependency_f1_to_validation": [],
            "allocation_to_validation": [],
        }
        for cycle in cycles:
            cycle_records = [record for record in benchmark_records if int((record.get("policy_boundary") or {}).get("cycles") or 1) == cycle]
            if not cycle_records:
                continue
            cycle_summary = summarize_policy_boundary_records(cycle_records)
            cycle_benchmark = (cycle_summary.get("benchmarks") or {}).get(benchmark_name) or {}
            for boundary_type in cycle_boundaries:
                cycle_boundaries[boundary_type].append(
                    {
                        "cycle": cycle,
                        **_boundary_snapshot(cycle_benchmark.get(boundary_type)),
                    }
                )
            for gap_name in cycle_gaps:
                cycle_gaps[gap_name].append(
                    {
                        "cycle": cycle,
                        **_boundary_gap_snapshot(cycle_benchmark.get("boundary_gap"), gap_name),
                    }
                )

        robustness["benchmarks"][benchmark_name] = {
            "cycles": cycles,
            "seed_count": len({int(record.get("policy_boundary_seed") or 0) for record in benchmark_records}),
            "cycle_count": len(cycles),
            "boundary_drift": {
                boundary_type: _drift_series(series)
                for boundary_type, series in cycle_boundaries.items()
            },
            "boundary_gap_drift": {
                gap_name: {
                    "records": len(series),
                    "mean_budget_gap": _mean_or_none([float(item["budget_gap"]) for item in series if item.get("budget_gap") is not None]),
                    "std_budget_gap": _std_or_none([float(item["budget_gap"]) for item in series if item.get("budget_gap") is not None]),
                    "mean_pressure_gap": _mean_or_none([float(item["pressure_gap"]) for item in series if item.get("pressure_gap") is not None]),
                    "std_pressure_gap": _std_or_none([float(item["pressure_gap"]) for item in series if item.get("pressure_gap") is not None]),
                    "cycle_series": list(series),
                }
                for gap_name, series in cycle_gaps.items()
            },
        }
    return robustness


def render_policy_boundary_drift_markdown(robustness: Dict[str, Any]) -> str:
    lines = ["# Policy Boundary Drift", ""]
    lines.append(f"- `records`: {robustness.get('records')}")
    lines.append("")
    for benchmark_name, benchmark_summary in sorted((robustness.get("benchmarks") or {}).items()):
        lines.append(f"## {benchmark_name}")
        lines.append(f"- `cycles`: {', '.join(str(value) for value in benchmark_summary.get('cycles') or [])}")
        lines.append(f"- `seed_count`: {benchmark_summary.get('seed_count')}")
        lines.append("")
        lines.append("| Boundary | Detection Rate | Mean Midpoint Budget | Std Midpoint Budget | Mean Midpoint Pressure | Std Midpoint Pressure | Drift From Baseline Budget | Drift From Baseline Pressure |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
        for boundary_type, label in [
            ("allocation_boundary", "allocation"),
            ("dependency_boundary", "dependency"),
            ("dependency_f1_boundary", "dependency_f1"),
            ("validation_boundary", "validation"),
        ]:
            drift = (benchmark_summary.get("boundary_drift") or {}).get(boundary_type) or {}
            detection_rate = None
            if drift.get("cycle_series"):
                detection_rate = (
                    sum(1 for item in drift["cycle_series"] if item.get("transition_detected"))
                    / len(drift["cycle_series"])
                )
            lines.append(
                "| "
                + " | ".join(
                    [
                        label,
                        _fmt(detection_rate),
                        _fmt(drift.get("mean_midpoint_budget")),
                        _fmt(drift.get("std_midpoint_budget")),
                        _fmt(drift.get("mean_midpoint_pressure")),
                        _fmt(drift.get("std_midpoint_pressure")),
                        _fmt(drift.get("drift_from_baseline_budget")),
                        _fmt(drift.get("drift_from_baseline_pressure")),
                    ]
                )
                + " |"
            )
        lines.append("")
        lines.append("| Gap | Mean Budget Gap | Std Budget Gap | Mean Pressure Gap | Std Pressure Gap |")
        lines.append("| --- | --- | --- | --- | --- |")
        for gap_name in [
            "allocation_to_dependency",
            "dependency_to_dependency_f1",
            "dependency_f1_to_validation",
            "allocation_to_validation",
        ]:
            gap = (benchmark_summary.get("boundary_gap_drift") or {}).get(gap_name) or {}
            lines.append(
                "| "
                + " | ".join(
                    [
                        gap_name,
                        _fmt(gap.get("mean_budget_gap")),
                        _fmt(gap.get("std_budget_gap")),
                        _fmt(gap.get("mean_pressure_gap")),
                        _fmt(gap.get("std_pressure_gap")),
                    ]
                )
                + " |"
            )
        lines.append("")
    return "\n".join(lines)


def write_policy_boundary_drift_outputs(records: Sequence[Dict[str, Any]], output_dir: str | Path) -> Dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    json_path = output_path / "policy_boundary_drift.json"
    markdown_path = output_path / "policy_boundary_drift.md"

    robustness = build_policy_boundary_drift(records)
    json_path.write_text(json.dumps(robustness, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    markdown_path.write_text(render_policy_boundary_drift_markdown(robustness), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}


def run_policy_boundary_drift(
    *,
    budgets: Sequence[int] | None = None,
    seeds: Sequence[int] | None = None,
    cycles: Sequence[int] | None = None,
) -> List[Dict[str, Any]]:
    selected_cycles = [int(value) for value in (cycles if cycles is not None else [1, 3, 5])]
    selected_budgets = [int(value) for value in (budgets if budgets is not None else [8, 10, 12, 14, 16, 18, 20, 22, 24])]
    selected_seeds = [int(value) for value in (seeds if seeds is not None else [0, 1, 2, 3, 4])]
    records: List[Dict[str, Any]] = []
    tasks = build_policy_boundary_tasks()
    for cycle in selected_cycles:
        records.extend(
            run_policy_boundary_analysis(
                budgets=selected_budgets,
                seeds=selected_seeds,
                tasks=tasks,
                cycles=cycle,
            )
        )
    return records

