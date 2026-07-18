from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Dict, Iterable, List, Sequence

from .policy_boundary_analysis import summarize_policy_boundary_records


@dataclass(frozen=True)
class BoundaryObservation:
    benchmark: str
    seed: int
    boundary_type: str
    transition_detected: bool
    boundary_upper_budget: int | None
    boundary_lower_budget: int | None
    boundary_pressure_index_upper: float | None
    boundary_pressure_index_lower: float | None

    @property
    def midpoint_budget(self) -> float | None:
        if self.boundary_upper_budget is None or self.boundary_lower_budget is None:
            return None
        return (float(self.boundary_upper_budget) + float(self.boundary_lower_budget)) / 2.0

    @property
    def midpoint_pressure(self) -> float | None:
        if self.boundary_pressure_index_upper is None or self.boundary_pressure_index_lower is None:
            return None
        return (float(self.boundary_pressure_index_upper) + float(self.boundary_pressure_index_lower)) / 2.0


def load_policy_boundary_records(path: str | Path) -> List[Dict[str, Any]]:
    input_path = Path(path)
    with input_path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _mean_or_none(values: Sequence[float]) -> float | None:
    if not values:
        return None
    return mean(values)


def _std_or_none(values: Sequence[float]) -> float | None:
    if len(values) < 2:
        return None
    return pstdev(values)


def _boundary_from_summary(benchmark_summary: Dict[str, Any], boundary_type: str) -> Dict[str, Any]:
    boundary = benchmark_summary.get(boundary_type) or {}
    return {
        "transition_detected": bool(boundary.get("transition_detected")),
        "boundary_upper_budget": boundary.get("boundary_upper_budget"),
        "boundary_lower_budget": boundary.get("boundary_lower_budget"),
        "boundary_pressure_index_upper": boundary.get("boundary_pressure_index_upper"),
        "boundary_pressure_index_lower": boundary.get("boundary_pressure_index_lower"),
    }


def _boundary_gap_from_summary(benchmark_summary: Dict[str, Any], gap_name: str) -> Dict[str, Any]:
    boundary_gap = benchmark_summary.get("boundary_gap") or {}
    return dict(boundary_gap.get(gap_name) or {})


def _make_observation(benchmark: str, seed: int, boundary_type: str, benchmark_summary: Dict[str, Any]) -> BoundaryObservation:
    boundary = _boundary_from_summary(benchmark_summary, boundary_type)
    return BoundaryObservation(
        benchmark=benchmark,
        seed=seed,
        boundary_type=boundary_type,
        transition_detected=bool(boundary["transition_detected"]),
        boundary_upper_budget=boundary["boundary_upper_budget"],
        boundary_lower_budget=boundary["boundary_lower_budget"],
        boundary_pressure_index_upper=boundary["boundary_pressure_index_upper"],
        boundary_pressure_index_lower=boundary["boundary_pressure_index_lower"],
    )


def _aggregate_boundary_observations(observations: Sequence[BoundaryObservation]) -> Dict[str, Any]:
    detected = [item for item in observations if item.transition_detected]
    midpoint_budgets = [item.midpoint_budget for item in detected if item.midpoint_budget is not None]
    midpoint_pressures = [item.midpoint_pressure for item in detected if item.midpoint_pressure is not None]
    return {
        "records": len(observations),
        "transition_detected_count": len(detected),
        "transition_detection_rate": (len(detected) / len(observations)) if observations else None,
        "mean_midpoint_budget": _mean_or_none([float(value) for value in midpoint_budgets if value is not None]),
        "std_midpoint_budget": _std_or_none([float(value) for value in midpoint_budgets if value is not None]),
        "mean_midpoint_pressure": _mean_or_none([float(value) for value in midpoint_pressures if value is not None]),
        "std_midpoint_pressure": _std_or_none([float(value) for value in midpoint_pressures if value is not None]),
        "seed_boundaries": [
            {
                "seed": item.seed,
                "transition_detected": item.transition_detected,
                "boundary_upper_budget": item.boundary_upper_budget,
                "boundary_lower_budget": item.boundary_lower_budget,
                "boundary_pressure_index_upper": item.boundary_pressure_index_upper,
                "boundary_pressure_index_lower": item.boundary_pressure_index_lower,
                "midpoint_budget": item.midpoint_budget,
                "midpoint_pressure": item.midpoint_pressure,
            }
            for item in observations
        ],
    }


