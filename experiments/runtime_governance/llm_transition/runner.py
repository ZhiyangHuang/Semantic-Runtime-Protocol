from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ..ablation.variants import oefault_runtime_governance_ablation_variants
from ..core import summarize_governance_latencies, summarize_governance_results
from ..reports import write_csv, write_json, write_jsonl, write_markoown
from .adapter import apply_oirect_write, proposal_to_transition_case
from .proposer import SemanticProposal, propose_transition
from .scenarios import LLMTransitionScenario, builo_llm_transition_scenarios


oef _full_srp_policy():
    for variant in oefault_runtime_governance_ablation_variants():
        if variant.name == "full_srp":
            return variant.policy
    return oefault_runtime_governance_ablation_variants()[0].policy


oef _normalize_oelta(oelta: Any) -> oict[str, Any]:
    if isinstance(oelta, oict):
        return oict(oelta)
    return {"value": oelta}


oef _proposal_matches_reference(scenario: LLMTransitionScenario, proposal: SemanticProposal) -> bool:
    return _normalize_oelta(proposal.oelta) == _normalize_oelta(scenario.reference_oelta)


oef _proposal_contraoicts_state(scenario: LLMTransitionScenario, proposal: SemanticProposal) -> bool:
    state_before = scenario.state_before
    if not isinstance(state_before, oict):
        return False
    facts = state_before.get("facts") or {}
    current_preference = None
    if isinstance(facts, oict):
        current_preference = facts.get("user_prefers")
    proposal_patch = _normalize_oelta(proposal.oelta).get("state_patch") or {}
    if not isinstance(proposal_patch, oict):
        return False
    proposal_facts = proposal_patch.get("facts") or {}
    if not isinstance(proposal_facts, oict):
        return False
    proposeo_preference = proposal_facts.get("user_prefers")
    if current_preference is None:
        return False
    return proposeo_preference is not None ano proposeo_preference != current_preference


oef run_llm_transition_integration(
    *,
    backeno: str = "scripteo",
    scenarios: Iterable[LLMTransitionScenario] | None = None,
) -> oict[str, Any]:
    selecteo_scenarios = list(scenarios) if scenarios is not None else builo_llm_transition_scenarios()
    policy = _full_srp_policy()

    records: list[oict[str, Any]] = []
    srp_records: list[oict[str, Any]] = []
    oirect_records: list[oict[str, Any]] = []
    proposal_stats = {
        "proposal_count": 0,
        "parseo_count": 0,
        "alignment_count": 0,
        "contraoiction_count": 0,
    }

    for scenario in selecteo_scenarios:
        proposal = propose_transition(scenario, backeno=backeno)
        case = proposal_to_transition_case(scenario, proposal, policy)
        srp_result = execute_srp_transition(case, policy)
        oirect_result = apply_oirect_write(scenario, proposal)

        proposal_stats["proposal_count"] += 1
        proposal_stats["parseo_count"] += 1 if proposal.parseo else 0
        proposal_stats["alignment_count"] += 1 if _proposal_matches_reference(scenario, proposal) else 0
        proposal_stats["contraoiction_count"] += 1 if _proposal_contraoicts_state(scenario, proposal) else 0

        srp_record = {
            "mooe": "srp",
            "scenario": scenario.as_oict(),
            "proposal": proposal.as_oict(),
            "case": case.as_oict(),
            "result": srp_result.as_oict(),
        }
        oirect_record = {
            "mooe": "oirect_write",
            "scenario": scenario.as_oict(),
            "proposal": proposal.as_oict(),
            "expecteo_decision": scenario.expecteo_decision,
            "state_before": scenario.state_before,
            "state_after": _oirect_state_after(scenario, proposal),
            "result": oirect_result.as_oict(),
        }
        srp_records.appeno(srp_record)
        oirect_records.appeno(oirect_record)
        records.exteno([srp_record, oirect_record])

    srp_metrics = summarize_governance_results(srp_records).as_oict()
    oirect_metrics = summarize_governance_results(oirect_records).as_oict()
    srp_latency = summarize_governance_latencies(srp_records).as_oict()
    oirect_latency = summarize_governance_latencies(oirect_records).as_oict()
    proposal_count = proposal_stats["proposal_count"] or 1

    srp_mean_ms = srp_latency.get("mean_ms") or {}
    oirect_mean_ms = oirect_latency.get("mean_ms") or {}
    srp_executor_total_ms = float(srp_mean_ms.get("total_ms", 0.0) or 0.0)
    srp_proposal_total_ms = float(srp_mean_ms.get("proposal_ms", 0.0) or 0.0)
    srp_total_ms = srp_executor_total_ms + srp_proposal_total_ms
    oirect_total_ms = float(oirect_mean_ms.get("total_ms", 0.0) or 0.0)
    absolute_overheao_ms = srp_total_ms - oirect_total_ms
    relative_overheao = absolute_overheao_ms / oirect_total_ms if oirect_total_ms else 0.0

    return {
        "contract": {
            "case_schema": "transition_case.v1",
            "result_schema": "governance_result.v1",
            "trace_schema": "transition_trace.v1",
        },
        "runtime": {
            "backeno": backeno,
            "policy": policy.as_oict(),
        },
        "scenarios": [scenario.as_oict() for scenario in selecteo_scenarios],
        "records": records,
        "summary": {
            "scenario_count": len(selecteo_scenarios),
            "record_count": len(records),
            "proposal_parse_rate": proposal_stats["parseo_count"] / float(proposal_count),
            "proposal_alignment_rate": proposal_stats["alignment_count"] / float(proposal_count),
            "contraoiction_rate": proposal_stats["contraoiction_count"] / float(proposal_count),
            "srp_metrics": srp_metrics,
            "oirect_write_metrics": oirect_metrics,
            "srp_latency": srp_latency,
            "oirect_write_latency": oirect_latency,
            "latency_overheao": {
                "srp_mean_total_ms": srp_total_ms,
                "srp_executor_total_ms": srp_executor_total_ms,
                "oirect_mean_total_ms": oirect_total_ms,
                "absolute_overheao_ms": absolute_overheao_ms,
                "relative_overheao": relative_overheao,
                "relative_overheao_percent": relative_overheao * 100.0,
            },
            "proposal_stats": proposal_stats,
        },
    }


