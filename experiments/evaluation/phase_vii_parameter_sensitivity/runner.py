from __future__ import annotations

import csv
import json
import subprocess
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from experiments.config import PhaseVIIBParameterSensitivityConfig, load_phase_vii_parameter_sensitivity_analysis_config

from .cases import build_parameter_sensitivity_runs as _build_parameter_sensitivity_runs
from .metrics import evaluate_parameter_sensitivity_runs, summarize_parameter_sensitivity_results
from .report import PhaseVIIBParameterSensitivityMarkdownReport
from .schema import SensitivityEvaluationReport, SensitivityMetricSchema, SensitivityParameters


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(__file__).resolve().parents[3],
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def build_parameter_sensitivity_runs(
    config: PhaseVIIBParameterSensitivityConfig | None = None,
):
    config = config or load_phase_vii_parameter_sensitivity_analysis_config()
    return _build_parameter_sensitivity_runs(config)


def run_phase_vii_parameter_sensitivity(
    config: PhaseVIIBParameterSensitivityConfig | None = None,
) -> dict[str, Any]:
    config = config or load_phase_vii_parameter_sensitivity_analysis_config()
    runs = build_parameter_sensitivity_runs(config)
    records = evaluate_parameter_sensitivity_runs(runs)
    summary = summarize_parameter_sensitivity_results(records)

    axis_summary: dict[str, list[dict[str, Any]]] = {}
    baseline_metrics = summary.get("baseline_metrics", {})
    for record in records:
        axis_summary.setdefault(record.run.axis_name, []).append(
            {
                "run_id": record.run.run_id,
                "axis_value": record.run.axis_value,
                "mean_semantic_coverage": record.metrics.mean_semantic_coverage,
                "mean_semantic_drift": record.metrics.mean_semantic_drift,
                "mean_relation_accuracy": record.metrics.mean_relation_accuracy,
                "mean_closure_accuracy": record.metrics.mean_closure_accuracy,
                "mean_evidence_cost": record.metrics.mean_evidence_cost,
                "drift_delta_vs_baseline": record.metrics.drift_delta_vs_baseline,
                "cost_delta_vs_baseline": record.metrics.evidence_cost_delta_vs_baseline,
            }
        )
    for rows in axis_summary.values():
        rows.sort(key=lambda row: str(row["axis_value"]))

    report = SensitivityEvaluationReport(
        report_id=f"phase_vii_parameter_sensitivity_{len(records)}",
        status="evaluated",
        baseline_parameters=SensitivityParameters(
            recovery_strategy=config.recovery_strategy,
            activation_threshold=config.baseline_activation_threshold,
            recovery_min_evidence=config.baseline_recovery_min_evidence,
            preserve_evidence=config.baseline_preserve_evidence,
            archive_relations=config.baseline_archive_relations,
            relation_depth=config.baseline_relation_depth,
        ),
        metric_schema=SensitivityMetricSchema(),
        records=records,
        summary=summary,
        axis_summary=axis_summary,
    )
    markdown = PhaseVIIBParameterSensitivityMarkdownReport(report=report, config=asdict(config)).render()
    return {
        "config": asdict(config),
        "report": report.as_dict(),
        "markdown": markdown,
        "runs": [run.as_dict() for run in runs],
        "baseline_metrics": baseline_metrics,
    }


