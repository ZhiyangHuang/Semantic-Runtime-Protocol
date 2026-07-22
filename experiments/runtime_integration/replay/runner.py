from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable

from ..adapter import RuntimeAdmissionPolicy, SemanticMemoryStore, SemanticRuntimeAdapter
from ..metrics import summarize_runtime_integration_records
from ..reports import write_csv, write_json, write_jsonl, write_markdown
from ..workloads import RuntimeIntegrationExample
from .loader import (
    DEFAULT_FIXTURE_PATH,
    build_candidate_from_example,
    load_runtime_integration_examples,
    load_runtime_integration_examples_from_fixture,
    load_runtime_integration_fixture_payload,
)
from .traces import RuntimeIntegrationTrace


def _render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary") or {}
    lines = [
        "# Runtime Integration Replay",
        "",
        "## Setup",
        f"- `runtime`: {report.get('runtime')}",
        f"- `mode`: {report.get('mode')}",
        f"- `workload_family`: {report.get('workload_family')}",
        f"- `snapshot_id`: {report.get('snapshot_id')}",
        "",
        "## Summary",
        f"- `transitions`: {summary.get('transition_count', 0)}",
        f"- `accepted`: {summary.get('accepted_count', 0)}",
        f"- `rejected`: {summary.get('rejected_count', 0)}",
        f"- `unsafe_accept_rate`: {summary.get('unsafe_accept_rate', 0.0):.6f}",
        f"- `false_rejection_rate`: {summary.get('false_rejection_rate', 0.0):.6f}",
        f"- `trace_completeness`: {summary.get('trace_completeness', 0.0):.3f}",
        f"- `mean_latency_ms`: {summary.get('mean_latency_ms', 0.0):.6f}",
        f"- `p95_latency_ms`: {summary.get('p95_latency_ms', 0.0):.6f}",
    ]
    return "\n".join(lines)


def run_runtime_integration_replay(
    *,
    examples: Iterable[RuntimeIntegrationExample] | None = None,
    mode: str = "replay",
    policy: RuntimeAdmissionPolicy | None = None,
    fixture_path: str | Path | None = None,
) -> dict[str, Any]:
    selected_fixture_path: Path | None = None
    selected_examples = list(examples) if examples is not None else []
    fixture_payload: dict[str, Any] | None = None
    if examples is None:
        selected_fixture_path = Path(fixture_path) if fixture_path is not None else DEFAULT_FIXTURE_PATH
        if selected_fixture_path.exists():
            fixture_payload = load_runtime_integration_fixture_payload(selected_fixture_path)
            selected_examples = load_runtime_integration_examples_from_fixture(selected_fixture_path)
        else:
            selected_examples = load_runtime_integration_examples()
    policy = policy or RuntimeAdmissionPolicy(mode=mode, commit_enabled=(mode == "controlled"))
    adapter = SemanticRuntimeAdapter(policy=policy, store=SemanticMemoryStore())

    records: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    for example in selected_examples:
        candidate = build_candidate_from_example(example)
        decision = adapter.evaluate(candidate)
        trace = RuntimeIntegrationTrace(
            transition_id=candidate.transition_id,
            example_id=example.example_id,
            family=example.family,
            category=example.category,
            validation=decision.governance_trace.get("validation") or {},
            evidence=decision.governance_trace.get("evidence") or {},
            governance=decision.governance_trace.get("governance") or {},
            execution=decision.governance_trace.get("execution") or {},
            timing=decision.governance_trace.get("timing") or {},
            metadata={
                "example": example.as_dict(),
                "candidate": candidate.as_dict(),
                "decision": decision.as_dict(),
            },
        )
        record = {
            "example_id": example.example_id,
            "family": example.family,
            "category": example.category,
            "expected_decision": example.expected_decision,
            "example": example.as_dict(),
            "candidate": candidate.as_dict(),
            "decision": decision.as_dict(),
            "trace": trace.as_dict(),
        }
        records.append(record)
        traces.append(trace.as_dict())

    summary = summarize_runtime_integration_records(records).as_dict()
    fixture_info: dict[str, Any] | None = None
    if selected_fixture_path is not None and selected_fixture_path.exists():
        fixture_bytes = selected_fixture_path.read_bytes()
        fixture_info = {
            "path": str(selected_fixture_path),
            "hash": hashlib.sha256(fixture_bytes).hexdigest(),
            "snapshot_id": (fixture_payload or {}).get("snapshot_id"),
            "runtime_contract": (fixture_payload or {}).get("runtime_contract"),
            "version": (fixture_payload or {}).get("version"),
            "adapter": (fixture_payload or {}).get("adapter"),
            "governance_policy": (fixture_payload or {}).get("governance_policy"),
        }
    report = {
        "runtime": "semantic_runtime_integration_scaffold",
        "mode": mode,
        "workload_family": "preference_correction_contradiction",
        "policy": policy.as_dict(),
        "fixture": fixture_info,
        "snapshot_id": (fixture_info or {}).get("snapshot_id") or "srp-runtime-v1.1-replay-0001",
        "examples": [example.as_dict() for example in selected_examples],
        "records": records,
        "traces": traces,
        "summary": summary,
    }
    return report


def write_runtime_integration_replay_outputs(report: dict[str, Any], output_dir: str | Path) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    json_path = write_json(output_path / "runtime_integration_report.json", report)
    jsonl_path = write_jsonl(output_path / "runtime_integration_traces.jsonl", report.get("traces") or [])
    csv_path = write_csv(output_path / "runtime_integration_records.csv", report.get("records") or [])
    markdown_path = write_markdown(output_path / "runtime_integration_report.md", _render_markdown(report))
    fixture = report.get("fixture") or {}
    manifest = {
        "version": "v1.1",
        "adapter": "deterministic_memory_adapter",
        "snapshot_id": report.get("snapshot_id"),
        "fixture_path": fixture.get("path"),
        "fixture_hash": fixture.get("hash"),
        "runtime_contract": fixture.get("runtime_contract"),
        "governance_policy": fixture.get("governance_policy"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    manifest_path = write_json(output_path / "runtime_integration_manifest.json", manifest)
    return {
        "runtime_integration_report_json": json_path,
        "runtime_integration_traces_jsonl": jsonl_path,
        "runtime_integration_records_csv": csv_path,
        "runtime_integration_report_md": markdown_path,
        "runtime_integration_manifest_json": manifest_path,
    }
