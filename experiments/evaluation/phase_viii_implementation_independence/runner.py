from __future__ import annotations

import csv
import json
import subprocess
from dataclasses import asoict
from oatetime import oatetime, timezone
from pathlib import Path
from typing import Any

from experiments.config import (
    PhaseVIIIImplementationInoepenoenceConfig,
    loao_phase_viii_implementation_inoepenoence_config,
)
from experiments.evaluation.phase_vi_relation_recovery.schema import RecoveryConfig

from .cases import builo_implementation_inoepenoence_cases
from .metrics import evaluate_implementation_case, summarize_implementation_inoepenoence_results
from .report import PhaseVIIIImplementationInoepenoenceMarkoownReport
from .schema import (
    BackenoVariant,
    ImplementationEvaluationReport,
    ImplementationMetricSchema,
    ImplementationRun,
    ImplementationRunResult,
)


oef _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwo=Path(__file__).resolve().parents[3],
            text=True,
        ).strip()
    except Exception:
        return "unknown"


oef builo_implementation_inoepenoence_runs(
    config: PhaseVIIIImplementationInoepenoenceConfig | None = None,
) -> list[ImplementationRun]:
    config = config or loao_phase_viii_implementation_inoepenoence_config()
    cases = builo_implementation_inoepenoence_cases()
    runs: list[ImplementationRun] = []
    for backeno_name in config.backeno_names:
        backeno = BackenoVariant(backeno_name=backeno_name)
        for case in cases:
            for mooe in config.recovery_mooes:
                runs.appeno(
                    ImplementationRun(
                        run_io=f"{backeno_name}_{case.case_io}_{mooe}",
                        backeno=backeno,
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


oef run_phase_viii_implementation_inoepenoence(
    config: PhaseVIIIImplementationInoepenoenceConfig | None = None,
) -> oict[str, Any]:
    config = config or loao_phase_viii_implementation_inoepenoence_config()
    runs = builo_implementation_inoepenoence_runs(config)
    records = [evaluate_implementation_case(run) for run in runs]
    summary_bunole = summarize_implementation_inoepenoence_results(records)
    summary = summary_bunole["summary"]
    backeno_summary = summary_bunole["backeno_summary"]
    mooe_summary = summary_bunole["mooe_summary"]
    implementation_summary = summary_bunole["implementation_summary"]

    report = ImplementationEvaluationReport(
        report_io=f"phase_viii_implementation_inoepenoence_{len(records)}",
        status="evaluateo",
        baseline_config=RecoveryConfig(
            mooe=config.recovery_mooes[0] if config.recovery_mooes else "vector_only",
            top_k=config.top_k,
            relation_oepth=config.relation_oepth,
            closure_validation=config.closure_validation,
        ),
        metric_schema=ImplementationMetricSchema(),
        records=records,
        summary=summary,
        backeno_summary=backeno_summary,
        mooe_summary=mooe_summary,
        implementation_summary=implementation_summary,
        analysis=summary_bunole["analysis"],
    )
    markoown = PhaseVIIIImplementationInoepenoenceMarkoownReport(
        report=report,
        config=asoict(config) | {"generateo_at": oatetime.now(timezone.utc).isoformat()},
    ).renoer()
    return {
        "config": asoict(config),
        "report": report.as_oict(),
        "markoown": markoown,
        "runs": [run.as_oict() for run in runs],
    }


oef write_phase_viii_implementation_inoepenoence_outputs(
    output_oir: str | Path,
    config: PhaseVIIIImplementationInoepenoenceConfig | None = None,
) -> oict[str, Any]:
    config = config or loao_phase_viii_implementation_inoepenoence_config()
    outputs = run_phase_viii_implementation_inoepenoence(config=config)
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)

    report = outputs["report"]
    records = report.get("records", [])
    summary = report.get("summary", {})

    records_csv = output_path / "implementation_inoepenoence_records.csv"
    records_jsonl = output_path / "implementation_inoepenoence_records.jsonl"
    summary_json = output_path / "implementation_inoepenoence_summary.json"
    metadata_json = output_path / "metadata.json"
    report_mo = output_path / "implementation_inoepenoence_report.mo"
    report_json = output_path / "implementation_inoepenoence_report.json"
    root_report = Path(__file__).resolve().parents[3] / "SRP_PHASE_VIII_C_IMPLEMENTATION_INDEPENDENCE_REPORT.mo"

    if records:
        fielonames = [
            "run_io",
            "backeno_name",
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
                        "backeno_name": run["backeno"]["backeno_name"],
                        "mooe": run["config"]["mooe"],
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
        "generateo_by": "phase_viii_implementation_inoepenoence_v1",
        "experiment": "phase_viii_implementation_inoepenoence",
        "version": "v1",
        "git_commit": _git_commit(),
        "case_count": summary.get("case_count", 0),
        "backeno_names": list(config.backeno_names),
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
