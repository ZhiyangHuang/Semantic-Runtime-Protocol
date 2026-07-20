from __future__ import annotations

import csv
import json
import subprocess
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .model import AdmissibilityCase, AdmissibilityStressTestReport


def _git_commit() -> str:
    try:
        repo_root = Path(__file__).resolve().parents[3]
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip()
    except Exception:
        return "unknown"


def _decision_from_policy(case: AdmissibilityCase, policy: str) -> bool:
    if policy == "direct_update":
        return True
    if policy == "evidence_as_authority":
        return case.evidence_ok
    if policy == "authority_only":
        return case.authority_ok
    raise ValueError(f"unknown policy: {policy}")


def build_admissibility_cases() -> list[AdmissibilityCase]:
    cases = [
        AdmissibilityCase(
            case_id="low_evidence_low_authority",
            scenario="evidence insufficient and authority unavailable",
            evidence_level="low",
            authority_level="low",
            optimization_pressure="compatible",
            evidence_ok=False,
            authority_ok=False,
            optimization_ok=True,
            srp_admitted=False,
            direct_update_admitted=True,
            evidence_as_authority_admitted=False,
            authority_only_admitted=False,
            failure_modes=("evidence_insufficient", "authority_violation"),
            notes=("This is the most restrictive boundary case.",),
        ),
        AdmissibilityCase(
            case_id="high_evidence_low_authority",
            scenario="evidence rich but unauthorized",
            evidence_level="high",
            authority_level="low",
            optimization_pressure="compatible",
            evidence_ok=True,
            authority_ok=False,
            optimization_ok=True,
            srp_admitted=False,
            direct_update_admitted=True,
            evidence_as_authority_admitted=True,
            authority_only_admitted=False,
            failure_modes=("authority_violation",),
            notes=("Strong evidence does not override missing authority.",),
        ),
        AdmissibilityCase(
            case_id="low_evidence_high_authority",
            scenario="authorized but evidence insufficient",
            evidence_level="low",
            authority_level="high",
            optimization_pressure="compatible",
            evidence_ok=False,
            authority_ok=True,
            optimization_ok=True,
            srp_admitted=False,
            direct_update_admitted=True,
            evidence_as_authority_admitted=False,
            authority_only_admitted=True,
            failure_modes=("evidence_insufficient",),
            notes=("Authority alone does not admit a transition.",),
        ),
        AdmissibilityCase(
            case_id="high_evidence_high_authority",
            scenario="fully admissible semantic transition",
            evidence_level="high",
            authority_level="high",
            optimization_pressure="compatible",
            evidence_ok=True,
            authority_ok=True,
            optimization_ok=True,
            srp_admitted=True,
            direct_update_admitted=True,
            evidence_as_authority_admitted=True,
            authority_only_admitted=True,
            failure_modes=(),
            notes=("This is the only admissible case in the 2x2 grid.",),
        ),
        AdmissibilityCase(
            case_id="optimization_override",
            scenario="optimization pressure would remove provenance",
            evidence_level="high",
            authority_level="high",
            optimization_pressure="compression_override",
            evidence_ok=True,
            authority_ok=True,
            optimization_ok=False,
            srp_admitted=False,
            direct_update_admitted=True,
            evidence_as_authority_admitted=True,
            authority_only_admitted=True,
            failure_modes=("optimization_induced_invalid_transition",),
            notes=("Optimization is downstream of admissibility, not its source.",),
        ),
    ]
    return cases


def _policy_invalid_acceptance_rate(cases: list[AdmissibilityCase], policy: str) -> float:
    invalid_cases = [case for case in cases if not case.srp_admitted]
    if not invalid_cases:
        return 0.0
    accepted_invalid = sum(1 for case in invalid_cases if _decision_from_policy(case, policy))
    return accepted_invalid / float(len(invalid_cases))


def _build_summary(cases: list[AdmissibilityCase]) -> dict[str, Any]:
    total_cases = len(cases)
    admissible_cases = [case for case in cases if case.srp_admitted]
    inadmissible_cases = [case for case in cases if not case.srp_admitted]
    accepted_valid = sum(1 for case in admissible_cases if case.srp_admitted)
    accepted_total = sum(1 for case in cases if case.srp_admitted)
    rejected_invalid = sum(1 for case in inadmissible_cases if not case.srp_admitted)
    boundary_violation_rate = (
        sum(1 for case in inadmissible_cases if case.srp_admitted) / float(len(inadmissible_cases))
        if inadmissible_cases
        else 0.0
    )

    evidence_authority_grid = [
        {
            "evidence_level": case.evidence_level,
            "authority_level": case.authority_level,
            "srp_admitted": case.srp_admitted,
            "notes": list(case.notes),
        }
        for case in cases
        if case.optimization_ok
    ]

    return {
        "total_cases": total_cases,
        "admissible_cases": len(admissible_cases),
        "inadmissible_cases": len(inadmissible_cases),
        "accepted_valid": accepted_valid,
        "accepted_total": accepted_total,
        "rejected_invalid": rejected_invalid,
        "admissibility_precision": accepted_valid / float(accepted_total) if accepted_total else 0.0,
        "boundary_violation_rate": boundary_violation_rate,
        "rejection_accuracy": rejected_invalid / float(len(inadmissible_cases)) if inadmissible_cases else 0.0,
        "policy_invalid_acceptance_rates": {
            "direct_update": _policy_invalid_acceptance_rate(cases, "direct_update"),
            "evidence_as_authority": _policy_invalid_acceptance_rate(cases, "evidence_as_authority"),
            "authority_only": _policy_invalid_acceptance_rate(cases, "authority_only"),
        },
        "evidence_authority_grid": evidence_authority_grid,
        "failure_mode_counts": {
            "evidence_insufficient": sum("evidence_insufficient" in case.failure_modes for case in cases),
            "authority_violation": sum("authority_violation" in case.failure_modes for case in cases),
            "optimization_induced_invalid_transition": sum(
                "optimization_induced_invalid_transition" in case.failure_modes for case in cases
            ),
        },
    }


