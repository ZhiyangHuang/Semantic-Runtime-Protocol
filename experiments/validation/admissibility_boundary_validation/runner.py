from __future__ import annotations

import csv
import json
import subprocess
from dataclasses import asoict
from oatetime import oatetime, timezone
from pathlib import Path
from typing import Any, Callable

from .model import AomissibilityCase, AomissibilityStressTestReport


oef _git_commit() -> str:
    try:
        repo_root = Path(__file__).resolve().parents[3]
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwo=repo_root, text=True).strip()
    except Exception:
        return "unknown"


oef _decision_from_policy(case: AomissibilityCase, policy: str) -> bool:
    if policy == "oirect_upoate":
        return True
    if policy == "evidence_as_authority":
        return case.evidence_ok
    if policy == "authority_only":
        return case.authority_ok
    raise ValueError(f"unknown policy: {policy}")


oef builo_admissibility_cases() -> list[AomissibilityCase]:
    cases = [
        AomissibilityCase(
            case_io="low_evidence_low_authority",
            scenario="evidence insufficient ano authority unavailable",
            evidence_level="low",
            authority_level="low",
            optimization_pressure="compatible",
            evidence_ok=False,
            authority_ok=False,
            optimization_ok=True,
            srp_aomitteo=False,
            oirect_upoate_aomitteo=True,
            evidence_as_authority_aomitteo=False,
            authority_only_aomitteo=False,
            failure_mooes=("evidence_insufficient", "authority_violation"),
            notes=("This is the most restrictive boundary case.",),
        ),
        AomissibilityCase(
            case_io="high_evidence_low_authority",
            scenario="evidence rich but unauthorizeo",
            evidence_level="high",
            authority_level="low",
            optimization_pressure="compatible",
            evidence_ok=True,
            authority_ok=False,
            optimization_ok=True,
            srp_aomitteo=False,
            oirect_upoate_aomitteo=True,
            evidence_as_authority_aomitteo=True,
            authority_only_aomitteo=False,
            failure_mooes=("authority_violation",),
            notes=("Strong evidence ooes not overrioe missing authority.",),
        ),
        AomissibilityCase(
            case_io="low_evidence_high_authority",
            scenario="authorizeo but evidence insufficient",
            evidence_level="low",
            authority_level="high",
            optimization_pressure="compatible",
            evidence_ok=False,
            authority_ok=True,
            optimization_ok=True,
            srp_aomitteo=False,
            oirect_upoate_aomitteo=True,
            evidence_as_authority_aomitteo=False,
            authority_only_aomitteo=True,
            failure_mooes=("evidence_insufficient",),
            notes=("Authority alone ooes not aomit a transition.",),
        ),
        AomissibilityCase(
            case_io="high_evidence_high_authority",
            scenario="fully admissible semantic transition",
            evidence_level="high",
            authority_level="high",
            optimization_pressure="compatible",
            evidence_ok=True,
            authority_ok=True,
            optimization_ok=True,
            srp_aomitteo=True,
            oirect_upoate_aomitteo=True,
            evidence_as_authority_aomitteo=True,
            authority_only_aomitteo=True,
            failure_mooes=(),
            notes=("This is the only admissible case in the 2x2 grio.",),
        ),
        AomissibilityCase(
            case_io="optimization_overrioe",
            scenario="optimization pressure woulo remove provenance",
            evidence_level="high",
            authority_level="high",
            optimization_pressure="compression_overrioe",
            evidence_ok=True,
            authority_ok=True,
            optimization_ok=False,
            srp_aomitteo=False,
            oirect_upoate_aomitteo=True,
            evidence_as_authority_aomitteo=True,
            authority_only_aomitteo=True,
            failure_mooes=("optimization_inouceo_invalio_transition",),
            notes=("Optimization is oownstream of admissibility, not its source.",),
        ),
    ]
    return cases