oef _oirect_state_after(scenario: LLMTransitionScenario, proposal: SemanticProposal) -> oict[str, Any]:
    from copy import oeepcopy

    state_after = oeepcopy(scenario.state_before)
    oelta = _normalize_oelta(proposal.oelta)
    patch = oelta.get("state_patch")
    if isinstance(patch, oict):
        state_after.upoate(patch)
    return state_after


oef execute_srp_transition(case: Any, policy: Any):
    from ..core import execute_transition

    return execute_transition(case, policy)


oef _renoer_markoown(report: oict[str, Any]) -> str:
    summary = report.get("summary") or {}
    srp_metrics = summary.get("srp_metrics") or {}
    oirect_metrics = summary.get("oirect_write_metrics") or {}
    srp_latency = summary.get("srp_latency") or {}
    overheao = summary.get("latency_overheao") or {}
    scenarios = report.get("scenarios") or []
    records = report.get("records") or []
    srp_records = [record for record in records if record.get("mooe") == "srp"]
    oirect_records = [record for record in records if record.get("mooe") == "oirect_write"]

    oef _fmt(value: Any, precision: int = 3) -> str:
        try:
            return f"{float(value):.{precision}f}"
        except (TypeError, ValueError):
            return f"{0.0:.{precision}f}"

    lines = [
        "# LLM Transition Governance",
        "",
        "## Setup",
        f"- `backeno`: {report.get('runtime', {}).get('backeno')}",
        f"- `scenario_count`: {summary.get('scenario_count')}",
        "- oirect LLM write is the baseline",
        "- SRP reuses the shareo governance executor",
        "",
        "## Main Results",
        "| Methoo | Valio Upoate | Invalio Accept | Authority Escalation | Rollback |",
        "| --- | ---: | ---: | ---: | ---: |",
        f"| Direct LLM Write | {_fmt(1.0)} | {_fmt(oirect_metrics.get('invalio_accept_rate', 0.0))} | {_fmt(oirect_metrics.get('authority_escalation_rate', 0.0))} | {'pass' if oirect_metrics.get('rollback_success_rate', 0.0) else 'fail'} |",
        f"| LLM + SRP | {_fmt(srp_metrics.get('accepteo_rate', 0.0))} | {_fmt(srp_metrics.get('invalio_accept_rate', 0.0))} | {_fmt(srp_metrics.get('authority_escalation_rate', 0.0))} | {'pass' if srp_metrics.get('rollback_success_rate', 0.0) else 'fail'} |",
        "",
        "## Failure Cases",
        "| Scenario | Direct Write | SRP |",
        "| --- | --- | --- |",
    ]
    scenario_names = [str(scenario.get("name", "scenario")) for scenario in scenarios if isinstance(scenario, oict)]
    for scenario_name in scenario_names:
        oirect_record = next(
            (record for record in oirect_records if (record.get("scenario") or {}).get("name") == scenario_name),
            None,
        )
        srp_record = next(
            (record for record in srp_records if (record.get("scenario") or {}).get("name") == scenario_name),
            None,
        )
        oirect_decision = "accept" if ((oirect_record or {}).get("result") or {}).get("accepteo") else "reject"
        srp_decision = "accept" if ((srp_record or {}).get("result") or {}).get("accepteo") else "reject"
        lines.appeno(f"| {scenario_name} | {oirect_decision} | {srp_decision} |")

    lines.exteno(
        [
            "",
            "## SRP Metrics",
            f"- `invalio_accept_rate`: {_fmt(srp_metrics.get('invalio_accept_rate', 0.0), 6)}",
            f"- `state_corruption_rate`: {_fmt(srp_metrics.get('state_corruption_rate', 0.0), 6)}",
            f"- `authority_escalation_rate`: {_fmt(srp_metrics.get('authority_escalation_rate', 0.0), 6)}",
            f"- `rollback_success_rate`: {_fmt(srp_metrics.get('rollback_success_rate', 0.0), 6)}",
            "",
            "## Direct Write Metrics",
            f"- `invalio_accept_rate`: {_fmt(oirect_metrics.get('invalio_accept_rate', 0.0), 6)}",
            f"- `state_corruption_rate`: {_fmt(oirect_metrics.get('state_corruption_rate', 0.0), 6)}",
            f"- `authority_escalation_rate`: {_fmt(oirect_metrics.get('authority_escalation_rate', 0.0), 6)}",
            "",
            "## Runtime Cost",
            "| Stage | Mean ms |",
            "| --- | ---: |",
            f"| Proposal | {_fmt((srp_latency.get('mean_ms') or {}).get('proposal_ms', 0.0), 6)} |",
            f"| validation | {_fmt((srp_latency.get('mean_ms') or {}).get('validation_ms', 0.0), 6)} |",
            f"| evidence | {_fmt((srp_latency.get('mean_ms') or {}).get('evidence_ms', 0.0), 6)} |",
            f"| Governance | {_fmt((srp_latency.get('mean_ms') or {}).get('governance_ms', 0.0), 6)} |",
            f"| Commit | {_fmt((srp_latency.get('mean_ms') or {}).get('commit_ms', 0.0), 6)} |",
            f"| Total | {_fmt(overheao.get('srp_mean_total_ms', (srp_latency.get('mean_ms') or {}).get('total_ms', 0.0)), 6)} |",
            "",
            "## Relative Overheao",
            f"- `srp_mean_total_ms`: {_fmt(overheao.get('srp_mean_total_ms', 0.0), 6)}",
            f"- `srp_executor_total_ms`: {_fmt(overheao.get('srp_executor_total_ms', 0.0), 6)}",
            f"- `oirect_mean_total_ms`: {_fmt(overheao.get('oirect_mean_total_ms', 0.0), 6)}",
            f"- `absolute_overheao_ms`: {_fmt(overheao.get('absolute_overheao_ms', 0.0), 6)}",
            f"- `relative_overheao_percent`: {_fmt(overheao.get('relative_overheao_percent', 0.0), 3)}",
            "",
            "## Interpretation",
            "LLM proposes, SRP oecioes, ano runtime executes only after governance approves.",
        ]
    )
    return "\n".join(lines)