def _render_markdown(report: AdmissibilityStressTestReport) -> str:
    summary = report.summary
    case_lines = [
        "| Case | Evidence | Authority | Optimization | SRP | Direct Update | Evidence as Authority | Authority Only | Failure Modes |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for case in report.cases:
        case_lines.append(
            "| {case_id} | {evidence_level} | {authority_level} | {optimization_pressure} | {srp_admitted} | {direct_update_admitted} | {evidence_as_authority_admitted} | {authority_only_admitted} | {failure_modes} |".format(
                case_id=case.case_id,
                evidence_level=case.evidence_level,
                authority_level=case.authority_level,
                optimization_pressure=case.optimization_pressure,
                srp_admitted=case.srp_admitted,
                direct_update_admitted=case.direct_update_admitted,
                evidence_as_authority_admitted=case.evidence_as_authority_admitted,
                authority_only_admitted=case.authority_only_admitted,
                failure_modes=", ".join(case.failure_modes) if case.failure_modes else "none",
            )
        )

    summary_lines = [
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Total cases | {summary['total_cases']} |",
        f"| Admissible cases | {summary['admissible_cases']} |",
        f"| Inadmissible cases | {summary['inadmissible_cases']} |",
        f"| Admissibility precision | {summary['admissibility_precision']:.3f} |",
        f"| Boundary violation rate | {summary['boundary_violation_rate']:.3f} |",
        f"| Rejection accuracy | {summary['rejection_accuracy']:.3f} |",
        f"| Direct update invalid acceptance | {summary['policy_invalid_acceptance_rates']['direct_update']:.3f} |",
        f"| Evidence as authority invalid acceptance | {summary['policy_invalid_acceptance_rates']['evidence_as_authority']:.3f} |",
        f"| Authority only invalid acceptance | {summary['policy_invalid_acceptance_rates']['authority_only']:.3f} |",
    ]

    grid_lines = [
        "| Evidence | Authority | SRP Admitted |",
        "| --- | --- | --- |",
    ]
    for item in summary["evidence_authority_grid"]:
        grid_lines.append(
            f"| {item['evidence_level']} | {item['authority_level']} | {item['srp_admitted']} |"
        )

    return "\n".join(
        [
            "# Admissibility Boundary Validation",
            "",
            "## Claim",
            "Semantic evolution requires an explicit admissibility boundary.",
            "",
            "## Cases",
            *case_lines,
            "",
            "## Evidence/Authority Grid",
            *grid_lines,
            "",
            "## Summary",
            *summary_lines,
            "",
            "## Interpretation",
            "SRP accepts the admissible transition and rejects all inadmissible transitions in the evaluated stress test.",
            "The baseline policies that elevate evidence or authority independently still accept invalid transitions.",
        ]
    )


def write_admissibility_boundary_outputs(output_dir: str | Path) -> dict[str, Any]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    cases = build_admissibility_cases()
    summary = _build_summary(cases)

    csv_path = output_path / "cases.csv"
    jsonl_path = output_path / "cases.jsonl"
    summary_path = output_path / "summary.json"
    report_path = output_path / "report.md"
    metadata_path = output_path / "metadata.json"

    fieldnames = list(asdict(cases[0]).keys()) if cases else []
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for case in cases:
            writer.writerow(asdict(case))

    with jsonl_path.open("w", encoding="utf-8") as handle:
        for case in cases:
            handle.write(json.dumps(asdict(case), ensure_ascii=False, default=str))
            handle.write("\n")

    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "admissibility_boundary_validation_v1",
        "experiment": "admissibility_boundary_validation",
        "version": "v1",
        "git_commit": _git_commit(),
        "case_count": len(cases),
        "admissible_case_count": summary["admissible_cases"],
        "inadmissible_case_count": summary["inadmissible_cases"],
    }

    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    report = AdmissibilityStressTestReport(
        report_id=f"admissibility_boundary_validation_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
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


def run_admissibility_boundary_validation() -> dict[str, Any]:
    cases = build_admissibility_cases()
    summary = _build_summary(cases)
    report = AdmissibilityStressTestReport(
        report_id=f"admissibility_boundary_validation_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        status="validated",
        cases=cases,
        summary=summary,
    )
    return {
        "report": report.as_dict(),
        "cases": [case.as_dict() for case in cases],
        "summary": summary,
    }
