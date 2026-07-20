from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from dataclasses import replace
from datetime import datetime, timezone
import os
from pathlib import Path
from typing import Any

from experiments.config import ExternalValidationLongMemEvalEvidenceConfig
from experiments.config import load_external_validation_longmemeval_evidence_config

from .evidence import run_longmemeval_evidence


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "external_validation_longmemeval_reality_check.env"


def _mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 6) if values else 0.0


def _group_by(records: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        if key == "baseline_name":
            value = record.get("run", {}).get("baseline_name", "")
        elif key == "benchmark_name":
            value = record.get("run", {}).get("benchmark_name", "")
        else:
            value = record.get(key, "")
        grouped[str(value)].append(record)
    return grouped


def _mean_metric(records: list[dict[str, Any]], field: str) -> float:
    return _mean([float(record.get("metrics", {}).get(field, 0.0)) for record in records])


def _canonical_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, default=str, separators=(",", ":"))


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_path_tree(path: Path) -> str:
    if not path.exists():
        return _sha256_text(f"missing:{path.as_posix()}")
    digest = hashlib.sha256()
    if path.is_file():
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
        return digest.hexdigest()
    for child in sorted(path.rglob("*")):
        if child.is_file():
            digest.update(child.relative_to(path).as_posix().encode("utf-8"))
            digest.update(child.read_bytes())
    return digest.hexdigest()


def _int_env(name: str, default: int = 0) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(float(raw))
    except Exception:
        return default


def load_longmemeval_reality_check_config(
    path: str | Path | None = None,
) -> ExternalValidationLongMemEvalEvidenceConfig:
    config_path = Path(path) if path is not None else DEFAULT_CONFIG_PATH
    config = load_external_validation_longmemeval_evidence_config(config_path)
    if config.benchmark_sample_limit <= 0:
        config = replace(config, benchmark_sample_limit=2)
    return config


def build_longmemeval_reality_check_report(outputs: dict[str, Any]) -> dict[str, Any]:
    runtime_manifest = outputs["runtime_manifest"]
    report = outputs["report"]
    records = list(report.get("records", []))
    summary = dict(report.get("summary", {}))
    benchmark_summary = dict(report.get("benchmark_summary", {}))
    baseline_summary = dict(report.get("baseline_summary", {}))
    pairwise_summary = dict(report.get("pairwise_summary", {}))
    failure_summary = dict(report.get("failure_summary", {}))

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

    srp_diagnostics = {
        "case_count": len(srp_records),
        "semantic_coverage_mean": _mean_metric(srp_records, "semantic_coverage"),
        "semantic_drift_mean": _mean_metric(srp_records, "semantic_drift"),
        "fact_accuracy_mean": _mean_metric(srp_records, "fact_accuracy"),
        "relation_accuracy_mean": _mean_metric(srp_records, "relation_accuracy"),
        "recovery_accuracy_mean": _mean_metric(srp_records, "recovery_accuracy"),
        "closure_accuracy_mean": _mean_metric(srp_records, "closure_accuracy"),
        "hallucinated_relation_rate_mean": _mean_metric(srp_records, "hallucinated_relation_rate"),
        "evidence_cost_mean": _mean_metric(srp_records, "evidence_cost"),
        "answer_accuracy_mean": _mean_metric(srp_records, "answer_accuracy"),
        "official_metric_score_mean": _mean_metric(srp_records, "official_metric_score"),
    }

    comparison_snapshot: dict[str, dict[str, float]] = {}
    for baseline_name, subset in sorted(by_baseline.items()):
        if baseline_name == "srp" or not subset or not srp_records:
            continue
        comparison_snapshot[baseline_name] = {
            "srp_minus_baseline_coverage": round(
                srp_diagnostics["semantic_coverage_mean"] - _mean_metric(subset, "semantic_coverage"), 6
            ),
            "srp_minus_baseline_drift": round(_mean_metric(subset, "semantic_drift") - srp_diagnostics["semantic_drift_mean"], 6),
            "srp_minus_baseline_relation_accuracy": round(
                srp_diagnostics["relation_accuracy_mean"] - _mean_metric(subset, "relation_accuracy"), 6
            ),
            "srp_minus_baseline_cost": round(srp_diagnostics["evidence_cost_mean"] - _mean_metric(subset, "evidence_cost"), 6),
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
        "srp_diagnostics": srp_diagnostics,
        "comparison_snapshot": comparison_snapshot,
        "negative_transition_signals": negative_transition_signals,
        "baseline_records": len(baseline_records),
    }


