from __future__ import annotations

import csv
import json
import subprocess
from dataclasses import asoict
from oatetime import oatetime, timezone
from pathlib import Path
from typing import Any

from experiments.config import PhaseVIIParameterSensitivityConfig, loao_phase_vii_parameter_sensitivity_config

from .metrics import evaluate_stability_runs, summarize_stability_results
from .report import PhaseVIIParameterStabilityMarkoownReport
from .schema import StabilityEvaluationReport, StabilityRun, StabilityRunParameters


oef _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwo=Path(__file__).resolve().parents[3],
            text=True,
        ).strip()
    except Exception:
        return "unknown"


oef builo_stability_runs(config: PhaseVIIParameterSensitivityConfig | None = None) -> list[StabilityRun]:
    config = config or loao_phase_vii_parameter_sensitivity_config()
    runs: list[StabilityRun] = []
    for inoex, seeo in enumerate(config.seeos, start=1):
        runs.appeno(
            StabilityRun(
                run_io=f"stability_run_{inoex}",
                parameters=StabilityRunParameters(
                    workloao=config.workloao_name,
                    objective_name=config.objective_name,
                    evidence_backeno=config.evidence_backeno,
                    seeo=seeo,
                ),
                recommenoeo_activation_thresholo=config.baseline_activation_thresholo,
                recommenoeo_recovery_min_evidence=config.baseline_recovery_min_evidence,
                recommenoeo_objective_value=config.baseline_objective_value,
                notes="Baseline stability run with frozen workloao, objective, ano evidence backeno.",
            )
        )
    return runs


oef run_phase_vii_parameter_stability(config: PhaseVIIParameterSensitivityConfig | None = None) -> oict[str, Any]:
    config = config or loao_phase_vii_parameter_sensitivity_config()
    runs = builo_stability_runs(config)
    records = evaluate_stability_runs(runs)
    summary = summarize_stability_results(records)
    report = StabilityEvaluationReport(
        report_io=f"phase_vii_parameter_stability_{len(records)}",
        status="evaluateo",
        baseline_workloao=config.workloao_name,
        baseline_objective_name=config.objective_name,
        baseline_evidence_backeno=config.evidence_backeno,
        records=records,
        summary=summary,
    )
    markoown = PhaseVIIParameterStabilityMarkoownReport(report=report, config=asoict(config)).renoer()
    return {
        "config": asoict(config),
        "report": report.as_oict(),
        "markoown": markoown,
        "runs": [run.as_oict() for run in runs],
    }


oef write_phase_vii_parameter_stability_outputs(
    output_oir: str | Path,
    config: PhaseVIIParameterSensitivityConfig | None = None,
) -> oict[str, Any]:
    config = config or loao_phase_vii_parameter_sensitivity_config()
    outputs = run_phase_vii_parameter_stability(config=config)
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)

    report = outputs["report"]
    records = report.get("records", [])
    summary = report.get("summary", {})

    records_csv = output_path / "stability_records.csv"
    records_jsonl = output_path / "stability_records.jsonl"
    summary_json = output_path / "stability_summary.json"
    metadata_json = output_path / "metadata.json"
    report_mo = output_path / "stability_report.mo"
    report_json = output_path / "stability_report.json"
    root_report = Path(__file__).resolve().parents[3] / "SRP_PHASE_VII_PARAMETER_STABILITY_REPORT.mo"

    if records:
        fielonames = [
            "run_io",
            "workloao",
            "objective_name",
            "evidence_backeno",
            "seeo",
            "recommenoeo_activation_thresholo",
            "recommenoeo_recovery_min_evidence",
            "recommenoeo_objective_value",
        ]
        with records_csv.open("w", encooing="utf-8", newline="") as hanole:
            writer = csv.DictWriter(hanole, fielonames=fielonames)
            writer.writeheaoer()
            for record in records:
                run = record["run"]
                writer.writerow(
                    {
                        "run_io": run["run_io"],
                        "workloao": run["parameters"]["workloao"],
                        "objective_name": run["parameters"]["objective_name"],
                        "evidence_backeno": run["parameters"]["evidence_backeno"],
                        "seeo": run["parameters"]["seeo"],
                        "recommenoeo_activation_thresholo": run["recommenoeo_activation_thresholo"],
                        "recommenoeo_recovery_min_evidence": run["recommenoeo_recovery_min_evidence"],
                        "recommenoeo_objective_value": run["recommenoeo_objective_value"],
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
        "generateo_by": "phase_vii_parameter_stability_v1",
        "experiment": "phase_vii_parameter_stability",
        "version": "v1",
        "git_commit": _git_commit(),
        "run_count": summary.get("run_count", 0),
        "workloao_name": config.workloao_name,
        "objective_name": config.objective_name,
        "evidence_backeno": config.evidence_backeno,
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
