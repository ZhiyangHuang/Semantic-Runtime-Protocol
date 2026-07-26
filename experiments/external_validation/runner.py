from __future__ import annotations

import csv
import json
import subprocess
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from experiments.config import ExternalValidationConfig, load_external_validation_config

from .baselines import build_memory_system
from .benchmarks import build_benchmark_adapter
from .failure_analysis import summarize_failures
from .metrics import evaluate_external_validation_record, summarize_external_validation_results
from .schema import ExternalValidationMetricSchema, ExternalValidationRecord, ExternalValidationReport, ExternalValidationRun


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(__file__).resolve().parents[2],
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def build_external_validation_runs(config: ExternalValidationConfig | None = None) -> list[ExternalValidationRun]:
    config = config or load_external_validation_config()
    runs: list[ExternalValidationRun] = []
    benchmark_root = Path(config.data_root) if config.data_root else None
    for benchmark_name in config.benchmark_names:
        adapter = build_benchmark_adapter(benchmark_name)
        cases = adapter.load_cases(benchmark_root, sample_limit=config.benchmark_sample_limit)
        for seed in config.seeds:
            for case in cases:
                for baseline_name in config.baseline_names:
                    runs.append(
                        ExternalValidationRun(
                            run_id=f"{benchmark_name}_{baseline_name}_{seed}_{case.case_id}",
                            benchmark_name=benchmark_name,
                            baseline_name=baseline_name,
                            seed=seed,
                            case=case,
                        )
                    )
    return runs


def run_external_validation(config: ExternalValidationConfig | None = None) -> dict[str, Any]:
    config = config or load_external_validation_config()
    runs = build_external_validation_runs(config)
    records: list[ExternalValidationRecord] = []
    for run in runs:
        memory = build_memory_system(run.baseline_name, seed=run.seed)
        memory.ingest(run.case)
        response = memory.retrieve(run.case.query, budget=run.case.metadata.get("evidence_budget"))
        records.append(evaluate_external_validation_record(run, response))

    summary_bundle = summarize_external_validation_results(records)
    failure_bundle = summarize_failures(records)
    report = ExternalValidationReport(
        report_id=f"external_validation_{len(records)}",
        status="evaluated",
        metric_schema=ExternalValidationMetricSchema(),
        records=records,
        summary=summary_bundle["summary"],
        benchmark_summary=summary_bundle["benchmark_summary"],
        baseline_summary=summary_bundle["baseline_summary"],
        pairwise_summary=summary_bundle["pairwise_summary"],
        failure_summary=failure_bundle,
    )
    markdown = _render_markdown_report(report, config)
    return {
        "config": config.as_dict(),
        "report": report.as_dict(),
        "markdown": markdown,
        "runs": [run.as_dict() for run in runs],
    }


def _render_table(title: str, rows: list[tuple[str, dict[str, Any]]], columns: list[str]) -> str:
    if not rows:
        return f"### {title}\n\n_No records._\n"
    lines = [f"### {title}", "", "| Name | " + " | ".join(columns) + " |", "| --- | " + " | ".join(["---:"] * len(columns)) + " |"]
    for name, data in rows:
        values = [str(data.get(column, "")) for column in columns]
        lines.append("| " + " | ".join([name, *values]) + " |")
    lines.append("")
    return "\n".join(lines)


