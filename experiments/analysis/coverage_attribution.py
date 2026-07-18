from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Sequence

from experiments.common.export_support import write_records_csv

from .semantic_delta import SemanticDelta, build_semantic_delta
from .semantic_snapshot import SemanticSnapshot, build_stage_snapshots
from .stagewise_loss_matrix import build_stagewise_loss_matrix


def _metric_average(records: Sequence[Dict[str, Any]], key: str) -> float | None:
    values: List[float] = []
    for record in records:
        value = record.get(key)
        if value is not None:
            values.append(float(value))
    if not values:
        return None
    return sum(values) / len(values)


def _coverage_of(snapshot: SemanticSnapshot, source: SemanticSnapshot) -> Dict[str, float | None]:
    source_sets = source.signature_sets()
    stage_sets = snapshot.signature_sets()
    keys = ["objects", "relations", "constraints", "attributes", "states", "frames", "conversations", "provenance", "lifecycle"]
    coverage: Dict[str, float | None] = {}
    for key in keys:
        source_count = len(source_sets[key])
        stage_count = len(stage_sets[key])
        if source_count == 0:
            coverage[key] = None
        else:
            coverage[key] = round(min(1.0, stage_count / source_count), 6)
    return coverage


def _root_cause_from_rows(rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    root: Dict[str, Any] = {}
    if not rows:
        return root
    dimensions = [
        "object_loss_count",
        "relation_loss_count",
        "constraint_loss_count",
        "frame_loss_count",
        "provenance_loss_count",
        "lifecycle_loss_count",
    ]
    for dim in dimensions:
        metric_key = f"{dim}_mean"
        best = max(rows, key=lambda row: float(row.get(metric_key) or 0.0))
        root[dim] = {
            "stage_transition": best.get("stage_transition"),
            "value": best.get(metric_key),
            "occurrences": best.get("occurrences"),
        }
    return root


def summarize_coverage_attribution(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "records": len(records),
        "records_with_snapshots": 0,
        "stage_coverage": defaultdict(list),
        "stagewise_loss_matrix": [],
        "root_cause": {},
        "traces": [],
    }
    all_deltas: List[SemanticDelta] = []
    for record in records:
        snapshots = build_stage_snapshots(record)
        if not snapshots:
            continue
        summary["records_with_snapshots"] += 1
        stage_order = [stage for stage in ["source", "extraction", "representation", "compression", "recovery", "validation"] if stage in snapshots]
        if not stage_order:
            continue
        source_snapshot = snapshots[stage_order[0]]
        stage_trace = {"task_id": record.get("task_id"), "cycle": record.get("cycle"), "stages": {}}
        for stage_name in stage_order:
            coverage = _coverage_of(snapshots[stage_name], source_snapshot)
            stage_trace["stages"][stage_name] = {
                "snapshot": snapshots[stage_name].as_dict(),
                "coverage": coverage,
            }
            for key, value in coverage.items():
                if value is not None:
                    summary["stage_coverage"][f"{stage_name}:{key}"].append(float(value))
        for left_stage, right_stage in zip(stage_order[:-1], stage_order[1:]):
            delta = build_semantic_delta(snapshots[left_stage], snapshots[right_stage])
            all_deltas.append(delta)
            stage_trace.setdefault("deltas", []).append(delta.as_dict())
        summary["traces"].append(stage_trace)

    rows = build_stagewise_loss_matrix(all_deltas)
    summary["stagewise_loss_matrix"] = rows
    averaged_stage_coverage = {}
    for key, values in summary["stage_coverage"].items():
        averaged_stage_coverage[key] = sum(values) / len(values) if values else None
    summary["stage_coverage"] = averaged_stage_coverage
    summary["root_cause"] = _root_cause_from_rows(rows)
    summary["coverage_after_validation_mean"] = _metric_average(records, "validation_coverage")
    summary["dependency_recall_mean"] = _metric_average(records, "dependency_recall")
    summary["graph_integrity_score_mean"] = _metric_average(records, "graph_integrity_score")
    return summary


def render_coverage_attribution_markdown(summary: Dict[str, Any]) -> str:
    lines = ["# Coverage Attribution", ""]
    lines.append(f"- `records`: {summary.get('records')}")
    lines.append(f"- `records_with_snapshots`: {summary.get('records_with_snapshots')}")
    lines.append(f"- `coverage_after_validation_mean`: {summary.get('coverage_after_validation_mean')}")
    lines.append("")

    lines.append("## Stage Coverage")
    rows = []
    for key, value in sorted((summary.get("stage_coverage") or {}).items()):
        rows.append([key, value])
    if rows:
        lines.extend(
            [
                "| Stage Metric | Value |",
                "| --- | --- |",
            ]
        )
        for row in rows:
            lines.append(f"| {row[0]} | {'' if row[1] is None else row[1]} |")
    else:
        lines.append("_No stage coverage data available._")
    lines.append("")

    lines.append("## Stagewise Loss Matrix")
    matrix = summary.get("stagewise_loss_matrix") or []
    if matrix:
        headers = [
            "stage_transition",
            "occurrences",
            "object_loss_count_mean",
            "relation_loss_count_mean",
            "constraint_loss_count_mean",
            "frame_loss_count_mean",
            "provenance_loss_count_mean",
            "lifecycle_loss_count_mean",
            "total_loss_mean",
        ]
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join("---" for _ in headers) + " |")
        for row in matrix:
            lines.append(
                "| "
                + " | ".join(
                    "" if row.get(header) is None else str(row.get(header))
                    for header in headers
                )
                + " |"
            )
    else:
        lines.append("_No stagewise matrix available._")
    lines.append("")

    lines.append("## Root Cause")
    root = summary.get("root_cause") or {}
    if root:
        for dim, info in root.items():
            lines.append(
                f"- `{dim}`: {info.get('stage_transition')} "
                f"(mean={info.get('value')}, n={info.get('occurrences')})"
            )
    else:
        lines.append("_No root-cause data available._")
    lines.append("")

    lines.append("## Traces")
    for trace in summary.get("traces") or []:
        lines.append(f"### {trace.get('task_id') or trace.get('cycle') or 'record'}")
        for stage_name, stage_info in (trace.get("stages") or {}).items():
            coverage = stage_info.get("coverage") or {}
            lines.append(f"- `{stage_name}`: {coverage}")
        lines.append("")
    return "\n".join(lines)