def write_phase_vii_parameter_sensitivity_outputs(
    output_dir: str | Path,
    config: PhaseVIIBParameterSensitivityConfig | None = None,
) -> dict[str, Any]:
    config = config or load_phase_vii_parameter_sensitivity_analysis_config()
    outputs = run_phase_vii_parameter_sensitivity(config=config)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    report = outputs["report"]
    records = report.get("records", [])
    summary = report.get("summary", {})
    baseline = report.get("baseline_parameters", {})

    records_csv = output_path / "sensitivity_records.csv"
    records_jsonl = output_path / "sensitivity_records.jsonl"
    summary_json = output_path / "sensitivity_summary.json"
    metadata_json = output_path / "metadata.json"
    report_md = output_path / "sensitivity_report.md"
    report_json = output_path / "sensitivity_report.json"
    root_report = Path(__file__).resolve().parents[3] / "SRP_PHASE_VII_PARAMETER_SENSITIVITY_REPORT.md"

    if records:
        fieldnames = [
            "run_id",
            "axis_name",
            "axis_value",
            "workload_name",
            "objective_name",
            "evidence_backend",
            "recovery_strategy",
            "activation_threshold",
            "recovery_min_evidence",
            "preserve_evidence",
            "archive_relations",
            "relation_depth",
            "mean_semantic_coverage",
            "mean_semantic_drift",
            "mean_fact_accuracy",
            "mean_relation_accuracy",
            "mean_recovery_accuracy",
            "mean_closure_accuracy",
            "mean_path_preservation",
            "mean_neighborhood_completeness",
            "mean_hallucinated_relation_rate",
            "mean_evidence_cost",
            "coverage_delta_vs_baseline",
            "drift_delta_vs_baseline",
            "fact_accuracy_delta_vs_baseline",
            "relation_accuracy_delta_vs_baseline",
            "recovery_accuracy_delta_vs_baseline",
            "closure_accuracy_delta_vs_baseline",
            "path_preservation_delta_vs_baseline",
            "neighborhood_completeness_delta_vs_baseline",
            "hallucinated_relation_rate_delta_vs_baseline",
            "evidence_cost_delta_vs_baseline",
        ]
        with records_csv.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                run = record["run"]
                metrics = record["metrics"]
                writer.writerow(
                    {
                        "run_id": run["run_id"],
                        "axis_name": run["axis_name"],
                        "axis_value": run["axis_value"],
                        "workload_name": run["workload_name"],
                        "objective_name": run["objective_name"],
                        "evidence_backend": run["evidence_backend"],
                        "recovery_strategy": run["parameters"]["recovery_strategy"],
                        "activation_threshold": run["parameters"]["activation_threshold"],
                        "recovery_min_evidence": run["parameters"]["recovery_min_evidence"],
                        "preserve_evidence": run["parameters"]["preserve_evidence"],
                        "archive_relations": run["parameters"]["archive_relations"],
                        "relation_depth": run["parameters"]["relation_depth"],
                        "mean_semantic_coverage": metrics["mean_semantic_coverage"],
                        "mean_semantic_drift": metrics["mean_semantic_drift"],
                        "mean_fact_accuracy": metrics["mean_fact_accuracy"],
                        "mean_relation_accuracy": metrics["mean_relation_accuracy"],
                        "mean_recovery_accuracy": metrics["mean_recovery_accuracy"],
                        "mean_closure_accuracy": metrics["mean_closure_accuracy"],
                        "mean_path_preservation": metrics["mean_path_preservation"],
                        "mean_neighborhood_completeness": metrics["mean_neighborhood_completeness"],
                        "mean_hallucinated_relation_rate": metrics["mean_hallucinated_relation_rate"],
                        "mean_evidence_cost": metrics["mean_evidence_cost"],
                        "coverage_delta_vs_baseline": metrics["coverage_delta_vs_baseline"],
                        "drift_delta_vs_baseline": metrics["drift_delta_vs_baseline"],
                        "fact_accuracy_delta_vs_baseline": metrics["fact_accuracy_delta_vs_baseline"],
                        "relation_accuracy_delta_vs_baseline": metrics["relation_accuracy_delta_vs_baseline"],
                        "recovery_accuracy_delta_vs_baseline": metrics["recovery_accuracy_delta_vs_baseline"],
                        "closure_accuracy_delta_vs_baseline": metrics["closure_accuracy_delta_vs_baseline"],
                        "path_preservation_delta_vs_baseline": metrics["path_preservation_delta_vs_baseline"],
                        "neighborhood_completeness_delta_vs_baseline": metrics["neighborhood_completeness_delta_vs_baseline"],
                        "hallucinated_relation_rate_delta_vs_baseline": metrics["hallucinated_relation_rate_delta_vs_baseline"],
                        "evidence_cost_delta_vs_baseline": metrics["evidence_cost_delta_vs_baseline"],
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
        "generated_by": "phase_vii_parameter_sensitivity_v1",
        "experiment": "phase_vii_parameter_sensitivity",
        "version": "v1",
        "git_commit": _git_commit(),
        "run_count": summary.get("run_count", 0),
        "workload_name": config.workload_name,
        "objective_name": config.objective_name,
        "evidence_backend": config.evidence_backend,
        "recovery_strategy": config.recovery_strategy,
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