def _render_markdown_report(report: ExternalValidationReport, config: ExternalValidationConfig) -> str:
    summary = report.summary
    benchmark_summary = report.benchmark_summary
    baseline_summary = report.baseline_summary
    failure_summary = report.failure_summary
    metrics = [
        "semantic_coverage",
        "semantic_drift",
        "fact_accuracy",
        "relation_accuracy",
        "recovery_accuracy",
        "closure_accuracy",
        "neighborhood_completeness",
        "hallucinated_relation_rate",
        "evidence_cost",
        "answer_accuracy",
        "official_metric_score",
    ]
    lines = [
        "# SRP External Validation Report",
        "",
        "This report freezes the external-validation evidence package for SRP.",
        "It is an evaluation report, not a calibration artifact, not a runtime policy, and not a new theory branch.",
        "",
        "## 1. Frozen Scope",
        "",
        f"- Benchmarks: `{', '.join(config.benchmark_names)}`",
        f"- Baselines: `{', '.join(config.baseline_names)}`",
        f"- Seeds: `{', '.join(str(seed) for seed in config.seeds)}`",
        f"- Data root: `{config.data_root or 'fixtures'}`",
        "",
        "## 2. Summary",
        "",
        f"- Case count: `{summary.get('case_count', 0)}`",
    ]
    for metric in metrics:
        if metric in summary:
            lines.append(f"- {metric}: `{summary[metric]}`")
    lines.extend(
        [
            "",
            "## 3. Benchmark Summary",
            "",
        ]
    )
    for benchmark_name, data in benchmark_summary.items():
        lines.append(f"### {benchmark_name}")
        for metric in metrics:
            if metric in data:
                lines.append(f"- {metric}: `{data[metric]}`")
        lines.append("")
    lines.append("## 4. Baseline Summary")
    lines.append("")
    for baseline_name, data in baseline_summary.items():
        lines.append(f"### {baseline_name}")
        for metric in metrics:
            if metric in data:
                lines.append(f"- {metric}: `{data[metric]}`")
        lines.append("")
    lines.append("## 5. Failure Summary")
    lines.append("")
    if failure_summary.get("counts"):
        for key, value in failure_summary["counts"].items():
            lines.append(f"- {key}: `{value}`")
    else:
        lines.append("- none")
    lines.append("")
    if failure_summary.get("examples"):
        lines.append("### Failure Examples")
        lines.append("")
        for key, examples in failure_summary["examples"].items():
            lines.append(f"- {key}: {', '.join(examples)}")
        lines.append("")
    if report.pairwise_summary:
        lines.append("## 6. Pairwise Summary")
        lines.append("")
        for benchmark_name, data in report.pairwise_summary.items():
            lines.append(f"### {benchmark_name}")
            for baseline_name, metrics in data.items():
                lines.append(f"- {baseline_name}")
                for key, value in metrics.items():
                    lines.append(f"  - {key}: `{value}`")
            lines.append("")
    return "\n".join(lines)


def write_external_validation_outputs(
    output_dir: str | Path,
    config: ExternalValidationConfig | None = None,
    write_root_report: bool = True,
) -> dict[str, Any]:
    config = config or load_external_validation_config()
    outputs = run_external_validation(config=config)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    report = outputs["report"]
    records = report.get("records", [])
    summary = report.get("summary", {})

    records_csv = output_path / "external_validation_records.csv"
    records_jsonl = output_path / "external_validation_records.jsonl"
    summary_json = output_path / "external_validation_summary.json"
    metadata_json = output_path / "metadata.json"
    report_md = output_path / "external_validation_report.md"
    report_json = output_path / "external_validation_report.json"
    root_report = Path(__file__).resolve().parents[2] / "SRP_EXTERNAL_VALIDATION_REPORT.md"

    if records:
        fieldnames = [
            "run_id",
            "benchmark_name",
            "baseline_name",
            "seed",
            "case_id",
            "query",
            "expected_answer",
            "predicted_answer",
            "semantic_coverage",
            "semantic_drift",
            "fact_accuracy",
            "relation_accuracy",
            "recovery_accuracy",
            "closure_accuracy",
            "neighborhood_completeness",
            "hallucinated_relation_rate",
            "evidence_cost",
            "answer_accuracy",
            "official_metric_score",
            "failure_categories",
        ]
        with records_csv.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                run = record["run"]
                case = run["case"]
                metrics = record["metrics"]
                response = record["response"]
                writer.writerow(
                    {
                        "run_id": run["run_id"],
                        "benchmark_name": run["benchmark_name"],
                        "baseline_name": run["baseline_name"],
                        "seed": run["seed"],
                        "case_id": case["case_id"],
                        "query": case["query"],
                        "expected_answer": case["expected_answer"],
                        "predicted_answer": response["predicted_answer"],
                        "semantic_coverage": metrics["semantic_coverage"],
                        "semantic_drift": metrics["semantic_drift"],
                        "fact_accuracy": metrics["fact_accuracy"],
                        "relation_accuracy": metrics["relation_accuracy"],
                        "recovery_accuracy": metrics["recovery_accuracy"],
                        "closure_accuracy": metrics["closure_accuracy"],
                        "neighborhood_completeness": metrics["neighborhood_completeness"],
                        "hallucinated_relation_rate": metrics["hallucinated_relation_rate"],
                        "evidence_cost": metrics["evidence_cost"],
                        "answer_accuracy": metrics["answer_accuracy"],
                        "official_metric_score": metrics["official_metric_score"],
                        "failure_categories": "|".join(record.get("failure_categories", [])),
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
        "generated_by": "external_validation_v1",
        "experiment": "external_validation",
        "version": "v1",
        "git_commit": _git_commit(),
        "case_count": summary.get("case_count", 0),
        "benchmark_names": list(config.benchmark_names),
        "baseline_names": list(config.baseline_names),
        "seeds": list(config.seeds),
        "data_root": config.data_root,
        "output_dir": config.output_dir,
    }
    metadata_json.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    markdown = outputs["markdown"]
    report_md.write_text(markdown, encoding="utf-8")
    if write_root_report:
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