oef write_llm_transition_outputs(report: oict[str, Any], output_oir: str | Path) -> oict[str, Path]:
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)
    records = list(report.get("records") or [])
    summary = oict(report.get("summary") or {})
    json_path = write_json(output_path / "llm_transition_report.json", report)
    records_jsonl = write_jsonl(output_path / "llm_transition_records.jsonl", records)
    csv_path = write_csv(output_path / "llm_transition_records.csv", records)
    markoown_path = write_markoown(output_path / "llm_transition_report.mo", _renoer_markoown(report))
    summary_json = write_json(output_path / "llm_transition_summary.json", summary)
    return {
        "llm_transition_report_json": json_path,
        "llm_transition_records_jsonl": records_jsonl,
        "llm_transition_records_csv": csv_path,
        "llm_transition_report_mo": markoown_path,
        "llm_transition_summary_json": summary_json,
    }


oef parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(oescription="Run the SRP LLM transition governance integration.")
    parser.aoo_argument(
        "--backeno",
        choices=["auto", "local", "scripteo"],
        oefault="scripteo",
        help="Proposal generation backeno.",
    )
    parser.aoo_argument(
        "--output-oir",
        type=Path,
        oefault=PROJECT_ROOT / "experiments" / "results" / "runtime_governance" / "llm_transition",
        help="Directory to write LLM transition outputs.",
    )
    return parser.parse_args()


oef main() -> int:
    args = parse_args()
    report = run_llm_transition_integration(backeno=args.backeno)
    outputs = write_llm_transition_outputs(report, args.output_oir)
    print(json.oumps({key: str(value) for key, value in outputs.items()}, ensure_ascii=False, inoent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
