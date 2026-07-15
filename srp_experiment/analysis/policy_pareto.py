from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from ..policy_intervention_harness import summarize_policy_intervention_records


def _mean(values: Sequence[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _metric(record: Dict[str, Any], key: str) -> float | None:
    value = record.get(key)
    if value is None:
        value = (record.get("experiment_result") or {}).get("metrics", {}).get(key)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_policy_intervention_records(path: str | Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def _suite_metrics(records: Sequence[Dict[str, Any]]) -> Dict[str, float | None]:
    return {
        "validation_coverage": _mean([value for value in (_metric(record, "validation_coverage") for record in records) if value is not None]),
        "graph_integrity_score": _mean([value for value in (_metric(record, "graph_integrity_score") for record in records) if value is not None]),
        "object_retention": _mean([value for value in (_metric(record, "object_retention") for record in records) if value is not None]),
        "weighted_object_retention": _mean([value for value in (_metric(record, "weighted_object_retention") for record in records) if value is not None]),
        "repair_cost": _mean([value for value in (_metric(record, "graph_repair_cost") for record in records) if value is not None]),
        "token_overhead": _mean([value for value in (_metric(record, "token_overhead") for record in records) if value is not None]),
    }


def _dominates(left: Dict[str, float | None], right: Dict[str, float | None]) -> bool:
    maximize = ["validation_coverage", "graph_integrity_score", "object_retention", "weighted_object_retention"]
    minimize = ["repair_cost", "token_overhead"]

    better_or_equal_all = True
    strictly_better = False

    for key in maximize:
        l_val = left.get(key)
        r_val = right.get(key)
        if l_val is None or r_val is None:
            return False
        if l_val < r_val:
            better_or_equal_all = False
            break
        if l_val > r_val:
            strictly_better = True

    if not better_or_equal_all:
        return False

    for key in minimize:
        l_val = left.get(key)
        r_val = right.get(key)
        if l_val is None or r_val is None:
            return False
        if l_val > r_val:
            better_or_equal_all = False
            break
        if l_val < r_val:
            strictly_better = True

    return better_or_equal_all and strictly_better


def summarize_policy_pareto(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    policy_summary = summarize_policy_intervention_records(records)
    suites = policy_summary.get("policy_suites") or {}
    suite_metrics = {
        suite_name: {
            "records": suite_summary.get("records"),
            "metrics": _suite_metrics([record for record in records if str(record.get("policy_suite") or "unknown") == suite_name]),
            "overrides": (next((record.get("policy_intervention", {}).get("overrides") for record in records if str(record.get("policy_suite") or "unknown") == suite_name), {}) or {}),
        }
        for suite_name, suite_summary in suites.items()
    }

    dominated_by: Dict[str, List[str]] = {suite_name: [] for suite_name in suite_metrics}
    dominates: Dict[str, List[str]] = {suite_name: [] for suite_name in suite_metrics}
    front: List[str] = []

    suite_names = list(suite_metrics.keys())
    for left_name in suite_names:
        left_metrics = suite_metrics[left_name]["metrics"]
        for right_name in suite_names:
            if left_name == right_name:
                continue
            right_metrics = suite_metrics[right_name]["metrics"]
            if _dominates(left_metrics, right_metrics):
                dominates[left_name].append(right_name)
            elif _dominates(right_metrics, left_metrics):
                dominated_by[left_name].append(right_name)

    for suite_name in suite_names:
        if not dominated_by[suite_name]:
            front.append(suite_name)

    tradeoff_pairs: List[Dict[str, Any]] = []
    ordered = sorted(suite_names)
    for i, left_name in enumerate(ordered):
        left_metrics = suite_metrics[left_name]["metrics"]
        for right_name in ordered[i + 1 :]:
            right_metrics = suite_metrics[right_name]["metrics"]
            tradeoff_pairs.append(
                {
                    "left": left_name,
                    "right": right_name,
                    "coverage_delta": _delta(left_metrics.get("validation_coverage"), right_metrics.get("validation_coverage")),
                    "integrity_delta": _delta(left_metrics.get("graph_integrity_score"), right_metrics.get("graph_integrity_score")),
                    "retention_delta": _delta(left_metrics.get("object_retention"), right_metrics.get("object_retention")),
                    "repair_cost_delta": _delta(right_metrics.get("repair_cost"), left_metrics.get("repair_cost")),
                }
            )

    return {
        "records": len(records),
        "policy_suites": suite_metrics,
        "pareto_front": sorted(front),
        "dominates": dominates,
        "dominated_by": dominated_by,
        "tradeoff_pairs": tradeoff_pairs,
        "baseline_suite": policy_summary.get("baseline_suite"),
        "policy_summary": policy_summary,
    }


def _delta(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return right - left


def render_policy_pareto_markdown(summary: Dict[str, Any]) -> str:
    lines = ["# Policy Pareto Analysis", ""]
    lines.append(f"- `records`: {summary.get('records')}")
    lines.append(f"- `baseline_suite`: {summary.get('baseline_suite')}")
    lines.append(f"- `pareto_front`: {summary.get('pareto_front')}")
    lines.append("")

    lines.append("## Policy Suites")
    lines.append(
        "| Suite | Validation Coverage | Graph Integrity | Object Retention | Weighted Retention | Repair Cost | Token Overhead | Dominated By | Dominates |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for suite_name, suite_info in sorted((summary.get("policy_suites") or {}).items()):
        metrics = suite_info.get("metrics") or {}
        lines.append(
            "| "
            + " | ".join(
                [
                    str(suite_name),
                    _fmt(metrics.get("validation_coverage")),
                    _fmt(metrics.get("graph_integrity_score")),
                    _fmt(metrics.get("object_retention")),
                    _fmt(metrics.get("weighted_object_retention")),
                    _fmt(metrics.get("repair_cost")),
                    _fmt(metrics.get("token_overhead")),
                    str((summary.get("dominated_by") or {}).get(suite_name)),
                    str((summary.get("dominates") or {}).get(suite_name)),
                ]
            )
            + " |"
        )
    lines.append("")

    lines.append("## Tradeoff Pairs")
    lines.append("| Left | Right | Coverage Delta | Integrity Delta | Retention Delta | Repair Cost Delta |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for pair in summary.get("tradeoff_pairs") or []:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(pair.get("left")),
                    str(pair.get("right")),
                    _fmt(pair.get("coverage_delta")),
                    _fmt(pair.get("integrity_delta")),
                    _fmt(pair.get("retention_delta")),
                    _fmt(pair.get("repair_cost_delta")),
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


def write_policy_pareto_outputs(records: Sequence[Dict[str, Any]], output_dir: str | Path) -> Dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    summary = summarize_policy_pareto(records)
    json_path = output_path / "pareto_front.json"
    markdown_path = output_path / "pareto_front.md"

    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    markdown_path.write_text(render_policy_pareto_markdown(summary), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}
