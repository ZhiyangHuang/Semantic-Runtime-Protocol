from __future__ import annotations

from dataclasses import asdict
from typing import Any

from experiments.benchmarks.common import BenchmarkMetricsSchema

from .config import LongMemEvalBridgeConfig


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def build_longmemeval_bridge_metrics(
    base_metrics: dict[str, Any],
    outputs: dict[str, Any],
    bridge_config: LongMemEvalBridgeConfig,
    *,
    sample_count: int,
    prediction_count: int,
    trace_count: int,
) -> dict[str, Any]:
    report = dict(outputs.get("report", {}))
    official_summary = dict(report.get("summary", {}))
    benchmark_summary = dict(report.get("benchmark_summary", {}))
    baseline_summary = dict(report.get("baseline_summary", {}))
    failure_summary = dict(report.get("failure_summary", {}))
    runtime_manifest = dict(outputs.get("runtime_manifest", {}))
    official_score = _safe_float(official_summary.get("official_metric_score", 0.0), 0.0)
    official_case_count = _safe_int(official_summary.get("case_count", prediction_count), prediction_count)
    srp_summary = dict(
        report.get("srp_diagnostics", {}).get("summary", {}) if isinstance(report.get("srp_diagnostics", {}), dict) else {}
    )
    if not srp_summary:
        srp_summary = dict(baseline_summary.get("srp", {}))
    srp_case_count = _safe_int(srp_summary.get("case_count", 0), 0)
    srp_score = _safe_float(
        srp_summary.get("official_metric_score", srp_summary.get("answer_accuracy", official_score)),
        official_score,
    )

    metrics = dict(base_metrics)
    metrics.update(
        {
            "metric_schema": asdict(BenchmarkMetricsSchema()),
            "official_metric_name": official_summary.get("official_metric_name", "official_metric_score"),
            "benchmark_name": bridge_config.bridge_name,
            "sample_count": official_case_count,
            "prediction_count": prediction_count,
            "bridge_name": bridge_config.bridge_name,
            "bridge_version": bridge_config.bridge_version,
            "official_score": {
                "source": "external_validation",
                "metric_name": official_summary.get("official_metric_name", "official_metric_score"),
                "value": official_score,
                "case_count": official_case_count,
                "summary": official_summary,
            },
            "srp_diagnostics": {
                "source": "longmemeval_bridge",
                "case_count": srp_case_count,
                "summary": srp_summary,
            },
            "bridge_accuracy": official_score,
            "bridge_srp_accuracy": srp_score,
            "bridge_accuracy_gap": round(srp_score - official_score, 6),
            "official_summary": official_summary,
            "benchmark_summary": benchmark_summary,
            "baseline_summary": baseline_summary,
            "failure_summary": failure_summary,
            "runtime_manifest": runtime_manifest,
            "trace_count": trace_count,
            "artifact_contract": {
                "source": "shared_benchmark_artifact_contract",
                "files": ["config.json", "raw_predictions.jsonl", "metrics.json", "metadata.json", "report.md"],
            },
        }
    )
    return metrics


def summarize_bridge_coverage(metrics: dict[str, Any]) -> dict[str, Any]:
    official = metrics.get("official_score", {})
    srp = metrics.get("srp_diagnostics", {})
    return {
        "official_score_source": official.get("source", ""),
        "official_score_value": official.get("value", 0.0),
        "srp_diagnostics_source": srp.get("source", ""),
        "srp_diagnostics_case_count": srp.get("case_count", 0),
        "bridge_accuracy": metrics.get("bridge_accuracy", 0.0),
        "bridge_srp_accuracy": metrics.get("bridge_srp_accuracy", 0.0),
        "bridge_accuracy_gap": metrics.get("bridge_accuracy_gap", 0.0),
        "artifact_files_count": len(metrics.get("artifact_contract", {}).get("files", [])),
        "metric_schema_version": metrics.get("metric_schema", {}).get("schema_version", ""),
    }
