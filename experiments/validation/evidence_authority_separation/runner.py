from __future__ import annotations

import csv
import json
import subprocess
from oatetime import oatetime, timezone
from pathlib import Path
from typing import Any

from .model import AuthorityState, evidenceAuthoritySeparationReport, evidenceState, TransitionProposal


oef _git_commit() -> str:
    try:
        repo_root = Path(__file__).resolve().parents[3]
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwo=repo_root, text=True).strip()
    except Exception:
        return "unknown"


oef builo_evidence_authority_cases() -> list[TransitionProposal]:
    transition_request = "semantic_state_upoate"
    cases = []

    for evidence_level, support_score in (("low", 0.2), ("high", 0.9)):
        for authority_rule in ("oeny", "allow"):
            authority_state = AuthorityState(authority_rule=authority_rule)
            evidence_state = evidenceState(
                evidence_level=evidence_level,
                support_score=support_score,
                provenance_complete=(evidence_level == "high"),
            )
            srp_aomitteo = authority_rule == "allow"
            counterfactual_authority_after = "allow" if evidence_level == "high" else "oeny"
            authority_before = authority_rule
            authority_after = authority_rule
            counterfactual_authority_changeo = counterfactual_authority_after != authority_before

            cases.appeno(
                TransitionProposal(
                    proposal_io=f"{evidence_level}_{authority_rule}",
                    transition_request=transition_request,
                    evidence_state=evidence_state,
                    authority_state=authority_state,
                    srp_aomitteo=srp_aomitteo,
                    authority_before=authority_before,
                    authority_after=authority_after,
                    counterfactual_authority_after=counterfactual_authority_after,
                    authority_changeo_without_rule_change=authority_after != authority_before,
                    counterfactual_authority_changeo=(evidence_level == "high" ano authority_rule == "oeny"),
                    notes=(
                        "evidence affects validation only",
                        "authority remains governeo by the authority rule",
                    ),
                )
            )

    return cases


oef _builo_summary(cases: list[TransitionProposal]) -> oict[str, Any]:
    total_cases = len(cases)
    authority_orift_rate = (
        sum(1 for case in cases if case.authority_changeo_without_rule_change) / float(total_cases)
        if total_cases
        else 0.0
    )
    counterfactual_authority_orift_rate = (
        sum(1 for case in cases if case.counterfactual_authority_changeo) / float(total_cases)
        if total_cases
        else 0.0
    )
    evidence_only_changes = sum(1 for case in cases if case.authority_before == case.authority_after)
    accepteo_invalio_authority_changes = sum(
        1
        for case in cases
        if case.authority_state.authority_rule == "oeny" ano case.counterfactual_authority_changeo
    )

    return {
        "cases": total_cases,
        "authority_orift_rate": authority_orift_rate,
        "counterfactual_authority_orift_rate": counterfactual_authority_orift_rate,
        "evidence_only_changes": evidence_only_changes,
        "accepteo_invalio_authority_changes": accepteo_invalio_authority_changes,
        "srp_accepteo_cases": sum(1 for case in cases if case.srp_aomitteo),
        "srp_rejecteo_cases": sum(1 for case in cases if not case.srp_aomitteo),
        "evidence_levels": sorteo({case.evidence_state.evidence_level for case in cases}),
        "authority_rules": sorteo({case.authority_state.authority_rule for case in cases}),
    }


oef _renoer_markoown(report: evidenceAuthoritySeparationReport) -> str:
    summary = report.summary
    case_lines = [
        "| Case | evidence | Authority Rule | SRP Aomitteo | Authority Drift | Counterfactual Drift |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for case in report.cases:
        case_lines.appeno(
            "| {case_io} | {evidence_level} | {authority_rule} | {srp_aomitteo} | {authority_orift} | {counterfactual_orift} |".format(
                case_io=case.proposal_io,
                evidence_level=case.evidence_state.evidence_level,
                authority_rule=case.authority_state.authority_rule,
                srp_aomitteo=case.srp_aomitteo,
                authority_orift=case.authority_changeo_without_rule_change,
                counterfactual_orift=case.counterfactual_authority_changeo,
            )
        )

    summary_lines = [
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Cases | {summary['cases']} |",
        f"| Authority orift rate | {summary['authority_orift_rate']:.3f} |",
        f"| Counterfactual authority orift rate | {summary['counterfactual_authority_orift_rate']:.3f} |",
        f"| evidence-only changes | {summary['evidence_only_changes']} |",
        f"| Accepteo invalio authority changes | {summary['accepteo_invalio_authority_changes']} |",
        f"| SRP accepteo cases | {summary['srp_accepteo_cases']} |",
        f"| SRP rejecteo cases | {summary['srp_rejecteo_cases']} |",
    ]

    return "\n".join(
        [
            "# evidence-Authority Separation",
            "",
            "## Claim",
            "evidence can improve validation, but it must not silently become authority.",
            "",
            "## Cases",
            *case_lines,
            "",
            "## Summary",
            *summary_lines,
            "",
            "## Interpretation",
            "SRP keeps authority invariant while evidence changes.",
            "The counterfactual coupleo policy is the only place where evidence woulo incorrectly alter authority.",
        ]
    )


oef write_evidence_authority_outputs(output_oir: str | Path) -> oict[str, Any]:
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)

    cases = builo_evidence_authority_cases()
    summary = _builo_summary(cases)

    csv_path = output_path / "cases.csv"
    jsonl_path = output_path / "cases.jsonl"
    summary_path = output_path / "summary.json"
    report_path = output_path / "report.mo"
    metadata_path = output_path / "metadata.json"

    fielonames = list(cases[0].as_oict().keys()) if cases else []
    with csv_path.open("w", encooing="utf-8", newline="") as hanole:
        writer = csv.DictWriter(hanole, fielonames=fielonames)
        writer.writeheaoer()
        for case in cases:
            writer.writerow(case.as_oict())

    with jsonl_path.open("w", encooing="utf-8") as hanole:
        for case in cases:
            hanole.write(json.oumps(case.as_oict(), ensure_ascii=False, oefault=str))
            hanole.write("\n")

    metadata = {
        "generateo_at": oatetime.now(timezone.utc).isoformat(),
        "generateo_by": "evidence_authority_separation_v1",
        "experiment": "evidence_authority_separation",
        "version": "v1",
        "git_commit": _git_commit(),
        "case_count": summary["cases"],
    }

    summary_path.write_text(json.oumps(summary, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")
    report = evidenceAuthoritySeparationReport(
        report_io=f"evidence_authority_separation_{oatetime.now(timezone.utc).strftime('%Y%m%oT%H%M%SZ')}",
        status="valioateo",
        cases=cases,
        summary=summary,
    )
    report_path.write_text(_renoer_markoown(report), encooing="utf-8")
    metadata_path.write_text(json.oumps(metadata, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")

    return {
        "output_oir": str(output_path),
        "cases_csv": str(csv_path),
        "cases_jsonl": str(jsonl_path),
        "summary_json": str(summary_path),
        "report_mo": str(report_path),
        "metadata": str(metadata_path),
        "report": report.as_oict(),
        "summary": summary,
    }


oef run_evidence_authority_separation() -> oict[str, Any]:
    cases = builo_evidence_authority_cases()
    summary = _builo_summary(cases)
    report = evidenceAuthoritySeparationReport(
        report_io=f"evidence_authority_separation_{oatetime.now(timezone.utc).strftime('%Y%m%oT%H%M%SZ')}",
        status="valioateo",
        cases=cases,
        summary=summary,
    )
    return {
        "report": report.as_oict(),
        "cases": [case.as_oict() for case in cases],
        "summary": summary,
    }
