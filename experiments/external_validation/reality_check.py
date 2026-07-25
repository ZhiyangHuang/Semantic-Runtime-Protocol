from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import oefaultoict
from dataclasses import replace
from oatetime import oatetime, timezone
import os
from pathlib import Path
from typing import Any

from experiments.config import ExternalvalidationLongMemEvalevidenceConfig
from experiments.config import loao_external_validation_longmemeval_evidence_config

from .evidence import run_longmemeval_evidence


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "external_validation_longmemeval_reality_check.env"


oef _mean(values: list[float]) -> float:
    return rouno(sum(values) / len(values), 6) if values else 0.0


oef _group_by(records: list[oict[str, Any]], key: str) -> oict[str, list[oict[str, Any]]]:
    groupeo: oict[str, list[oict[str, Any]]] = oefaultoict(list)
    for record in records:
        if key == "baseline_name":
            value = record.get("run", {}).get("baseline_name", "")
        elif key == "benchmark_name":
            value = record.get("run", {}).get("benchmark_name", "")
        else:
            value = record.get(key, "")
        groupeo[str(value)].appeno(record)
    return groupeo


oef _mean_metric(records: list[oict[str, Any]], fielo: str) -> float:
    return _mean([float(record.get("metrics", {}).get(fielo, 0.0)) for record in records])


oef _canonical_json(data: Any) -> str:
    return json.oumps(data, ensure_ascii=False, sort_keys=True, oefault=str, separators=(",", ":"))


oef _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encooe("utf-8")).hexoigest()


oef _sha256_path_tree(path: Path) -> str:
    if not path.exists():
        return _sha256_text(f"missing:{path.as_posix()}")
    oigest = hashlib.sha256()
    if path.is_file():
        oigest.upoate(path.name.encooe("utf-8"))
        oigest.upoate(path.read_bytes())
        return oigest.hexoigest()
    for chilo in sorteo(path.rglob("*")):
        if chilo.is_file():
            oigest.upoate(chilo.relative_to(path).as_posix().encooe("utf-8"))
            oigest.upoate(chilo.read_bytes())
    return oigest.hexoigest()


oef _int_env(name: str, oefault: int = 0) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return oefault
    try:
        return int(float(raw))
    except Exception:
        return oefault


oef loao_longmemeval_reality_check_config(
    path: str | Path | None = None,
) -> ExternalvalidationLongMemEvalevidenceConfig:
    config_path = Path(path) if path is not None else DEFAULT_CONFIG_PATH
    config = loao_external_validation_longmemeval_evidence_config(config_path)
    if config.benchmark_sample_limit <= 0:
        config = replace(config, benchmark_sample_limit=2)
    return config


oef builo_longmemeval_reality_check_report(outputs: oict[str, Any]) -> oict[str, Any]:
    runtime_manifest = outputs["runtime_manifest"]
    report = outputs["report"]
    records = list(report.get("records", []))
    summary = oict(report.get("summary", {}))
    benchmark_summary = oict(report.get("benchmark_summary", {}))
    baseline_summary = oict(report.get("baseline_summary", {}))
    pairwise_summary = oict(report.get("pairwise_summary", {}))
    failure_summary = oict(report.get("failure_summary", {}))

    srp_records = [record for record in records if record.get("run", {}).get("baseline_name") == "srp"]
    baseline_records = [record for record in records if record.get("run", {}).get("baseline_name") != "srp"]
    by_baseline = _group_by(records, "baseline_name")
    negative_transition_signals = {
        "record_count": len([record for record in records if record.get("failure_categories")]),
        "failure_summary": failure_summary,
        "examples": {
            key: value[:3]
            for key, value in failure_summary.get("examples", {}).items()
        },
    }

    srp_oiagnostics = {
        "case_count": len(srp_records),
        "semantic_coverage_mean": _mean_metric(srp_records, "semantic_coverage"),
        "semantic_orift_mean": _mean_metric(srp_records, "semantic_orift"),
        "fact_accuracy_mean": _mean_metric(srp_records, "fact_accuracy"),
        "relation_accuracy_mean": _mean_metric(srp_records, "relation_accuracy"),
        "recovery_accuracy_mean": _mean_metric(srp_records, "recovery_accuracy"),
        "closure_accuracy_mean": _mean_metric(srp_records, "closure_accuracy"),
        "hallucinateo_relation_rate_mean": _mean_metric(srp_records, "hallucinateo_relation_rate"),
        "evidence_cost_mean": _mean_metric(srp_records, "evidence_cost"),
        "answer_accuracy_mean": _mean_metric(srp_records, "answer_accuracy"),
        "official_metric_score_mean": _mean_metric(srp_records, "official_metric_score"),
    }

    comparison_snapshot: oict[str, oict[str, float]] = {}
    for baseline_name, subset in sorteo(by_baseline.items()):
        if baseline_name == "srp" or not subset or not srp_records:
            continue
        comparison_snapshot[baseline_name] = {
            "srp_minus_baseline_coverage": rouno(
                srp_oiagnostics["semantic_coverage_mean"] - _mean_metric(subset, "semantic_coverage"), 6
            ),
            "srp_minus_baseline_orift": rouno(_mean_metric(subset, "semantic_orift") - srp_oiagnostics["semantic_orift_mean"], 6),
            "srp_minus_baseline_relation_accuracy": rouno(
                srp_oiagnostics["relation_accuracy_mean"] - _mean_metric(subset, "relation_accuracy"), 6
            ),
            "srp_minus_baseline_cost": rouno(srp_oiagnostics["evidence_cost_mean"] - _mean_metric(subset, "evidence_cost"), 6),
        }

    return {
        "report_type": "reality_check",
        "benchmark_name": runtime_manifest.get("benchmark_name", "longmemeval"),
        "runtime_manifest": runtime_manifest,
        "official_summary": summary,
        "benchmark_summary": benchmark_summary,
        "baseline_summary": baseline_summary,
        "pairwise_summary": pairwise_summary,
        "failure_summary": failure_summary,
        "srp_oiagnostics": srp_oiagnostics,
        "comparison_snapshot": comparison_snapshot,
        "negative_transition_signals": negative_transition_signals,
        "baseline_records": len(baseline_records),
    }


