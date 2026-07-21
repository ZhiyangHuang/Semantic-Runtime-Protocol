from __future__ import annotations

from typing import Any

from .metrics import summarize_prediction_records
from .schema import BenchmarkRunBundle


def _render_mapping_section(title: str, payload: dict[str, Any]) -> list[str]:
    lines = [f"## {title}", ""]
    for key in sorted(payload.keys()):
        value = payload[key]
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    return lines


def render_benchmark_report(bundle: BenchmarkRunBundle) -> str:
    summary = summarize_prediction_records(bundle.predictions)
    lines = [
        f"# {bundle.config.benchmark_name} Benchmark Report",
        "",
        "This report is generated from the shared benchmark execution layer.",
        "",
    ]
    lines.extend(_render_mapping_section("Experiment Setup", bundle.config.as_dict()))
    lines.extend(_render_mapping_section("Summary", summary))
    lines.extend(_render_mapping_section("Benchmark Metrics", bundle.metrics))
    lines.extend(
        [
            "## Reproducibility",
            "",
            f"- sample_count: `{len(bundle.cases)}`",
            f"- prediction_count: `{len(bundle.predictions)}`",
            f"- report_format: `shared-benchmark-report-v1`",
            "",
        ]
    )
    if bundle.predictions:
        lines.extend(
            [
                "## Sample Predictions",
                "",
                "| case_id | variant | prediction | is_correct | error |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for prediction in bundle.predictions[:10]:
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(prediction.case_id),
                        str(prediction.variant),
                        str(prediction.prediction).replace("|", "\\|"),
                        str(prediction.is_correct),
                        str(prediction.error or ""),
                    ]
                )
                + " |"
            )
        lines.append("")
    return "\n".join(lines)