def load_coverage_attribution_records(path: str | Path) -> List[Dict[str, Any]]:
    output: List[Dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            output.append(json.loads(line))
    return output


def write_coverage_attribution_outputs(records: Sequence[Dict[str, Any]], output_dir: str | Path) -> Dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    summary = summarize_coverage_attribution(records)
    json_path = output_path / "coverage_attribution.json"
    markdown_path = output_path / "coverage_attribution.md"
    matrix_path = output_path / "stagewise_loss_matrix.csv"
    trace_path = output_path / "semantic_snapshot_trace.json"
    delta_path = output_path / "semantic_delta_trace.json"
    root_path = output_path / "coverage_root_cause.md"

    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    markdown_path.write_text(render_coverage_attribution_markdown(summary), encoding="utf-8")
    write_records_csv(summary.get("stagewise_loss_matrix") or [], matrix_path)
    trace_path.write_text(json.dumps(summary.get("traces") or [], ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    delta_trace = []
    for trace in summary.get("traces") or []:
        delta_trace.extend(trace.get("deltas") or [])
    delta_path.write_text(json.dumps(delta_trace, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    root_markdown = ["# Coverage Root Cause", ""]
    root = summary.get("root_cause") or {}
    if root:
        for dim, info in root.items():
            root_markdown.append(
                f"- `{dim}`: {info.get('stage_transition')} "
                f"(mean={info.get('value')}, n={info.get('occurrences')})"
            )
    else:
        root_markdown.append("_No root-cause data available._")
    root_path.write_text("\n".join(root_markdown), encoding="utf-8")
    return {
        "json": json_path,
        "markdown": markdown_path,
        "matrix_csv": matrix_path,
        "semantic_snapshot_trace": trace_path,
        "semantic_delta_trace": delta_path,
        "root_cause_markdown": root_path,
    }
