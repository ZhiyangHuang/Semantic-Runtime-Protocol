from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List, Sequence


def _flatten_dict(prefix: str, value, output: Dict[str, object]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            nested_prefix = f"{prefix}_{key}" if prefix else key
            _flatten_dict(nested_prefix, item, output)
    else:
        output[prefix] = value


def flatten_record_for_csv(record: Dict[str, object]) -> Dict[str, object]:
    flat: Dict[str, object] = {}
    for key, value in record.items():
        if key == "lifecycle_summary" and isinstance(value, dict):
            _flatten_dict("lifecycle_summary", value, flat)
            continue
        if isinstance(value, dict):
            _flatten_dict(key, value, flat)
        else:
            flat[key] = value
    return flat


def flatten_records_for_csv(records: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    return [flatten_record_for_csv(record) for record in records]


def _stringify_cell(value) -> str:
    if isinstance(value, list):
        return "|".join("" if item is None else str(item) for item in value)
    if isinstance(value, dict):
        return str(value)
    if value is None:
        return ""
    return str(value)


def write_records_csv(records: Sequence[Dict[str, object]], path: str | Path) -> Path:
    flattened = flatten_records_for_csv(records)
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: List[str] = []
    for record in flattened:
        for key in record.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in flattened:
            writer.writerow({key: _stringify_cell(record.get(key)) for key in fieldnames})
    return output_path


def _format_markdown_scalar(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return f"{value:.6f}".rstrip("0").rstrip(".")
    return str(value)


def _format_markdown_table(headers: Sequence[str], rows: Sequence[Sequence[object]]) -> List[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_format_markdown_scalar(cell) for cell in row) + " |")
    return lines


def _object_detail_rows(items: Sequence[object]) -> List[List[object]]:
    rows: List[List[object]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        rows.append(
            [
                item.get("object_id"),
                item.get("type"),
                item.get("value"),
                item.get("confidence"),
                item.get("evidence_pointer"),
            ]
        )
    return rows


def render_record_markdown(record: Dict[str, object]) -> str:
    experiment_result = record.get("experiment_result") or {}
    runtime = experiment_result.get("runtime") or {}
    compression = experiment_result.get("compression") or {}
    reconstruction = experiment_result.get("reconstruction") or {}
    validation = experiment_result.get("validation") or {}
    repair = experiment_result.get("repair") or {}
    repair_diagnostics = repair.get("diagnostics") or {}
    metrics = experiment_result.get("metrics") or {}
    lifecycle = experiment_result.get("lifecycle_attribution") or {}
    transitions = lifecycle.get("transitions") or {}

    title = record.get("task_id") or f"cycle-{record.get('cycle')}"
    lines = [f"## {title}", ""]
    lines.append(f"- `schema_version`: {_format_markdown_scalar(experiment_result.get('schema_version'))}")
    lines.append(f"- `cycle`: {_format_markdown_scalar(record.get('cycle'))}")
    lines.append(f"- `runtime_round`: {_format_markdown_scalar(runtime.get('round'))}")
    lines.append(f"- `validation_passed`: {_format_markdown_scalar(validation.get('passed'))}")
    lines.append(f"- `state_committed`: {_format_markdown_scalar(metrics.get('state_committed'))}")
    if record.get("task_source"):
        lines.append(f"- `task_source`: {_format_markdown_scalar(record.get('task_source'))}")
    lines.append("")

    lines.append("### Core Metrics")
    lines.extend(
        _format_markdown_table(
            ["Metric", "Value"],
            [
                ["validation_coverage", validation.get("coverage")],
                ["validation_alignment", validation.get("alignment")],
                ["integrity_gap", metrics.get("integrity_gap")],
                ["semantic_compression_loss", metrics.get("semantic_compression_loss")],
                ["object_retention", metrics.get("object_retention")],
                ["weighted_object_retention", metrics.get("weighted_object_retention")],
                ["lost_important_object_count", metrics.get("lost_important_object_count")],
                ["structured_state_package_present", reconstruction.get("structured_state_package_present")],
                ["compressed_size", compression.get("compressed_size")],
                ["compression_ratio", compression.get("compression_ratio")],
                ["lifecycle_inflation", metrics.get("lifecycle_inflation")],
                ["object_inflation_ratio", metrics.get("object_inflation_ratio")],
                ["graph_integrity_score", metrics.get("graph_integrity_score")],
                ["graph_object_survival_rate", metrics.get("graph_object_survival_rate")],
                ["graph_dependency_recall", metrics.get("graph_dependency_recall")],
                ["graph_constraint_accuracy", metrics.get("graph_constraint_accuracy")],
                ["graph_hallucination_rate", metrics.get("graph_hallucination_rate")],
                ["graph_dependency_closure_rate", metrics.get("graph_dependency_closure_rate")],
                ["graph_recovery_precision", metrics.get("graph_recovery_precision")],
                ["graph_repair_cost", metrics.get("graph_repair_cost")],
                ["semantic_similarity", metrics.get("semantic_similarity")],
                ["semantic_drift", metrics.get("semantic_drift")],
            ],
        )
    )
    lines.append("")

    lines.append("### Repair Diagnostics")
    lines.extend(
        _format_markdown_table(
            ["Field", "Value"],
            [
                ["repair_attempted", repair_diagnostics.get("repair_attempted")],
                ["coverage_before_repair", repair_diagnostics.get("coverage_before_repair")],
                ["coverage_after_repair", repair_diagnostics.get("coverage_after_repair")],
                ["repair_gain", repair_diagnostics.get("repair_gain")],
                ["critical_failures_before", repair_diagnostics.get("critical_failures_before")],
                ["critical_failures_after", repair_diagnostics.get("critical_failures_after")],
                ["token_overhead", repair_diagnostics.get("token_overhead")],
            ],
        )
    )
    lines.append("")

    graph_recovery = reconstruction.get("graph_recovery_result") or {}
    if graph_recovery:
        lines.append("### Graph Recovery")
        lines.extend(
            _format_markdown_table(
                ["Field", "Value"],
                [
                    ["dependency_closure_rate", graph_recovery.get("dependency_closure_rate")],
                    ["graph_recovery_precision", graph_recovery.get("graph_recovery_precision")],
                    ["repair_cost", graph_recovery.get("repair_cost")],
                    ["dependency_edge_count", graph_recovery.get("dependency_edge_count")],
                    ["blocked_count", graph_recovery.get("blocked_count")],
                ],
            )
        )
        lines.append("")

    lines.append("### Lifecycle Stages")
    stage_rows = []
    for stage_name in ["source", "compressed", "recovered", "repaired", "allocated", "executed"]:
        stage = lifecycle.get(stage_name) or {}
        stage_rows.append(
            [
                stage_name,
                stage.get("present"),
                stage.get("object_count"),
                stage.get("raw_object_count"),
                stage.get("recall"),
                stage.get("precision"),
            ]
        )
    lines.extend(
        _format_markdown_table(
            ["Stage", "Present", "Object Count", "Raw Object Count", "Recall", "Precision"],
            stage_rows,
        )
    )
    lines.append("")

    lines.append("### Lifecycle Transitions")
    transition_rows = []
    for name in [
        "source_to_compressed",
        "compressed_to_recovered",
        "recovered_to_repaired",
        "repaired_to_allocated",
        "recovered_to_allocated",
        "allocated_to_executed",
    ]:
        transition = transitions.get(name) or {}
        transition_rows.append(
            [
                name,
                transition.get("present"),
                transition.get("retained_count"),
                transition.get("missing_count"),
                transition.get("hallucinated_count"),
                transition.get("recall"),
                transition.get("precision"),
            ]
        )
    lines.extend(
        _format_markdown_table(
            ["Transition", "Present", "Retained", "Missing", "Hallucinated", "Recall", "Precision"],
            transition_rows,
        )
    )
    lines.append("")

    lines.append("### Lifecycle Transition Details")
    detail_transition_names = [
        "source_to_compressed",
        "compressed_to_recovered",
        "recovered_to_repaired",
        "repaired_to_allocated",
        "recovered_to_allocated",
        "allocated_to_executed",
    ]
    for name in detail_transition_names:
        transition = transitions.get(name) or {}
        lines.append(f"#### {name}")
        if not transition:
            lines.append("_No transition data available._")
            lines.append("")
            continue
        for bucket in ["retained", "missing", "hallucinated"]:
            lines.append(f"**{bucket.title()}**")
            rows = _object_detail_rows(transition.get(bucket) or [])
            if rows:
                lines.extend(
                    _format_markdown_table(
                        ["Object ID", "Type", "Value", "Confidence", "Evidence Pointer"],
                        rows,
                    )
                )
            else:
                lines.append("_None_")
            lines.append("")
    semantic_graph = experiment_result.get("semantic_graph") or {}
    graph = semantic_graph.get("graph") or {}
    graph_validation = semantic_graph.get("validation") or {}
    lines.append("### Semantic Runtime Graph")
    lines.extend(
        _format_markdown_table(
            ["Field", "Value"],
            [
                ["schema_version", graph.get("schema_version")],
                ["root_id", graph.get("root_id")],
                ["node_count", (graph.get("summary") or {}).get("node_count")],
                ["edge_count", (graph.get("summary") or {}).get("edge_count")],
                ["object_survival_rate", graph_validation.get("object_survival_rate")],
                ["dependency_recall", graph_validation.get("dependency_recall")],
                ["constraint_accuracy", graph_validation.get("constraint_accuracy")],
                ["hallucination_rate", graph_validation.get("hallucination_rate")],
                ["graph_integrity_score", graph_validation.get("graph_integrity_score")],
            ],
        )
    )
    lines.append("")
    return "\n".join(lines)


def render_records_markdown(records: Sequence[Dict[str, object]]) -> str:
    lines = ["# SRP Experiment Audit", ""]
    for index, record in enumerate(records):
        if index:
            lines.append("")
        lines.append(render_record_markdown(record))
    lines.append("")
    return "\n".join(lines)


def write_records_markdown(records: Sequence[Dict[str, object]], path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_records_markdown(records), encoding="utf-8")
    return output_path


def load_records(path: Path):
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def load_tasks(path: Path):
    with path.open("r", encoding="utf-8-sig") as handle:
        payload = json.load(handle)
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        if "tasks" in payload and isinstance(payload["tasks"], list):
            return payload["tasks"]
        return [payload]
    raise ValueError(f"Unsupported task payload in {path}")


def load_tasks_jsonl(path: Path):
    tasks = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                tasks.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_number}") from exc
    return tasks


def expand_task_inputs(values):
    expanded = []
    for value in values or []:
        path = Path(value)
        if path.is_dir():
            expanded.extend(sorted(path.glob("*.json")))
        else:
            expanded.append(path)
    return expanded


def apply_task_identity(record: dict, task: dict, task_path: Path, task_id_prefix: str = "") -> None:
    task_id = task.get("id") if isinstance(task, dict) else None
    if task_id_prefix and task_id:
        task_id = f"{task_id_prefix}{task_id}"
    record["task_id"] = task_id
    record["task_source"] = str(task_path)


def default_task() -> dict:
    return {
        "id": "export-csv-demo",
        "initial_state": {
            "constraints": ["Preserve the key fact."],
            "memory": "Preserve the key fact while keeping the summary compact.",
        },
        "query_expectations": [[["Preserve the key fact."]]],
        "expected_keywords": ["fact", "summary"],
    }
