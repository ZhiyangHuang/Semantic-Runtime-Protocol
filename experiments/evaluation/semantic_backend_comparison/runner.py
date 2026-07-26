from __future__ import annotations

import csv
import json
import subprocess
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

from experiments.config import SemanticBackendComparisonConfig, load_semantic_backend_comparison_config

from .backend import build_comparison_cases
from .evaluator import SemanticBackendComparator
from .local_model_backend import LocalModelEvidenceBackend
from .report import SemanticBackendComparisonMarkdownReport
from .vector_backend import VectorOnlyEvaluationBackend


def run_semantic_backend_comparison(
    config: SemanticBackendComparisonConfig | None = None,
) -> dict[str, Any]:
    config = config or load_semantic_backend_comparison_config()
    cases = build_comparison_cases()
    baseline_backend = VectorOnlyEvaluationBackend(threshold=config.vector_similarity_threshold)
    variant_backend = LocalModelEvidenceBackend(
        model_name=config.local_model_name,
        base_url=config.local_model_url,
        timeout_seconds=config.model_timeout_seconds,
        enabled=config.local_model_enabled,
        fallback_to_heuristic=config.fallback_to_heuristic,
    )
    comparator = SemanticBackendComparator(baseline_backend, variant_backend)
    report = comparator.compare(cases)
    markdown = SemanticBackendComparisonMarkdownReport(report=report, config=asdict(config)).render()
    return {
        "config": asdict(config),
        "report": report.as_dict(),
        "markdown": markdown,
        "cases": [case.as_dict() for case in cases],
    }


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(__file__).resolve().parents[3],
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def _render_summary_figure(summary: dict[str, Any], output_png: Path, output_pdf: Path) -> None:
    labels = [
        "vector_acc",
        "variant_acc",
        "agreement",
        "review_rate",
        "authority_violation_accept_rate",
    ]
    values = [
        float(summary.get("vector_accuracy", 0.0)),
        float(summary.get("variant_accuracy", 0.0)),
        float(summary.get("agreement_rate", 0.0)),
        float(summary.get("review_rate", 0.0)),
        float(summary.get("authority_violation_final_accept_rate", 0.0)),
    ]

    fig, ax = plt.subplots(figsize=(8.2, 4.8), dpi=160)
    bars = ax.bar(labels, values, color=["#4C78A8", "#F58518", "#54A24B", "#B279A2", "#E45756"], edgecolor="#2f2f2f")
    ax.set_title("SRP Semantic Backend Comparison Summary")
    ax.set_ylabel("rate")
    ax.set_ylim(0.0, 1.05)
    ax.tick_params(axis="x", rotation=18)

    for bar, value in zip(bars, values, strict=False):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02, f"{value:.2f}", ha="center", va="bottom")

    fig.tight_layout()
    fig.savefig(output_png, bbox_inches="tight")
    fig.savefig(output_pdf, bbox_inches="tight")
    plt.close(fig)


def write_semantic_backend_comparison_outputs(
    output_dir: str | Path,
    config: SemanticBackendComparisonConfig | None = None,
) -> dict[str, Any]:
    config = config or load_semantic_backend_comparison_config()
    outputs = run_semantic_backend_comparison(config=config)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    figures_dir = output_path / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    report = outputs["report"]
    records = report.get("records", [])
    summary = report.get("summary", {})

    records_csv = output_path / "comparison_records.csv"
    records_jsonl = output_path / "comparison_records.jsonl"
    summary_json = output_path / "comparison_summary.json"
    metadata_json = output_path / "metadata.json"
    report_md = output_path / "comparison_report.md"
    report_json = output_path / "comparison_report.json"
    figure_png = figures_dir / "backend_summary.png"
    figure_pdf = figures_dir / "backend_summary.pdf"

    if records:
        fieldnames = [
            "case_id",
            "category",
            "expected_verdict",
            "vector_decision",
            "variant_decision",
            "final_decision",
            "agreement",
            "vector_mode",
            "variant_mode",
            "vector_score",
            "variant_score",
            "vector_latency_seconds",
            "variant_latency_seconds",
            "vector_reason",
            "variant_reason",
            "variant_fallback_used",
        ]
        with records_csv.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                writer.writerow(
                    {
                        "case_id": record["case"]["case_id"],
                        "category": record["case"]["category"],
                        "expected_verdict": record["expected_verdict"],
                        "vector_decision": record["vector_outcome"]["decision"],
                        "variant_decision": record["variant_outcome"]["decision"],
                        "final_decision": record["final_decision"],
                        "agreement": record["agreement"],
                        "vector_mode": record["vector_outcome"]["mode"],
                        "variant_mode": record["variant_outcome"]["mode"],
                        "vector_score": record["vector_outcome"]["score"],
                        "variant_score": record["variant_outcome"]["score"],
                        "vector_latency_seconds": record["vector_outcome"]["latency_seconds"],
                        "variant_latency_seconds": record["variant_outcome"]["latency_seconds"],
                        "vector_reason": record["vector_outcome"]["reason"],
                        "variant_reason": record["variant_outcome"]["reason"],
                        "variant_fallback_used": record["variant_outcome"]["fallback_used"],
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
        "generated_by": "semantic_backend_comparison_v2",
        "experiment": "semantic_backend_comparison",
        "version": "v2",
        "git_commit": _git_commit(),
        "case_count": summary.get("case_count", 0),
        "authority_violation_case_count": summary.get("authority_violation_case_count", 0),
    }
    metadata_json.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    markdown = outputs["markdown"]
    report_md.write_text(markdown, encoding="utf-8")
    root_report = Path(__file__).resolve().parents[3] / "SRP_SEMANTIC_BACKEND_COMPARISON_REPORT.md"
    root_report.write_text(markdown, encoding="utf-8")

    _render_summary_figure(summary, figure_png, figure_pdf)

    return {
        "output_dir": str(output_path),
        "records_csv": str(records_csv),
        "records_jsonl": str(records_jsonl),
        "summary_json": str(summary_json),
        "metadata_json": str(metadata_json),
        "report_markdown": str(report_md),
        "report_json": str(report_json),
        "root_report_markdown": str(root_report),
        "figures": {
            "backend_summary_png": str(figure_png),
            "backend_summary_pdf": str(figure_pdf),
        },
        "report": report,
        "config": outputs["config"],
        "cases": outputs["cases"],
    }