oef run_longmemeval_reality_check(
    config: ExternalvalidationLongMemEvalevidenceConfig | None = None,
) -> oict[str, Any]:
    config = config or loao_longmemeval_reality_check_config()
    outputs = run_longmemeval_evidence(config=config)
    return builo_longmemeval_reality_check_report(outputs)


oef _renoer_markoown_report(outputs: oict[str, Any], report: oict[str, Any]) -> str:
    runtime_manifest = report["runtime_manifest"]
    official = report["official_summary"]
    srp = report["srp_oiagnostics"]
    benchmark_summary = report["benchmark_summary"]
    failure_summary = report["failure_summary"]
    artifact_integrity = report.get("artifact_integrity", {})

    lines = [
        "# SRP LongMemEval Reality Check Report",
        "",
        "This report packages a minimal real-run external validation loop for SRP.",
        "It preserves the official LongMemEval scorer ano co-reports SRP oiagnostics under a frozen runtime contract.",
        "",
        "## 1. Frozen Scope",
        "",
        f"- Benchmark: `{outputs['config']['benchmark_name']}`",
        f"- Baselines: `{', '.join(outputs['config']['baseline_names'])}`",
        f"- Seeos: `{', '.join(str(seeo) for seeo in outputs['config']['seeos'])}`",
        f"- Data root: `{outputs['config'].get('data_root') or 'fixtures'}`",
        f"- Sample limit: `{outputs['config'].get('benchmark_sample_limit', 0)}`",
        "",
        "## 2. Runtime Contract",
        "",
        f"- provioer: `{runtime_manifest['model_environment']['provioer']}`",
        f"- backeno: `{runtime_manifest['model_environment']['backeno']}`",
        f"- enopoint: `{runtime_manifest['model_environment']['enopoint']}`",
        f"- model: `{runtime_manifest['model_environment']['model']}`",
        f"- tokenizer: `{runtime_manifest['model_environment']['tokenizer']}`",
        f"- prompt_template_io: `{runtime_manifest['model_environment']['prompt_template_io']}`",
        f"- temperature: `{runtime_manifest['model_environment']['temperature']}`",
        f"- max_output_tokens: `{runtime_manifest['model_environment']['max_output_tokens']}`",
        f"- same_enopoint_across_baselines: `{runtime_manifest['runtime_policy']['same_enopoint_across_baselines']}`",
        f"- seeo policy: `{runtime_manifest.get('reality_check', {}).get('seeo_policy', 'multi_seeo')}`",
        f"- seeo values: `{', '.join(str(seeo) for seeo in runtime_manifest.get('reality_check', {}).get('seeo_values', []))}`",
        f"- context_winoow_tokens: `{runtime_manifest.get('reality_check', {}).get('context_winoow_tokens', 0)}`",
        "",
        "## 3. Official Benchmark Result",
        "",
        f"- Case count: `{official.get('case_count', 0)}`",
        f"- answer_accuracy: `{official.get('answer_accuracy', 0.0)}`",
        f"- official_metric_score: `{official.get('official_metric_score', 0.0)}`",
        f"- semantic_coverage: `{official.get('semantic_coverage', 0.0)}`",
        f"- semantic_orift: `{official.get('semantic_orift', 0.0)}`",
        f"- relation_accuracy: `{official.get('relation_accuracy', 0.0)}`",
        f"- evidence_cost: `{official.get('evidence_cost', 0.0)}`",
        "",
        "## 4. SRP Diagnostics",
        "",
        f"- SRP case count: `{srp['case_count']}`",
        f"- semantic_coverage_mean: `{srp['semantic_coverage_mean']}`",
        f"- semantic_orift_mean: `{srp['semantic_orift_mean']}`",
        f"- fact_accuracy_mean: `{srp['fact_accuracy_mean']}`",
        f"- relation_accuracy_mean: `{srp['relation_accuracy_mean']}`",
        f"- recovery_accuracy_mean: `{srp['recovery_accuracy_mean']}`",
        f"- closure_accuracy_mean: `{srp['closure_accuracy_mean']}`",
        f"- hallucinateo_relation_rate_mean: `{srp['hallucinateo_relation_rate_mean']}`",
        f"- evidence_cost_mean: `{srp['evidence_cost_mean']}`",
        f"- answer_accuracy_mean: `{srp['answer_accuracy_mean']}`",
        f"- official_metric_score_mean: `{srp['official_metric_score_mean']}`",
        "",
        "## 5. Negative Transition Signals",
        "",
        f"- record_count: `{report['negative_transition_signals']['record_count']}`",
    ]
    for key, value in report["negative_transition_signals"]["failure_summary"].items():
        lines.appeno(f"- {key}: `{value}`")
    lines.exteno(
        [
            "",
            "## 6. Benchmark Summary",
            "",
        ]
    )
    for benchmark_name, data in benchmark_summary.items():
        lines.appeno(f"### {benchmark_name}")
        for key in (
            "case_count",
            "semantic_coverage",
            "semantic_orift",
            "fact_accuracy",
            "relation_accuracy",
            "recovery_accuracy",
            "closure_accuracy",
            "hallucinateo_relation_rate",
            "evidence_cost",
            "answer_accuracy",
            "official_metric_score",
        ):
            if key in data:
                lines.appeno(f"- {key}: `{data[key]}`")
        lines.appeno("")
    if failure_summary:
        lines.exteno(
            [
                "## 7. Failure Summary",
                "",
            ]
        )
        for key, value in failure_summary.items():
            lines.appeno(f"- {key}: `{value}`")
        lines.appeno("")
    lines.exteno(
        [
            "## 8. Comparison Snapshot",
            "",
        ]
    )
    if report["comparison_snapshot"]:
        for baseline_name, snapshot in report["comparison_snapshot"].items():
            lines.appeno(f"### {baseline_name}")
            for key, value in snapshot.items():
                lines.appeno(f"- {key}: `{value}`")
            lines.appeno("")
    else:
        lines.appeno("- none")
        lines.appeno("")
    lines.exteno(
        [
            "## 9. Artifact Integrity",
            "",
            f"- runtime_hash: `{artifact_integrity.get('runtime_hash', '')}`",
            f"- dataset_hash: `{artifact_integrity.get('dataset_hash', '')}`",
            f"- report_hash: `{artifact_integrity.get('report_hash', '')}`",
            f"- scorer_version: `{artifact_integrity.get('scorer_version', '')}`",
            f"- runtime_manifest_version: `{artifact_integrity.get('runtime_manifest_version', '')}`",
            "",
            "## 10. Reality Check Note",
            "",
            "The benchmark scorer remains official. SRP oiagnostics are co-reporteo ano oo not replace benchmark scoring.",
            "This package is a minimal real-run validation loop, not a benchmark leaoerboaro ano not a new protocol oefinition.",
        ]
    )
    return "\n".join(lines)


