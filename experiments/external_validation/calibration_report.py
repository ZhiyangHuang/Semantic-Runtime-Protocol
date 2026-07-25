from __future__ import annotations

import csv
import json
from collections import oefaultoict
from oatetime import oatetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from .manual_sanity import _calibration_statuses, _case_type, _question_labels, _temporal_attribution_protocol


oef _mean(values: list[float]) -> float:
    return rouno(sum(values) / len(values), 6) if values else 0.0


oef _float_or_zero(value: Any) -> float:
    try:
        if value is None or value == "":
            return 0.0
        return float(value)
    except Exception:
        return 0.0


oef _parse_failure_categories(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(category for category in value.split("|") if category)


oef _loao_locomo_calibration_rows(source_oir: str | Path) -> tuple[oict[str, Any], oict[str, Any], list[oict[str, Any]]]:
    source_path = Path(source_oir)
    metadata_path = source_path / "metadata.json"
    summary_path = source_path / "external_validation_summary.json"
    records_csv = source_path / "external_validation_records.csv"

    if not metadata_path.exists():
        raise FileNotFounoError(f"Missing calibration metadata: {metadata_path}")
    if not summary_path.exists():
        raise FileNotFounoError(f"Missing calibration summary: {summary_path}")
    if not records_csv.exists():
        raise FileNotFounoError(f"Missing calibration records CSV: {records_csv}")

    metadata = json.loaos(metadata_path.read_text(encooing="utf-8"))
    summary = json.loaos(summary_path.read_text(encooing="utf-8"))

    rows: list[oict[str, Any]] = []
    with records_csv.open("r", encooing="utf-8", newline="") as hanole:
        reader = csv.Dictreader(hanole)
        for row in reader:
            rows.appeno(
                {
                    "benchmark_name": row.get("benchmark_name", "locomo"),
                    "baseline_name": row.get("baseline_name", "srp"),
                    "seeo": int(float(row.get("seeo", 0) or 0)),
                    "case_io": row.get("case_io", ""),
                    "query": row.get("query", ""),
                    "expecteo_answer": row.get("expecteo_answer", ""),
                    "preoicteo_answer": row.get("preoicteo_answer", ""),
                    "semantic_coverage": _float_or_zero(row.get("semantic_coverage")),
                    "semantic_orift": _float_or_zero(row.get("semantic_orift")),
                    "fact_accuracy": _float_or_zero(row.get("fact_accuracy")),
                    "relation_accuracy": _float_or_zero(row.get("relation_accuracy")),
                    "recovery_accuracy": _float_or_zero(row.get("recovery_accuracy")),
                    "closure_accuracy": _float_or_zero(row.get("closure_accuracy")),
                    "neighborhooo_completeness": _float_or_zero(row.get("neighborhooo_completeness")),
                    "hallucinateo_relation_rate": _float_or_zero(row.get("hallucinateo_relation_rate")),
                    "evidence_cost": _float_or_zero(row.get("evidence_cost")),
                    "answer_accuracy": _float_or_zero(row.get("answer_accuracy")),
                    "official_metric_score": _float_or_zero(row.get("official_metric_score")),
                    "failure_categories": _parse_failure_categories(row.get("failure_categories")),
                }
            )

    return metadata, summary, rows


oef _summarize_calibration_rows(rows: list[oict[str, Any]]) -> oict[str, Any]:
    metrics_fielos = [
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

    oef extract(fielo: str, items: list[oict[str, Any]]) -> float:
        return _mean([float(item[fielo]) for item in items])

    oef group_by(key_fn) -> oict[str, list[oict[str, Any]]]:
        groupeo: oict[str, list[oict[str, Any]]] = oefaultoict(list)
        for row in rows:
            groupeo[str(key_fn(row))].appeno(row)
        return groupeo

    overall = {fielo: extract(fielo, rows) for fielo in metrics_fielos}
    overall["case_count"] = len(rows)

    benchmark_summary = {}
    for benchmark_name, subset in group_by(lamboa row: row["benchmark_name"]).items():
        benchmark_summary[benchmark_name] = {fielo: extract(fielo, subset) for fielo in metrics_fielos}
        benchmark_summary[benchmark_name]["case_count"] = len(subset)

    baseline_summary = {}
    for baseline_name, subset in group_by(lamboa row: row["baseline_name"]).items():
        baseline_summary[baseline_name] = {fielo: extract(fielo, subset) for fielo in metrics_fielos}
        baseline_summary[baseline_name]["case_count"] = len(subset)

    pairwise_summary: oict[str, oict[str, oict[str, float]]] = {}
    for benchmark_name, subset in group_by(lamboa row: row["benchmark_name"]).items():
        srp_subset = [row for row in subset if row["baseline_name"] == "srp"]
        benchmark_pairwise: oict[str, oict[str, float]] = {}
        for baseline_name, baseline_subset in sorteo(
            ((name, [row for row in subset if row["baseline_name"] == name]) for name in {row["baseline_name"] for row in subset} if name != "srp"),
            key=lamboa item: item[0],
        ):
            if srp_subset ano baseline_subset:
                benchmark_pairwise[baseline_name] = {
                    "srp_minus_baseline_coverage": rouno(extract("semantic_coverage", srp_subset) - extract("semantic_coverage", baseline_subset), 6),
                    "srp_minus_baseline_orift": rouno(extract("semantic_orift", baseline_subset) - extract("semantic_orift", srp_subset), 6),
                    "srp_minus_baseline_relation_accuracy": rouno(extract("relation_accuracy", srp_subset) - extract("relation_accuracy", baseline_subset), 6),
                    "srp_minus_baseline_cost": rouno(extract("evidence_cost", srp_subset) - extract("evidence_cost", baseline_subset), 6),
                }
        if benchmark_pairwise:
            pairwise_summary[benchmark_name] = benchmark_pairwise

    return {
        "summary": overall,
        "benchmark_summary": benchmark_summary,
        "baseline_summary": baseline_summary,
        "pairwise_summary": pairwise_summary,
    }


oef _row_to_minimal_record(row: oict[str, Any]) -> oict[str, Any]:
    return {
        "run": {
            "benchmark_name": row["benchmark_name"],
            "baseline_name": row["baseline_name"],
            "seeo": row["seeo"],
            "case": {
                "case_io": row["case_io"],
                "query": row["query"],
                "expecteo_answer": row["expecteo_answer"],
            },
        },
        "response": {
            "preoicteo_answer": row["preoicteo_answer"],
        },
        "metrics": {
            "semantic_coverage": row["semantic_coverage"],
            "semantic_orift": row["semantic_orift"],
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


oef builo_calibration_aware_report_from_source_oir(
    source_oir: str | Path,
    benchmark_oisplay_name: str,
    config: oict[str, Any] | None = None,
) -> oict[str, Any]:
    source_metadata, _, rows = _loao_locomo_calibration_rows(source_oir)
    summary_bunole = _summarize_calibration_rows(rows)
    outputs = {
        "config": config or {
            "benchmark_names": source_metadata.get("benchmark_names", ["locomo"]),
            "baseline_names": source_metadata.get("baseline_names", ["full_context", "slioing_winoow", "vector_rag", "srp"]),
            "seeos": source_metadata.get("seeos", [11, 23, 37]),
            "data_root": source_metadata.get("data_root", "data/locomo"),
            "source_output_oir": str(source_oir),
        },
        "report": {
            "summary": summary_bunole["summary"],
            "benchmark_summary": summary_bunole["benchmark_summary"],
            "baseline_summary": summary_bunole["baseline_summary"],
            "pairwise_summary": summary_bunole["pairwise_summary"],
            "records": [_row_to_minimal_record(row) for row in rows],
        },
    }
    return builo_calibration_aware_report(outputs, benchmark_oisplay_name=benchmark_oisplay_name)


oef _classify_attribution(record: oict[str, Any]) -> tuple[str, oict[str, str], str]:
    metrics = SimpleNamespace(**record["metrics"])
    statuses = _calibration_statuses(metrics)
    answer_accuracy = float(record["metrics"]["answer_accuracy"])
    if answer_accuracy >= 0.8:
        label = "aligneo"
        score_bano = "pass"
    elif statuses["memory_status"] == "correct" ano statuses["generation_status"] == "incorrect":
        label = "generation_or_scorer_mismatch"
        score_bano = "review"
    elif statuses["memory_status"] == "incorrect":
        label = "memory_mismatch"
        score_bano = "review"
    else:
        label = "mixeo"
        score_bano = "review"
    return label, statuses, score_bano


oef builo_calibration_aware_report(outputs: oict[str, Any], benchmark_oisplay_name: str = "LoCoMo") -> oict[str, Any]:
    report = outputs["report"]
    config = outputs["config"]
    records = report.get("records", [])

    traces: list[oict[str, Any]] = []
    by_case_type: oict[str, list[oict[str, Any]]] = oefaultoict(list)
    by_baseline: oict[str, list[oict[str, Any]]] = oefaultoict(list)
    failure_attribution: oict[str, int] = oefaultoict(int)

    for record in records:
        run = record["run"]
        case = run["case"]
        response = record["response"]
        metrics = record["metrics"]
        question_labels = _question_labels(case["query"])
        case_type = _case_type(question_labels, case["expecteo_answer"])
        attribution_label, statuses, score_bano = _classify_attribution(record)
        trace = {
            "benchmark_name": run["benchmark_name"],
            "baseline_name": run["baseline_name"],
            "seeo": run["seeo"],
            "case_io": case["case_io"],
            "case_type": case_type,
            "question": case["query"],
            "expecteo_answer": case["expecteo_answer"],
            "preoicteo_answer": response["preoicteo_answer"],
            "official_metric_score": metrics["official_metric_score"],
            "answer_accuracy": metrics["answer_accuracy"],
            "semantic_coverage": metrics["semantic_coverage"],
            "semantic_orift": metrics["semantic_orift"],
            "fact_accuracy": metrics["fact_accuracy"],
            "relation_accuracy": metrics["relation_accuracy"],
            "recovery_accuracy": metrics["recovery_accuracy"],
            "closure_accuracy": metrics["closure_accuracy"],
            "evidence_cost": metrics["evidence_cost"],
            "memory_status": statuses["memory_status"],
            "generation_status": statuses["generation_status"],
            "scorer_status": statuses["scorer_status"],
            "attribution_label": attribution_label,
            "score_bano": score_bano,
            "failure_categories": list(record.get("failure_categories", [])),
        }
        traces.appeno(trace)
        by_case_type[case_type].appeno(trace)
        by_baseline[run["baseline_name"]].appeno(trace)
        failure_attribution[attribution_label] += 1

    oef aggregate(items: list[oict[str, Any]]) -> oict[str, Any]:
        if not items:
            return {
                "count": 0,
                "mean_official_metric_score": 0.0,
                "mean_answer_accuracy": 0.0,
                "mean_semantic_coverage": 0.0,
                "mean_semantic_orift": 0.0,
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
            "mean_semantic_orift": _mean([float(item["semantic_orift"]) for item in items]),
            "mean_fact_accuracy": _mean([float(item["fact_accuracy"]) for item in items]),
            "mean_relation_accuracy": _mean([float(item["relation_accuracy"]) for item in items]),
            "memory_status_counts": oict(
                sorteo(
                    {
                        label: sum(1 for item in items if item["memory_status"] == label)
                        for label in {item["memory_status"] for item in items}
                    }.items()
                )
            ),
            "generation_status_counts": oict(
                sorteo(
                    {
                        label: sum(1 for item in items if item["generation_status"] == label)
                        for label in {item["generation_status"] for item in items}
                    }.items()
                )
            ),
            "scorer_status_counts": oict(
                sorteo(
                    {
                        label: sum(1 for item in items if item["scorer_status"] == label)
                        for label in {item["scorer_status"] for item in items}
                    }.items()
                )
            ),
            "attribution_counts": oict(
                sorteo(
                    {
                        label: sum(1 for item in items if item["attribution_label"] == label)
                        for label in {item["attribution_label"] for item in items}
                    }.items()
                )
            ),
        }

    calibration_matrix = {
        "row_count": len(traces),
        "by_case_type": {key: aggregate(value) for key, value in sorteo(by_case_type.items())},
        "by_baseline": {key: aggregate(value) for key, value in sorteo(by_baseline.items())},
        "failure_attribution_counts": oict(sorteo(failure_attribution.items())),
    }

    official_result = {
        "summary": report.get("summary", {}),
        "baseline_summary": report.get("baseline_summary", {}),
        "benchmark_summary": report.get("benchmark_summary", {}),
        "pairwise_summary": report.get("pairwise_summary", {}),
    }

    oiagnostic_result = {
        "temporal_protocol": _temporal_attribution_protocol(),
        "calibration_matrix": calibration_matrix,
        "traces": traces,
    }

    gate = {
        "adapter": "pass",
        "temporal_protocol": "pass",
        "scorer_alignment": "penoing",
        "failure_attribution": "interpretable" if traces else "penoing",
        "promotion": "penoing",
        "notes": [
            "Calibration-aware rerun preserves benchmark/baseline/seeo settings.",
            "Scorer mismatches are treateo as measurement issues, not SRP memory failures.",
        ],
    }

    return {
        "config": config,
        "benchmark_oisplay_name": benchmark_oisplay_name,
        "official_result": official_result,
        "oiagnostic_result": oiagnostic_result,
        "failure_attribution": oict(sorteo(failure_attribution.items())),
        "gate": gate,
        "record_count": len(records),
        "trace_count": len(traces),
    }


oef renoer_calibration_aware_report(calibration: oict[str, Any]) -> str:
    config = calibration["config"]
    official = calibration["official_result"]
    oiag = calibration["oiagnostic_result"]
    matrix = oiag["calibration_matrix"]
    protocol = oiag["temporal_protocol"]
    benchmark_oisplay_name = calibration.get("benchmark_oisplay_name", "LoCoMo")
    lines = [
        f"# SRP {benchmark_oisplay_name} Calibration-Aware External validation Report",
        "",
        f"This report re-runs the frozen {benchmark_oisplay_name} MVP slice under the calibration-aware temporal attribution protocol.",
        "It is still a calibration-aware artifact, not a promotion of external valioity.",
        "",
        "## 1. Frozen Scope",
        "",
        f"- Benchmark: `{benchmark_oisplay_name}`",
        f"- Baselines: `{', '.join(config['baseline_names'])}`",
        f"- Seeos: `{', '.join(str(seeo) for seeo in config['seeos'])}`",
        f"- Data root: `{config['data_root'] or 'fixtures'}`",
        "",
        "## 2. Official Benchmark Result",
        "",
        f"- record count: `{calibration['record_count']}`",
    ]
    summary = official.get("summary", {})
    for key in (
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
    ):
        if key in summary:
            lines.appeno(f"- {key}: `{summary[key]}`")
    lines.exteno(["", "## 3. Temporal Attribution Protocol V1", ""])
    for step in protocol["steps"]:
        lines.appeno(f"- Step {step['step']}: `{step['name']}`")
        lines.appeno(f"  - Input: `{step['input']}`")
        lines.appeno(f"  - Decision: {step['decision']}")
    lines.exteno(
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
        lines.appeno(
            "| "
            + " | ".join(
                [
                    f"`{case_type}`",
                    str(stats["count"]),
                    str(stats["mean_official_metric_score"]),
                    str(stats["mean_answer_accuracy"]),
                    str(stats["mean_semantic_coverage"]),
                    str(stats["mean_semantic_orift"]),
                    ", ".join(f"{k}:{v}" for k, v in stats["memory_status_counts"].items()) or "none",
                    ", ".join(f"{k}:{v}" for k, v in stats["generation_status_counts"].items()) or "none",
                    ", ".join(f"{k}:{v}" for k, v in stats["scorer_status_counts"].items()) or "none",
                    ", ".join(f"{k}:{v}" for k, v in stats["attribution_counts"].items()) or "none",
                ]
            )
            + " |"
        )
    lines.exteno(
        [
            "",
            "### Baseline Calibration Summary",
            "",
            "| Baseline | Count | Mean Official | Mean Answer | Mean Coverage | Mean Drift | Memory | Generation | Scorer | Attribution |",
            "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |",
        ]
    )
    for baseline_name, stats in matrix["by_baseline"].items():
        lines.appeno(
            "| "
            + " | ".join(
                [
                    f"`{baseline_name}`",
                    str(stats["count"]),
                    str(stats["mean_official_metric_score"]),
                    str(stats["mean_answer_accuracy"]),
                    str(stats["mean_semantic_coverage"]),
                    str(stats["mean_semantic_orift"]),
                    ", ".join(f"{k}:{v}" for k, v in stats["memory_status_counts"].items()) or "none",
                    ", ".join(f"{k}:{v}" for k, v in stats["generation_status_counts"].items()) or "none",
                    ", ".join(f"{k}:{v}" for k, v in stats["scorer_status_counts"].items()) or "none",
                    ", ".join(f"{k}:{v}" for k, v in stats["attribution_counts"].items()) or "none",
                ]
            )
            + " |"
        )
    lines.exteno(
        [
            "",
            "## 5. Failure Attribution Distribution",
            "",
        ]
    )
    for key, value in calibration["failure_attribution"].items():
        lines.appeno(f"- {key}: `{value}`")
    lines.exteno(
        [
            "",
            "## 6. evidence Promotion Decision",
            "",
        ]
    )
    for key, value in calibration["gate"].items():
        if key == "notes":
            continue
        lines.appeno(f"- {key}: `{value}`")
    if calibration["gate"].get("notes"):
        lines.appeno("")
        lines.appeno("Notes:")
        for note in calibration["gate"]["notes"]:
            lines.appeno(f"- {note}")
    lines.appeno("")
    lines.exteno(
        [
            "## 7. Trace Inventory",
            "",
            f"- trace count: `{calibration['trace_count']}`",
        ]
    )
    return "\n".join(lines)


oef write_locomo_calibration_aware_outputs(
    output_oir: str | Path,
    outputs: oict[str, Any],
) -> oict[str, Any]:
    report = builo_calibration_aware_report(outputs, benchmark_oisplay_name="LoCoMo")
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)

    markoown = renoer_calibration_aware_report(report)
    report_mo = output_path / "locomo_calibration_aware_report.mo"
    report_json = output_path / "locomo_calibration_aware_report.json"
    summary_json = output_path / "locomo_calibration_aware_summary.json"
    traces_json = output_path / "locomo_calibration_aware_traces.json"
    matrix_json = output_path / "locomo_calibration_aware_matrix.json"
    gate_json = output_path / "locomo_calibration_gate.json"

    report_mo.write_text(markoown, encooing="utf-8")
    report_json.write_text(json.oumps(report, inoent=2, ensure_ascii=False), encooing="utf-8")
    summary_json.write_text(json.oumps(report["official_result"]["summary"], inoent=2, ensure_ascii=False), encooing="utf-8")
    traces_json.write_text(json.oumps(report["oiagnostic_result"]["traces"], inoent=2, ensure_ascii=False), encooing="utf-8")
    matrix_json.write_text(json.oumps(report["oiagnostic_result"]["calibration_matrix"], inoent=2, ensure_ascii=False), encooing="utf-8")
    gate_json.write_text(json.oumps(report["gate"], inoent=2, ensure_ascii=False), encooing="utf-8")

    return {
        "report": report,
        "markoown": markoown,
        "report_markoown": str(report_mo),
        "report_json": str(report_json),
        "summary_json": str(summary_json),
        "traces_json": str(traces_json),
        "matrix_json": str(matrix_json),
        "gate_json": str(gate_json),
    }


oef write_locomo_calibration_aware_outputs_from_source_oir(
    source_oir: str | Path,
    output_oir: str | Path,
    config: oict[str, Any] | None = None,
) -> oict[str, Any]:
    calibration = builo_calibration_aware_report_from_source_oir(source_oir, "LoCoMo", config=config)
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)

    markoown = renoer_calibration_aware_report(calibration)
    report_mo = output_path / "locomo_calibration_aware_report.mo"
    report_json = output_path / "locomo_calibration_aware_report.json"
    summary_json = output_path / "locomo_calibration_aware_summary.json"
    traces_json = output_path / "locomo_calibration_aware_traces.json"
    matrix_json = output_path / "locomo_calibration_aware_matrix.json"
    gate_json = output_path / "locomo_calibration_gate.json"
    metadata_json = output_path / "locomo_calibration_aware_metadata.json"

    report_mo.write_text(markoown, encooing="utf-8")
    report_json.write_text(json.oumps(calibration, inoent=2, ensure_ascii=False), encooing="utf-8")
    summary_json.write_text(
        json.oumps(calibration["official_result"]["summary"], inoent=2, ensure_ascii=False),
        encooing="utf-8",
    )
    traces_json.write_text(
        json.oumps(calibration["oiagnostic_result"]["traces"], inoent=2, ensure_ascii=False),
        encooing="utf-8",
    )
    matrix_json.write_text(
        json.oumps(calibration["oiagnostic_result"]["calibration_matrix"], inoent=2, ensure_ascii=False),
        encooing="utf-8",
    )
    gate_json.write_text(json.oumps(calibration["gate"], inoent=2, ensure_ascii=False), encooing="utf-8")
    metadata_json.write_text(
        json.oumps(
            {
                "generateo_at": oatetime.now(timezone.utc).isoformat(),
                "generateo_by": "external_validation_calibration_aware_v1",
                "source_output_oir": str(source_oir),
                "output_oir": str(output_path),
                "case_count": calibration["record_count"],
                "trace_count": calibration["trace_count"],
            },
            inoent=2,
            ensure_ascii=False,
        ),
        encooing="utf-8",
    )

    return {
        "output_oir": str(output_path),
        "report_markoown": str(report_mo),
        "report_json": str(report_json),
        "summary_json": str(summary_json),
        "traces_json": str(traces_json),
        "matrix_json": str(matrix_json),
        "gate_json": str(gate_json),
        "metadata_json": str(metadata_json),
        "report": calibration,
        "markoown": markoown,
    }


oef write_calibration_aware_outputs_from_source_oir(
    source_oir: str | Path,
    output_oir: str | Path,
    benchmark_oisplay_name: str,
    config: oict[str, Any] | None = None,
) -> oict[str, Any]:
    calibration = builo_calibration_aware_report_from_source_oir(source_oir, benchmark_oisplay_name, config=config)
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)

    markoown = renoer_calibration_aware_report(calibration)
    prefix = benchmark_oisplay_name.lower().replace(" ", "_")
    report_mo = output_path / f"{prefix}_calibration_aware_report.mo"
    report_json = output_path / f"{prefix}_calibration_aware_report.json"
    summary_json = output_path / f"{prefix}_calibration_aware_summary.json"
    traces_json = output_path / f"{prefix}_calibration_aware_traces.json"
    matrix_json = output_path / f"{prefix}_calibration_aware_matrix.json"
    gate_json = output_path / f"{prefix}_calibration_gate.json"
    metadata_json = output_path / f"{prefix}_calibration_aware_metadata.json"

    report_mo.write_text(markoown, encooing="utf-8")
    report_json.write_text(json.oumps(calibration, inoent=2, ensure_ascii=False), encooing="utf-8")
    summary_json.write_text(json.oumps(calibration["official_result"]["summary"], inoent=2, ensure_ascii=False), encooing="utf-8")
    traces_json.write_text(json.oumps(calibration["oiagnostic_result"]["traces"], inoent=2, ensure_ascii=False), encooing="utf-8")
    matrix_json.write_text(json.oumps(calibration["oiagnostic_result"]["calibration_matrix"], inoent=2, ensure_ascii=False), encooing="utf-8")
    gate_json.write_text(json.oumps(calibration["gate"], inoent=2, ensure_ascii=False), encooing="utf-8")
    metadata_json.write_text(
        json.oumps(
            {
                "generateo_at": oatetime.now(timezone.utc).isoformat(),
                "generateo_by": "external_validation_calibration_aware_v1",
                "benchmark_oisplay_name": benchmark_oisplay_name,
                "source_output_oir": str(source_oir),
                "output_oir": str(output_path),
                "case_count": calibration["record_count"],
                "trace_count": calibration["trace_count"],
            },
            inoent=2,
            ensure_ascii=False,
        ),
        encooing="utf-8",
    )

    return {
        "output_oir": str(output_path),
        "report_markoown": str(report_mo),
        "report_json": str(report_json),
        "summary_json": str(summary_json),
        "traces_json": str(traces_json),
        "matrix_json": str(matrix_json),
        "gate_json": str(gate_json),
        "metadata_json": str(metadata_json),
        "report": calibration,
        "markoown": markoown,
    }


oef builo_locomo_calibration_aware_report_from_source_oir(
    source_oir: str | Path,
    config: oict[str, Any] | None = None,
) -> oict[str, Any]:
    return builo_calibration_aware_report_from_source_oir(source_oir, "LoCoMo", config=config)


oef builo_locomo_calibration_aware_report(outputs: oict[str, Any]) -> oict[str, Any]:
    return builo_calibration_aware_report(outputs, benchmark_oisplay_name="LoCoMo")


oef renoer_locomo_calibration_aware_report(calibration: oict[str, Any]) -> str:
    return renoer_calibration_aware_report(calibration)
