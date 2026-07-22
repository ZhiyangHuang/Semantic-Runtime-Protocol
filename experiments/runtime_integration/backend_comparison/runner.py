from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ..adapter import (
    DeterministicMemoryAdapter,
    InMemoryGraphStore,
    RuntimeAdmissionPolicy,
    SemanticRuntimeAdapter,
)
from ..metrics import summarize_runtime_integration_records
from ..reports import write_csv, write_json, write_jsonl, write_markdown
from ..replay import build_candidate_from_example, load_runtime_integration_examples_from_fixture, load_runtime_integration_fixture_payload
from ..replay.loader import DEFAULT_FIXTURE_PATH
from ..replay.traces import RuntimeIntegrationTrace


def _render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary") or {}
    comparison = report.get("comparison") or {}
    lines = [
        "# Runtime Backend Consistency",
        "",
        "## Setup",
        f"- `snapshot_id`: {report.get('snapshot_id')}",
        f"- `parent_snapshot`: {report.get('parent_snapshot')}",
        f"- `evaluation_type`: {report.get('evaluation_type')}",
        f"- `fixture_path`: {report.get('fixture', {}).get('path')}",
        "",
        "## Summary",
        f"- `transition_count`: {summary.get('transition_count', 0)}",
        f"- `backend_consistency_rate`: {comparison.get('backend_consistency_rate', 0.0):.6f}",
        f"- `decision_mismatch_count`: {comparison.get('decision_mismatch_count', 0)}",
        f"- `trace_completeness`: {summary.get('trace_completeness', 0.0):.3f}",
    ]
    return "\n".join(lines)


def _run_single_backend(
    *,
    backend_name: str,
    backend: Any,
    policy: RuntimeAdmissionPolicy,
    fixture_path: str | Path | None = None,
) -> dict[str, Any]:
    selected_path = Path(fixture_path) if fixture_path is not None else DEFAULT_FIXTURE_PATH
    payload = load_runtime_integration_fixture_payload(selected_path)
    examples = load_runtime_integration_examples_from_fixture(selected_path)
    adapter = SemanticRuntimeAdapter(policy=policy, store=backend)

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

    summary = summarize_runtime_integration_records(records).as_dict()
    return {
        "backend": backend_name,
        "fixture": {
            "path": str(selected_path),
            "hash": hashlib.sha256(selected_path.read_bytes()).hexdigest(),
            "runtime_contract": payload.get("runtime_contract"),
            "version": payload.get("version"),
            "snapshot_id": payload.get("snapshot_id"),
            "adapter": payload.get("adapter"),
        },
        "policy": policy.as_dict(),
        "records": records,
        "traces": traces,
        "summary": summary,
    }


def run_runtime_integration_backend_consistency(
    *,
    fixture_path: str | Path | None = None,
) -> dict[str, Any]:
    policy = RuntimeAdmissionPolicy(mode="replay", commit_enabled=False)
    snapshot_id = "srp-runtime-v1.1-backend-0001"
    parent_snapshot = "srp-runtime-v1.1-replay-0001"
    backends = ["deterministic_memory_adapter", "in_memory_graph_store"]
    deterministic = _run_single_backend(
        backend_name="deterministic_memory_adapter",
        backend=DeterministicMemoryAdapter(),
        policy=policy,
        fixture_path=fixture_path,
    )
    graph = _run_single_backend(
        backend_name="in_memory_graph_store",
        backend=InMemoryGraphStore(),
        policy=policy,
        fixture_path=fixture_path,
    )

    deterministic_decisions = [record.get("decision", {}).get("accepted", False) for record in deterministic.get("records") or []]
    graph_decisions = [record.get("decision", {}).get("accepted", False) for record in graph.get("records") or []]
    mismatches = sum(1 for left, right in zip(deterministic_decisions, graph_decisions) if bool(left) != bool(right))
    total = max(len(deterministic_decisions), len(graph_decisions))
    consistency_rate = 1.0 if total == 0 else 1.0 - (mismatches / float(total))

    report = {
        "snapshot_id": snapshot_id,
        "parent_snapshot": parent_snapshot,
        "evaluation_type": "backend_consistency",
        "mode": "backend_consistency",
        "backends_evaluated": list(backends),
        "fixture": deterministic.get("fixture"),
        "backends": {
            "deterministic_memory_adapter": deterministic,
            "in_memory_graph_store": graph,
        },
        "comparison": {
            "backend_consistency_rate": consistency_rate,
            "decision_mismatch_count": mismatches,
            "comparison_total": total,
        },
        "summary": {
            "transition_count": total,
            "trace_completeness": min(
                float((deterministic.get("summary") or {}).get("trace_completeness", 0.0)),
                float((graph.get("summary") or {}).get("trace_completeness", 0.0)),
            ),
        },
    }
    return report


def write_runtime_integration_backend_consistency_outputs(report: dict[str, Any], output_dir: str | Path) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    backend_dir = output_path / "backend_comparison"
    backend_dir.mkdir(parents=True, exist_ok=True)
    deterministic = report.get("backends", {}).get("deterministic_memory_adapter") or {}
    graph = report.get("backends", {}).get("in_memory_graph_store") or {}
    deterministic_path = write_json(backend_dir / "in_memory.json", deterministic)
    graph_path = write_json(backend_dir / "graph_store.json", graph)
    report_json = write_json(output_path / "runtime_backend_consistency_report.json", report)
    traces_jsonl = write_jsonl(output_path / "runtime_backend_consistency_traces.jsonl", (deterministic.get("traces") or []) + (graph.get("traces") or []))
    records_csv = write_csv(output_path / "runtime_backend_consistency_records.csv", (deterministic.get("records") or []) + (graph.get("records") or []))
    markdown_path = write_markdown(output_path / "runtime_backend_consistency_report.md", _render_markdown(report))
    manifest = {
        "snapshot_id": report.get("snapshot_id"),
        "parent_snapshot": report.get("parent_snapshot"),
        "evaluation_type": report.get("evaluation_type"),
        "runtime_contract": (report.get("fixture") or {}).get("runtime_contract"),
        "fixture_path": (report.get("fixture") or {}).get("path"),
        "fixture_hash": (report.get("fixture") or {}).get("hash"),
        "backends": list(report.get("backends_evaluated") or []),
    }
    manifest_path = write_json(output_path / "runtime_backend_consistency_manifest.json", manifest)
    return {
        "runtime_backend_consistency_report_json": report_json,
        "runtime_backend_consistency_traces_jsonl": traces_jsonl,
        "runtime_backend_consistency_records_csv": records_csv,
        "runtime_backend_consistency_report_md": markdown_path,
        "runtime_backend_consistency_manifest_json": manifest_path,
        "runtime_backend_in_memory_json": deterministic_path,
        "runtime_backend_graph_store_json": graph_path,
    }
