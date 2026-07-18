from __future__ import annotations

import json
import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Sequence

from .srp.export import write_records_csv, write_records_markdown
from .srp.pipeline import run_srp


@dataclass(frozen=True)
class RecoveryAblationSuite:
    name: str
    reconstruction_policy: str
    task: Dict[str, Any]
    client_factory: Callable[[], Any] | None = None


class HybridRecoveryMockClient:
    def __init__(self) -> None:
        self._recovery_calls = 0

    def generate_with_usage(self, prompt, **kwargs):
        prompt_text = str(prompt)
        if prompt_text.startswith("Compress semantic state."):
            payload = {
                "memory_summary": "Keep the blue key. Preserve the red key. The answer is B. The room is quiet.",
                "constraints": ["Keep the blue key.", "Preserve the red key."],
                "anchor_terms": ["blue", "red", "answer"],
                "term_map": {},
                "loss_risks": ["extra descriptive facts may be dropped"],
            }
            text = json.dumps(payload, ensure_ascii=False)
            return {
                "text": text,
                "raw_text": text,
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
                "stripped_thinking": None,
            }
        if prompt_text.startswith("Recover concise semantic state."):
            self._recovery_calls += 1
            text = "Keep the blue key. Preserve the red key. The answer is B. The room is quiet."
            if self._recovery_calls > 1:
                text = "Keep the blue key. Preserve the red key. The answer is B. The room is quiet. The sky is clear."
            return {
                "text": text,
                "raw_text": text,
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
                "stripped_thinking": None,
            }
        text = "The answer is B."
        return {
            "text": text,
            "raw_text": text,
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            "stripped_thinking": None,
        }


def _ablation_task() -> Dict[str, Any]:
    return {
        "id": "controlled-recovery-ablation",
        "task_type": "text_vs_structured_recovery",
        "source": "Controlled SRP Recovery Ablation",
        "initial_state": {
            "constraints": [
                "Keep the blue key.",
                "Preserve the red key.",
            ],
            "memory": "Keep the blue key. Preserve the red key. The answer is B. The room is quiet. The sky is clear.",
        },
        "query_expectations": [[["Keep the blue key."]]],
        "expected_keywords": ["blue", "red", "answer"],
        "metadata": {
            "benchmark": "Controlled SRP Recovery Ablation",
            "scenario": "text vs structured recovery",
        },
    }


def build_recovery_ablation_suites() -> List[RecoveryAblationSuite]:
    task = _ablation_task()
    return [
        RecoveryAblationSuite("text_only_recovery", "unrestricted", task, client_factory=None),
        RecoveryAblationSuite("structured_only_recovery", "minimal", task, client_factory=None),
        RecoveryAblationSuite("hybrid_recovery", "constrained", task, client_factory=HybridRecoveryMockClient),
    ]


def available_suite_names() -> List[str]:
    return [suite.name for suite in build_recovery_ablation_suites()]


def select_recovery_ablation_suites(names: Sequence[str] | None = None) -> List[RecoveryAblationSuite]:
    suites = build_recovery_ablation_suites()
    if not names:
        return suites
    requested = {str(name).strip() for name in names if str(name).strip()}
    if not requested or "all" in requested:
        return suites
    selected = [suite for suite in suites if suite.name in requested]
    missing = requested - {suite.name for suite in selected}
    if missing:
        raise ValueError(f"Unknown recovery ablation suite(s): {', '.join(sorted(missing))}")
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


def _apply_ablation_identity(record: Dict[str, Any], suite: RecoveryAblationSuite) -> None:
    record["task_id"] = record.get("task_id") or suite.task.get("id")
    record["task_source"] = "recovery_ablation"
    record["ablation_suite"] = suite.name
    record["reconstruction_policy"] = suite.reconstruction_policy
    record["controlled_ablation"] = {
        "suite": suite.name,
        "task_id": suite.task.get("id"),
        "task_type": suite.task.get("task_type"),
        "reconstruction_policy": suite.reconstruction_policy,
    }


def run_recovery_ablation(
    suites: Sequence[str] | None = None,
    *,
    cycles: int = 1,
) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for suite in select_recovery_ablation_suites(suites):
        client = suite.client_factory() if suite.client_factory is not None else None
        with _temporary_env({"SRP_RECONSTRUCTION_POLICY": suite.reconstruction_policy}):
            task_records = run_srp(suite.task, cycles=cycles, client=client)
        for record in task_records:
            _apply_ablation_identity(record, suite)
        records.extend(task_records)
    return records


def _metric_average(records: Sequence[Dict[str, Any]], key_path: Sequence[str]) -> float | None:
    values: List[float] = []
    for record in records:
        current: Any = record
        for key in key_path:
            if not isinstance(current, dict):
                current = None
                break
            current = current.get(key)
        if current is not None:
            values.append(float(current))
    if not values:
        return None
    return sum(values) / len(values)


def summarize_recovery_ablation(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "records": len(records),
        "suites": {},
    }
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for record in records:
        suite = str(record.get("ablation_suite") or "unknown")
        grouped.setdefault(suite, []).append(record)
    for suite_name, suite_records in grouped.items():
        summary["suites"][suite_name] = {
            "records": len(suite_records),
            "validation_passed": sum(1 for record in suite_records if record.get("validation_passed")),
            "validation_coverage": _metric_average(suite_records, ["validation_coverage"]),
            "important_recall": _metric_average(suite_records, ["experiment_result", "metrics", "important_object_recall"]),
            "task_critical_recall": _metric_average(suite_records, ["experiment_result", "metrics", "task_critical_object_recall"]),
            "recovered_object_count": _metric_average(suite_records, ["experiment_result", "lifecycle_attribution", "recovered", "recovered_object_count"]),
            "hallucinated_count": _metric_average(suite_records, ["experiment_result", "lifecycle_attribution", "recovered", "hallucinated_count"]),
            "object_inflation_ratio": _metric_average(suite_records, ["experiment_result", "metrics", "object_inflation_ratio"]),
            "reconstruction_policy": suite_records[0].get("reconstruction_policy") if suite_records else None,
        }
    return summary


def render_recovery_ablation_summary_markdown(summary: Dict[str, Any]) -> str:
    lines = ["# Text vs Structured Recovery Ablation", ""]
    lines.extend(
        [
            "| Suite | Policy | Records | Validation Passed | Validation Coverage | Important Recall | Task Critical Recall | Recovered Object Count | Hallucinated Count | Object Inflation Ratio |",
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
                    fmt(suite_summary.get("important_recall")),
                    fmt(suite_summary.get("task_critical_recall")),
                    fmt(suite_summary.get("recovered_object_count")),
                    fmt(suite_summary.get("hallucinated_count")),
                    fmt(suite_summary.get("object_inflation_ratio")),
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def write_recovery_ablation_outputs(
    records: Sequence[Dict[str, Any]],
    output_dir: str | Path,
) -> Dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_path / "recovery_ablation_records.jsonl"
    csv_path = output_path / "recovery_ablation_records.csv"
    markdown_path = output_path / "recovery_ablation_audit.md"
    summary_path = output_path / "recovery_ablation_summary.md"

    with jsonl_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    summary = summarize_recovery_ablation(records)
    write_records_csv(records, csv_path)
    write_records_markdown(records, markdown_path)
    summary_path.write_text(render_recovery_ablation_summary_markdown(summary), encoding="utf-8")
    return {
        "jsonl": jsonl_path,
        "csv": csv_path,
        "markdown": markdown_path,
        "summary": summary_path,
    }

