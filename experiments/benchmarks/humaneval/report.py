from __future__ import annotations

from typing import Any

from experiments.benchmarks.common import BenchmarkRunBundle


def _render_key_values(title: str, payload: dict[str, Any], keys: tuple[str, ...] | None = None) -> list[str]:
    lines = [f"## {title}", ""]
    if not payload:
        lines.append("- none")
        lines.append("")
        return lines
    items = keys or tuple(sorted(payload.keys()))
    for key in items:
        if key in payload:
            lines.append(f"- {key}: `{payload[key]}`")
    lines.append("")
    return lines


def render_humaneval_report(bundle: BenchmarkRunBundle, execution_results: list[dict[str, Any]]) -> str:
    metrics = dict(bundle.metrics)
    metadata = dict(bundle.metadata)
    failure_categories = dict(metrics.get("failure_categories", {}))
    lines = [
        "# HumanEval Benchmark Report",
        "",
        "This report is generated from the HumanEval execution bridge.",
        "",
        "## Evaluation Authority",
        "",
        "- benchmark authority: `experiments/benchmarks/humaneval`",
        "- execution authority: `subprocess_isolation_v1`",
        f"- runtime sandbox policy: `{metadata.get('execution_sandbox_policy', 'subprocess_isolation_v1')}`",
        f"- allow_network: `{metadata.get('allow_network', False)}`",
        "",
        "## Experiment Setup",
        "",
    ]
    lines.extend(_render_key_values("Configuration", bundle.config.as_dict()))
    lines.extend(_render_key_values("Metrics Summary", metrics))
    lines.extend(
        [
            "## Execution Summary",
            "",
            f"- execution_result_count: `{len(execution_results)}`",
            f"- pass@1: `{metrics.get('pass@1', 0.0)}`",
            f"- baseline_pass@1: `{metrics.get('baseline_pass@1', 0.0)}`",
            f"- srp_pass@1: `{metrics.get('srp_pass@1', 0.0)}`",
            f"- pass@1_gap: `{metrics.get('pass@1_gap', 0.0)}`",
            "",
        ]
    )
    lines.extend(
        [
            "## Failure Summary",
            "",
        ]
    )
    if failure_categories:
        for key, value in sorted(failure_categories.items()):
            lines.append(f"- {key}: `{value}`")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Reproducibility",
            "",
            f"- sample_count: `{len(bundle.cases)}`",
            f"- prediction_count: `{len(bundle.predictions)}`",
            f"- report_format: `shared-benchmark-report-v1`",
            f"- execution_results_format: `humaneval-execution-results-v1`",
            "",
            "## Artifact Contract",
            "",
            "- config.json",
            "- raw_predictions.jsonl",
            "- execution_results.json",
            "- metrics.json",
            "- metadata.json",
            "- report.md",
            "",
            "## Provenance",
            "",
        ]
    )
    for key in (
        "generated_at",
        "generated_by",
        "benchmark_name",
        "dataset_version",
        "model",
        "prompt_format",
        "runner_version",
        "executor_version",
    ):
        if key in metadata:
            lines.append(f"- {key}: `{metadata[key]}`")
    lines.extend(
        [
            "",
            "## Execution Results Preview",
            "",
            "| task_id | variant | passed | failure_category | execution_time_seconds |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for record in execution_results[:10]:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(record.get("task_id", "")).replace("|", "\\|"),
                    str(record.get("variant", "")).replace("|", "\\|"),
                    str(record.get("passed", "")).replace("|", "\\|"),
                    str(record.get("failure_category", "")).replace("|", "\\|"),
                    str(record.get("execution_time_seconds", "")).replace("|", "\\|"),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- reference solutions and hidden tests are not serialized into the prompt-visible artifact",
            "- execution payloads remain isolated from the shared artifact surface",
        ]
    )
    return "\n".join(lines).strip() + "\n"

