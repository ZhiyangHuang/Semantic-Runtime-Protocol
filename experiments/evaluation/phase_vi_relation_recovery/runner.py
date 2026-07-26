from __future__ import annotations

import csv
import json
import subprocess
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from experiments.config import PhaseVIRelationRecoveryConfig, load_phase_vi_relation_recovery_config

from .cases import build_relation_recovery_cases
from .metrics import evaluate_relation_recovery_case, summarize_relation_recovery_results
from .report import PhaseVIRelationRecoveryMarkdownReport
from .schema import (
    RecoveryConfig,
    RelationRecoveryEvaluationReport,
    RelationRecoveryMetricSchema,
)


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(__file__).resolve().parents[3],
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def run_phase_vi_relation_recovery(config: PhaseVIRelationRecoveryConfig | None = None) -> dict[str, Any]:
    config = config or load_phase_vi_relation_recovery_config()
    cases = build_relation_recovery_cases()
    records = []
    for case in cases:
        for mode in config.recovery_modes:
            recovery_config = RecoveryConfig(
                mode=mode,
                top_k=config.top_k,
                relation_depth=config.relation_depth,
                closure_validation=config.closure_validation,
            )
            records.append(evaluate_relation_recovery_case(case, recovery_config))
    summary = summarize_relation_recovery_results(records)
    baseline_config = RecoveryConfig(
        mode=config.recovery_modes[0] if config.recovery_modes else "vector_only",
        top_k=config.top_k,
        relation_depth=config.relation_depth,
        closure_validation=config.closure_validation,
    )
    report = RelationRecoveryEvaluationReport(
        report_id=f"phase_vi_relation_recovery_{len(records)}",
        status="evaluated",
        baseline_config=baseline_config,
        metric_schema=RelationRecoveryMetricSchema(),
        records=records,
        summary=summary,
    )
    markdown = PhaseVIRelationRecoveryMarkdownReport(report=report, config=asdict(config)).render()
    return {
        "config": asdict(config),
        "report": report.as_dict(),
        "markdown": markdown,
        "cases": [case.as_dict() for case in cases],
    }


def write_phase_vi_relation_recovery_outputs(
    output_dir: str | Path,
    config: PhaseVIRelationRecoveryConfig | None = None,
) -> dict[str, Any]:
    config = config or load_phase_vi_relation_recovery_config()
    outputs = run_phase_vi_relation_recovery(config=config)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    report = outputs["report"]
    records = report.get("records", [])
    summary = report.get("summary", {})
    baseline = report.get("baseline_config", {})

    records_csv = output_path / "relation_recovery_records.csv"
    records_jsonl = output_path / "relation_recovery_records.jsonl"
    summary_json = output_path / "relation_recovery_summary.json"
    metadata_json = output_path / "metadata.json"
    report_md = output_path / "relation_recovery_report.md"
    report_json = output_path / "relation_recovery_report.json"
    root_report = Path(__file__).resolve().parents[3] / "SRP_PHASE_VI_RELATION_AWARE_RECOVERY_REPORT.md"

    if records:
        fieldnames = [
            "case_id",
            "category",
            "mode",
            "semantic_coverage",
            "semantic_drift",
            "fact_accuracy",
            "relation_accuracy",
            "recovery_accuracy",
            "closure_accuracy",
            "path_preservation",
            "neighborhood_completeness",
            "hallucinated_relation_rate",
            "evidence_cost",
            "original_node_count",
            "original_edge_count",
            "recovered_node_count",
            "recovered_edge_count",
            "matched_node_count",
            "matched_edge_count",
            "missing_node_count",
            "hallucinated_node_count",
            "hallucinated_edge_count",
            "top_k",
            "relation_depth",
            "closure_validation",
        ]
        with records_csv.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                case = record["case"]
                config_data = record["config"]
                metrics = record["metrics"]
                writer.writerow(
                    {
                        "case_id": case["case_id"],
                        "category": case["category"],
                        "mode": config_data["mode"],
                        "semantic_coverage": metrics["semantic_coverage"],
                        "semantic_drift": metrics["semantic_drift"],
                        "fact_accuracy": metrics["fact_accuracy"],
                        "relation_accuracy": metrics["relation_accuracy"],
                        "recovery_accuracy": metrics["recovery_accuracy"],
                        "closure_accuracy": metrics["closure_accuracy"],
                        "path_preservation": metrics["path_preservation"],
                        "neighborhood_completeness": metrics["neighborhood_completeness"],
                        "hallucinated_relation_rate": metrics["hallucinated_relation_rate"],
                        "evidence_cost": metrics["evidence_cost"],
                        "original_node_count": metrics["original_node_count"],
                        "original_edge_count": metrics["original_edge_count"],
                        "recovered_node_count": metrics["recovered_node_count"],
                        "recovered_edge_count": metrics["recovered_edge_count"],
                        "matched_node_count": metrics["matched_node_count"],
                        "matched_edge_count": metrics["matched_edge_count"],
                        "missing_node_count": metrics["missing_node_count"],
                        "hallucinated_node_count": metrics["hallucinated_node_count"],
                        "hallucinated_edge_count": metrics["hallucinated_edge_count"],
                        "top_k": config_data["top_k"],
                        "relation_depth": config_data["relation_depth"],
                        "closure_validation": config_data["closure_validation"],
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
        "generated_by": "phase_vi_relation_recovery_v1",
        "experiment": "phase_vi_relation_recovery",
        "version": "v1",
        "git_commit": _git_commit(),
        "case_count": summary.get("case_count", 0),
        "recovery_modes": list(config.recovery_modes),
        "top_k": config.top_k,
        "relation_depth": config.relation_depth,
        "closure_validation": config.closure_validation,
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
        "cases": outputs["cases"],
    }
