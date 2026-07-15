from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Sequence

from .decision_trace import build_compression_decision_trace


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


def load_decision_attribution_records(path: str | Path) -> List[Dict[str, Any]]:
    output: List[Dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            output.append(json.loads(line))
    return output


def summarize_decision_attribution(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    traces = [build_compression_decision_trace(record) for record in records]
    summary: Dict[str, Any] = {
        "records": len(records),
        "records_with_traces": len(traces),
        "traces": traces,
        "scenarios": {},
        "root_cause": {},
        "chunk_reason_counts": defaultdict(int),
        "object_reason_counts": defaultdict(int),
    }

    for trace in traces:
        summary["chunk_reason_counts"].update(trace.get("summary", {}).get("chunk_reason_counts", {}))
        summary["object_reason_counts"].update(trace.get("summary", {}).get("object_reason_counts", {}))

    for scenario in sorted({str(trace.get("compression_scenario") or "unknown") for trace in traces}):
        scenario_traces = [trace for trace in traces if str(trace.get("compression_scenario") or "unknown") == scenario]
        if not scenario_traces:
            continue
        summaries = [trace.get("summary") or {} for trace in scenario_traces]
        root_causes = [trace.get("root_cause") or {} for trace in scenario_traces]
        summary["scenarios"][scenario] = {
            "records": len(scenario_traces),
            "mean_selected_chunk_score": _mean([value for value in [s.get("mean_selected_chunk_score") for s in summaries] if value is not None]),
            "mean_dropped_chunk_score": _mean([value for value in [s.get("mean_dropped_chunk_score") for s in summaries] if value is not None]),
            "mean_retained_object_importance": _mean([value for value in [s.get("mean_retained_object_importance") for s in summaries] if value is not None]),
            "mean_dropped_object_importance": _mean([value for value in [s.get("mean_dropped_object_importance") for s in summaries] if value is not None]),
            "mean_retained_object_confidence": _mean([value for value in [s.get("mean_retained_object_confidence") for s in summaries] if value is not None]),
            "mean_dropped_object_confidence": _mean([value for value in [s.get("mean_dropped_object_confidence") for s in summaries] if value is not None]),
            "high_importance_drop_count": sum(int(s.get("high_importance_drop_count") or 0) for s in summaries),
            "low_importance_drop_count": sum(int(s.get("low_importance_drop_count") or 0) for s in summaries),
            "supporting_chunk_cut_count": sum(int(s.get("supporting_chunk_cut_count") or 0) for s in summaries),
            "dominant_object_reason": _mode([item.get("dominant_object_reason") for item in root_causes]),
            "dominant_chunk_reason": _mode([item.get("dominant_chunk_reason") for item in root_causes]),
        }

    summary["chunk_reason_counts"] = dict(summary["chunk_reason_counts"])
    summary["object_reason_counts"] = dict(summary["object_reason_counts"])
    summary["compression_coverage_mean"] = _metric_average(records, "validation_coverage")
    summary["weighted_object_retention_mean"] = _metric_average(records, "weighted_object_retention")
    summary["graph_integrity_score_mean"] = _metric_average(records, "graph_integrity_score")
    summary["root_cause"] = {
        "dominant_chunk_reason": _mode([trace.get("root_cause", {}).get("dominant_chunk_reason") for trace in traces]),
        "dominant_object_reason": _mode([trace.get("root_cause", {}).get("dominant_object_reason") for trace in traces]),
        "supporting_chunk_cut_count": sum(int(trace.get("root_cause", {}).get("supporting_chunk_cut_count") or 0) for trace in traces),
        "high_importance_drop_count": sum(int(trace.get("root_cause", {}).get("high_importance_drop_count") or 0) for trace in traces),
        "low_importance_drop_count": sum(int(trace.get("root_cause", {}).get("low_importance_drop_count") or 0) for trace in traces),
    }
    return summary


def render_decision_attribution_markdown(summary: Dict[str, Any]) -> str:
    lines = ["# Decision Attribution", ""]
    lines.append(f"- `records`: {summary.get('records')}")
    lines.append(f"- `records_with_traces`: {summary.get('records_with_traces')}")
    lines.append(f"- `validation_coverage_mean`: {summary.get('compression_coverage_mean')}")
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
    scenario_rows = []
    for scenario, scenario_summary in sorted((summary.get("scenarios") or {}).items()):
        scenario_rows.append(
            [
                scenario,
                scenario_summary.get("records"),
                scenario_summary.get("dominant_object_reason"),
                scenario_summary.get("dominant_chunk_reason"),
                scenario_summary.get("supporting_chunk_cut_count"),
                scenario_summary.get("high_importance_drop_count"),
                scenario_summary.get("low_importance_drop_count"),
                scenario_summary.get("mean_dropped_object_importance"),
                scenario_summary.get("mean_retained_object_importance"),
            ]
        )
    if scenario_rows:
        lines.extend(
            [
                "| Scenario | Records | Dominant Object Reason | Dominant Chunk Reason | Supporting Chunk Cuts | High-Importance Drops | Low-Importance Drops | Mean Dropped Importance | Mean Retained Importance |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for row in scenario_rows:
            lines.append("| " + " | ".join("" if value is None else str(value) for value in row) + " |")
    else:
        lines.append("_No scenario data available._")
    lines.append("")

    lines.append("## Reason Counts")
    lines.append("| Reason | Chunk Count | Object Count |")
    lines.append("| --- | --- | --- |")
    reasons = sorted(set((summary.get("chunk_reason_counts") or {}).keys()) | set((summary.get("object_reason_counts") or {}).keys()))
    for reason in reasons:
        lines.append(
            f"| {reason} | {(summary.get('chunk_reason_counts') or {}).get(reason, 0)} | {(summary.get('object_reason_counts') or {}).get(reason, 0)} |"
        )
    lines.append("")

    lines.append("## Traces")
    for trace in summary.get("traces") or []:
        lines.append(f"### {trace.get('task_id') or trace.get('cycle') or 'record'}")
        lines.append(f"- `scenario`: {trace.get('compression_scenario')}")
        lines.append(f"- `object_support_enabled`: {trace.get('object_support_enabled')}")
        lines.append(f"- `top_k`: {trace.get('top_k')}")
        lines.append(f"- `cutoff_score`: {trace.get('cutoff_score')}")
        lines.append("")
    return "\n".join(lines)


def write_decision_attribution_outputs(records: Sequence[Dict[str, Any]], output_dir: str | Path) -> Dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    summary = summarize_decision_attribution(records)
    json_path = output_path / "decision_attribution.json"
    markdown_path = output_path / "decision_attribution.md"
    trace_path = output_path / "compression_decision_trace.json"
    root_path = output_path / "decision_root_cause.md"

    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    markdown_path.write_text(render_decision_attribution_markdown(summary), encoding="utf-8")
    trace_path.write_text(json.dumps(summary.get("traces") or [], ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    root_markdown = ["# Decision Root Cause", ""]
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
