from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple


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


def _suite_metrics(records: Sequence[Dict[str, Any]]) -> Dict[str, float | None]:
    return {
        "validation_coverage": _mean([value for value in (_metric_value(record, "validation_coverage") for record in records) if value is not None]),
        "graph_integrity_score": _mean([value for value in (_metric_value(record, "graph_integrity_score") for record in records) if value is not None]),
        "object_retention": _mean([value for value in (_metric_value(record, "object_retention") for record in records) if value is not None]),
        "weighted_object_retention": _mean([value for value in (_metric_value(record, "weighted_object_retention") for record in records) if value is not None]),
        "repair_cost": _mean([value for value in (_metric_value(record, "graph_repair_cost") for record in records) if value is not None]),
        "token_overhead": _mean([value for value in (_metric_value(record, "token_overhead") for record in records) if value is not None]),
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


def _delta(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return right - left


def load_policy_intervention_records(path: str | Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def _summarize_policy_suites(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "records": len(records),
        "policy_suites": {},
        "baseline_suite": None,
        "best_by_validation_coverage": None,
        "best_by_graph_integrity": None,
        "best_by_object_retention": None,
    }
    suite_names = sorted({str(record.get("policy_suite") or "unknown") for record in records})
    baseline_suite = "baseline" if "baseline" in suite_names else (suite_names[0] if suite_names else None)
    summary["baseline_suite"] = baseline_suite
    baseline_records = [record for record in records if str(record.get("policy_suite") or "unknown") == baseline_suite] if baseline_suite else []

    for suite_name in suite_names:
        suite_records = [record for record in records if str(record.get("policy_suite") or "unknown") == suite_name]
        if not suite_records:
            continue
        summary["policy_suites"][suite_name] = {
            "records": len(suite_records),
            "validation_passed_rate": _mean([_metric_value(record, "validation_passed") or 0.0 for record in suite_records]) if suite_records else None,
            "validation_coverage_mean": _suite_metrics(suite_records).get("validation_coverage"),
            "important_recall_mean": _mean([value for value in (_metric_value(record, "important_object_recall") for record in suite_records) if value is not None]),
            "task_critical_recall_mean": _mean([value for value in (_metric_value(record, "task_critical_object_recall") for record in suite_records) if value is not None]),
            "graph_integrity_score_mean": _suite_metrics(suite_records).get("graph_integrity_score"),
            "repair_cost_mean": _suite_metrics(suite_records).get("repair_cost"),
            "object_inflation_ratio_mean": _mean([value for value in (_metric_value(record, "object_inflation_ratio") for record in suite_records) if value is not None]),
            "lifecycle_inflation_mean": _mean([value for value in (_metric_value(record, "lifecycle_inflation") for record in suite_records) if value is not None]),
            "object_retention_mean": _suite_metrics(suite_records).get("object_retention"),
            "weighted_object_retention_mean": _suite_metrics(suite_records).get("weighted_object_retention"),
            "lost_important_object_count_mean": _mean([value for value in (_metric_value(record, "lost_important_object_count") for record in suite_records) if value is not None]),
            "token_overhead_mean": _suite_metrics(suite_records).get("token_overhead"),
            "budget_pressure_mean": _mean([value for value in (_metric_value(record, "budget_pressure") for record in suite_records) if value is not None]),
        }
        if baseline_records:
            baseline_coverage = _suite_metrics(baseline_records).get("validation_coverage")
            baseline_repair_cost = _suite_metrics(baseline_records).get("repair_cost")
            baseline_integrity = _suite_metrics(baseline_records).get("graph_integrity_score")
            baseline_important = _mean([value for value in (_metric_value(record, "important_object_recall") for record in baseline_records) if value is not None])
            baseline_object_retention = _suite_metrics(baseline_records).get("object_retention")
            suite_summary = summary["policy_suites"][suite_name]
            suite_summary["delta_validation_coverage"] = (
                None
                if baseline_coverage is None or suite_summary["validation_coverage_mean"] is None
                else suite_summary["validation_coverage_mean"] - baseline_coverage
            )
            suite_summary["delta_repair_cost"] = (
                None
                if baseline_repair_cost is None or suite_summary["repair_cost_mean"] is None
                else suite_summary["repair_cost_mean"] - baseline_repair_cost
            )
            suite_summary["delta_graph_integrity_score"] = (
                None
                if baseline_integrity is None or suite_summary["graph_integrity_score_mean"] is None
                else suite_summary["graph_integrity_score_mean"] - baseline_integrity
            )
            suite_summary["delta_important_recall"] = (
                None
                if baseline_important is None or suite_summary["important_recall_mean"] is None
                else suite_summary["important_recall_mean"] - baseline_important
            )
            suite_summary["delta_object_retention"] = (
                None
                if baseline_object_retention is None or suite_summary["object_retention_mean"] is None
                else suite_summary["object_retention_mean"] - baseline_object_retention
            )

    def _best(key: str, prefer_higher: bool = True) -> str | None:
        candidates: List[tuple[float, str]] = []
        for suite_name, suite_summary in (summary.get("policy_suites") or {}).items():
            value = suite_summary.get(key)
            if value is None:
                continue
            try:
                candidates.append((float(value), suite_name))
            except (TypeError, ValueError):
                continue
        if not candidates:
            return None
        candidates.sort(reverse=prefer_higher)
        return candidates[0][1]

    summary["best_by_validation_coverage"] = _best("validation_coverage_mean", prefer_higher=True)
    summary["best_by_graph_integrity"] = _best("graph_integrity_score_mean", prefer_higher=True)
    summary["best_by_object_retention"] = _best("object_retention_mean", prefer_higher=True)
    return summary


def summarize_policy_pareto(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    policy_summary = _summarize_policy_suites(records)
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


def _fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


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


def write_policy_pareto_outputs(records: Sequence[Dict[str, Any]], output_dir: str | Path) -> Dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    summary = summarize_policy_pareto(records)
    json_path = output_path / "pareto_front.json"
    markdown_path = output_path / "pareto_front.md"

    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    markdown_path.write_text(render_policy_pareto_markdown(summary), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}
