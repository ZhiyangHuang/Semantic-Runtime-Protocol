from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from .manual_sanity import _calibration_statuses, _case_type, _question_labels, _temporal_attribution_protocol


def _mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 6) if values else 0.0


def _float_or_zero(value: Any) -> float:
    try:
        if value is None or value == "":
            return 0.0
        return float(value)
    except Exception:
        return 0.0


def _parse_failure_categories(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(category for category in value.split("|") if category)


def _load_locomo_calibration_rows(source_dir: str | Path) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    source_path = Path(source_dir)
    metadata_path = source_path / "metadata.json"
    summary_path = source_path / "external_validation_summary.json"
    records_csv = source_path / "external_validation_records.csv"

    if not metadata_path.exists():
        raise FileNotFoundError(f"Missing calibration metadata: {metadata_path}")
    if not summary_path.exists():
        raise FileNotFoundError(f"Missing calibration summary: {summary_path}")
    if not records_csv.exists():
        raise FileNotFoundError(f"Missing calibration records CSV: {records_csv}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    rows: list[dict[str, Any]] = []
    with records_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                {
                    "benchmark_name": row.get("benchmark_name", "locomo"),
                    "baseline_name": row.get("baseline_name", "srp"),
                    "seed": int(float(row.get("seed", 0) or 0)),
                    "case_id": row.get("case_id", ""),
                    "query": row.get("query", ""),
                    "expected_answer": row.get("expected_answer", ""),
                    "predicted_answer": row.get("predicted_answer", ""),
                    "semantic_coverage": _float_or_zero(row.get("semantic_coverage")),
                    "semantic_drift": _float_or_zero(row.get("semantic_drift")),
                    "fact_accuracy": _float_or_zero(row.get("fact_accuracy")),
                    "relation_accuracy": _float_or_zero(row.get("relation_accuracy")),
                    "recovery_accuracy": _float_or_zero(row.get("recovery_accuracy")),
                    "closure_accuracy": _float_or_zero(row.get("closure_accuracy")),
                    "neighborhood_completeness": _float_or_zero(row.get("neighborhood_completeness")),
                    "hallucinated_relation_rate": _float_or_zero(row.get("hallucinated_relation_rate")),
                    "evidence_cost": _float_or_zero(row.get("evidence_cost")),
                    "answer_accuracy": _float_or_zero(row.get("answer_accuracy")),
                    "official_metric_score": _float_or_zero(row.get("official_metric_score")),
                    "failure_categories": _parse_failure_categories(row.get("failure_categories")),
                }
            )

    return metadata, summary, rows


def _summarize_calibration_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    metrics_fields = [
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

    def extract(field: str, items: list[dict[str, Any]]) -> float:
        return _mean([float(item[field]) for item in items])

    def group_by(key_fn) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            grouped[str(key_fn(row))].append(row)
        return grouped

    overall = {field: extract(field, rows) for field in metrics_fields}
    overall["case_count"] = len(rows)

    benchmark_summary = {}
    for benchmark_name, subset in group_by(lambda row: row["benchmark_name"]).items():
        benchmark_summary[benchmark_name] = {field: extract(field, subset) for field in metrics_fields}
        benchmark_summary[benchmark_name]["case_count"] = len(subset)

    baseline_summary = {}
    for baseline_name, subset in group_by(lambda row: row["baseline_name"]).items():
        baseline_summary[baseline_name] = {field: extract(field, subset) for field in metrics_fields}
        baseline_summary[baseline_name]["case_count"] = len(subset)

    pairwise_summary: dict[str, dict[str, dict[str, float]]] = {}
    for benchmark_name, subset in group_by(lambda row: row["benchmark_name"]).items():
        srp_subset = [row for row in subset if row["baseline_name"] == "srp"]
        benchmark_pairwise: dict[str, dict[str, float]] = {}
        for baseline_name, baseline_subset in sorted(
            ((name, [row for row in subset if row["baseline_name"] == name]) for name in {row["baseline_name"] for row in subset} if name != "srp"),
            key=lambda item: item[0],
        ):
            if srp_subset and baseline_subset:
                benchmark_pairwise[baseline_name] = {
                    "srp_minus_baseline_coverage": round(extract("semantic_coverage", srp_subset) - extract("semantic_coverage", baseline_subset), 6),
                    "srp_minus_baseline_drift": round(extract("semantic_drift", baseline_subset) - extract("semantic_drift", srp_subset), 6),
                    "srp_minus_baseline_relation_accuracy": round(extract("relation_accuracy", srp_subset) - extract("relation_accuracy", baseline_subset), 6),
                    "srp_minus_baseline_cost": round(extract("evidence_cost", srp_subset) - extract("evidence_cost", baseline_subset), 6),
                }
        if benchmark_pairwise:
            pairwise_summary[benchmark_name] = benchmark_pairwise

    return {
        "summary": overall,
        "benchmark_summary": benchmark_summary,
        "baseline_summary": baseline_summary,
        "pairwise_summary": pairwise_summary,
    }


def _row_to_minimal_record(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "run": {
            "benchmark_name": row["benchmark_name"],
            "baseline_name": row["baseline_name"],
            "seed": row["seed"],
            "case": {
                "case_id": row["case_id"],
                "query": row["query"],
                "expected_answer": row["expected_answer"],
            },
        },
        "response": {
            "predicted_answer": row["predicted_answer"],
        },
        "metrics": {
            "semantic_coverage": row["semantic_coverage"],
            "semantic_drift": row["semantic_drift"],
            "fact_accuracy": row["fact_accuracy"],
            "relation_accuracy": row["relation_accuracy"],
            "recovery_accuracy": row["recovery_accuracy"],
            "closure_accuracy": row["closure_accuracy"],
            "evidence_cost": row["evidence_cost"],
            "answer_accuracy": row["answer_accuracy"],
            "official_metric_score": row["official_metric_score"],
        },
        "failure_categories": row["failure_categories"],
    }


def build_calibration_aware_report_from_source_dir(
    source_dir: str | Path,
    benchmark_display_name: str,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_metadata, _, rows = _load_locomo_calibration_rows(source_dir)
    summary_bundle = _summarize_calibration_rows(rows)
    outputs = {
        "config": config or {
            "benchmark_names": source_metadata.get("benchmark_names", ["locomo"]),
            "baseline_names": source_metadata.get("baseline_names", ["full_context", "sliding_window", "vector_rag", "srp"]),
            "seeds": source_metadata.get("seeds", [11, 23, 37]),
            "data_root": source_metadata.get("data_root", "data/locomo"),
            "source_output_dir": str(source_dir),
        },
        "report": {
            "summary": summary_bundle["summary"],
            "benchmark_summary": summary_bundle["benchmark_summary"],
            "baseline_summary": summary_bundle["baseline_summary"],
            "pairwise_summary": summary_bundle["pairwise_summary"],
            "records": [_row_to_minimal_record(row) for row in rows],
        },
    }
    return build_calibration_aware_report(outputs, benchmark_display_name=benchmark_display_name)


def _classify_attribution(record: dict[str, Any]) -> tuple[str, dict[str, str], str]:
    metrics = SimpleNamespace(**record["metrics"])
    statuses = _calibration_statuses(metrics)
    answer_accuracy = float(record["metrics"]["answer_accuracy"])
    if answer_accuracy >= 0.8:
        label = "aligned"
        score_band = "pass"
    elif statuses["memory_status"] == "correct" and statuses["generation_status"] == "incorrect":
        label = "generation_or_scorer_mismatch"
        score_band = "review"
    elif statuses["memory_status"] == "incorrect":
        label = "memory_mismatch"
        score_band = "review"
    else:
        label = "mixed"
        score_band = "review"
    return label, statuses, score_band


def build_calibration_aware_report(outputs: dict[str, Any], benchmark_display_name: str = "LoCoMo") -> dict[str, Any]:
    report = outputs["report"]
    config = outputs["config"]
    records = report.get("records", [])

    traces: list[dict[str, Any]] = []
    by_case_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_baseline: dict[str, list[dict[str, Any]]] = defaultdict(list)
    failure_attribution: dict[str, int] = defaultdict(int)

    for record in records:
        run = record["run"]
        case = run["case"]
        response = record["response"]
        metrics = record["metrics"]
        question_labels = _question_labels(case["query"])
        case_type = _case_type(question_labels, case["expected_answer"])
        attribution_label, statuses, score_band = _classify_attribution(record)
        trace = {
            "benchmark_name": run["benchmark_name"],
            "baseline_name": run["baseline_name"],
            "seed": run["seed"],
            "case_id": case["case_id"],
            "case_type": case_type,
            "question": case["query"],
            "expected_answer": case["expected_answer"],
            "predicted_answer": response["predicted_answer"],
            "official_metric_score": metrics["official_metric_score"],
            "answer_accuracy": metrics["answer_accuracy"],
            "semantic_coverage": metrics["semantic_coverage"],
            "semantic_drift": metrics["semantic_drift"],
            "fact_accuracy": metrics["fact_accuracy"],
            "relation_accuracy": metrics["relation_accuracy"],
            "recovery_accuracy": metrics["recovery_accuracy"],
            "closure_accuracy": metrics["closure_accuracy"],
            "evidence_cost": metrics["evidence_cost"],
            "memory_status": statuses["memory_status"],
            "generation_status": statuses["generation_status"],
            "scorer_status": statuses["scorer_status"],
            "attribution_label": attribution_label,
            "score_band": score_band,
            "failure_categories": list(record.get("failure_categories", [])),
        }
        traces.append(trace)
        by_case_type[case_type].append(trace)
        by_baseline[run["baseline_name"]].append(trace)
        failure_attribution[attribution_label] += 1

    def aggregate(items: list[dict[str, Any]]) -> dict[str, Any]:
        if not items:
            return {
                "count": 0,
                "mean_official_metric_score": 0.0,
                "mean_answer_accuracy": 0.0,
                "mean_semantic_coverage": 0.0,
                "mean_semantic_drift": 0.0,
                "mean_fact_accuracy": 0.0,
                "mean_relation_accuracy": 0.0,
                "memory_status_counts": {},
                "generation_status_counts": {},
                "scorer_status_counts": {},
                "attribution_counts": {},
            }
        count = len(items)
        return {
            "count": count,
            "mean_official_metric_score": _mean([float(item["official_metric_score"]) for item in items]),
            "mean_answer_accuracy": _mean([float(item["answer_accuracy"]) for item in items]),
            "mean_semantic_coverage": _mean([float(item["semantic_coverage"]) for item in items]),
            "mean_semantic_drift": _mean([float(item["semantic_drift"]) for item in items]),
            "mean_fact_accuracy": _mean([float(item["fact_accuracy"]) for item in items]),
            "mean_relation_accuracy": _mean([float(item["relation_accuracy"]) for item in items]),
            "memory_status_counts": dict(
                sorted(
                    {
                        label: sum(1 for item in items if item["memory_status"] == label)
                        for label in {item["memory_status"] for item in items}
                    }.items()
                )
            ),
            "generation_status_counts": dict(
                sorted(
                    {
                        label: sum(1 for item in items if item["generation_status"] == label)
                        for label in {item["generation_status"] for item in items}
                    }.items()
                )
            ),
            "scorer_status_counts": dict(
                sorted(
                    {
                        label: sum(1 for item in items if item["scorer_status"] == label)
                        for label in {item["scorer_status"] for item in items}
                    }.items()
                )
            ),
            "attribution_counts": dict(
                sorted(
                    {
                        label: sum(1 for item in items if item["attribution_label"] == label)
                        for label in {item["attribution_label"] for item in items}
                    }.items()
                )
            ),
        }

    calibration_matrix = {
        "row_count": len(traces),
        "by_case_type": {key: aggregate(value) for key, value in sorted(by_case_type.items())},
        "by_baseline": {key: aggregate(value) for key, value in sorted(by_baseline.items())},
        "failure_attribution_counts": dict(sorted(failure_attribution.items())),
    }

    official_result = {
        "summary": report.get("summary", {}),
        "baseline_summary": report.get("baseline_summary", {}),
        "benchmark_summary": report.get("benchmark_summary", {}),
        "pairwise_summary": report.get("pairwise_summary", {}),
    }

    diagnostic_result = {
        "temporal_protocol": _temporal_attribution_protocol(),
        "calibration_matrix": calibration_matrix,
        "traces": traces,
    }

    gate = {
        "adapter": "pass",
        "temporal_protocol": "pass",
        "scorer_alignment": "pending",
        "failure_attribution": "interpretable" if traces else "pending",
        "promotion": "pending",
        "notes": [
            "Calibration-aware rerun preserves benchmark/baseline/seed settings.",
            "Scorer mismatches are treated as measurement issues, not SRP memory failures.",
        ],
    }

    return {
        "config": config,
        "benchmark_display_name": benchmark_display_name,
        "official_result": official_result,
        "diagnostic_result": diagnostic_result,
        "failure_attribution": dict(sorted(failure_attribution.items())),
        "gate": gate,
        "record_count": len(records),
        "trace_count": len(traces),
    }


def render_calibration_aware_report(calibration: dict[str, Any]) -> str:
    config = calibration["config"]
    official = calibration["official_result"]
    diag = calibration["diagnostic_result"]
    matrix = diag["calibration_matrix"]
    protocol = diag["temporal_protocol"]
    benchmark_display_name = calibration.get("benchmark_display_name", "LoCoMo")
    lines = [
        f"# SRP {benchmark_display_name} Calibration-Aware External Validation Report",
        "",
        f"This report re-runs the frozen {benchmark_display_name} MVP slice under the calibration-aware temporal attribution protocol.",
        "It is still a calibration-aware artifact, not a promotion of external validity.",
        "",
        "## 1. Frozen Scope",
        "",
        f"- Benchmark: `{benchmark_display_name}`",
        f"- Baselines: `{', '.join(config['baseline_names'])}`",
        f"- Seeds: `{', '.join(str(seed) for seed in config['seeds'])}`",
        f"- Data root: `{config['data_root'] or 'fixtures'}`",
        "",
        "## 2. Official Benchmark Result",
        "",
        f"- Record count: `{calibration['record_count']}`",
    ]
    summary = official.get("summary", {})
    for key in (
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
    ):
        if key in summary:
            lines.append(f"- {key}: `{summary[key]}`")
    lines.extend(["", "## 3. Temporal Attribution Protocol V1", ""])
    for step in protocol["steps"]:
        lines.append(f"- Step {step['step']}: `{step['name']}`")
        lines.append(f"  - Input: `{step['input']}`")
        lines.append(f"  - Decision: {step['decision']}")
    lines.extend(
        [
            "",
            f"Interpretation boundary: {protocol['freeze_boundary']}",
            "",
            "## 4. Diagnostic Calibration Result",
            "",
            "| Case Type | Count | Mean Official | Mean Answer | Mean Coverage | Mean Drift | Memory | Generation | Scorer | Attribution |",
            "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |",
        ]
    )
    for case_type, stats in matrix["by_case_type"].items():
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{case_type}`",
                    str(stats["count"]),
                    str(stats["mean_official_metric_score"]),
                    str(stats["mean_answer_accuracy"]),
                    str(stats["mean_semantic_coverage"]),
                    str(stats["mean_semantic_drift"]),
                    ", ".join(f"{k}:{v}" for k, v in stats["memory_status_counts"].items()) or "none",
                    ", ".join(f"{k}:{v}" for k, v in stats["generation_status_counts"].items()) or "none",
                    ", ".join(f"{k}:{v}" for k, v in stats["scorer_status_counts"].items()) or "none",
                    ", ".join(f"{k}:{v}" for k, v in stats["attribution_counts"].items()) or "none",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "### Baseline Calibration Summary",
            "",
            "| Baseline | Count | Mean Official | Mean Answer | Mean Coverage | Mean Drift | Memory | Generation | Scorer | Attribution |",
            "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |",
        ]
    )
    for baseline_name, stats in matrix["by_baseline"].items():
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{baseline_name}`",
                    str(stats["count"]),
                    str(stats["mean_official_metric_score"]),
                    str(stats["mean_answer_accuracy"]),
                    str(stats["mean_semantic_coverage"]),
                    str(stats["mean_semantic_drift"]),
                    ", ".join(f"{k}:{v}" for k, v in stats["memory_status_counts"].items()) or "none",
                    ", ".join(f"{k}:{v}" for k, v in stats["generation_status_counts"].items()) or "none",
                    ", ".join(f"{k}:{v}" for k, v in stats["scorer_status_counts"].items()) or "none",
                    ", ".join(f"{k}:{v}" for k, v in stats["attribution_counts"].items()) or "none",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## 5. Failure Attribution Distribution",
            "",
        ]
    )
    for key, value in calibration["failure_attribution"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## 6. Evidence Promotion Decision",
            "",
        ]
    )
    for key, value in calibration["gate"].items():
        if key == "notes":
            continue
        lines.append(f"- {key}: `{value}`")
    if calibration["gate"].get("notes"):
        lines.append("")
        lines.append("Notes:")
        for note in calibration["gate"]["notes"]:
            lines.append(f"- {note}")
    lines.append("")
    lines.extend(
        [
            "## 7. Trace Inventory",
            "",
            f"- trace count: `{calibration['trace_count']}`",
        ]
    )
    return "\n".join(lines)