def run_longmemeval_reality_check(
    config: ExternalValidationLongMemEvalEvidenceConfig | None = None,
) -> dict[str, Any]:
    config = config or load_longmemeval_reality_check_config()
    outputs = run_longmemeval_evidence(config=config)
    return build_longmemeval_reality_check_report(outputs)


def _render_markdown_report(outputs: dict[str, Any], report: dict[str, Any]) -> str:
    runtime_manifest = report["runtime_manifest"]
    official = report["official_summary"]
    srp = report["srp_diagnostics"]
    benchmark_summary = report["benchmark_summary"]
    failure_summary = report["failure_summary"]
    artifact_integrity = report.get("artifact_integrity", {})

    lines = [
        "# SRP LongMemEval Reality Check Report",
        "",
        "This report packages a minimal real-run external validation loop for SRP.",
        "It preserves the official LongMemEval scorer and co-reports SRP diagnostics under a frozen runtime contract.",
        "",
        "## 1. Frozen Scope",
        "",
        f"- Benchmark: `{outputs['config']['benchmark_name']}`",
        f"- Baselines: `{', '.join(outputs['config']['baseline_names'])}`",
        f"- Seeds: `{', '.join(str(seed) for seed in outputs['config']['seeds'])}`",
        f"- Data root: `{outputs['config'].get('data_root') or 'fixtures'}`",
        f"- Sample limit: `{outputs['config'].get('benchmark_sample_limit', 0)}`",
        "",
        "## 2. Runtime Contract",
        "",
        f"- provider: `{runtime_manifest['model_environment']['provider']}`",
        f"- backend: `{runtime_manifest['model_environment']['backend']}`",
        f"- endpoint: `{runtime_manifest['model_environment']['endpoint']}`",
        f"- model: `{runtime_manifest['model_environment']['model']}`",
        f"- tokenizer: `{runtime_manifest['model_environment']['tokenizer']}`",
        f"- prompt_template_id: `{runtime_manifest['model_environment']['prompt_template_id']}`",
        f"- temperature: `{runtime_manifest['model_environment']['temperature']}`",
        f"- max_output_tokens: `{runtime_manifest['model_environment']['max_output_tokens']}`",
        f"- same_endpoint_across_baselines: `{runtime_manifest['runtime_policy']['same_endpoint_across_baselines']}`",
        f"- seed policy: `{runtime_manifest.get('reality_check', {}).get('seed_policy', 'multi_seed')}`",
        f"- seed values: `{', '.join(str(seed) for seed in runtime_manifest.get('reality_check', {}).get('seed_values', []))}`",
        f"- context_window_tokens: `{runtime_manifest.get('reality_check', {}).get('context_window_tokens', 0)}`",
        "",
        "## 3. Official Benchmark Result",
        "",
        f"- Case count: `{official.get('case_count', 0)}`",
        f"- answer_accuracy: `{official.get('answer_accuracy', 0.0)}`",
        f"- official_metric_score: `{official.get('official_metric_score', 0.0)}`",
        f"- semantic_coverage: `{official.get('semantic_coverage', 0.0)}`",
        f"- semantic_drift: `{official.get('semantic_drift', 0.0)}`",
        f"- relation_accuracy: `{official.get('relation_accuracy', 0.0)}`",
        f"- evidence_cost: `{official.get('evidence_cost', 0.0)}`",
        "",
        "## 4. SRP Diagnostics",
        "",
        f"- SRP case count: `{srp['case_count']}`",
        f"- semantic_coverage_mean: `{srp['semantic_coverage_mean']}`",
        f"- semantic_drift_mean: `{srp['semantic_drift_mean']}`",
        f"- fact_accuracy_mean: `{srp['fact_accuracy_mean']}`",
        f"- relation_accuracy_mean: `{srp['relation_accuracy_mean']}`",
        f"- recovery_accuracy_mean: `{srp['recovery_accuracy_mean']}`",
        f"- closure_accuracy_mean: `{srp['closure_accuracy_mean']}`",
        f"- hallucinated_relation_rate_mean: `{srp['hallucinated_relation_rate_mean']}`",
        f"- evidence_cost_mean: `{srp['evidence_cost_mean']}`",
        f"- answer_accuracy_mean: `{srp['answer_accuracy_mean']}`",
        f"- official_metric_score_mean: `{srp['official_metric_score_mean']}`",
        "",
        "## 5. Negative Transition Signals",
        "",
        f"- record_count: `{report['negative_transition_signals']['record_count']}`",
    ]
    for key, value in report["negative_transition_signals"]["failure_summary"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## 6. Benchmark Summary",
            "",
        ]
    )
    for benchmark_name, data in benchmark_summary.items():
        lines.append(f"### {benchmark_name}")
        for key in (
            "case_count",
            "semantic_coverage",
            "semantic_drift",
            "fact_accuracy",
            "relation_accuracy",
            "recovery_accuracy",
            "closure_accuracy",
            "hallucinated_relation_rate",
            "evidence_cost",
            "answer_accuracy",
            "official_metric_score",
        ):
            if key in data:
                lines.append(f"- {key}: `{data[key]}`")
        lines.append("")
    if failure_summary:
        lines.extend(
            [
                "## 7. Failure Summary",
                "",
            ]
        )
        for key, value in failure_summary.items():
            lines.append(f"- {key}: `{value}`")
        lines.append("")
    lines.extend(
        [
            "## 8. Comparison Snapshot",
            "",
        ]
    )
    if report["comparison_snapshot"]:
        for baseline_name, snapshot in report["comparison_snapshot"].items():
            lines.append(f"### {baseline_name}")
            for key, value in snapshot.items():
                lines.append(f"- {key}: `{value}`")
            lines.append("")
    else:
        lines.append("- none")
        lines.append("")
    lines.extend(
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
            "The benchmark scorer remains official. SRP diagnostics are co-reported and do not replace benchmark scoring.",
            "This package is a minimal real-run validation loop, not a benchmark leaderboard and not a new protocol definition.",
        ]
    )
    return "\n".join(lines)


