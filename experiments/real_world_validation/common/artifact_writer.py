from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .schemas import ValidationRun


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def _render_report(run: ValidationRun) -> str:
    metrics = run.as_dict()["metrics"]
    lines = [
        "# Real Validation Report",
        "",
        "This report bundle is generated from the real-validation branch.",
        "",
        "## Metadata",
        "",
    ]
    for key, value in run.metadata.items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Claim Mapping",
            "",
        ]
    )
    mapping = run.claim_mapping.as_dict()
    for key, value in mapping.items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Metrics",
            "",
            "### Transition",
            "",
        ]
    )
    for key, value in metrics["transition_metrics"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "### Governance", ""])
    for key, value in metrics["governance_metrics"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "### Task", ""])
    for key, value in metrics["task_metrics"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Decision", ""])
    for key, value in run.decision.as_dict().items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    return "\n".join(lines)


def write_validation_bundle(output_dir: str | Path, run: ValidationRun) -> dict[str, str]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    payload = run.as_dict()

    metadata_path = output_path / "metadata.json"
    claim_mapping_path = output_path / "claim_mapping.json"
    dataset_manifest_path = output_path / "dataset_manifest.json"
    run_config_path = output_path / "run_config.json"
    metrics_path = output_path / "metrics.json"
    failure_cases_path = output_path / "failure_cases.json"
    decision_path = output_path / "decision.json"
    report_path = output_path / "report.md"
    records_path = output_path / "transition_records.json"

    _write_json(metadata_path, payload["metadata"])
    _write_json(claim_mapping_path, payload["claim_mapping"])
    _write_json(dataset_manifest_path, payload["dataset_manifest"])
    _write_json(run_config_path, payload["run_config"])
    _write_json(metrics_path, payload["metrics"])
    _write_json(failure_cases_path, payload["failure_cases"])
    _write_json(decision_path, payload["decision"])
    _write_json(records_path, payload["transition_records"])
    report_path.write_text(_render_report(run), encoding="utf-8")

    return {
        "metadata_json": str(metadata_path),
        "claim_mapping_json": str(claim_mapping_path),
        "dataset_manifest_json": str(dataset_manifest_path),
        "run_config_json": str(run_config_path),
        "metrics_json": str(metrics_path),
        "failure_cases_json": str(failure_cases_path),
        "decision_json": str(decision_path),
        "transition_records_json": str(records_path),
        "report_markdown": str(report_path),
    }