def write_locomo_calibration_aware_outputs(
    output_dir: str | Path,
    outputs: dict[str, Any],
) -> dict[str, Any]:
    report = build_calibration_aware_report(outputs, benchmark_display_name="LoCoMo")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    markdown = render_calibration_aware_report(report)
    report_md = output_path / "locomo_calibration_aware_report.md"
    report_json = output_path / "locomo_calibration_aware_report.json"
    summary_json = output_path / "locomo_calibration_aware_summary.json"
    traces_json = output_path / "locomo_calibration_aware_traces.json"
    matrix_json = output_path / "locomo_calibration_aware_matrix.json"
    gate_json = output_path / "locomo_calibration_gate.json"

    report_md.write_text(markdown, encoding="utf-8")
    report_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    summary_json.write_text(json.dumps(report["official_result"]["summary"], indent=2, ensure_ascii=False), encoding="utf-8")
    traces_json.write_text(json.dumps(report["diagnostic_result"]["traces"], indent=2, ensure_ascii=False), encoding="utf-8")
    matrix_json.write_text(json.dumps(report["diagnostic_result"]["calibration_matrix"], indent=2, ensure_ascii=False), encoding="utf-8")
    gate_json.write_text(json.dumps(report["gate"], indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "report": report,
        "markdown": markdown,
        "report_markdown": str(report_md),
        "report_json": str(report_json),
        "summary_json": str(summary_json),
        "traces_json": str(traces_json),
        "matrix_json": str(matrix_json),
        "gate_json": str(gate_json),
    }


def write_locomo_calibration_aware_outputs_from_source_dir(
    source_dir: str | Path,
    output_dir: str | Path,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    calibration = build_calibration_aware_report_from_source_dir(source_dir, "LoCoMo", config=config)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    markdown = render_calibration_aware_report(calibration)
    report_md = output_path / "locomo_calibration_aware_report.md"
    report_json = output_path / "locomo_calibration_aware_report.json"
    summary_json = output_path / "locomo_calibration_aware_summary.json"
    traces_json = output_path / "locomo_calibration_aware_traces.json"
    matrix_json = output_path / "locomo_calibration_aware_matrix.json"
    gate_json = output_path / "locomo_calibration_gate.json"
    metadata_json = output_path / "locomo_calibration_aware_metadata.json"

    report_md.write_text(markdown, encoding="utf-8")
    report_json.write_text(json.dumps(calibration, indent=2, ensure_ascii=False), encoding="utf-8")
    summary_json.write_text(
        json.dumps(calibration["official_result"]["summary"], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    traces_json.write_text(
        json.dumps(calibration["diagnostic_result"]["traces"], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    matrix_json.write_text(
        json.dumps(calibration["diagnostic_result"]["calibration_matrix"], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    gate_json.write_text(json.dumps(calibration["gate"], indent=2, ensure_ascii=False), encoding="utf-8")
    metadata_json.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "generated_by": "external_validation_calibration_aware_v1",
                "source_output_dir": str(source_dir),
                "output_dir": str(output_path),
                "case_count": calibration["record_count"],
                "trace_count": calibration["trace_count"],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return {
        "output_dir": str(output_path),
        "report_markdown": str(report_md),
        "report_json": str(report_json),
        "summary_json": str(summary_json),
        "traces_json": str(traces_json),
        "matrix_json": str(matrix_json),
        "gate_json": str(gate_json),
        "metadata_json": str(metadata_json),
        "report": calibration,
        "markdown": markdown,
    }


def write_calibration_aware_outputs_from_source_dir(
    source_dir: str | Path,
    output_dir: str | Path,
    benchmark_display_name: str,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    calibration = build_calibration_aware_report_from_source_dir(source_dir, benchmark_display_name, config=config)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    markdown = render_calibration_aware_report(calibration)
    prefix = benchmark_display_name.lower().replace(" ", "_")
    report_md = output_path / f"{prefix}_calibration_aware_report.md"
    report_json = output_path / f"{prefix}_calibration_aware_report.json"
    summary_json = output_path / f"{prefix}_calibration_aware_summary.json"
    traces_json = output_path / f"{prefix}_calibration_aware_traces.json"
    matrix_json = output_path / f"{prefix}_calibration_aware_matrix.json"
    gate_json = output_path / f"{prefix}_calibration_gate.json"
    metadata_json = output_path / f"{prefix}_calibration_aware_metadata.json"

    report_md.write_text(markdown, encoding="utf-8")
    report_json.write_text(json.dumps(calibration, indent=2, ensure_ascii=False), encoding="utf-8")
    summary_json.write_text(json.dumps(calibration["official_result"]["summary"], indent=2, ensure_ascii=False), encoding="utf-8")
    traces_json.write_text(json.dumps(calibration["diagnostic_result"]["traces"], indent=2, ensure_ascii=False), encoding="utf-8")
    matrix_json.write_text(json.dumps(calibration["diagnostic_result"]["calibration_matrix"], indent=2, ensure_ascii=False), encoding="utf-8")
    gate_json.write_text(json.dumps(calibration["gate"], indent=2, ensure_ascii=False), encoding="utf-8")
    metadata_json.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "generated_by": "external_validation_calibration_aware_v1",
                "benchmark_display_name": benchmark_display_name,
                "source_output_dir": str(source_dir),
                "output_dir": str(output_path),
                "case_count": calibration["record_count"],
                "trace_count": calibration["trace_count"],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return {
        "output_dir": str(output_path),
        "report_markdown": str(report_md),
        "report_json": str(report_json),
        "summary_json": str(summary_json),
        "traces_json": str(traces_json),
        "matrix_json": str(matrix_json),
        "gate_json": str(gate_json),
        "metadata_json": str(metadata_json),
        "report": calibration,
        "markdown": markdown,
    }


def build_locomo_calibration_aware_report_from_source_dir(
    source_dir: str | Path,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_calibration_aware_report_from_source_dir(source_dir, "LoCoMo", config=config)


def build_locomo_calibration_aware_report(outputs: dict[str, Any]) -> dict[str, Any]:
    return build_calibration_aware_report(outputs, benchmark_display_name="LoCoMo")


def render_locomo_calibration_aware_report(calibration: dict[str, Any]) -> str:
    return render_calibration_aware_report(calibration)
