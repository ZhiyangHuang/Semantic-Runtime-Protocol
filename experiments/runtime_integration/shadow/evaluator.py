from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Iterable

from ..adapter import DeterministicMemoryAdapter, RuntimeAdmissionPolicy, SemanticRuntimeAdapter
from ..reports import write_csv, write_json, write_jsonl, write_markdown
from ..replay import build_candidate_from_example, load_runtime_integration_examples_from_fixture, load_runtime_integration_fixture_payload
from ..replay.loader import DEFAULT_FIXTURE_PATH
from ..replay.traces import RuntimeIntegrationTrace
from ..workloads import RuntimeIntegrationExample
from .records import ShadowTransitionRecord


def _render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary") or {}
    lines = [
        "# Runtime Shadow Observation",
        "",
        "## Setup",
        f"- `snapshot_id`: {report.get('snapshot_id')}",
        f"- `parent_snapshot`: {report.get('parent_snapshot')}",
        f"- `fixture_path`: {report.get('fixture', {}).get('path')}",
        "",
        "## Summary",
        f"- `transition_count`: {summary.get('transition_count', 0)}",
        f"- `shadow_rejection_rate`: {summary.get('shadow_rejection_rate', 0.0):.6f}",
        f"- `runtime_disagreement_rate`: {summary.get('runtime_disagreement_rate', 0.0):.6f}",
        f"- `admission_latency_overhead_ms`: {summary.get('admission_latency_overhead_ms', 0.0):.6f}",
        f"- `trace_completeness`: {summary.get('trace_completeness', 0.0):.3f}",
    ]
    return "\n".join(lines)


def _evaluate_backend(
    *,
    backend_name: str,
    policy: RuntimeAdmissionPolicy,
    examples: Iterable[RuntimeIntegrationExample],
    fixture_payload: dict[str, Any],
    selected_path: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    adapter = SemanticRuntimeAdapter(policy=policy, store=DeterministicMemoryAdapter())
    records: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    for example in examples:
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
                "backend": backend_name,
                "fixture_path": str(selected_path),
                "runtime_contract": fixture_payload.get("runtime_contract"),
            },
        )
        records.append(
            {
                "example_id": example.example_id,
                "family": example.family,
                "category": example.category,
                "expected_decision": example.expected_decision,
                "backend": backend_name,
                "example": example.as_dict(),
                "candidate": candidate.as_dict(),
                "decision": decision.as_dict(),
                "trace": trace.as_dict(),
            }
        )
        traces.append(trace.as_dict())
    return records, traces


