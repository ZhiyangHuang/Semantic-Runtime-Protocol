from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Sequence

from .policy_trace import build_policy_trace


def _mean(values: Sequence[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def load_policy_attribution_records(path: str | Path) -> List[Dict[str, Any]]:
    output: List[Dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            output.append(json.loads(line))
    return output


def summarize_policy_attribution(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    traces = [build_policy_trace(record) for record in records]
    object_traces = [entry for trace in traces for entry in trace.get("traces") or []]
    summary: Dict[str, Any] = {
        "records": len(records),
        "records_with_traces": len(traces),
        "traces": traces,
        "scenarios": {},
        "root_cause": {},
        "reason_counts": defaultdict(int),
    }

    for entry in object_traces:
        reason = entry.get("reason")
        if reason is not None:
            summary["reason_counts"][reason] += 1

    for scenario in sorted({str(trace.get("compression_scenario") or "unknown") for trace in traces}):
        scenario_traces = [trace for trace in traces if str(trace.get("compression_scenario") or "unknown") == scenario]
        if not scenario_traces:
            continue
        scenario_objects = [entry for trace in scenario_traces for entry in trace.get("traces") or []]
        summary["scenarios"][scenario] = {
            "records": len(scenario_traces),
            "dominant_policy_reason": _most_common([entry.get("reason") for entry in scenario_objects]),
            "mean_importance_score": _mean([float(entry.get("importance_score") or 0.0) for entry in scenario_objects]) if scenario_objects else None,
            "mean_retention_margin": _mean([float(entry.get("margins", {}).get("retention_margin") or 0.0) for entry in scenario_objects]) if scenario_objects else None,
            "mean_archive_margin": _mean([float(entry.get("margins", {}).get("archive_margin") or 0.0) for entry in scenario_objects]) if scenario_objects else None,
            "mean_verification_margin": _mean([float(entry.get("margins", {}).get("verification_margin") or 0.0) for entry in scenario_objects]) if scenario_objects else None,
            "budget_pressure": _mean([float(trace.get("summary", {}).get("budget_pressure") or 0.0) for trace in scenario_traces]),
        }

    summary["reason_counts"] = dict(summary["reason_counts"])
    summary["root_cause"] = {
        "dominant_policy_reason": _most_common([entry.get("reason") for entry in object_traces]),
        "reason_counts": dict(summary["reason_counts"]),
        "mean_importance_score": _mean([float(entry.get("importance_score") or 0.0) for entry in object_traces]) if object_traces else None,
        "mean_retention_margin": _mean([float(entry.get("margins", {}).get("retention_margin") or 0.0) for entry in object_traces]) if object_traces else None,
        "mean_archive_margin": _mean([float(entry.get("margins", {}).get("archive_margin") or 0.0) for entry in object_traces]) if object_traces else None,
        "mean_verification_margin": _mean([float(entry.get("margins", {}).get("verification_margin") or 0.0) for entry in object_traces]) if object_traces else None,
        "budget_pressure": _mean([float(trace.get("summary", {}).get("budget_pressure") or 0.0) for trace in traces]),
        "policy": traces[0].get("policy") if traces else {},
    }
    return summary


def _most_common(values: Sequence[Any]) -> Any:
    counts: Dict[Any, int] = {}
    for value in values:
        if value is None:
            continue
        counts[value] = counts.get(value, 0) + 1
    if not counts:
        return None
    return max(counts.items(), key=lambda item: (item[1], str(item[0])))[0]


def render_policy_attribution_markdown(summary: Dict[str, Any]) -> str:
    lines = ["# Policy Attribution", ""]
    lines.append(f"- `records`: {summary.get('records')}")
    lines.append(f"- `records_with_traces`: {summary.get('records_with_traces')}")
    lines.append("")

    lines.append("## Root Cause")
    root = summary.get("root_cause") or {}
    if root:
        for key, value in root.items():
            lines.append(f"- `{key}`: {value}")
    else:
        lines.append("_No root-cause data available._")
    lines.append("")

    lines.append("## Scenario Summary")
    rows = []
    for scenario, scenario_summary in sorted((summary.get("scenarios") or {}).items()):
        rows.append(
            [
                scenario,
                scenario_summary.get("records"),
                scenario_summary.get("dominant_policy_reason"),
                scenario_summary.get("mean_importance_score"),
                scenario_summary.get("mean_retention_margin"),
                scenario_summary.get("mean_archive_margin"),
                scenario_summary.get("mean_verification_margin"),
                scenario_summary.get("budget_pressure"),
            ]
        )
    if rows:
        lines.extend(
            [
                "| Scenario | Records | Dominant Policy Reason | Mean Importance Score | Mean Retention Margin | Mean Archive Margin | Mean Verification Margin | Budget Pressure |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for row in rows:
            lines.append("| " + " | ".join("" if value is None else str(value) for value in row) + " |")
    else:
        lines.append("_No scenario data available._")
    lines.append("")

    lines.append("## Reason Counts")
    lines.append("| Reason | Count |")
    lines.append("| --- | --- |")
    for reason, count in sorted((summary.get("reason_counts") or {}).items()):
        lines.append(f"| {reason} | {count} |")
    lines.append("")

    lines.append("## Policy Profile")
    policy = root.get("policy") or {}
    if policy:
        for key, value in policy.items():
            lines.append(f"- `{key}`: {value}")
    else:
        lines.append("_No policy profile available._")
    lines.append("")

    lines.append("## Example Objects")
    traces = sorted(
        summary.get("traces") or [],
        key=lambda item: (
            float(item.get("summary", {}).get("budget_pressure") or 0.0),
            str(item.get("compression_scenario") or ""),
        ),
    )
    for trace in traces[:8]:
        lines.append(f"### {trace.get('compression_scenario')}")
        lines.append(f"- `budget_pressure`: {trace.get('summary', {}).get('budget_pressure')}")
        lines.append(f"- `compression_ratio`: {trace.get('summary', {}).get('compression_ratio')}")
        lines.append(f"- `policy`: {trace.get('policy')}")
        lines.append("")
    return "\n".join(lines)


def write_policy_attribution_outputs(records: Sequence[Dict[str, Any]], output_dir: str | Path) -> Dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    summary = summarize_policy_attribution(records)
    json_path = output_path / "policy_attribution.json"
    markdown_path = output_path / "policy_attribution.md"
    trace_path = output_path / "policy_trace.json"
    root_path = output_path / "policy_root_cause.md"

    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    markdown_path.write_text(render_policy_attribution_markdown(summary), encoding="utf-8")
    trace_path.write_text(json.dumps(summary.get("traces") or [], ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    root_markdown = ["# Policy Root Cause", ""]
    root = summary.get("root_cause") or {}
    if root:
        for key, value in root.items():
            root_markdown.append(f"- `{key}`: {value}")
    else:
        root_markdown.append("_No root-cause data available._")
    root_path.write_text("\n".join(root_markdown), encoding="utf-8")
    return {
        "json": json_path,
        "markdown": markdown_path,
        "trace": trace_path,
        "root_cause_markdown": root_path,
    }
