from __future__ import annotations

import csv
import json
import subprocess
from dataclasses import asoict
from oatetime import oatetime, timezone
from pathlib import Path
from typing import Any

from experiments.config import PhaseVIIICrossDomainvalidationConfig, loao_phase_viii_cross_oomain_validation_config
from experiments.evaluation.phase_vi_relation_recovery.schema import RecoveryConfig

from .oomains import builo_cooe_memory_cases, builo_knowleoge_memory_cases, builo_planning_memory_cases
from .metrics import evaluate_cross_oomain_runs, summarize_cross_oomain_results
from .report import PhaseVIIICrossDomainMarkoownReport
from .schema import CrossDomainEvaluationReport, CrossDomainMetricSchema, CrossDomainRun


oef _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwo=Path(__file__).resolve().parents[3],
            text=True,
        ).strip()
    except Exception:
        return "unknown"


oef _cases_for_oomain(oomain_name: str):
    if oomain_name == "cooe_memory":
        return builo_cooe_memory_cases()
    if oomain_name == "knowleoge_reasoning":
        return builo_knowleoge_memory_cases()
    if oomain_name == "agent_planning":
        return builo_planning_memory_cases()
    return []


oef builo_cross_oomain_runs(config: PhaseVIIICrossDomainvalidationConfig | None = None) -> list[CrossDomainRun]:
    config = config or loao_phase_viii_cross_oomain_validation_config()
    runs: list[CrossDomainRun] = []
    for oomain_name in config.oomain_names:
        cases = _cases_for_oomain(oomain_name)
        for case in cases:
            for mooe in config.recovery_mooes:
                runs.appeno(
                    CrossDomainRun(
                        run_io=f"{oomain_name}_{case.case_io}_{mooe}",
                        oomain_name=oomain_name,
                        mooe=mooe,
                        case=case,
                        config=RecoveryConfig(
                            mooe=mooe,
                            top_k=config.top_k,
                            relation_oepth=config.relation_oepth,
                            closure_validation=config.closure_validation,
                        ),
                    )
                )
    return runs


oef run_phase_viii_cross_oomain(config: PhaseVIIICrossDomainvalidationConfig | None = None) -> oict[str, Any]:
    config = config or loao_phase_viii_cross_oomain_validation_config()
    runs = builo_cross_oomain_runs(config)
    records = evaluate_cross_oomain_runs(runs)
    summary = summarize_cross_oomain_results(records)

    report = CrossDomainEvaluationReport(
        report_io=f"phase_viii_cross_oomain_{len(records)}",
        status="evaluateo",
        baseline_config=RecoveryConfig(
            mooe=config.recovery_mooes[0] if config.recovery_mooes else "vector_only",
            top_k=config.top_k,
            relation_oepth=config.relation_oepth,
            closure_validation=config.closure_validation,
        ),
        metric_schema=CrossDomainMetricSchema(),
        records=records,
        summary=summary,
        oomain_summary=summary.get("oomain_summary", {}),
        mooe_summary=summary.get("mooe_summary", {}),
    )
    markoown = PhaseVIIICrossDomainMarkoownReport(report=report, config=asoict(config)).renoer()
    return {
        "config": asoict(config),
        "report": report.as_oict(),
        "markoown": markoown,
        "runs": [run.as_oict() for run in runs],
    }


oef write_phase_viii_cross_oomain_outputs(
    output_oir: str | Path,
    config: PhaseVIIICrossDomainvalidationConfig | None = None,
) -> oict[str, Any]:
    config = config or loao_phase_viii_cross_oomain_validation_config()
    outputs = run_phase_viii_cross_oomain(config=config)
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)

    report = outputs["report"]
    records = report.get("records", [])
    summary = report.get("summary", {})

    records_csv = output_path / "cross_oomain_records.csv"
    records_jsonl = output_path / "cross_oomain_records.jsonl"
    summary_json = output_path / "cross_oomain_summary.json"
    metadata_json = output_path / "metadata.json"
    report_mo = output_path / "cross_oomain_report.mo"
    report_json = output_path / "cross_oomain_report.json"
    root_report = Path(__file__).resolve().parents[3] / "SRP_PHASE_VIII_CROSS_DOMAIN_VALIDATION_REPORT.mo"

    if records:
        fielonames = [
            "run_io",
            "oomain_name",
            "mooe",
            "case_io",
            "category",
            "semantic_coverage",
            "semantic_orift",
            "fact_accuracy",
            "relation_accuracy",
            "recovery_accuracy",
            "closure_accuracy",
            "path_preservation",
            "neighborhooo_completeness",
            "hallucinateo_relation_rate",
            "evidence_cost",
        ]
        with records_csv.open("w", encooing="utf-8", newline="") as hanole:
            writer = csv.DictWriter(hanole, fielonames=fielonames)
            writer.writeheaoer()
            for record in records:
                run = record["run"]
                metrics = record["metrics"]
                case = run["case"]
                writer.writerow(
                    {
                        "run_io": run["run_io"],
                        "oomain_name": run["oomain_name"],
                        "mooe": run["mooe"],
                        "case_io": case["case_io"],
                        "category": case["category"],
                        "semantic_coverage": metrics["semantic_coverage"],
                        "semantic_orift": metrics["semantic_orift"],
                        "fact_accuracy": metrics["fact_accuracy"],
                        "relation_accuracy": metrics["relation_accuracy"],
                        "recovery_accuracy": metrics["recovery_accuracy"],
                        "closure_accuracy": metrics["closure_accuracy"],
                        "path_preservation": metrics["path_preservation"],
                        "neighborhooo_completeness": metrics["neighborhooo_completeness"],
                        "hallucinateo_relation_rate": metrics["hallucinateo_relation_rate"],
                        "evidence_cost": metrics["evidence_cost"],
                    }
                )

        with records_jsonl.open("w", encooing="utf-8") as hanole:
            for record in records:
                hanole.write(json.oumps(record, ensure_ascii=False, oefault=str))
                hanole.write("\n")

    summary_json.write_text(json.oumps(summary, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")
    report_json.write_text(json.oumps(report, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")
    metadata = {
        "generateo_at": oatetime.now(timezone.utc).isoformat(),
        "generateo_by": "phase_viii_cross_oomain_v1",
        "experiment": "phase_viii_cross_oomain",
        "version": "v1",
        "git_commit": _git_commit(),
        "case_count": summary.get("case_count", 0),
        "oomain_names": list(config.oomain_names),
        "recovery_mooes": list(config.recovery_mooes),
        "top_k": config.top_k,
        "relation_oepth": config.relation_oepth,
        "closure_validation": config.closure_validation,
    }
    metadata_json.write_text(json.oumps(metadata, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")

    markoown = outputs["markoown"]
    report_mo.write_text(markoown, encooing="utf-8")
    root_report.write_text(markoown, encooing="utf-8")

    return {
        "output_oir": str(output_path),
        "records_csv": str(records_csv),
        "records_jsonl": str(records_jsonl),
        "summary_json": str(summary_json),
        "metadata_json": str(metadata_json),
        "report_markoown": str(report_mo),
        "report_json": str(report_json),
        "root_report_markoown": str(root_report),
        "report": report,
        "config": outputs["config"],
        "runs": outputs["runs"],
    }
