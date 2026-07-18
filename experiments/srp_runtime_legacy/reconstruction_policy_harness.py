from __future__ import annotations

import json
import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence

from .srp.export import write_records_csv, write_records_markdown
from .srp.pipeline import run_srp


@dataclass(frozen=True)
class ReconstructionPolicySuite:
    name: str
    reconstruction_policy: str
    task: Dict[str, Any]


def _policy_task() -> Dict[str, Any]:
    return {
        "id": "controlled-reconstruction-policy",
        "task_type": "reconstruction_policy_comparison",
        "source": "Controlled SRP Reconstruction Policy Comparison",
        "initial_state": {
            "constraints": [
                "Preserve the blue key.",
                "Preserve the red key.",
            ],
            "memory": "Preserve the blue key. Preserve the red key. The answer is B. The room is quiet. The floor is warm.",
        },
        "query_expectations": [[["Preserve the blue key."]]],
        "expected_keywords": ["blue", "red", "answer"],
        "metadata": {
            "benchmark": "Controlled SRP Reconstruction Policy Comparison",
            "scenario": "reconstruction policy comparison",
        },
    }


def build_reconstruction_policy_suites() -> List[ReconstructionPolicySuite]:
    task = _policy_task()
    return [
        ReconstructionPolicySuite("unrestricted", "unrestricted", task),
        ReconstructionPolicySuite("constrained", "constrained", task),
        ReconstructionPolicySuite("minimal", "minimal", task),
    ]


def available_suite_names() -> List[str]:
    return [suite.name for suite in build_reconstruction_policy_suites()]


def select_reconstruction_policy_suites(names: Sequence[str] | None = None) -> List[ReconstructionPolicySuite]:
    suites = build_reconstruction_policy_suites()
    if not names:
        return suites
    requested = {str(name).strip() for name in names if str(name).strip()}
    if not requested or "all" in requested:
        return suites
    selected = [suite for suite in suites if suite.name in requested]
    missing = requested - {suite.name for suite in selected}
    if missing:
        raise ValueError(f"Unknown reconstruction policy suite(s): {', '.join(sorted(missing))}")
    return selected


@contextmanager
def _temporary_env(overrides: Dict[str, str]):
    previous: Dict[str, str | None] = {}
    try:
        for key, value in overrides.items():
            previous[key] = os.environ.get(key)
            os.environ[key] = value
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _apply_policy_identity(record: Dict[str, Any], suite: ReconstructionPolicySuite) -> None:
    record["task_id"] = record.get("task_id") or suite.task.get("id")
    record["task_source"] = "reconstruction_policy_comparison"
    record["reconstruction_policy_suite"] = suite.name
    record["reconstruction_policy"] = suite.reconstruction_policy
    record["controlled_reconstruction_policy"] = {
        "suite": suite.name,
        "task_id": suite.task.get("id"),
        "task_type": suite.task.get("task_type"),
        "reconstruction_policy": suite.reconstruction_policy,
    }


def _policy_metric(record: Dict[str, Any], *path: str) -> Any:
    current: Any = record
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def run_reconstruction_policy_comparison(
    suites: Sequence[str] | None = None,
    *,
    cycles: int = 1,
) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for suite in select_reconstruction_policy_suites(suites):
        with _temporary_env({"SRP_RECONSTRUCTION_POLICY": suite.reconstruction_policy}):
            task_records = run_srp(suite.task, cycles=cycles, client=None)
        for record in task_records:
            _apply_policy_identity(record, suite)
        records.extend(task_records)
    return records