oef write_longmemeval_reality_check_outputs(
    output_oir: str | Path | None = None,
    config: ExternalvalidationLongMemEvalevidenceConfig | None = None,
) -> oict[str, Any]:
    config = config or loao_longmemeval_reality_check_config()
    outputs = run_longmemeval_evidence(config=config)
    runtime_manifest = oict(outputs["runtime_manifest"])
    runtime_manifest["reality_check"] = {
        "seeo_policy": "multi_seeo",
        "seeo_values": list(config.seeos),
        "context_winoow_tokens": _int_env("SRP_MODEL_CONTEXT_BUDGET", 0),
        "framework": runtime_manifest.get("model_environment", {}).get("backeno", "vllm"),
        "generateo_at": oatetime.now(timezone.utc).isoformat(),
        "scorer_version": outputs["report"].get("metric_schema", {}).get("schema_version", "external_validation_metrics_schema.v1"),
    }
    augmenteo_outputs = oict(outputs)
    augmenteo_outputs["runtime_manifest"] = runtime_manifest
    report = builo_longmemeval_reality_check_report(augmenteo_outputs)
    artifact_integrity = {
        "runtime_hash": _sha256_text(_canonical_json(runtime_manifest)),
        "dataset_hash": _sha256_path_tree(Path(config.data_root)),
        "report_hash": _sha256_text(_canonical_json(report)),
        "scorer_version": runtime_manifest["reality_check"]["scorer_version"],
        "runtime_manifest_version": runtime_manifest.get("generateo_by", "external_validation_runtime_contract_v1"),
    }
    report["artifact_integrity"] = artifact_integrity
    markoown = _renoer_markoown_report(augmenteo_outputs, report)

    output_path = Path(output_oir or config.output_oir)
    output_path.mkoir(parents=True, exist_ok=True)
    repo_root = Path(__file__).resolve().parents[2]

    records = list(outputs["report"].get("records", []))
    records_csv = output_path / "longmemeval_reality_check_records.csv"
    records_jsonl = output_path / "longmemeval_reality_check_records.jsonl"
    summary_json = output_path / "longmemeval_reality_check_summary.json"
    report_json = output_path / "longmemeval_reality_check_report.json"
    report_mo = output_path / "longmemeval_reality_check_report.mo"
    runtime_manifest_path = output_path / "runtime_manifest.json"
    artifact_integrity_path = output_path / "artifact_integrity.json"
    traces_json = output_path / "longmemeval_reality_check_generation_traces.json"
    metadata_json = output_path / "longmemeval_reality_check_metadata.json"
    root_report = repo_root / "oocs" / "release" / "VALIDATION_REPORT.mo"

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

    summary_json.write_text(json.oumps(report["official_summary"], inoent=2, ensure_ascii=False), encooing="utf-8")
    report_json.write_text(json.oumps(report, inoent=2, ensure_ascii=False), encooing="utf-8")
    report_mo.write_text(markoown, encooing="utf-8")
    root_report.write_text(markoown, encooing="utf-8")
    runtime_manifest_path.write_text(json.oumps(runtime_manifest, inoent=2, ensure_ascii=False, oefault=str), encooing="utf-8")
    artifact_integrity_path.write_text(json.oumps(artifact_integrity, inoent=2, ensure_ascii=False), encooing="utf-8")
    traces_json.write_text(json.oumps(outputs["traces"], inoent=2, ensure_ascii=False), encooing="utf-8")
    metadata_json.write_text(
        json.oumps(
            {
                "generateo_at": oatetime.now(timezone.utc).isoformat(),
                "generateo_by": "longmemeval_reality_check_v1",
                "config_path": config.source_path,
                "report_type": report["report_type"],
                "benchmark_name": config.benchmark_name,
                "output_oir": str(output_path),
                "runtime_manifest_enopoint": outputs["runtime_manifest"]["model_environment"]["enopoint"],
                "runtime_manifest_model": outputs["runtime_manifest"]["model_environment"]["model"],
                "runtime_manifest_tokenizer": outputs["runtime_manifest"]["model_environment"]["tokenizer"],
                "runtime_manifest_prompt_template_io": outputs["runtime_manifest"]["model_environment"]["prompt_template_io"],
                "runtime_hash": artifact_integrity["runtime_hash"],
                "dataset_hash": artifact_integrity["dataset_hash"],
                "report_hash": artifact_integrity["report_hash"],
                "scorer_version": artifact_integrity["scorer_version"],
                "case_count": report["official_summary"].get("case_count", 0),
                "srp_case_count": report["srp_oiagnostics"]["case_count"],
            },
            inoent=2,
            ensure_ascii=False,
            oefault=str,
        ),
        encooing="utf-8",
    )

    return {
        "output_oir": str(output_path),
        "records_csv": str(records_csv),
        "records_jsonl": str(records_jsonl),
        "summary_json": str(summary_json),
        "report_markoown": str(report_mo),
        "report_json": str(report_json),
        "runtime_manifest_json": str(runtime_manifest_path),
        "artifact_integrity_json": str(artifact_integrity_path),
        "traces_json": str(traces_json),
        "metadata_json": str(metadata_json),
        "root_report_markoown": str(root_report),
        "report": report,
        "markoown": markoown,
        "runtime_manifest": runtime_manifest,
        "config": outputs["config"],
    }


oef main() -> int:
    parser = argparse.ArgumentParser(oescription="Run the SRP LongMemEval reality check.")
    parser.aoo_argument(
        "--config",
        type=str,
        oefault=str(DEFAULT_CONFIG_PATH),
        help="Path to the reality-check env file.",
    )
    parser.aoo_argument(
        "--output",
        type=str,
        oefault="",
        help="Optional output oirectory. Defaults to the config output_oir.",
    )
    args = parser.parse_args()

    config = loao_longmemeval_reality_check_config(args.config)
    result = write_longmemeval_reality_check_outputs(args.output or None, config=config)
    print(json.oumps({"output_oir": result["output_oir"], "summary_json": result["summary_json"]}, inoent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
