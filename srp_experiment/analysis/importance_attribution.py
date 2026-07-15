from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Sequence

from .importance_trace import build_importance_trace


def _metric_average(records: Sequence[Dict[str, Any]], key: str) -> float | None:
    values: List[float] = []
    for record in records:
        value = record.get(key)
        if value is not None:
            values.append(float(value))
    if not values:
        return None
    return sum(values) / len(values)


def _mean(values: Sequence[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _mode(values: Sequence[Any]) -> Any:
    counts: Dict[Any, int] = {}
    for value in values:
        if value is None:
            continue
        counts[value] = counts.get(value, 0) + 1
    if not counts:
        return None
    return max(counts.items(), key=lambda item: (item[1], str(item[0])))[0]


def load_importance_attribution_records(path: str | Path) -> List[Dict[str, Any]]:
    output: List[Dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            output.append(json.loads(line))
    return output


def _summarize_component_means(traces: Sequence[Dict[str, Any]]) -> Dict[str, float | None]:
    keys = [
        "structural_salience",
        "semantic_salience",
        "temporal_salience",
        "dialogue_salience",
        "constraint_participation",
        "goal_relevance",
        "user_emphasis",
        "confidence_strength",
        "dependency_support",
        "provenance_strength",
    ]
    output: Dict[str, float | None] = {}
    for key in keys:
        values: List[float] = []
        for trace in traces:
            components = trace.get("components") or {}
            if components.get(key) is not None:
                values.append(float(components.get(key)))
        output[key] = _mean(values)
    return output


def summarize_importance_attribution(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    traces = [build_importance_trace(record) for record in records]
    object_traces = [entry for trace in traces for entry in trace.get("traces") or []]
    summary: Dict[str, Any] = {
        "records": len(records),
        "records_with_traces": len(traces),
        "traces": traces,
        "scenarios": {},
        "root_cause": {},
        "reason_counts": defaultdict(int),
    }

    for trace in object_traces:
        reason = trace.get("reason")
        if reason is not None:
            summary["reason_counts"][reason] += 1

    for scenario in sorted({str(trace.get("compression_scenario") or "unknown") for trace in traces}):
        scenario_traces = [trace for trace in traces if str(trace.get("compression_scenario") or "unknown") == scenario]
        if not scenario_traces:
            continue
        scenario_object_traces = [entry for trace in scenario_traces for entry in trace.get("traces") or []]
        low_reasons = [entry.get("reason") for entry in scenario_object_traces if (entry.get("observed_importance") or 0.0) < 0.5]
        summary["scenarios"][scenario] = {
            "records": len(scenario_traces),
            "mean_observed_importance": _mean([value for value in [entry.get("observed_importance") for entry in scenario_object_traces] if value is not None]),
            "mean_proxy_importance": _mean([value for value in [entry.get("proxy_importance") for entry in scenario_object_traces] if value is not None]),
            "mean_importance_score": _mean([value for value in [entry.get("importance_score") for entry in scenario_object_traces] if value is not None]),
            "mean_importance_gap": _mean([value for value in [entry.get("importance_gap") for entry in scenario_object_traces] if value is not None]),
            "high_importance_object_count": sum(1 for entry in scenario_object_traces if (entry.get("importance_score") or 0.0) >= 0.8),
            "dominant_low_importance_reason": _mode(low_reasons),
            "dominant_root_cause": _mode([entry.get("reason") for entry in scenario_object_traces if (entry.get("importance_score") or 0.0) < 0.5]),
        }

    summary["reason_counts"] = dict(summary["reason_counts"])
    summary["mean_observed_importance"] = _mean([value for value in [entry.get("observed_importance") for entry in object_traces] if value is not None])
    summary["mean_proxy_importance"] = _mean([value for value in [entry.get("proxy_importance") for entry in object_traces] if value is not None])
    summary["mean_importance_gap"] = _mean([value for value in [entry.get("importance_gap") for entry in object_traces] if value is not None])
    summary["component_means"] = _summarize_component_means(object_traces)
    summary["root_cause"] = {
        "dominant_low_importance_reason": _mode([entry.get("reason") for entry in object_traces if (entry.get("importance_score") or 0.0) < 0.5]),
        "reason_counts": dict(summary["reason_counts"]),
        "mean_observed_importance": summary["mean_observed_importance"],
        "mean_proxy_importance": summary["mean_proxy_importance"],
        "mean_importance_score": _mean([value for value in [entry.get("importance_score") for entry in object_traces] if value is not None]),
        "mean_importance_gap": summary["mean_importance_gap"],
        "component_means": summary["component_means"],
        "retained_component_means": _summarize_component_means([entry for entry in object_traces if entry.get("retained")]),
        "dropped_component_means": _summarize_component_means([entry for entry in object_traces if not entry.get("retained")]),
    }
    return summary


def render_importance_attribution_markdown(summary: Dict[str, Any]) -> str:
    lines = ["# Importance Attribution", ""]
    lines.append(f"- `records`: {summary.get('records')}")
    lines.append(f"- `records_with_traces`: {summary.get('records_with_traces')}")
    lines.append(f"- `mean_observed_importance`: {summary.get('mean_observed_importance')}")
    lines.append(f"- `mean_proxy_importance`: {summary.get('mean_proxy_importance')}")
    lines.append(f"- `mean_importance_score`: {summary.get('mean_importance_score')}")
    lines.append(f"- `mean_importance_gap`: {summary.get('mean_importance_gap')}")
    lines.append("")

    lines.append("## Root Cause")
    root = summary.get("root_cause") or {}
    if root:
        for key, value in root.items():
            lines.append(f"- `{key}`: {value}")
    else:
        lines.append("_No root-cause data available._")
    lines.append("")

    lines.append("## Component Means")
    lines.append("| Component | Mean |")
    lines.append("| --- | --- |")
    for key, value in sorted((summary.get("component_means") or {}).items()):
        lines.append(f"| {key} | {'' if value is None else value} |")
    lines.append("")

    lines.append("## Scenario Summary")
    rows = []
    for scenario, scenario_summary in sorted((summary.get("scenarios") or {}).items()):
        rows.append(
            [
                scenario,
                scenario_summary.get("records"),
                scenario_summary.get("dominant_low_importance_reason"),
                scenario_summary.get("dominant_root_cause"),
                scenario_summary.get("high_importance_object_count"),
                scenario_summary.get("mean_observed_importance"),
                scenario_summary.get("mean_proxy_importance"),
                scenario_summary.get("mean_importance_gap"),
            ]
        )
    if rows:
        lines.extend(
            [
                "| Scenario | Records | Dominant Low-Importance Reason | Dominant Root Cause | High-Importance Objects | Mean Observed Importance | Mean Proxy Importance | Mean Importance Gap |",
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

    lines.append("## Example Objects")
    traces = sorted(
        summary.get("traces") or [],
        key=lambda item: (
            float(item.get("observed_importance") or 0.0),
            str(item.get("object_id") or ""),
        ),
    )
    for trace in traces[:12]:
        lines.append(f"### {trace.get('object_id')}")
        lines.append(f"- `type`: {trace.get('type')}")
        lines.append(f"- `value`: {trace.get('value')}")
        lines.append(f"- `observed_importance`: {trace.get('observed_importance')}")
        lines.append(f"- `proxy_importance`: {trace.get('proxy_importance')}")
        lines.append(f"- `importance_gap`: {trace.get('importance_gap')}")
        lines.append(f"- `reason`: {trace.get('reason')}")
        lines.append(f"- `retained`: {trace.get('retained')}")
        lines.append(f"- `components`: {trace.get('components')}")
        lines.append("")
    return "\n".join(lines)


def write_importance_attribution_outputs(records: Sequence[Dict[str, Any]], output_dir: str | Path) -> Dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    summary = summarize_importance_attribution(records)
    json_path = output_path / "importance_attribution.json"
    markdown_path = output_path / "importance_attribution.md"
    trace_path = output_path / "importance_trace.json"
    root_path = output_path / "importance_root_cause.md"

    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    markdown_path.write_text(render_importance_attribution_markdown(summary), encoding="utf-8")
    trace_path.write_text(json.dumps(summary.get("traces") or [], ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    root_markdown = ["# Importance Root Cause", ""]
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
