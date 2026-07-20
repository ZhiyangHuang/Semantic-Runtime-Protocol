from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from .schemas import BoundaryCase, BoundaryDecision, BoundaryReportMetadata


def _canonical_json(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash_payload(payload: object) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def build_report_summary(
    cases: list[BoundaryCase],
    decisions: list[BoundaryDecision],
    replay_consistency: float,
) -> dict[str, object]:
    expected_lookup = {case.case_id: bool(case.expected.get("admissible", False)) for case in cases}
    decision_lookup = {decision.case_id: decision for decision in decisions}

    total_cases = len(cases)
    accepted_cases = sum(1 for decision in decisions if decision.admissible)
    rejected_cases = total_cases - accepted_cases

    invalid_cases = [case for case in cases if not expected_lookup[case.case_id]]
    invalid_accepted = sum(1 for case in invalid_cases if decision_lookup[case.case_id].admissible)
    boundary_violation_rate = invalid_accepted / float(len(invalid_cases)) if invalid_cases else 0.0

    authority_drift_violations = sum(
        1 for decision in decisions if float(decision.governance_result.get("authority_drift", 0.0)) != 0.0
    )
    authority_drift_rate = authority_drift_violations / float(total_cases) if total_cases else 0.0

    accepted_expected = sum(1 for case in cases if expected_lookup[case.case_id] and decision_lookup[case.case_id].admissible)
    admissibility_precision = accepted_expected / float(accepted_cases) if accepted_cases else 0.0

    rejection_accuracy = (
        sum(1 for case in invalid_cases if not decision_lookup[case.case_id].admissible) / float(len(invalid_cases))
        if invalid_cases
        else 0.0
    )

    return {
        "total_cases": total_cases,
        "accepted_cases": accepted_cases,
        "rejected_cases": rejected_cases,
        "admissibility_precision": admissibility_precision,
        "boundary_violation_rate": boundary_violation_rate,
        "authority_drift_rate": authority_drift_rate,
        "rejection_accuracy": rejection_accuracy,
        "replay_consistency": replay_consistency,
    }


def build_report_bundle(
    cases: list[BoundaryCase],
    decisions: list[BoundaryDecision],
    metadata: BoundaryReportMetadata,
    replay_consistency: float,
) -> dict[str, object]:
    summary = build_report_summary(cases, decisions, replay_consistency)
    metadata_dict = metadata.as_dict()
    metadata_dict["case_hash"] = _hash_payload([case.as_dict() for case in cases])
    metadata_dict["decision_hash"] = _hash_payload([decision.as_dict() for decision in decisions])
    metadata_dict["summary_hash"] = _hash_payload(summary)
    metadata_dict["report_hash"] = _hash_payload(
        {
            "cases": [case.as_dict() for case in cases],
            "decisions": [decision.as_dict() for decision in decisions],
            "summary": summary,
            "metadata": metadata_dict,
        }
    )
    return {
        "cases": [case.as_dict() for case in cases],
        "decisions": [decision.as_dict() for decision in decisions],
        "summary": summary,
        "metadata": metadata_dict,
    }


def _render_markdown(
    cases: list[BoundaryCase],
    decisions: list[BoundaryDecision],
    summary: dict[str, object],
    metadata: dict[str, object],
) -> str:
    decision_lookup = {decision.case_id: decision for decision in decisions}
    case_rows = []
    for case in cases:
        decision = decision_lookup[case.case_id]
        case_rows.append(
            f"| {case.case_id} | {decision.admissible} | {case.expected.get('admissible', False)} | "
            f"{float(decision.verification_result.get('evidence_strength', 0.0)):.2f} | "
            f"{bool(decision.governance_result.get('authority_allowed', False))} |"
        )

    return "\n".join(
        [
            "# SRP Boundary Report",
            "",
            f"Contract: `{metadata['runtime_contract']}`",
            f"Contract Version: `{metadata['contract_version']}`",
            f"Schema Version: `{metadata['schema_version']}`",
            f"Evaluator Version: `{metadata['evaluator_version']}`",
            f"Adapter: `{metadata['adapter_name']}`",
            f"Version: `{metadata['version']}`",
            f"Seed: `{metadata['seed']}`",
            "",
            f"Cases: `{summary['total_cases']}`",
            f"Accepted: `{summary['accepted_cases']}`",
            f"Rejected: `{summary['rejected_cases']}`",
            "",
            "## Governance Metrics",
            "",
            f"- Boundary Violation Rate: `{summary['boundary_violation_rate']:.3f}`",
            f"- Authority Drift Rate: `{summary['authority_drift_rate']:.3f}`",
            f"- Replay Consistency: `{summary['replay_consistency']:.3f}`",
            "",
            "## Decisions",
            "",
            "| Case | Admissible | Expected | Evidence Strength | Authority Allowed |",
            "| --- | --- | --- | ---: | --- |",
            *case_rows,
        ]
    )


def generate_report(
    cases: Iterable[BoundaryCase],
    decisions: Iterable[BoundaryDecision],
    output_dir: str | Path,
    metadata: BoundaryReportMetadata,
    replay_consistency: float = 1.0,
) -> dict[str, str]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    case_list = list(cases)
    decision_list = list(decisions)
    bundle = build_report_bundle(case_list, decision_list, metadata, replay_consistency)

    cases_path = output_path / "cases.jsonl"
    decisions_path = output_path / "decisions.jsonl"
    summary_path = output_path / "summary.json"
    report_path = output_path / "report.md"
    metadata_path = output_path / "metadata.json"

    with cases_path.open("w", encoding="utf-8") as handle:
        for case in case_list:
            handle.write(_canonical_json(case.as_dict()))
            handle.write("\n")

    with decisions_path.open("w", encoding="utf-8") as handle:
        for decision in decision_list:
            handle.write(_canonical_json(decision.as_dict()))
            handle.write("\n")

    summary_path.write_text(json.dumps(bundle["summary"], ensure_ascii=False, indent=2), encoding="utf-8")
    metadata_path.write_text(json.dumps(bundle["metadata"], ensure_ascii=False, indent=2), encoding="utf-8")
    report_path.write_text(
        _render_markdown(case_list, decision_list, bundle["summary"], bundle["metadata"]),
        encoding="utf-8",
    )

    return {
        "output_dir": str(output_path),
        "cases_jsonl": str(cases_path),
        "decisions_jsonl": str(decisions_path),
        "summary_json": str(summary_path),
        "report_md": str(report_path),
        "metadata_json": str(metadata_path),
        "report_hash": bundle["metadata"]["report_hash"],
        "case_hash": bundle["metadata"]["case_hash"],
        "decision_hash": bundle["metadata"]["decision_hash"],
    }
