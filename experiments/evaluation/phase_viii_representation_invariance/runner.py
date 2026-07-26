from __future__ import annotations

import csv
import json
import subprocess
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from experiments.config import (
    PhaseVIIIRepresentationInvarianceConfig,
    load_phase_viii_representation_invariance_config,
)
from experiments.evaluation.phase_vi_relation_recovery.schema import RecoveryConfig

from .cases import build_representation_invariance_cases
from .metrics import evaluate_representation_case, summarize_representation_invariance_results
from .report import PhaseVIIIRepresentationInvarianceMarkdownReport
from .schema import (
    RepresentationEvaluationReport,
    RepresentationMetricSchema,
    RepresentationRun,
    RepresentationRunResult,
    RepresentationVariant,
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


def build_representation_invariance_runs(
    config: PhaseVIIIRepresentationInvarianceConfig | None = None,
) -> list[RepresentationRun]:
    config = config or load_phase_viii_representation_invariance_config()
    cases = build_representation_invariance_cases()
    runs: list[RepresentationRun] = []
    for encoder_name in config.encoder_names:
        for parser_name in config.parser_names:
            representation = RepresentationVariant(encoder_name=encoder_name, parser_name=parser_name)
            for case in cases:
                for mode in config.recovery_modes:
                    runs.append(
                        RepresentationRun(
                            run_id=f"{encoder_name}_{parser_name}_{case.case_id}_{mode}",
                            representation=representation,
                            case=case,
                            config=RecoveryConfig(
                                mode=mode,
                                top_k=config.top_k,
                                relation_depth=config.relation_depth,
                                closure_validation=config.closure_validation,
                            ),
                        )
                    )
    return runs


def run_phase_viii_representation_invariance(
    config: PhaseVIIIRepresentationInvarianceConfig | None = None,
) -> dict[str, Any]:
    config = config or load_phase_viii_representation_invariance_config()
    runs = build_representation_invariance_runs(config)
    records = [evaluate_representation_case(run) for run in runs]
    summary_bundle = summarize_representation_invariance_results(records)
    summary = summary_bundle["summary"]
    encoder_summary = summary_bundle["encoder_summary"]
    parser_summary = summary_bundle["parser_summary"]
    mode_summary = summary_bundle["mode_summary"]
    representation_summary = summary_bundle["representation_summary"]

    report = RepresentationEvaluationReport(
        report_id=f"phase_viii_representation_invariance_{len(records)}",
        status="evaluated",
        baseline_config=RecoveryConfig(
            mode=config.recovery_modes[0] if config.recovery_modes else "vector_only",
            top_k=config.top_k,
            relation_depth=config.relation_depth,
            closure_validation=config.closure_validation,
        ),
        metric_schema=RepresentationMetricSchema(),
        records=records,
        summary=summary,
        encoder_summary=encoder_summary,
        parser_summary=parser_summary,
        mode_summary=mode_summary,
        representation_summary=representation_summary,
        analysis=summary_bundle["analysis"],
    )
    markdown = PhaseVIIIRepresentationInvarianceMarkdownReport(report=report, config=asdict(config) | {"generated_at": datetime.now(timezone.utc).isoformat()}).render()
    return {
        "config": asdict(config),
        "report": report.as_dict(),
        "markdown": markdown,
        "runs": [run.as_dict() for run in runs],
    }


def write_phase_viii_representation_invariance_outputs(
    output_dir: str | Path,
    config: PhaseVIIIRepresentationInvarianceConfig | None = None,
) -> dict[str, Any]:
    config = config or load_phase_viii_representation_invariance_config()
    outputs = run_phase_viii_representation_invariance(config=config)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    report = outputs["report"]
    records = report.get("records", [])
    summary = report.get("summary", {})

    records_csv = output_path / "representation_invariance_records.csv"
    records_jsonl = output_path / "representation_invariance_records.jsonl"
    summary_json = output_path / "representation_invariance_summary.json"
    metadata_json = output_path / "metadata.json"
    report_md = output_path / "representation_invariance_report.md"
    report_json = output_path / "representation_invariance_report.json"
    root_report = Path(__file__).resolve().parents[3] / "SRP_PHASE_VIII_B_REPRESENTATION_INVARIANCE_REPORT.md"

    if records:
        fieldnames = [
            "run_id",
            "encoder_name",
            "parser_name",
            "mode",
            "case_id",
            "category",
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
        ]
        with records_csv.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                run = record["run"]
                metrics = record["metrics"]
                case = run["case"]
                writer.writerow(
                    {
                        "run_id": run["run_id"],
                        "encoder_name": run["representation"]["encoder_name"],
                        "parser_name": run["representation"]["parser_name"],
                        "mode": run["config"]["mode"],
                        "case_id": case["case_id"],
                        "category": case["category"],
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
        "generated_by": "phase_viii_representation_invariance_v1",
        "experiment": "phase_viii_representation_invariance",
        "version": "v1",
        "git_commit": _git_commit(),
        "case_count": summary.get("case_count", 0),
        "encoder_names": list(config.encoder_names),
        "parser_names": list(config.parser_names),
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
        "runs": outputs["runs"],
    }
