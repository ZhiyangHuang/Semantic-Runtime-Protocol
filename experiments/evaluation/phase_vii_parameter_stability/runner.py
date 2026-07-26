from __future__ import annotations

import csv
import json
import subprocess
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from experiments.config import PhaseVIIParameterSensitivityConfig, load_phase_vii_parameter_sensitivity_config

from .metrics import evaluate_stability_runs, summarize_stability_results
from .report import PhaseVIIParameterStabilityMarkdownReport
from .schema import StabilityEvaluationReport, StabilityRun, StabilityRunParameters


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(__file__).resolve().parents[3],
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def build_stability_runs(config: PhaseVIIParameterSensitivityConfig | None = None) -> list[StabilityRun]:
    config = config or load_phase_vii_parameter_sensitivity_config()
    runs: list[StabilityRun] = []
    for index, seed in enumerate(config.seeds, start=1):
        runs.append(
            StabilityRun(
                run_id=f"stability_run_{index}",
                parameters=StabilityRunParameters(
                    workload=config.workload_name,
                    objective_name=config.objective_name,
                    evidence_backend=config.evidence_backend,
                    seed=seed,
                ),
                recommended_activation_threshold=config.baseline_activation_threshold,
                recommended_recovery_min_evidence=config.baseline_recovery_min_evidence,
                recommended_objective_value=config.baseline_objective_value,
                notes="Baseline stability run with frozen workload, objective, and evidence backend.",
            )
        )
    return runs


def run_phase_vii_parameter_stability(config: PhaseVIIParameterSensitivityConfig | None = None) -> dict[str, Any]:
    config = config or load_phase_vii_parameter_sensitivity_config()
    runs = build_stability_runs(config)
    records = evaluate_stability_runs(runs)
    summary = summarize_stability_results(records)
    report = StabilityEvaluationReport(
        report_id=f"phase_vii_parameter_stability_{len(records)}",
        status="evaluated",
        baseline_workload=config.workload_name,
        baseline_objective_name=config.objective_name,
        baseline_evidence_backend=config.evidence_backend,
        records=records,
        summary=summary,
    )
    markdown = PhaseVIIParameterStabilityMarkdownReport(report=report, config=asdict(config)).render()
    return {
        "config": asdict(config),
        "report": report.as_dict(),
        "markdown": markdown,
        "runs": [run.as_dict() for run in runs],
    }


def write_phase_vii_parameter_stability_outputs(
    output_dir: str | Path,
    config: PhaseVIIParameterSensitivityConfig | None = None,
) -> dict[str, Any]:
    config = config or load_phase_vii_parameter_sensitivity_config()
    outputs = run_phase_vii_parameter_stability(config=config)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    report = outputs["report"]
    records = report.get("records", [])
    summary = report.get("summary", {})

    records_csv = output_path / "stability_records.csv"
    records_jsonl = output_path / "stability_records.jsonl"
    summary_json = output_path / "stability_summary.json"
    metadata_json = output_path / "metadata.json"
    report_md = output_path / "stability_report.md"
    report_json = output_path / "stability_report.json"
    root_report = Path(__file__).resolve().parents[3] / "SRP_PHASE_VII_PARAMETER_STABILITY_REPORT.md"

    if records:
        fieldnames = [
            "run_id",
            "workload",
            "objective_name",
            "evidence_backend",
            "seed",
            "recommended_activation_threshold",
            "recommended_recovery_min_evidence",
            "recommended_objective_value",
        ]
        with records_csv.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                run = record["run"]
                writer.writerow(
                    {
                        "run_id": run["run_id"],
                        "workload": run["parameters"]["workload"],
                        "objective_name": run["parameters"]["objective_name"],
                        "evidence_backend": run["parameters"]["evidence_backend"],
                        "seed": run["parameters"]["seed"],
                        "recommended_activation_threshold": run["recommended_activation_threshold"],
                        "recommended_recovery_min_evidence": run["recommended_recovery_min_evidence"],
                        "recommended_objective_value": run["recommended_objective_value"],
                    }
                )

        with records_jsonl.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False, default=str))
                handle.write("\n")

    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "phase_vii_parameter_stability_v1",
        "experiment": "phase_vii_parameter_stability",
        "version": "v1",
        "git_commit": _git_commit(),
        "run_count": summary.get("run_count", 0),
        "workload_name": config.workload_name,
        "objective_name": config.objective_name,
        "evidence_backend": config.evidence_backend,
    }
    metadata_json.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    markdown = outputs["markdown"]
    report_md.write_text(markdown, encoding="utf-8")
    root_report.write_text(markdown, encoding="utf-8")

    return {
        "output_dir": str(output_path),
        "records_csv": str(records_csv),
        "records_jsonl": str(records_jsonl),
        "summary_json": str(summary_json),
        "metadata_json": str(metadata_json),
        "report_markdown": str(report_md),
        "report_json": str(report_json),
        "root_report_markdown": str(root_report),
        "report": report,
        "config": outputs["config"],
        "runs": outputs["runs"],
    }
