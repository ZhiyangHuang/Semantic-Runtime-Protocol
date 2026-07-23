from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ..ablation.variants import default_runtime_governance_ablation_variants
from ..core import summarize_governance_latencies, summarize_governance_results
from ..reports import write_csv, write_json, write_jsonl, write_markdown
from .adapter import apply_direct_write, proposal_to_transition_case
from .proposer import SemanticProposal, propose_transition
from .scenarios import LLMTransitionScenario, build_llm_transition_scenarios


def _full_srp_policy():
    for variant in default_runtime_governance_ablation_variants():
        if variant.name == "full_srp":
            return variant.policy
    return default_runtime_governance_ablation_variants()[0].policy


def _normalize_delta(delta: Any) -> dict[str, Any]:
    if isinstance(delta, dict):
        return dict(delta)
    return {"value": delta}


def _proposal_matches_reference(scenario: LLMTransitionScenario, proposal: SemanticProposal) -> bool:
    return _normalize_delta(proposal.delta) == _normalize_delta(scenario.reference_delta)


def _proposal_contradicts_state(scenario: LLMTransitionScenario, proposal: SemanticProposal) -> bool:
    state_before = scenario.state_before
    if not isinstance(state_before, dict):
        return False
    facts = state_before.get("facts") or {}
    current_preference = None
    if isinstance(facts, dict):
        current_preference = facts.get("user_prefers")
    proposal_patch = _normalize_delta(proposal.delta).get("state_patch") or {}
    if not isinstance(proposal_patch, dict):
        return False
    proposal_facts = proposal_patch.get("facts") or {}
    if not isinstance(proposal_facts, dict):
        return False
    proposed_preference = proposal_facts.get("user_prefers")
    if current_preference is None:
        return False
    return proposed_preference is not None and proposed_preference != current_preference


def run_llm_transition_integration(
    *,
    backend: str = "scripted",
    scenarios: Iterable[LLMTransitionScenario] | None = None,
) -> dict[str, Any]:
    selected_scenarios = list(scenarios) if scenarios is not None else build_llm_transition_scenarios()
    policy = _full_srp_policy()

    records: list[dict[str, Any]] = []
    srp_records: list[dict[str, Any]] = []
    direct_records: list[dict[str, Any]] = []
    proposal_stats = {
        "proposal_count": 0,
        "parsed_count": 0,
        "alignment_count": 0,
        "contradiction_count": 0,
    }

    for scenario in selected_scenarios:
        proposal = propose_transition(scenario, backend=backend)
        case = proposal_to_transition_case(scenario, proposal, policy)
        srp_result = execute_srp_transition(case, policy)
        direct_result = apply_direct_write(scenario, proposal)

        proposal_stats["proposal_count"] += 1
        proposal_stats["parsed_count"] += 1 if proposal.parsed else 0
        proposal_stats["alignment_count"] += 1 if _proposal_matches_reference(scenario, proposal) else 0
        proposal_stats["contradiction_count"] += 1 if _proposal_contradicts_state(scenario, proposal) else 0

        srp_record = {
            "mode": "srp",
            "scenario": scenario.as_dict(),
            "proposal": proposal.as_dict(),
            "case": case.as_dict(),
            "result": srp_result.as_dict(),
        }
        direct_record = {
            "mode": "direct_write",
            "scenario": scenario.as_dict(),
            "proposal": proposal.as_dict(),
            "expected_decision": scenario.expected_decision,
            "state_before": scenario.state_before,
            "state_after": _direct_state_after(scenario, proposal),
            "result": direct_result.as_dict(),
        }
        srp_records.append(srp_record)
        direct_records.append(direct_record)
        records.extend([srp_record, direct_record])

    srp_metrics = summarize_governance_results(srp_records).as_dict()
    direct_metrics = summarize_governance_results(direct_records).as_dict()
    srp_latency = summarize_governance_latencies(srp_records).as_dict()
    direct_latency = summarize_governance_latencies(direct_records).as_dict()
    proposal_count = proposal_stats["proposal_count"] or 1

    srp_mean_ms = srp_latency.get("mean_ms") or {}
    direct_mean_ms = direct_latency.get("mean_ms") or {}
    srp_executor_total_ms = float(srp_mean_ms.get("total_ms", 0.0) or 0.0)
    srp_proposal_total_ms = float(srp_mean_ms.get("proposal_ms", 0.0) or 0.0)
    srp_total_ms = srp_executor_total_ms + srp_proposal_total_ms
    direct_total_ms = float(direct_mean_ms.get("total_ms", 0.0) or 0.0)
    absolute_overhead_ms = srp_total_ms - direct_total_ms
    relative_overhead = absolute_overhead_ms / direct_total_ms if direct_total_ms else 0.0

    return {
        "contract": {
            "case_schema": "transition_case.v1",
            "result_schema": "governance_result.v1",
            "trace_schema": "transition_trace.v1",
        },
        "runtime": {
            "backend": backend,
            "policy": policy.as_dict(),
        },
        "scenarios": [scenario.as_dict() for scenario in selected_scenarios],
        "records": records,
        "summary": {
            "scenario_count": len(selected_scenarios),
            "record_count": len(records),
            "proposal_parse_rate": proposal_stats["parsed_count"] / float(proposal_count),
            "proposal_alignment_rate": proposal_stats["alignment_count"] / float(proposal_count),
            "contradiction_rate": proposal_stats["contradiction_count"] / float(proposal_count),
            "srp_metrics": srp_metrics,
            "direct_write_metrics": direct_metrics,
            "srp_latency": srp_latency,
            "direct_write_latency": direct_latency,
            "latency_overhead": {
                "srp_mean_total_ms": srp_total_ms,
                "srp_executor_total_ms": srp_executor_total_ms,
                "direct_mean_total_ms": direct_total_ms,
                "absolute_overhead_ms": absolute_overhead_ms,
                "relative_overhead": relative_overhead,
                "relative_overhead_percent": relative_overhead * 100.0,
            },
            "proposal_stats": proposal_stats,
        },
    }


