from __future__ import annotations

from typing import Any, Dict, List, Sequence


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
