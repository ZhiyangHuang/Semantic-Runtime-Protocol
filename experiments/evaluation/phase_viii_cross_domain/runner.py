from __future__ import annotations

import csv
import json
import subprocess
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from experiments.config import PhaseVIIICrossDomainValidationConfig, load_phase_viii_cross_domain_validation_config
from experiments.evaluation.phase_vi_relation_recovery.schema import RecoveryConfig

from .domains import build_code_memory_cases, build_knowledge_memory_cases, build_planning_memory_cases
from .metrics import evaluate_cross_domain_runs, summarize_cross_domain_results
from .report import PhaseVIIICrossDomainMarkdownReport
from .schema import CrossDomainEvaluationReport, CrossDomainMetricSchema, CrossDomainRun


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(__file__).resolve().parents[3],
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def _cases_for_domain(domain_name: str):
    if domain_name == "code_memory":
        return build_code_memory_cases()
    if domain_name == "knowledge_reasoning":
        return build_knowledge_memory_cases()
    if domain_name == "agent_planning":
        return build_planning_memory_cases()
    return []


def build_cross_domain_runs(config: PhaseVIIICrossDomainValidationConfig | None = None) -> list[CrossDomainRun]:
    config = config or load_phase_viii_cross_domain_validation_config()
    runs: list[CrossDomainRun] = []
    for domain_name in config.domain_names:
        cases = _cases_for_domain(domain_name)
        for case in cases:
            for mode in config.recovery_modes:
                runs.append(
                    CrossDomainRun(
                        run_id=f"{domain_name}_{case.case_id}_{mode}",
                        domain_name=domain_name,
                        mode=mode,
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


def run_phase_viii_cross_domain(config: PhaseVIIICrossDomainValidationConfig | None = None) -> dict[str, Any]:
    config = config or load_phase_viii_cross_domain_validation_config()
    runs = build_cross_domain_runs(config)
    records = evaluate_cross_domain_runs(runs)
    summary = summarize_cross_domain_results(records)

    report = CrossDomainEvaluationReport(
        report_id=f"phase_viii_cross_domain_{len(records)}",
        status="evaluated",
        baseline_config=RecoveryConfig(
            mode=config.recovery_modes[0] if config.recovery_modes else "vector_only",
            top_k=config.top_k,
            relation_depth=config.relation_depth,
            closure_validation=config.closure_validation,
        ),
        metric_schema=CrossDomainMetricSchema(),
        records=records,
        summary=summary,
        domain_summary=summary.get("domain_summary", {}),
        mode_summary=summary.get("mode_summary", {}),
    )
    markdown = PhaseVIIICrossDomainMarkdownReport(report=report, config=asdict(config)).render()
    return {
        "config": asdict(config),
        "report": report.as_dict(),
        "markdown": markdown,
        "runs": [run.as_dict() for run in runs],
    }


def write_phase_viii_cross_domain_outputs(
    output_dir: str | Path,
    config: PhaseVIIICrossDomainValidationConfig | None = None,
) -> dict[str, Any]:
    config = config or load_phase_viii_cross_domain_validation_config()
    outputs = run_phase_viii_cross_domain(config=config)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    report = outputs["report"]
    records = report.get("records", [])
    summary = report.get("summary", {})

    records_csv = output_path / "cross_domain_records.csv"
    records_jsonl = output_path / "cross_domain_records.jsonl"
    summary_json = output_path / "cross_domain_summary.json"
    metadata_json = output_path / "metadata.json"
    report_md = output_path / "cross_domain_report.md"
    report_json = output_path / "cross_domain_report.json"
    root_report = Path(__file__).resolve().parents[3] / "SRP_PHASE_VIII_CROSS_DOMAIN_VALIDATION_REPORT.md"

    if records:
        fieldnames = [
            "run_id",
            "domain_name",
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
                        "domain_name": run["domain_name"],
                        "mode": run["mode"],
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
        "generated_by": "phase_viii_cross_domain_v1",
        "experiment": "phase_viii_cross_domain",
        "version": "v1",
        "git_commit": _git_commit(),
        "case_count": summary.get("case_count", 0),
        "domain_names": list(config.domain_names),
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
