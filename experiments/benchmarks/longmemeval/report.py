from __future__ import annotations

from typing import Any

from .config import LongMemEvalBridgeConfig


def _render_key_value_block(title: str, payload: dict[str, Any], keys: tuple[str, ...] | None = None) -> list[str]:
    lines = [f"## {title}", ""]
    if not payload:
        lines.append("- none")
        lines.append("")
        return lines
    items = keys or tuple(sorted(payload.keys()))
    for key in items:
        if key in payload:
            value = payload[key]
            lines.append(f"- {key}: `{value}`")
    lines.append("")
    return lines


def render_longmemeval_bridge_report(
    bundle,
    outputs: dict[str, Any],
    bridge_config: LongMemEvalBridgeConfig,
    metrics: dict[str, Any],
) -> str:
    runtime_manifest = outputs.get("runtime_manifest", {})
    report = outputs.get("report", {})
    official_summary = dict(report.get("summary", {}))
    srp = dict(metrics.get("srp_diagnostics", {}))
    failure_summary = dict(report.get("failure_summary", {}))
    benchmark_summary = dict(report.get("benchmark_summary", {}))
    baseline_summary = dict(report.get("baseline_summary", {}))
    official_score = dict(metrics.get("official_score", {}))
    artifact_contract = dict(metrics.get("artifact_contract", {}))
    metadata = dict(bundle.metadata)

    lines = [
        "# LongMemEval Bridge Report",
        "",
        "This report packages the official LongMemEval external-validation evidence under the shared benchmark artifact surface.",
        "The official scorer remains owned by `experiments/external_validation/`; the bridge only packages and maps the outputs.",
        "",
        "## Evaluation Authority",
        "",
        f"- official scorer owner: `{official_score.get('source', 'external_validation')}`",
        f"- srp diagnostics owner: `{srp.get('source', 'longmemeval_bridge')}`",
        f"- runtime contract owner: `{metadata.get('runtime_contract_owner', 'external_validation')}`",
        f"- payload policy: `{metadata.get('payload_policy', 'not_stored_in_repository')}`",
        "",
        "## Bridge Summary",
        "",
        f"- bridge_name: `{bridge_config.bridge_name}`",
        f"- bridge_version: `{bridge_config.bridge_version}`",
        f"- bridge_output_dir: `{bridge_config.bridge_output_dir}`",
        f"- benchmark_name: `{bundle.config.benchmark_name}`",
        f"- dataset_version: `{bundle.config.dataset_version}`",
        f"- sample_count: `{metrics.get('sample_count', len(bundle.cases))}`",
        f"- prediction_count: `{metrics.get('prediction_count', len(bundle.predictions))}`",
        f"- official_metric_name: `{metrics.get('official_metric_name', 'official_metric_score')}`",
        "",
        "## Official Result",
        "",
    ]
    lines.extend(
        _render_key_value_block(
            "Official Benchmark Summary",
            official_summary,
            (
                "case_count",
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
            ),
        )
    )
    lines.extend(
        [
            "## SRP Diagnostics",
            "",
        ]
    )
    srp_summary = dict(srp.get("summary", {}))
    lines.extend(
        _render_key_value_block(
            "SRP Diagnostic Summary",
            srp_summary,
            (
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
            ),
        )
    )
    lines.extend(
        [
            "## Bridge Metrics",
            "",
        ]
    )
    lines.extend(
        _render_key_value_block(
            "Shared Metric Mapping",
            {
                "bridge_accuracy": metrics.get("bridge_accuracy", 0.0),
                "bridge_srp_accuracy": metrics.get("bridge_srp_accuracy", 0.0),
                "bridge_accuracy_gap": metrics.get("bridge_accuracy_gap", 0.0),
                "official_score_source": official_score.get("source", ""),
                "official_score_value": official_score.get("value", 0.0),
                "srp_diagnostics_source": srp.get("source", ""),
                "srp_diagnostics_case_count": srp.get("case_count", 0),
                "artifact_files_count": len(artifact_contract.get("files", [])),
                "metric_schema_version": metrics.get("metric_schema", {}).get("schema_version", ""),
            },
        )
    )
    lines.extend(
        [
            "## Failure Summary",
            "",
        ]
    )
    if failure_summary:
        for key, value in failure_summary.items():
            lines.append(f"- {key}: `{value}`")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Benchmark Summary",
            "",
        ]
    )
    if benchmark_summary:
        for benchmark_name, data in benchmark_summary.items():
            lines.append(f"### {benchmark_name}")
            for key, value in data.items():
                lines.append(f"- {key}: `{value}`")
            lines.append("")
    else:
        lines.append("- none")
        lines.append("")
    lines.extend(
        [
            "## Baseline Summary",
            "",
        ]
    )
    if baseline_summary:
        for baseline_name, data in baseline_summary.items():
            lines.append(f"### {baseline_name}")
            for key, value in data.items():
                lines.append(f"- {key}: `{value}`")
            lines.append("")
    else:
        lines.append("- none")
        lines.append("")
    lines.extend(
        [
            "## Runtime Manifest",
            "",
        ]
    )
    model_environment = runtime_manifest.get("model_environment", {}) if isinstance(runtime_manifest, dict) else {}
    runtime_policy = runtime_manifest.get("runtime_policy", {}) if isinstance(runtime_manifest, dict) else {}
    for key in (
        "provider",
        "backend",
        "endpoint",
        "model",
        "tokenizer",
        "prompt_template_id",
        "temperature",
        "max_output_tokens",
    ):
        if key in model_environment:
            lines.append(f"- {key}: `{model_environment[key]}`")
    for key, value in runtime_policy.items():
        lines.append(f"- runtime_policy.{key}: `{value}`")
    lines.extend(
        [
            "",
            "## Provenance",
            "",
        ]
    )
    for key in (
        "bridge_name",
        "bridge_version",
        "bridge_config_path",
        "bridge_output_dir",
        "official_scorer_owner",
        "runtime_contract_owner",
        "trace_count",
    ):
        if key in metadata:
            lines.append(f"- {key}: `{metadata[key]}`")
    lines.extend(
        [
            "",
            "## Artifact Contract",
            "",
        ]
    )
    for key, value in artifact_contract.items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## External Validation Evidence",
            "",
            "The official LongMemEval evidence remains owned by `experiments/external_validation/` and is not reinterpreted here.",
            "This bridge report preserves the official result, SRP diagnostics, and provenance without replacing scorer authority.",
            "",
            "The shared writer captures artifact hashes in metadata.json after serialization.",
        ]
    )
    return "\n".join(lines).strip() + "\n"
