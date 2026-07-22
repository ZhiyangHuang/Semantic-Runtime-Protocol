from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

from ..adapter import DeterministicMemoryAdapter, RuntimeAdmissionPolicy, SemanticRuntimeAdapter
from ..reports import write_csv, write_json, write_jsonl, write_markdown
from ..replay import (
    build_candidate_from_example,
    load_runtime_integration_examples_from_fixture,
    load_runtime_integration_fixture_payload,
)
from ..replay.loader import DEFAULT_FIXTURE_PATH
from ..replay.traces import RuntimeIntegrationTrace
from ..workloads import RuntimeIntegrationExample
from .records import ControlledAdmissionRecord


def _p95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(round(0.95 * (len(ordered) - 1)))))
    return ordered[index]


def _render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary") or {}
    lines = [
        "# Runtime Controlled Admission",
        "",
        "## Setup",
        f"- `snapshot_id`: {report.get('snapshot_id')}",
        f"- `parent_snapshot`: {report.get('parent_snapshot')}",
        f"- `fixture_path`: {report.get('fixture', {}).get('path')}",
        "",
        "## Summary",
        f"- `transition_count`: {summary.get('transition_count', 0)}",
        f"- `rollback_success_rate`: {summary.get('rollback_success_rate', 0.0):.6f}",
        f"- `invalid_commit_rate`: {summary.get('invalid_commit_rate', 0.0):.6f}",
        f"- `state_preservation_rate`: {summary.get('state_preservation_rate', 0.0):.6f}",
        f"- `admission_latency_overhead_ms`: {summary.get('admission_latency_overhead_ms', 0.0):.6f}",
        f"- `trace_completeness`: {summary.get('trace_completeness', 0.0):.3f}",
    ]
    return "\n".join(lines)


