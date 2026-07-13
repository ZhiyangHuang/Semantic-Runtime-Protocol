from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Sequence

from .srp.export import write_records_csv, write_records_markdown
from .srp.pipeline import run_srp


SuiteName = str


@dataclass(frozen=True)
class ControlledSuite:
    name: SuiteName
    task: Dict[str, Any]
    client_factory: Callable[[], Any] | None = None


class RepairLoopMockClient:
    def __init__(self) -> None:
        self._recovery_calls = 0

    def generate_with_usage(self, prompt, **kwargs):
        prompt_text = str(prompt)
        if prompt_text.startswith("Compress semantic state."):
            payload = {
                "memory_summary": "Keep the key constraint. The answer is B.",
                "constraints": ["Preserve the key constraint."],
                "anchor_terms": ["constraint", "answer"],
                "term_map": {},
                "loss_risks": ["compressed for deterministic repair-loop testing"],
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
            if self._recovery_calls == 1:
                text = "The answer is B."
            else:
                text = "Preserve the key constraint. The answer is B."
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


def _controlled_task(
    *,
    task_id: str,
    task_type: str,
    memory: str,
    constraints: Sequence[str],
    expected_keywords: Sequence[str],
    query_expectations: Sequence[Sequence[Sequence[str]]],
    important_objects: Sequence[Dict[str, Any]] | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    task_metadata = dict(metadata or {})
    task_metadata.setdefault("benchmark", "Controlled SRP Harness")
    task_metadata.setdefault("harness_suite", task_type)
    if important_objects is not None:
        task_metadata["important_objects"] = list(important_objects)
    return {
        "id": task_id,
        "task_type": task_type,
        "source": "Controlled SRP Harness",
        "initial_state": {
            "constraints": list(constraints),
            "memory": memory,
        },
        "query_expectations": [list(item) for item in query_expectations],
        "expected_keywords": list(expected_keywords),
        "metadata": task_metadata,
    }


def build_controlled_suites() -> List[ControlledSuite]:
    structured_recovery_task = _controlled_task(
        task_id="controlled-structured-recovery",
        task_type="structured_recovery",
        memory="Keep the blue key. Preserve the red key. The answer is B.",
        constraints=["Keep the blue key.", "Preserve the red key."],
        expected_keywords=["blue", "red", "answer"],
        query_expectations=[[["Keep the blue key."]]],
        important_objects=[
            {
                "object_id": "blue-key",
                "type": "fact",
                "value": "Keep the blue key.",
                "confidence": 1.0,
                "evidence_pointer": "memory:1",
            },
            {
                "object_id": "red-key",
                "type": "fact",
                "value": "Preserve the red key.",
                "confidence": 1.0,
                "evidence_pointer": "memory:2",
            },
        ],
        metadata={"scenario": "structured recovery"},
    )
    object_retention_task = _controlled_task(
        task_id="controlled-object-retention",
        task_type="object_retention",
        memory="Keep the blue key. Keep the red key. Preserve the answer B.",
        constraints=["Keep the blue key.", "Keep the red key."],
        expected_keywords=["blue", "red", "answer"],
        query_expectations=[[["Keep the blue key."]]],
        important_objects=[
            {
                "object_id": "blue-key",
                "type": "fact",
                "value": "Keep the blue key.",
                "confidence": 1.0,
                "evidence_pointer": "memory:1",
            },
            {
                "object_id": "red-key",
                "type": "fact",
                "value": "Keep the red key.",
                "confidence": 1.0,
                "evidence_pointer": "memory:2",
            },
        ],
        metadata={"scenario": "object retention"},
    )
    repair_loop_task = _controlled_task(
        task_id="controlled-repair-loop",
        task_type="repair_loop",
        memory="Preserve the key constraint. The answer is B.",
        constraints=["Preserve the key constraint."],
        expected_keywords=["constraint", "answer"],
        query_expectations=[[["Preserve the key constraint."]]],
        important_objects=[
            {
                "object_id": "key-constraint",
                "type": "constraint",
                "value": "Preserve the key constraint.",
                "confidence": 1.0,
                "evidence_pointer": "memory:1",
            }
        ],
        metadata={"scenario": "repair loop"},
    )
    return [
        ControlledSuite("structured_recovery", structured_recovery_task, client_factory=None),
        ControlledSuite("object_retention", object_retention_task, client_factory=None),
        ControlledSuite("repair_loop", repair_loop_task, client_factory=RepairLoopMockClient),
    ]


def available_suite_names() -> List[str]:
    return [suite.name for suite in build_controlled_suites()]


def select_controlled_suites(names: Sequence[str] | None = None) -> List[ControlledSuite]:
    suites = build_controlled_suites()
    if not names:
        return suites
    requested = {str(name).strip() for name in names if str(name).strip()}
    if not requested or "all" in requested:
        return suites
    selected = [suite for suite in suites if suite.name in requested]
    missing = requested - {suite.name for suite in selected}
    if missing:
        raise ValueError(f"Unknown controlled harness suite(s): {', '.join(sorted(missing))}")
    return selected


def _apply_harness_identity(record: Dict[str, Any], suite: ControlledSuite) -> None:
    record["task_id"] = record.get("task_id") or suite.task.get("id")
    record["task_source"] = "controlled_harness"
    record["harness_suite"] = suite.name
    record["task_type"] = suite.task.get("task_type")
    record["controlled_harness"] = {
        "suite": suite.name,
        "task_id": suite.task.get("id"),
        "task_type": suite.task.get("task_type"),
    }


def run_controlled_harness(
    suites: Sequence[str] | None = None,
    *,
    cycles: int = 1,
) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for suite in select_controlled_suites(suites):
        client = suite.client_factory() if suite.client_factory is not None else None
        task_records = run_srp(suite.task, cycles=cycles, client=client)
        for record in task_records:
            _apply_harness_identity(record, suite)
        records.extend(task_records)
    return records


def summarize_controlled_records(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "records": len(records),
        "suites": {},
    }
    for record in records:
        suite = str(record.get("harness_suite") or "unknown")
        suite_summary = summary["suites"].setdefault(
            suite,
            {
                "records": 0,
                "validation_passed": 0,
                "repair_attempted": 0,
                "important_recall_values": [],
                "task_critical_recall_values": [],
                "token_overhead_values": [],
            },
        )
        suite_summary["records"] += 1
        if record.get("validation_passed"):
            suite_summary["validation_passed"] += 1
        if record.get("repair_attempted"):
            suite_summary["repair_attempted"] += 1
        metrics = (record.get("experiment_result") or {}).get("metrics") or {}
        important_recall = metrics.get("important_object_recall")
        task_critical_recall = metrics.get("task_critical_object_recall")
        token_overhead = (
            record.get("token_overhead")
            if record.get("token_overhead") is not None
            else ((record.get("repair_diagnostics") or {}).get("token_overhead"))
        )
        if important_recall is not None:
            suite_summary["important_recall_values"].append(float(important_recall))
        if task_critical_recall is not None:
            suite_summary["task_critical_recall_values"].append(float(task_critical_recall))
        if token_overhead is not None:
            suite_summary["token_overhead_values"].append(float(token_overhead))
    for suite_summary in summary["suites"].values():
        important_recall_values = suite_summary.pop("important_recall_values")
        task_critical_recall_values = suite_summary.pop("task_critical_recall_values")
        token_overhead_values = suite_summary.pop("token_overhead_values")
        suite_summary["important_recall"] = (
            sum(important_recall_values) / len(important_recall_values) if important_recall_values else None
        )
        suite_summary["task_critical_recall"] = (
            sum(task_critical_recall_values) / len(task_critical_recall_values) if task_critical_recall_values else None
        )
        suite_summary["token_overhead"] = (
            sum(token_overhead_values) / len(token_overhead_values) if token_overhead_values else None
        )
    return summary


def render_controlled_summary_markdown(summary: Dict[str, Any]) -> str:
    lines = ["# Controlled SRP Harness Summary", ""]
    lines.extend(
        [
            "| Suite | Records | Validation Passed | Repair Attempted | Important Recall | Task Critical Recall | Token Overhead |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for suite_name, suite_summary in sorted((summary.get("suites") or {}).items()):
        lines.append(
            "| "
            + " | ".join(
                [
                    str(suite_name),
                    str(suite_summary.get("records")),
                    str(suite_summary.get("validation_passed")),
                    str(suite_summary.get("repair_attempted")),
                    "" if suite_summary.get("important_recall") is None else f'{suite_summary.get("important_recall"):.6f}'.rstrip("0").rstrip("."),
                    "" if suite_summary.get("task_critical_recall") is None else f'{suite_summary.get("task_critical_recall"):.6f}'.rstrip("0").rstrip("."),
                    "" if suite_summary.get("token_overhead") is None else f'{suite_summary.get("token_overhead"):.6f}'.rstrip("0").rstrip("."),
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def write_controlled_outputs(
    records: Sequence[Dict[str, Any]],
    output_dir: str | Path,
) -> Dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_path / "controlled_harness_records.jsonl"
    csv_path = output_path / "controlled_harness_records.csv"
    markdown_path = output_path / "controlled_harness_audit.md"
    summary_path = output_path / "controlled_harness_summary.md"

    with jsonl_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    summary = summarize_controlled_records(records)
    write_records_csv(records, csv_path)
    write_records_markdown(records, markdown_path)
    summary_path.write_text(render_controlled_summary_markdown(summary), encoding="utf-8")
    return {
        "jsonl": jsonl_path,
        "csv": csv_path,
        "markdown": markdown_path,
        "summary": summary_path,
    }
