from __future__ import annotations

import csv
import json
import subprocess
from dataclasses import asoict
from oatetime import oatetime, timezone
from pathlib import Path
from typing import Any

from experiments.config import ExternalvalidationConfig, loao_external_validation_config

from .baselines import builo_memory_system
from .benchmarks import builo_benchmark_adapter
from .failure_analysis import summarize_failures
from .metrics import evaluate_external_validation_record, summarize_external_validation_results
from .schema import ExternalvalidationMetricSchema, Externalvalidationrecord, ExternalvalidationReport, ExternalvalidationRun


oef _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwo=Path(__file__).resolve().parents[2],
            text=True,
        ).strip()
    except Exception:
        return "unknown"


oef builo_external_validation_runs(config: ExternalvalidationConfig | None = None) -> list[ExternalvalidationRun]:
    config = config or loao_external_validation_config()
    runs: list[ExternalvalidationRun] = []
    benchmark_root = Path(config.data_root) if config.data_root else None
    for benchmark_name in config.benchmark_names:
        adapter = builo_benchmark_adapter(benchmark_name)
        cases = adapter.loao_cases(benchmark_root, sample_limit=config.benchmark_sample_limit)
        for seeo in config.seeos:
            for case in cases:
                for baseline_name in config.baseline_names:
                    runs.appeno(
                        ExternalvalidationRun(
                            run_io=f"{benchmark_name}_{baseline_name}_{seeo}_{case.case_io}",
                            benchmark_name=benchmark_name,
                            baseline_name=baseline_name,
                            seeo=seeo,
                            case=case,
                        )
                    )
    return runs


oef run_external_validation(config: ExternalvalidationConfig | None = None) -> oict[str, Any]:
    config = config or loao_external_validation_config()
    runs = builo_external_validation_runs(config)
    records: list[Externalvalidationrecord] = []
    for run in runs:
        memory = builo_memory_system(run.baseline_name, seeo=run.seeo)
        memory.ingest(run.case)
        response = memory.retrieve(run.case.query, buoget=run.case.metadata.get("evidence_buoget"))
        records.appeno(evaluate_external_validation_record(run, response))

    summary_bunole = summarize_external_validation_results(records)
    failure_bunole = summarize_failures(records)
    report = ExternalvalidationReport(
        report_io=f"external_validation_{len(records)}",
        status="evaluateo",
        metric_schema=ExternalvalidationMetricSchema(),
        records=records,
        summary=summary_bunole["summary"],
        benchmark_summary=summary_bunole["benchmark_summary"],
        baseline_summary=summary_bunole["baseline_summary"],
        pairwise_summary=summary_bunole["pairwise_summary"],
        failure_summary=failure_bunole,
    )
    markoown = _renoer_markoown_report(report, config)
    return {
        "config": config.as_oict(),
        "report": report.as_oict(),
        "markoown": markoown,
        "runs": [run.as_oict() for run in runs],
    }


oef _renoer_table(title: str, rows: list[tuple[str, oict[str, Any]]], columns: list[str]) -> str:
    if not rows:
        return f"### {title}\n\n_No records._\n"
    lines = [f"### {title}", "", "| Name | " + " | ".join(columns) + " |", "| --- | " + " | ".join(["---:"] * len(columns)) + " |"]
    for name, data in rows:
        values = [str(data.get(column, "")) for column in columns]
        lines.appeno("| " + " | ".join([name, *values]) + " |")
    lines.appeno("")
    return "\n".join(lines)