def run_runtime_integration_controlled(
    *,
    examples: Iterable[RuntimeIntegrationExample] | None = None,
    fixture_path: str | Path | None = None,
) -> dict[str, Any]:
    selected_path = Path(fixture_path) if fixture_path is not None else DEFAULT_FIXTURE_PATH
    fixture_payload = load_runtime_integration_fixture_payload(selected_path)
    selected_examples = list(examples) if examples is not None else load_runtime_integration_examples_from_fixture(selected_path)

    snapshot_id = "srp-runtime-v1.1-admission-0001"
    parent_snapshot = "srp-runtime-v1.1-shadow-0001"

    policy = RuntimeAdmissionPolicy(
        minimum_confidence=0.75,
        require_evidence=True,
        block_authority_escalation=True,
        enforce_transition_kind_checks=True,
        commit_enabled=True,
        mode="controlled_admission",
        name="runtime_controlled_admission_policy_v1",
    )
    adapter = SemanticRuntimeAdapter(policy=policy, store=DeterministicMemoryAdapter())

    records: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    rollback_success_count = 0
    invalid_commit_count = 0
    committed_count = 0
    latency_ms: list[float] = []

    for example in selected_examples:
        candidate = build_candidate_from_example(example)
        state_before = adapter.store.snapshot()
        decision = adapter.evaluate(candidate)
        state_after_commit = adapter.store.snapshot()
        committed = bool(decision.accepted)
        if committed:
            committed_count += 1
        invalid_commit = (not example.expected_decision) and state_after_commit != state_before
        if invalid_commit:
            invalid_commit_count += 1
        state_after_rollback = state_after_commit
        rollback_success = True
        if committed:
            state_after_rollback = adapter.store.rollback_transition(candidate.transition_id)
            rollback_success = state_after_rollback == state_before
            if rollback_success:
                rollback_success_count += 1
        else:
            rollback_success = state_after_rollback == state_before

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
                "state_before": state_before,
                "state_after_commit": state_after_commit,
                "state_after_rollback": state_after_rollback,
            },
        )
        record = ControlledAdmissionRecord(
            transition_id=candidate.transition_id,
            example_id=example.example_id,
            family=example.family,
            category=example.category,
            candidate=candidate.as_dict(),
            decision=decision.as_dict(),
            state_before=state_before,
            state_after_commit=state_after_commit,
            state_after_rollback=state_after_rollback,
            committed=committed,
            rollback_success=rollback_success,
            invalid_commit=invalid_commit,
            latency_ms={
                "decision_ms": round(float(decision.latency_ms), 6),
                "commit_ms": round(float(decision.governance_trace.get("timing", {}).get("commit_ms", 0.0) or 0.0), 6),
                "total_ms": round(float(decision.latency_ms), 6),
            },
            metadata={
                "example": example.as_dict(),
                "fixture_path": str(selected_path),
                "runtime_contract": fixture_payload.get("runtime_contract"),
            },
        )
        records.append(
            {
                **record.as_dict(),
                "expected_decision": example.expected_decision,
                "trace": trace.as_dict(),
            }
        )
        traces.append(trace.as_dict())
        latency_ms.append(float(decision.latency_ms))

    transition_count = len(records)
    invalid_total = sum(1 for record in records if not bool(record.get("expected_decision", False)))
    valid_total = sum(1 for record in records if bool(record.get("expected_decision", False)))
    rollback_success_rate = (rollback_success_count / float(committed_count)) if committed_count else 0.0
    invalid_commit_rate = (invalid_commit_count / float(invalid_total)) if invalid_total else 0.0
    state_preservation_rate = (
        sum(1 for record in records if record.get("state_before") == record.get("state_after_rollback")) / float(transition_count)
        if transition_count
        else 0.0
    )
    trace_completeness = (
        sum(
            1
            for trace in traces
            if all(field in trace for field in ("validation", "evidence", "governance", "execution", "timing", "metadata"))
        )
        / float(transition_count)
        if transition_count
        else 0.0
    )

    report = {
        "snapshot_id": snapshot_id,
        "parent_snapshot": parent_snapshot,
        "evaluation_type": "controlled_admission",
        "mode": "controlled",
        "fixture": {
            "path": str(selected_path),
            "hash": hashlib.sha256(selected_path.read_bytes()).hexdigest(),
            "runtime_contract": fixture_payload.get("runtime_contract"),
            "version": fixture_payload.get("version"),
            "snapshot_id": fixture_payload.get("snapshot_id"),
            "adapter": fixture_payload.get("adapter"),
        },
        "policy": policy.as_dict(),
        "records": records,
        "traces": traces,
        "summary": {
            "transition_count": transition_count,
            "valid_transition_count": valid_total,
            "invalid_transition_count": invalid_total,
            "committed_count": committed_count,
            "rollback_success_rate": rollback_success_rate,
            "invalid_commit_rate": invalid_commit_rate,
            "state_preservation_rate": state_preservation_rate,
            "admission_latency_overhead_ms": mean(latency_ms) if latency_ms else 0.0,
            "admission_latency_overhead_p95_ms": _p95(latency_ms),
            "trace_completeness": trace_completeness,
        },
        "comparison": {
            "rollback_success_count": rollback_success_count,
            "invalid_commit_count": invalid_commit_count,
            "committed_count": committed_count,
            "transition_count": transition_count,
        },
    }
    return report


def write_runtime_integration_controlled_outputs(report: dict[str, Any], output_dir: str | Path) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    json_path = write_json(output_path / "runtime_admission_report.json", report)
    jsonl_path = write_jsonl(output_path / "runtime_admission_traces.jsonl", report.get("traces") or [])
    csv_path = write_csv(output_path / "runtime_admission_records.csv", report.get("records") or [])
    markdown_path = write_markdown(output_path / "runtime_admission_report.md", _render_markdown(report))
    manifest = {
        "snapshot_id": report.get("snapshot_id"),
        "parent_snapshot": report.get("parent_snapshot"),
        "evaluation_type": report.get("evaluation_type"),
        "runtime_contract": (report.get("fixture") or {}).get("runtime_contract"),
        "fixture_path": (report.get("fixture") or {}).get("path"),
        "fixture_hash": (report.get("fixture") or {}).get("hash"),
        "policy": report.get("policy"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    manifest_path = write_json(output_path / "runtime_admission_manifest.json", manifest)
    return {
        "runtime_admission_report_json": json_path,
        "runtime_admission_traces_jsonl": jsonl_path,
        "runtime_admission_records_csv": csv_path,
        "runtime_admission_report_md": markdown_path,
        "runtime_admission_manifest_json": manifest_path,
    }