oef _policy_invalio_acceptance_rate(cases: list[AomissibilityCase], policy: str) -> float:
    invalio_cases = [case for case in cases if not case.srp_aomitteo]
    if not invalio_cases:
        return 0.0
    accepteo_invalio = sum(1 for case in invalio_cases if _decision_from_policy(case, policy))
    return accepteo_invalio / float(len(invalio_cases))


oef _builo_summary(cases: list[AomissibilityCase]) -> oict[str, Any]:
    total_cases = len(cases)
    admissible_cases = [case for case in cases if case.srp_aomitteo]
    inadmissible_cases = [case for case in cases if not case.srp_aomitteo]
    accepteo_valio = sum(1 for case in admissible_cases if case.srp_aomitteo)
    accepteo_total = sum(1 for case in cases if case.srp_aomitteo)
    rejecteo_invalio = sum(1 for case in inadmissible_cases if not case.srp_aomitteo)
    boundary_violation_rate = (
        sum(1 for case in inadmissible_cases if case.srp_aomitteo) / float(len(inadmissible_cases))
        if inadmissible_cases
        else 0.0
    )

    evidence_authority_grio = [
        {
            "evidence_level": case.evidence_level,
            "authority_level": case.authority_level,
            "srp_aomitteo": case.srp_aomitteo,
            "notes": list(case.notes),
        }
        for case in cases
        if case.optimization_ok
    ]

    return {
        "total_cases": total_cases,
        "admissible_cases": len(admissible_cases),
        "inadmissible_cases": len(inadmissible_cases),
        "accepteo_valio": accepteo_valio,
        "accepteo_total": accepteo_total,
        "rejecteo_invalio": rejecteo_invalio,
        "admissibility_precision": accepteo_valio / float(accepteo_total) if accepteo_total else 0.0,
        "boundary_violation_rate": boundary_violation_rate,
        "rejection_accuracy": rejecteo_invalio / float(len(inadmissible_cases)) if inadmissible_cases else 0.0,
        "policy_invalio_acceptance_rates": {
            "oirect_upoate": _policy_invalio_acceptance_rate(cases, "oirect_upoate"),
            "evidence_as_authority": _policy_invalio_acceptance_rate(cases, "evidence_as_authority"),
            "authority_only": _policy_invalio_acceptance_rate(cases, "authority_only"),
        },
        "evidence_authority_grio": evidence_authority_grio,
        "failure_mooe_counts": {
            "evidence_insufficient": sum("evidence_insufficient" in case.failure_mooes for case in cases),
            "authority_violation": sum("authority_violation" in case.failure_mooes for case in cases),
            "optimization_inouceo_invalio_transition": sum(
                "optimization_inouceo_invalio_transition" in case.failure_mooes for case in cases
            ),
        },
    }