def _direct_state_after(scenario: LLMTransitionScenario, proposal: SemanticProposal) -> dict[str, Any]:
    from copy import deepcopy

    state_after = deepcopy(scenario.state_before)
    delta = _normalize_delta(proposal.delta)
    patch = delta.get("state_patch")
    if isinstance(patch, dict):
        state_after.update(patch)
    return state_after


def execute_srp_transition(case: Any, policy: Any):
    from ..core import execute_transition

    return execute_transition(case, policy)


def _render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary") or {}
    srp_metrics = summary.get("srp_metrics") or {}
    direct_metrics = summary.get("direct_write_metrics") or {}
    srp_latency = summary.get("srp_latency") or {}
    overhead = summary.get("latency_overhead") or {}
    scenarios = report.get("scenarios") or []
    records = report.get("records") or []
    srp_records = [record for record in records if record.get("mode") == "srp"]
    direct_records = [record for record in records if record.get("mode") == "direct_write"]

    def _fmt(value: Any, precision: int = 3) -> str:
        try:
            return f"{float(value):.{precision}f}"
        except (TypeError, ValueError):
            return f"{0.0:.{precision}f}"

    lines = [
        "# LLM Transition Governance",
        "",
        "## Setup",
        f"- `backend`: {report.get('runtime', {}).get('backend')}",
        f"- `scenario_count`: {summary.get('scenario_count')}",
        "- direct LLM write is the baseline",
        "- SRP reuses the shared governance executor",
        "",
        "## Main Results",
        "| Method | Valid Update | Invalid Accept | Authority Escalation | Rollback |",
        "| --- | ---: | ---: | ---: | ---: |",
        f"| Direct LLM Write | {_fmt(1.0)} | {_fmt(direct_metrics.get('invalid_accept_rate', 0.0))} | {_fmt(direct_metrics.get('authority_escalation_rate', 0.0))} | {'pass' if direct_metrics.get('rollback_success_rate', 0.0) else 'fail'} |",
        f"| LLM + SRP | {_fmt(srp_metrics.get('accepted_rate', 0.0))} | {_fmt(srp_metrics.get('invalid_accept_rate', 0.0))} | {_fmt(srp_metrics.get('authority_escalation_rate', 0.0))} | {'pass' if srp_metrics.get('rollback_success_rate', 0.0) else 'fail'} |",
        "",
        "## Failure Cases",
        "| Scenario | Direct Write | SRP |",
        "| --- | --- | --- |",
    ]
    scenario_names = [str(scenario.get("name", "scenario")) for scenario in scenarios if isinstance(scenario, dict)]
    for scenario_name in scenario_names:
        direct_record = next(
            (record for record in direct_records if (record.get("scenario") or {}).get("name") == scenario_name),
            None,
        )
        srp_record = next(
            (record for record in srp_records if (record.get("scenario") or {}).get("name") == scenario_name),
            None,
        )
        direct_decision = "accept" if ((direct_record or {}).get("result") or {}).get("accepted") else "reject"
        srp_decision = "accept" if ((srp_record or {}).get("result") or {}).get("accepted") else "reject"
        lines.append(f"| {scenario_name} | {direct_decision} | {srp_decision} |")

    lines.extend(
        [
            "",
            "## SRP Metrics",
            f"- `invalid_accept_rate`: {_fmt(srp_metrics.get('invalid_accept_rate', 0.0), 6)}",
            f"- `state_corruption_rate`: {_fmt(srp_metrics.get('state_corruption_rate', 0.0), 6)}",
            f"- `authority_escalation_rate`: {_fmt(srp_metrics.get('authority_escalation_rate', 0.0), 6)}",
            f"- `rollback_success_rate`: {_fmt(srp_metrics.get('rollback_success_rate', 0.0), 6)}",
            "",
            "## Direct Write Metrics",
            f"- `invalid_accept_rate`: {_fmt(direct_metrics.get('invalid_accept_rate', 0.0), 6)}",
            f"- `state_corruption_rate`: {_fmt(direct_metrics.get('state_corruption_rate', 0.0), 6)}",
            f"- `authority_escalation_rate`: {_fmt(direct_metrics.get('authority_escalation_rate', 0.0), 6)}",
            "",
            "## Runtime Cost",
            "| Stage | Mean ms |",
            "| --- | ---: |",
            f"| Proposal | {_fmt((srp_latency.get('mean_ms') or {}).get('proposal_ms', 0.0), 6)} |",
            f"| Validation | {_fmt((srp_latency.get('mean_ms') or {}).get('validation_ms', 0.0), 6)} |",
            f"| Evidence | {_fmt((srp_latency.get('mean_ms') or {}).get('evidence_ms', 0.0), 6)} |",
            f"| Governance | {_fmt((srp_latency.get('mean_ms') or {}).get('governance_ms', 0.0), 6)} |",
            f"| Commit | {_fmt((srp_latency.get('mean_ms') or {}).get('commit_ms', 0.0), 6)} |",
            f"| Total | {_fmt(overhead.get('srp_mean_total_ms', (srp_latency.get('mean_ms') or {}).get('total_ms', 0.0)), 6)} |",
            "",
            "## Relative Overhead",
            f"- `srp_mean_total_ms`: {_fmt(overhead.get('srp_mean_total_ms', 0.0), 6)}",
            f"- `srp_executor_total_ms`: {_fmt(overhead.get('srp_executor_total_ms', 0.0), 6)}",
            f"- `direct_mean_total_ms`: {_fmt(overhead.get('direct_mean_total_ms', 0.0), 6)}",
            f"- `absolute_overhead_ms`: {_fmt(overhead.get('absolute_overhead_ms', 0.0), 6)}",
            f"- `relative_overhead_percent`: {_fmt(overhead.get('relative_overhead_percent', 0.0), 3)}",
            "",
            "## Interpretation",
            "LLM proposes, SRP decides, and runtime executes only after governance approves.",
        ]
    )
    return "\n".join(lines)


