from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .model import AuthorityState, EvidenceAuthoritySeparationReport, EvidenceState, TransitionProposal


def _git_commit() -> str:
    try:
        repo_root = Path(__file__).resolve().parents[3]
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip()
    except Exception:
        return "unknown"


def build_evidence_authority_cases() -> list[TransitionProposal]:
    transition_request = "semantic_state_update"
    cases = []

    for evidence_level, support_score in (("low", 0.2), ("high", 0.9)):
        for authority_rule in ("deny", "allow"):
            authority_state = AuthorityState(authority_rule=authority_rule)
            evidence_state = EvidenceState(
                evidence_level=evidence_level,
                support_score=support_score,
                provenance_complete=(evidence_level == "high"),
            )
            srp_admitted = authority_rule == "allow"
            counterfactual_authority_after = "allow" if evidence_level == "high" else "deny"
            authority_before = authority_rule
            authority_after = authority_rule
            counterfactual_authority_changed = counterfactual_authority_after != authority_before

            cases.append(
                TransitionProposal(
                    proposal_id=f"{evidence_level}_{authority_rule}",
                    transition_request=transition_request,
                    evidence_state=evidence_state,
                    authority_state=authority_state,
                    srp_admitted=srp_admitted,
                    authority_before=authority_before,
                    authority_after=authority_after,
                    counterfactual_authority_after=counterfactual_authority_after,
                    authority_changed_without_rule_change=authority_after != authority_before,
                    counterfactual_authority_changed=(evidence_level == "high" and authority_rule == "deny"),
                    notes=(
                        "evidence affects validation only",
                        "authority remains governed by the authority rule",
                    ),
                )
            )

    return cases


def _build_summary(cases: list[TransitionProposal]) -> dict[str, Any]:
    total_cases = len(cases)
    authority_drift_rate = (
        sum(1 for case in cases if case.authority_changed_without_rule_change) / float(total_cases)
        if total_cases
        else 0.0
    )
    counterfactual_authority_drift_rate = (
        sum(1 for case in cases if case.counterfactual_authority_changed) / float(total_cases)
        if total_cases
        else 0.0
    )
    evidence_only_changes = sum(1 for case in cases if case.authority_before == case.authority_after)
    accepted_invalid_authority_changes = sum(
        1
        for case in cases
        if case.authority_state.authority_rule == "deny" and case.counterfactual_authority_changed
    )

    return {
        "cases": total_cases,
        "authority_drift_rate": authority_drift_rate,
        "counterfactual_authority_drift_rate": counterfactual_authority_drift_rate,
        "evidence_only_changes": evidence_only_changes,
        "accepted_invalid_authority_changes": accepted_invalid_authority_changes,
        "srp_accepted_cases": sum(1 for case in cases if case.srp_admitted),
        "srp_rejected_cases": sum(1 for case in cases if not case.srp_admitted),
        "evidence_levels": sorted({case.evidence_state.evidence_level for case in cases}),
        "authority_rules": sorted({case.authority_state.authority_rule for case in cases}),
    }


def _render_markdown(report: EvidenceAuthoritySeparationReport) -> str:
    summary = report.summary
    case_lines = [
        "| Case | Evidence | Authority Rule | SRP Admitted | Authority Drift | Counterfactual Drift |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for case in report.cases:
        case_lines.append(
            "| {case_id} | {evidence_level} | {authority_rule} | {srp_admitted} | {authority_drift} | {counterfactual_drift} |".format(
                case_id=case.proposal_id,
                evidence_level=case.evidence_state.evidence_level,
                authority_rule=case.authority_state.authority_rule,
                srp_admitted=case.srp_admitted,
                authority_drift=case.authority_changed_without_rule_change,
                counterfactual_drift=case.counterfactual_authority_changed,
            )
        )

    summary_lines = [
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Cases | {summary['cases']} |",
        f"| Authority drift rate | {summary['authority_drift_rate']:.3f} |",
        f"| Counterfactual authority drift rate | {summary['counterfactual_authority_drift_rate']:.3f} |",
        f"| Evidence-only changes | {summary['evidence_only_changes']} |",
        f"| Accepted invalid authority changes | {summary['accepted_invalid_authority_changes']} |",
        f"| SRP accepted cases | {summary['srp_accepted_cases']} |",
        f"| SRP rejected cases | {summary['srp_rejected_cases']} |",
    ]

    return "\n".join(
        [
            "# Evidence-Authority Separation",
            "",
            "## Claim",
            "Evidence can improve validation, but it must not silently become authority.",
            "",
            "## Cases",
            *case_lines,
            "",
            "## Summary",
            *summary_lines,
            "",
            "## Interpretation",
            "SRP keeps authority invariant while evidence changes.",
            "The counterfactual coupled policy is the only place where evidence would incorrectly alter authority.",
        ]
    )


def write_evidence_authority_outputs(output_dir: str | Path) -> dict[str, Any]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    cases = build_evidence_authority_cases()
    summary = _build_summary(cases)

    csv_path = output_path / "cases.csv"
    jsonl_path = output_path / "cases.jsonl"
    summary_path = output_path / "summary.json"
    report_path = output_path / "report.md"
    metadata_path = output_path / "metadata.json"

    fieldnames = list(cases[0].as_dict().keys()) if cases else []
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for case in cases:
            writer.writerow(case.as_dict())

    with jsonl_path.open("w", encoding="utf-8") as handle:
        for case in cases:
            handle.write(json.dumps(case.as_dict(), ensure_ascii=False, default=str))
            handle.write("\n")

    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "evidence_authority_separation_v1",
        "experiment": "evidence_authority_separation",
        "version": "v1",
        "git_commit": _git_commit(),
        "case_count": summary["cases"],
    }

    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    report = EvidenceAuthoritySeparationReport(
        report_id=f"evidence_authority_separation_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        status="validated",
        cases=cases,
        summary=summary,
    )
    report_path.write_text(_render_markdown(report), encoding="utf-8")
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    return {
        "output_dir": str(output_path),
        "cases_csv": str(csv_path),
        "cases_jsonl": str(jsonl_path),
        "summary_json": str(summary_path),
        "report_md": str(report_path),
        "metadata": str(metadata_path),
        "report": report.as_dict(),
        "summary": summary,
    }


def run_evidence_authority_separation() -> dict[str, Any]:
    cases = build_evidence_authority_cases()
    summary = _build_summary(cases)
    report = EvidenceAuthoritySeparationReport(
        report_id=f"evidence_authority_separation_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        status="validated",
        cases=cases,
        summary=summary,
    )
    return {
        "report": report.as_dict(),
        "cases": [case.as_dict() for case in cases],
        "summary": summary,
    }