def write_longmemeval_reality_check_outputs(
    output_dir: str | Path | None = None,
    config: ExternalValidationLongMemEvalEvidenceConfig | None = None,
) -> dict[str, Any]:
    config = config or load_longmemeval_reality_check_config()
    outputs = run_longmemeval_evidence(config=config)
    runtime_manifest = dict(outputs["runtime_manifest"])
    runtime_manifest["reality_check"] = {
        "seed_policy": "multi_seed",
        "seed_values": list(config.seeds),
        "context_window_tokens": _int_env("SRP_MODEL_CONTEXT_BUDGET", 0),
        "framework": runtime_manifest.get("model_environment", {}).get("backend", "vllm"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scorer_version": outputs["report"].get("metric_schema", {}).get("schema_version", "external_validation_metrics_schema.v1"),
    }
    augmented_outputs = dict(outputs)
    augmented_outputs["runtime_manifest"] = runtime_manifest
    report = build_longmemeval_reality_check_report(augmented_outputs)
    artifact_integrity = {
        "runtime_hash": _sha256_text(_canonical_json(runtime_manifest)),
        "dataset_hash": _sha256_path_tree(Path(config.data_root)),
        "report_hash": _sha256_text(_canonical_json(report)),
        "scorer_version": runtime_manifest["reality_check"]["scorer_version"],
        "runtime_manifest_version": runtime_manifest.get("generated_by", "external_validation_runtime_contract_v1"),
    }
    report["artifact_integrity"] = artifact_integrity
    markdown = _render_markdown_report(augmented_outputs, report)

    output_path = Path(output_dir or config.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    repo_root = Path(__file__).resolve().parents[2]

    records = list(outputs["report"].get("records", []))
    records_csv = output_path / "longmemeval_reality_check_records.csv"
    records_jsonl = output_path / "longmemeval_reality_check_records.jsonl"
    summary_json = output_path / "longmemeval_reality_check_summary.json"
    report_json = output_path / "longmemeval_reality_check_report.json"
    report_md = output_path / "longmemeval_reality_check_report.md"
    runtime_manifest_path = output_path / "runtime_manifest.json"
    artifact_integrity_path = output_path / "artifact_integrity.json"
    traces_json = output_path / "longmemeval_reality_check_generation_traces.json"
    metadata_json = output_path / "longmemeval_reality_check_metadata.json"
    root_report = repo_root / "audit" / "REAL_VALIDATION_REPORT.md"

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

    summary_json.write_text(json.dumps(report["official_summary"], indent=2, ensure_ascii=False), encoding="utf-8")
    report_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    report_md.write_text(markdown, encoding="utf-8")
    root_report.write_text(markdown, encoding="utf-8")
    runtime_manifest_path.write_text(json.dumps(runtime_manifest, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    artifact_integrity_path.write_text(json.dumps(artifact_integrity, indent=2, ensure_ascii=False), encoding="utf-8")
    traces_json.write_text(json.dumps(outputs["traces"], indent=2, ensure_ascii=False), encoding="utf-8")
    metadata_json.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "generated_by": "longmemeval_reality_check_v1",
                "config_path": config.source_path,
                "report_type": report["report_type"],
                "benchmark_name": config.benchmark_name,
                "output_dir": str(output_path),
                "runtime_manifest_endpoint": outputs["runtime_manifest"]["model_environment"]["endpoint"],
                "runtime_manifest_model": outputs["runtime_manifest"]["model_environment"]["model"],
                "runtime_manifest_tokenizer": outputs["runtime_manifest"]["model_environment"]["tokenizer"],
                "runtime_manifest_prompt_template_id": outputs["runtime_manifest"]["model_environment"]["prompt_template_id"],
                "runtime_hash": artifact_integrity["runtime_hash"],
                "dataset_hash": artifact_integrity["dataset_hash"],
                "report_hash": artifact_integrity["report_hash"],
                "scorer_version": artifact_integrity["scorer_version"],
                "case_count": report["official_summary"].get("case_count", 0),
                "srp_case_count": report["srp_diagnostics"]["case_count"],
            },
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )

    return {
        "output_dir": str(output_path),
        "records_csv": str(records_csv),
        "records_jsonl": str(records_jsonl),
        "summary_json": str(summary_json),
        "report_markdown": str(report_md),
        "report_json": str(report_json),
        "runtime_manifest_json": str(runtime_manifest_path),
        "artifact_integrity_json": str(artifact_integrity_path),
        "traces_json": str(traces_json),
        "metadata_json": str(metadata_json),
        "root_report_markdown": str(root_report),
        "report": report,
        "markdown": markdown,
        "runtime_manifest": runtime_manifest,
        "config": outputs["config"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the SRP LongMemEval reality check.")
    parser.add_argument(
        "--config",
        type=str,
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to the reality-check env file.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="",
        help="Optional output directory. Defaults to the config output_dir.",
    )
    args = parser.parse_args()

    config = load_longmemeval_reality_check_config(args.config)
    result = write_longmemeval_reality_check_outputs(args.output or None, config=config)
    print(json.dumps({"output_dir": result["output_dir"], "summary_json": result["summary_json"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