def summarize_reconstruction_policy_comparison(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "records": len(records),
        "suites": {},
    }
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for record in records:
        suite = str(record.get("reconstruction_policy_suite") or "unknown")
        grouped.setdefault(suite, []).append(record)
    for suite_name, suite_records in grouped.items():
        summary["suites"][suite_name] = {
            "records": len(suite_records),
            "validation_passed": sum(1 for record in suite_records if record.get("validation_passed")),
            "validation_coverage": _mean([record.get("validation_coverage") for record in suite_records]),
            "recovered_object_count": _mean([_policy_metric(record, "experiment_result", "lifecycle_attribution", "recovered", "recovered_object_count") for record in suite_records]),
            "hallucinated_count": _mean([_policy_metric(record, "experiment_result", "lifecycle_attribution", "recovered", "hallucinated_count") for record in suite_records]),
            "reconstruction_precision": _mean([_reconstruction_precision(record) for record in suite_records]),
            "reconstruction_selectivity": _mean([_reconstruction_selectivity(record) for record in suite_records]),
            "minimality_score": _mean([_minimality_score(record) for record in suite_records]),
            "reconstruction_policy": suite_records[0].get("reconstruction_policy") if suite_records else None,
        }
    return summary


def _mean(values: Sequence[Any]) -> float | None:
    numbers = [float(value) for value in values if value is not None]
    if not numbers:
        return None
    return sum(numbers) / len(numbers)


def _reconstruction_result(record: Dict[str, Any]) -> Dict[str, Any]:
    return _policy_metric(record, "experiment_result", "reconstruction", "reconstruction_result") or {}


def _reconstruction_selectivity(record: Dict[str, Any]) -> float | None:
    metric = _reconstruction_result(record)
    available = metric.get("available_object_count")
    selected = metric.get("selected_object_count")
    if available is None or not available:
        return None
    if selected is None:
        return None
    return float(selected) / float(available)


def _reconstruction_precision(record: Dict[str, Any]) -> float | None:
    metric = _reconstruction_result(record)
    selected = metric.get("selected_object_count")
    rejected = metric.get("rejected_object_count")
    recovered_count = _policy_metric(record, "experiment_result", "lifecycle_attribution", "recovered", "recovered_object_count")
    if recovered_count is None and selected is not None and rejected is not None:
        recovered_count = float(selected) + float(rejected)
    if recovered_count is None or recovered_count <= 0:
        return None
    return float(selected or 0) / recovered_count


def _minimality_score(record: Dict[str, Any]) -> float | None:
    selectivity = _reconstruction_selectivity(record)
    if selectivity is None:
        return None
    return max(0.0, 1.0 - selectivity)


def render_reconstruction_policy_summary_markdown(summary: Dict[str, Any]) -> str:
    lines = ["# Reconstruction Policy Comparison", ""]
    lines.extend(
        [
            "| Suite | Policy | Records | Validation Passed | Validation Coverage | Recovered Object Count | Hallucinated Count | Reconstruction Precision | Reconstruction Selectivity | Minimality Score |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for suite_name, suite_summary in sorted((summary.get("suites") or {}).items()):
        def fmt(value):
            if value is None:
                return ""
            if isinstance(value, float):
                return f"{value:.6f}".rstrip("0").rstrip(".")
            return str(value)

        lines.append(
            "| "
            + " | ".join(
                [
                    str(suite_name),
                    fmt(suite_summary.get("reconstruction_policy")),
                    fmt(suite_summary.get("records")),
                    fmt(suite_summary.get("validation_passed")),
                    fmt(suite_summary.get("validation_coverage")),
                    fmt(suite_summary.get("recovered_object_count")),
                    fmt(suite_summary.get("hallucinated_count")),
                    fmt(suite_summary.get("reconstruction_precision")),
                    fmt(suite_summary.get("reconstruction_selectivity")),
                    fmt(suite_summary.get("minimality_score")),
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def write_reconstruction_policy_outputs(
    records: Sequence[Dict[str, Any]],
    output_dir: str | Path,
) -> Dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_path / "reconstruction_policy_records.jsonl"
    csv_path = output_path / "reconstruction_policy_records.csv"
    markdown_path = output_path / "reconstruction_policy_audit.md"
    summary_path = output_path / "reconstruction_policy_summary.md"

    with jsonl_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    summary = summarize_reconstruction_policy_comparison(records)
    write_records_csv(records, csv_path)
    write_records_markdown(records, markdown_path)
    summary_path.write_text(render_reconstruction_policy_summary_markdown(summary), encoding="utf-8")
    return {
        "jsonl": jsonl_path,
        "csv": csv_path,
        "markdown": markdown_path,
        "summary": summary_path,
    }