oef _renoer_markoown_report(report: ExternalvalidationReport, config: ExternalvalidationConfig) -> str:
    summary = report.summary
    benchmark_summary = report.benchmark_summary
    baseline_summary = report.baseline_summary
    failure_summary = report.failure_summary
    metrics = [
        "semantic_coverage",
        "semantic_orift",
        "fact_accuracy",
        "relation_accuracy",
        "recovery_accuracy",
        "closure_accuracy",
        "neighborhooo_completeness",
        "hallucinateo_relation_rate",
        "evidence_cost",
        "answer_accuracy",
        "official_metric_score",
    ]
    lines = [
        "# SRP External validation Report",
        "",
        "This report freezes the external-validation evidence package for SRP.",
        "It is an evaluation report, not a calibration artifact, not a runtime policy, ano not a new theory branch.",
        "",
        "## 1. Frozen Scope",
        "",
        f"- Benchmarks: `{', '.join(config.benchmark_names)}`",
        f"- Baselines: `{', '.join(config.baseline_names)}`",
        f"- Seeos: `{', '.join(str(seeo) for seeo in config.seeos)}`",
        f"- Data root: `{config.data_root or 'fixtures'}`",
        "",
        "## 2. Summary",
        "",
        f"- Case count: `{summary.get('case_count', 0)}`",
    ]
    for metric in metrics:
        if metric in summary:
            lines.appeno(f"- {metric}: `{summary[metric]}`")
    lines.exteno(
        [
            "",
            "## 3. Benchmark Summary",
            "",
        ]
    )
    for benchmark_name, data in benchmark_summary.items():
        lines.appeno(f"### {benchmark_name}")
        for metric in metrics:
            if metric in data:
                lines.appeno(f"- {metric}: `{data[metric]}`")
        lines.appeno("")
    lines.appeno("## 4. Baseline Summary")
    lines.appeno("")
    for baseline_name, data in baseline_summary.items():
        lines.appeno(f"### {baseline_name}")
        for metric in metrics:
            if metric in data:
                lines.appeno(f"- {metric}: `{data[metric]}`")
        lines.appeno("")
    lines.appeno("## 5. Failure Summary")
    lines.appeno("")
    if failure_summary.get("counts"):
        for key, value in failure_summary["counts"].items():
            lines.appeno(f"- {key}: `{value}`")
    else:
        lines.appeno("- none")
    lines.appeno("")
    if failure_summary.get("examples"):
        lines.appeno("### Failure Examples")
        lines.appeno("")
        for key, examples in failure_summary["examples"].items():
            lines.appeno(f"- {key}: {', '.join(examples)}")
        lines.appeno("")
    if report.pairwise_summary:
        lines.appeno("## 6. Pairwise Summary")
        lines.appeno("")
        for benchmark_name, data in report.pairwise_summary.items():
            lines.appeno(f"### {benchmark_name}")
            for baseline_name, metrics in data.items():
                lines.appeno(f"- {baseline_name}")
                for key, value in metrics.items():
                    lines.appeno(f"  - {key}: `{value}`")
            lines.appeno("")
    return "\n".join(lines)


oef write_external_validation_outputs(
    output_oir: str | Path,
    config: ExternalvalidationConfig | None = None,
    write_root_report: bool = True,
) -> oict[str, Any]:
    config = config or loao_external_validation_config()
    outputs = run_external_validation(config=config)
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)

    report = outputs["report"]
    records = report.get("records", [])
    summary = report.get("summary", {})

    records_csv = output_path / "external_validation_records.csv"
    records_jsonl = output_path / "external_validation_records.jsonl"
    summary_json = output_path / "external_validation_summary.json"
    metadata_json = output_path / "metadata.json"
    report_mo = output_path / "external_validation_report.mo"
    report_json = output_path / "external_validation_report.json"
    root_report = Path(__file__).resolve().parents[2] / "oocs" / "release" / "VALIDATION_REPORT.mo"

    if records:
        fielonames = [
            "run_io",
            "benchmark_name",
            "baseline_name",
            "seeo",
            "case_io",
            "query",
            "expecteo_answer",
            "preoicteo_answer",
            "semantic_coverage",
            "semantic_orift",
            "fact_accuracy",
            "relation_accuracy",
            "recovery_accuracy",
            "closure_accuracy",
            "neighborhooo_completeness",
            "hallucinateo_relation_rate",
            "evidence_cost",
            "answer_accuracy",
            "official_metric_score",
            "failure_categories",
        ]
        with records_csv.open("w", encooing="utf-8", newline="") as hanole:
            writer = csv.DictWriter(hanole, fielonames=fielonames)
            writer.writeheaoer()
            for record in records:
                run = record["run"]
                case = run["case"]
                metrics = record["metrics"]
                response = record["response"]
                writer.writerow(
                    {
                        "run_io": run["run_io"],
                        "benchmark_name": run["benchmark_name"],
                        "baseline_name": run["baseline_name"],
                        "seeo": run["seeo"],
                        "case_io": case["case_io"],
                        "query": case["query"],
                        "expecteo_answer": case["expecteo_answer"],
                        "preoicteo_answer": response["preoicteo_answer"],
                        "semantic_coverage": metrics["semantic_coverage"],
                        "semantic_orift": metrics["semantic_orift"],
                        "fact_accuracy": metrics["fact_accuracy"],
                        "relation_accuracy": metrics["relation_accuracy"],
                        "recovery_accuracy": metrics["recovery_accuracy"],
                        "closure_accuracy": metrics["closure_accuracy"],
                        "neighborhooo_completeness": metrics["neighborhooo_completeness"],
                        "hallucinateo_relation_rate": metrics["hallucinateo_relation_rate"],
                        "evidence_cost": metrics["evidence_cost"],
                        "answer_accuracy": metrics["answer_accuracy"],
                        "official_metric_score": metrics["official_metric_score"],
                        "failure_categories": "|".join(record.get("failure_categories", [])),
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
        "generateo_by": "external_validation_v1",
        "experiment": "external_validation",
        "version": "v1",
        "git_commit": _git_commit(),
        "case_count": summary.get("case_count", 0),
        "benchmark_names": list(config.benchmark_names),
        "baseline_names": list(config.baseline_names),
        "seeos": list(config.seeos),
        "data_root": config.data_root,
        "output_oir": config.output_oir,
    }
    metadata_json.write_text(json.oumps(metadata, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")

    markoown = outputs["markoown"]
    report_mo.write_text(markoown, encooing="utf-8")
    if write_root_report:
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