def _aggregate_gap_observations(gaps: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    budget_gaps = [float(item["budget_gap"]) for item in gaps if item.get("budget_gap") is not None]
    pressure_gaps = [float(item["pressure_gap"]) for item in gaps if item.get("pressure_gap") is not None]
    return {
        "records": len(gaps),
        "mean_budget_gap": _mean_or_none(budget_gaps),
        "std_budget_gap": _std_or_none(budget_gaps),
        "mean_pressure_gap": _mean_or_none(pressure_gaps),
        "std_pressure_gap": _std_or_none(pressure_gaps),
        "observations": list(gaps),
    }


def build_policy_boundary_robustness(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    summary = summarize_policy_boundary_records(records)
    benchmark_names = sorted((summary.get("benchmarks") or {}).keys())
    robustness: Dict[str, Any] = {
        "records": len(records),
        "benchmarks": {},
    }
    boundary_types = [
        "allocation_boundary",
        "dependency_boundary",
        "dependency_f1_boundary",
        "validation_boundary",
    ]
    gap_types = [
        "allocation_to_dependency",
        "dependency_to_dependency_f1",
        "dependency_f1_to_validation",
        "allocation_to_validation",
    ]

    for benchmark_name in benchmark_names:
        benchmark_records = [record for record in records if str(record.get("policy_boundary_suite") or "unknown") == benchmark_name]
        seed_values = sorted({int(record.get("policy_boundary_seed") or 0) for record in benchmark_records})
        observations: Dict[str, List[BoundaryObservation]] = {boundary_type: [] for boundary_type in boundary_types}
        gaps: Dict[str, List[Dict[str, Any]]] = {gap_type: [] for gap_type in gap_types}

        for seed in seed_values:
            seed_records = [record for record in benchmark_records if int(record.get("policy_boundary_seed") or 0) == seed]
            if not seed_records:
                continue
            seed_summary = summarize_policy_boundary_records(seed_records)
            benchmark_summary = (seed_summary.get("benchmarks") or {}).get(benchmark_name) or {}
            for boundary_type in boundary_types:
                observations[boundary_type].append(_make_observation(benchmark_name, seed, boundary_type, benchmark_summary))
            for gap_type in gap_types:
                gaps[gap_type].append(_boundary_gap_from_summary(benchmark_summary, gap_type))

        benchmark_result = {
            "seeds": seed_values,
            "seed_count": len(seed_values),
            "boundary_stability": {
                boundary_type: _aggregate_boundary_observations(observations[boundary_type])
                for boundary_type in boundary_types
            },
            "boundary_gap_stability": {
                gap_type: _aggregate_gap_observations(gaps[gap_type])
                for gap_type in gap_types
            },
        }
        robustness["benchmarks"][benchmark_name] = benchmark_result
    return robustness


def render_policy_boundary_robustness_markdown(robustness: Dict[str, Any]) -> str:
    lines = ["# Policy Boundary Robustness", ""]
    lines.append(f"- `records`: {robustness.get('records')}")
    lines.append("")
    for benchmark_name, benchmark_summary in sorted((robustness.get("benchmarks") or {}).items()):
        lines.append(f"## {benchmark_name}")
        lines.append(f"- `seed_count`: {benchmark_summary.get('seed_count')}")
        lines.append("")
        lines.append("| Boundary | Detection Rate | Mean Midpoint Budget | Std Midpoint Budget | Mean Midpoint Pressure | Std Midpoint Pressure |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for boundary_type, label in [
            ("allocation_boundary", "allocation"),
            ("dependency_boundary", "dependency"),
            ("dependency_f1_boundary", "dependency_f1"),
            ("validation_boundary", "validation"),
        ]:
            boundary = (benchmark_summary.get("boundary_stability") or {}).get(boundary_type) or {}
            lines.append(
                "| "
                + " | ".join(
                    [
                        label,
                        _fmt(boundary.get("transition_detection_rate")),
                        _fmt(boundary.get("mean_midpoint_budget")),
                        _fmt(boundary.get("std_midpoint_budget")),
                        _fmt(boundary.get("mean_midpoint_pressure")),
                        _fmt(boundary.get("std_midpoint_pressure")),
                    ]
                )
                + " |"
            )
        lines.append("")
        lines.append("| Gap | Mean Budget Gap | Std Budget Gap | Mean Pressure Gap | Std Pressure Gap |")
        lines.append("| --- | --- | --- | --- | --- |")
        for gap_type in [
            "allocation_to_dependency",
            "dependency_to_dependency_f1",
            "dependency_f1_to_validation",
            "allocation_to_validation",
        ]:
            gap = (benchmark_summary.get("boundary_gap_stability") or {}).get(gap_type) or {}
            lines.append(
                "| "
                + " | ".join(
                    [
                        gap_type,
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


def _fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}".rstrip("0").rstrip(".")
    return str(value)


def write_policy_boundary_robustness_outputs(records: Sequence[Dict[str, Any]], output_dir: str | Path) -> Dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    json_path = output_path / "policy_boundary_robustness.json"
    markdown_path = output_path / "policy_boundary_robustness.md"

    robustness = build_policy_boundary_robustness(records)
    json_path.write_text(json.dumps(robustness, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    markdown_path.write_text(render_policy_boundary_robustness_markdown(robustness), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}