def write_llm_transition_outputs(report: dict[str, Any], output_dir: str | Path) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    records = list(report.get("records") or [])
    summary = dict(report.get("summary") or {})
    json_path = write_json(output_path / "llm_transition_report.json", report)
    records_jsonl = write_jsonl(output_path / "llm_transition_records.jsonl", records)
    csv_path = write_csv(output_path / "llm_transition_records.csv", records)
    markdown_path = write_markdown(output_path / "llm_transition_report.md", _render_markdown(report))
    summary_json = write_json(output_path / "llm_transition_summary.json", summary)
    return {
        "llm_transition_report_json": json_path,
        "llm_transition_records_jsonl": records_jsonl,
        "llm_transition_records_csv": csv_path,
        "llm_transition_report_md": markdown_path,
        "llm_transition_summary_json": summary_json,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SRP LLM transition governance integration.")
    parser.add_argument(
        "--backend",
        choices=["auto", "local", "scripted"],
        default="scripted",
        help="Proposal generation backend.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "experiments" / "results" / "runtime_governance" / "llm_transition",
        help="Directory to write LLM transition outputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_llm_transition_integration(backend=args.backend)
    outputs = write_llm_transition_outputs(report, args.output_dir)
    print(json.dumps({key: str(value) for key, value in outputs.items()}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