def run_runtime_integration_shadow(
    *,
    examples: Iterable[RuntimeIntegrationExample] | None = None,
    fixture_path: str | Path | None = None,
) -> dict[str, Any]:
    selected_path = Path(fixture_path) if fixture_path is not None else DEFAULT_FIXTURE_PATH
    fixture_payload = load_runtime_integration_fixture_payload(selected_path)
    selected_examples = list(examples) if examples is not None else load_runtime_integration_examples_from_fixture(selected_path)
    shadow_snapshot_id = "srp-runtime-v1.1-shadow-0001"
    parent_snapshot = "srp-runtime-v1.1-backend-0001"

    baseline_policy = RuntimeAdmissionPolicy(
        minimum_confidence=0.0,
        require_evidence=False,
        block_authority_escalation=False,
        enforce_transition_kind_checks=False,
        commit_enabled=False,
        mode="shadow_baseline",
        name="runtime_shadow_baseline_policy_v1",
    )
    srp_policy = RuntimeAdmissionPolicy(
        minimum_confidence=0.75,
        require_evidence=True,
        block_authority_escalation=True,
        commit_enabled=False,
        mode="shadow_observation",
        name="runtime_shadow_observation_policy_v1",
    )

    baseline_records, baseline_traces = _evaluate_backend(
        backend_name="existing_runtime",
        policy=baseline_policy,
        examples=selected_examples,
        fixture_payload=fixture_payload,
        selected_path=selected_path,
    )
    srp_records, srp_traces = _evaluate_backend(
        backend_name="srp_shadow",
        policy=srp_policy,
        examples=selected_examples,
        fixture_payload=fixture_payload,
        selected_path=selected_path,
    )

    records: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    for baseline_record, srp_record, baseline_trace, srp_trace in zip(baseline_records, srp_records, baseline_traces, srp_traces):
        baseline_decision = baseline_record.get("decision") or {}
        srp_decision = srp_record.get("decision") or {}
        baseline_latency = float(baseline_decision.get("latency_ms", 0.0) or 0.0)
        srp_latency = float(srp_decision.get("latency_ms", 0.0) or 0.0)
        actual_runtime_action = "accept" if bool(baseline_decision.get("accepted", False)) else "reject"
        srp_action = "accept" if bool(srp_decision.get("accepted", False)) else "reject"
        would_block = actual_runtime_action == "accept" and srp_action == "reject"
        shadow_record = ShadowTransitionRecord(
            transition_id=str(baseline_record.get("example_id") or "unknown"),
            example_id=str(baseline_record.get("example_id") or "unknown"),
            family=str(baseline_record.get("family") or "unknown"),
            category=str(baseline_record.get("category") or "unknown"),
            candidate=dict(baseline_record.get("candidate") or {}),
            actual_runtime_action=actual_runtime_action,
            srp_decision={
                "decision": srp_decision.get("decision"),
                "accepted": srp_decision.get("accepted"),
                "violated_rules": list(srp_decision.get("violated_rules") or []),
            },
            would_block=would_block,
            latency_ms={
                "runtime": round(baseline_latency, 6),
                "srp": round(srp_latency, 6),
                "overhead_ms": round(srp_latency - baseline_latency, 6),
                "overhead_pct": round(((srp_latency - baseline_latency) / baseline_latency) if baseline_latency else 0.0, 6),
            },
            metadata={
                "baseline": baseline_record,
                "srp": srp_record,
                "fixture_path": str(selected_path),
            },
        )
        records.append(
            {
                "example_id": shadow_record.example_id,
                "family": shadow_record.family,
                "category": shadow_record.category,
                "actual_runtime_action": shadow_record.actual_runtime_action,
                "srp_decision": shadow_record.srp_decision,
                "would_block": shadow_record.would_block,
                "latency_ms": shadow_record.latency_ms,
                "candidate": shadow_record.candidate,
                "baseline_record": baseline_record,
                "srp_record": srp_record,
            }
        )
        traces.append(
            {
                "transition_id": shadow_record.transition_id,
                "example_id": shadow_record.example_id,
                "family": shadow_record.family,
                "category": shadow_record.category,
                "actual_runtime_action": shadow_record.actual_runtime_action,
                "srp_decision": shadow_record.srp_decision,
                "would_block": shadow_record.would_block,
                "latency_ms": shadow_record.latency_ms,
                "metadata": shadow_record.metadata,
            }
        )

    total = len(records)
    shadow_rejection_count = sum(1 for record in records if bool(record.get("would_block", False)))
    disagreement_count = sum(
        1
        for record in records
        if str(record.get("actual_runtime_action")) != ("accept" if bool((record.get("srp_decision") or {}).get("accepted", False)) else "reject")
    )
    overheads = [float((record.get("latency_ms") or {}).get("overhead_ms", 0.0) or 0.0) for record in records]
    overhead_pcts = [float((record.get("latency_ms") or {}).get("overhead_pct", 0.0) or 0.0) for record in records]
    trace_completeness = 0.0
    if total:
        trace_fields = ("transition_id", "example_id", "family", "category", "actual_runtime_action", "srp_decision", "would_block", "latency_ms", "metadata")
        trace_completeness = sum(
            1 for trace in traces if all(field in trace for field in trace_fields)
        ) / float(total)

    report = {
        "snapshot_id": shadow_snapshot_id,
        "parent_snapshot": parent_snapshot,
        "evaluation_type": "shadow_observation",
        "mode": "shadow",
        "fixture": {
            "path": str(selected_path),
            "hash": hashlib.sha256(selected_path.read_bytes()).hexdigest(),
            "runtime_contract": fixture_payload.get("runtime_contract"),
            "version": fixture_payload.get("version"),
            "snapshot_id": fixture_payload.get("snapshot_id"),
            "adapter": fixture_payload.get("adapter"),
        },
        "policies": {
            "baseline": baseline_policy.as_dict(),
            "srp": srp_policy.as_dict(),
        },
        "records": records,
        "traces": traces,
        "summary": {
            "transition_count": total,
            "shadow_rejection_rate": (shadow_rejection_count / float(total)) if total else 0.0,
            "runtime_disagreement_rate": (disagreement_count / float(total)) if total else 0.0,
            "admission_latency_overhead_ms": (sum(overheads) / float(total)) if total else 0.0,
            "admission_latency_overhead_pct": (sum(overhead_pcts) / float(total)) if total else 0.0,
            "trace_completeness": trace_completeness,
        },
        "comparison": {
            "shadow_rejection_count": shadow_rejection_count,
            "runtime_disagreement_count": disagreement_count,
            "baseline_accept_count": sum(1 for record in records if str(record.get("actual_runtime_action")) == "accept"),
            "srp_accept_count": sum(1 for record in records if bool((record.get("srp_decision") or {}).get("accepted", False))),
        },
    }
    return report


def write_runtime_integration_shadow_outputs(report: dict[str, Any], output_dir: str | Path) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    json_path = write_json(output_path / "runtime_shadow_report.json", report)
    jsonl_path = write_jsonl(output_path / "runtime_shadow_traces.jsonl", report.get("traces") or [])
    csv_path = write_csv(output_path / "runtime_shadow_records.csv", report.get("records") or [])
    markdown_path = write_markdown(output_path / "runtime_shadow_report.md", _render_markdown(report))
    manifest = {
        "snapshot_id": report.get("snapshot_id"),
        "parent_snapshot": report.get("parent_snapshot"),
        "evaluation_type": report.get("evaluation_type"),
        "runtime_contract": (report.get("fixture") or {}).get("runtime_contract"),
        "fixture_path": (report.get("fixture") or {}).get("path"),
        "fixture_hash": (report.get("fixture") or {}).get("hash"),
        "policies": report.get("policies"),
    }
    manifest_path = write_json(output_path / "runtime_shadow_manifest.json", manifest)
    return {
        "runtime_shadow_report_json": json_path,
        "runtime_shadow_traces_jsonl": jsonl_path,
        "runtime_shadow_records_csv": csv_path,
        "runtime_shadow_report_md": markdown_path,
        "runtime_shadow_manifest_json": manifest_path,
    }