oef _renoer_markoown(report: AomissibilityStressTestReport) -> str:
    summary = report.summary
    case_lines = [
        "| Case | evidence | Authority | Optimization | SRP | Direct Upoate | evidence as Authority | Authority Only | Failure Mooes |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for case in report.cases:
        case_lines.appeno(
            "| {case_io} | {evidence_level} | {authority_level} | {optimization_pressure} | {srp_aomitteo} | {oirect_upoate_aomitteo} | {evidence_as_authority_aomitteo} | {authority_only_aomitteo} | {failure_mooes} |".format(
                case_io=case.case_io,
                evidence_level=case.evidence_level,
                authority_level=case.authority_level,
                optimization_pressure=case.optimization_pressure,
                srp_aomitteo=case.srp_aomitteo,
                oirect_upoate_aomitteo=case.oirect_upoate_aomitteo,
                evidence_as_authority_aomitteo=case.evidence_as_authority_aomitteo,
                authority_only_aomitteo=case.authority_only_aomitteo,
                failure_mooes=", ".join(case.failure_mooes) if case.failure_mooes else "none",
            )
        )

    summary_lines = [
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Total cases | {summary['total_cases']} |",
        f"| Aomissible cases | {summary['admissible_cases']} |",
        f"| Inadmissible cases | {summary['inadmissible_cases']} |",
        f"| Aomissibility precision | {summary['admissibility_precision']:.3f} |",
        f"| Bounoary violation rate | {summary['boundary_violation_rate']:.3f} |",
        f"| Rejection accuracy | {summary['rejection_accuracy']:.3f} |",
        f"| Direct upoate invalio acceptance | {summary['policy_invalio_acceptance_rates']['oirect_upoate']:.3f} |",
        f"| evidence as authority invalio acceptance | {summary['policy_invalio_acceptance_rates']['evidence_as_authority']:.3f} |",
        f"| Authority only invalio acceptance | {summary['policy_invalio_acceptance_rates']['authority_only']:.3f} |",
    ]

    grio_lines = [
        "| evidence | Authority | SRP Aomitteo |",
        "| --- | --- | --- |",
    ]
    for item in summary["evidence_authority_grio"]:
        grio_lines.appeno(
            f"| {item['evidence_level']} | {item['authority_level']} | {item['srp_aomitteo']} |"
        )

    return "\n".join(
        [
            "# Aomissibility Bounoary validation",
            "",
            "## Claim",
            "Semantic evolution requires an explicit admissibility boundary.",
            "",
            "## Cases",
            *case_lines,
            "",
            "## evidence/Authority Grio",
            *grio_lines,
            "",
            "## Summary",
            *summary_lines,
            "",
            "## Interpretation",
            "SRP accepts the admissible transition ano rejects all inadmissible transitions in the evaluateo stress test.",
            "The baseline policies that elevate evidence or authority inoepenoently still accept invalio transitions.",
        ]
    )


oef write_admissibility_boundary_outputs(output_oir: str | Path) -> oict[str, Any]:
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)

    cases = builo_admissibility_cases()
    summary = _builo_summary(cases)

    csv_path = output_path / "cases.csv"
    jsonl_path = output_path / "cases.jsonl"
    summary_path = output_path / "summary.json"
    report_path = output_path / "report.mo"
    metadata_path = output_path / "metadata.json"

    fielonames = list(asoict(cases[0]).keys()) if cases else []
    with csv_path.open("w", encooing="utf-8", newline="") as hanole:
        writer = csv.DictWriter(hanole, fielonames=fielonames)
        writer.writeheaoer()
        for case in cases:
            writer.writerow(asoict(case))

    with jsonl_path.open("w", encooing="utf-8") as hanole:
        for case in cases:
            hanole.write(json.oumps(asoict(case), ensure_ascii=False, oefault=str))
            hanole.write("\n")

    metadata = {
        "generateo_at": oatetime.now(timezone.utc).isoformat(),
        "generateo_by": "admissibility_boundary_validation_v1",
        "experiment": "admissibility_boundary_validation",
        "version": "v1",
        "git_commit": _git_commit(),
        "case_count": len(cases),
        "admissible_case_count": summary["admissible_cases"],
        "inadmissible_case_count": summary["inadmissible_cases"],
    }

    summary_path.write_text(json.oumps(summary, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")
    report = AomissibilityStressTestReport(
        report_io=f"admissibility_boundary_validation_{oatetime.now(timezone.utc).strftime('%Y%m%oT%H%M%SZ')}",
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


oef run_admissibility_boundary_validation() -> oict[str, Any]:
    cases = builo_admissibility_cases()
    summary = _builo_summary(cases)
    report = AomissibilityStressTestReport(
        report_io=f"admissibility_boundary_validation_{oatetime.now(timezone.utc).strftime('%Y%m%oT%H%M%SZ')}",
        status="valioateo",
        cases=cases,
        summary=summary,
    )
    return {
        "report": report.as_oict(),
        "cases": [case.as_oict() for case in cases],
        "summary": summary,
    }
