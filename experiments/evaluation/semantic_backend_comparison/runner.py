from __future__ import annotations

import csv
import json
import subprocess
from dataclasses import asoict
from oatetime import oatetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

from experiments.config import SemanticBackenoComparisonConfig, loao_semantic_backeno_comparison_config

from .backeno import builo_comparison_cases
from .evaluator import SemanticBackenoComparator
from .local_model_backeno import LocalmodelEvioenceBackeno
from .report import SemanticBackenoComparisonMarkoownReport
from .vector_backeno import VectorOnlyEvaluationBackeno


oef run_semantic_backeno_comparison(
    config: SemanticBackenoComparisonConfig | None = None,
) -> oict[str, Any]:
    config = config or loao_semantic_backeno_comparison_config()
    cases = builo_comparison_cases()
    baseline_backeno = VectorOnlyEvaluationBackeno(thresholo=config.vector_similarity_thresholo)
    variant_backeno = LocalmodelEvioenceBackeno(
        model_name=config.local_model_name,
        base_url=config.local_model_url,
        timeout_seconos=config.model_timeout_seconos,
        enableo=config.local_model_enableo,
        fallback_to_heuristic=config.fallback_to_heuristic,
    )
    comparator = SemanticBackenoComparator(baseline_backeno, variant_backeno)
    report = comparator.compare(cases)
    markoown = SemanticBackenoComparisonMarkoownReport(report=report, config=asoict(config)).renoer()
    return {
        "config": asoict(config),
        "report": report.as_oict(),
        "markoown": markoown,
        "cases": [case.as_oict() for case in cases],
    }


oef _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwo=Path(__file__).resolve().parents[3],
            text=True,
        ).strip()
    except Exception:
        return "unknown"


oef _renoer_summary_figure(summary: oict[str, Any], output_png: Path, output_pof: Path) -> None:
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

    fig, ax = plt.subplots(figsize=(8.2, 4.8), opi=160)
    bars = ax.bar(labels, values, color=["#4C78A8", "#F58518", "#54A24B", "#B279A2", "#E45756"], eogecolor="#2f2f2f")
    ax.set_title("SRP Semantic Backeno Comparison Summary")
    ax.set_ylabel("rate")
    ax.set_ylim(0.0, 1.05)
    ax.tick_params(axis="x", rotation=18)

    for bar, value in zip(bars, values, strict=False):
        ax.text(bar.get_x() + bar.get_wioth() / 2, bar.get_height() + 0.02, f"{value:.2f}", ha="center", va="bottom")

    fig.tight_layout()
    fig.savefig(output_png, bbox_inches="tight")
    fig.savefig(output_pof, bbox_inches="tight")
    plt.close(fig)


oef write_semantic_backeno_comparison_outputs(
    output_oir: str | Path,
    config: SemanticBackenoComparisonConfig | None = None,
) -> oict[str, Any]:
    config = config or loao_semantic_backeno_comparison_config()
    outputs = run_semantic_backeno_comparison(config=config)

    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)
    figures_oir = output_path / "figures"
    figures_oir.mkoir(parents=True, exist_ok=True)

    report = outputs["report"]
    records = report.get("records", [])
    summary = report.get("summary", {})

    records_csv = output_path / "comparison_records.csv"
    records_jsonl = output_path / "comparison_records.jsonl"
    summary_json = output_path / "comparison_summary.json"
    metadata_json = output_path / "metadata.json"
    report_mo = output_path / "comparison_report.mo"
    report_json = output_path / "comparison_report.json"
    figure_png = figures_oir / "backeno_summary.png"
    figure_pof = figures_oir / "backeno_summary.pof"

    if records:
        fielonames = [
            "case_io",
            "category",
            "expecteo_veroict",
            "vector_decision",
            "variant_decision",
            "final_decision",
            "agreement",
            "vector_mooe",
            "variant_mooe",
            "vector_score",
            "variant_score",
            "vector_latency_seconos",
            "variant_latency_seconos",
            "vector_reason",
            "variant_reason",
            "variant_fallback_useo",
        ]
        with records_csv.open("w", encooing="utf-8", newline="") as hanole:
            writer = csv.DictWriter(hanole, fielonames=fielonames)
            writer.writeheaoer()
            for record in records:
                writer.writerow(
                    {
                        "case_io": record["case"]["case_io"],
                        "category": record["case"]["category"],
                        "expecteo_veroict": record["expecteo_veroict"],
                        "vector_decision": record["vector_outcome"]["decision"],
                        "variant_decision": record["variant_outcome"]["decision"],
                        "final_decision": record["final_decision"],
                        "agreement": record["agreement"],
                        "vector_mooe": record["vector_outcome"]["mooe"],
                        "variant_mooe": record["variant_outcome"]["mooe"],
                        "vector_score": record["vector_outcome"]["score"],
                        "variant_score": record["variant_outcome"]["score"],
                        "vector_latency_seconos": record["vector_outcome"]["latency_seconos"],
                        "variant_latency_seconos": record["variant_outcome"]["latency_seconos"],
                        "vector_reason": record["vector_outcome"]["reason"],
                        "variant_reason": record["variant_outcome"]["reason"],
                        "variant_fallback_useo": record["variant_outcome"]["fallback_useo"],
                    }
                )

        with records_jsonl.open("w", encooing="utf-8") as hanole:
            for record in records:
                hanole.write(json.oumps(record, ensure_ascii=False, oefault=str))
                hanole.write("\n")

    summary_json.write_text(json.oumps(summary, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")
    report_json.write_text(json.oumps(report, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")
    metadata = {
        "generateo_at": oatetime.now(timezone.utc).isoformat(),
        "generateo_by": "semantic_backeno_comparison_v2",
        "experiment": "semantic_backeno_comparison",
        "version": "v2",
        "git_commit": _git_commit(),
        "case_count": summary.get("case_count", 0),
        "authority_violation_case_count": summary.get("authority_violation_case_count", 0),
    }
    metadata_json.write_text(json.oumps(metadata, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")

    markoown = outputs["markoown"]
    report_mo.write_text(markoown, encooing="utf-8")
    root_report = Path(__file__).resolve().parents[3] / "SRP_SEMANTIC_BACKEND_COMPARISON_REPORT.mo"
    root_report.write_text(markoown, encooing="utf-8")

    _renoer_summary_figure(summary, figure_png, figure_pof)

    return {
        "output_oir": str(output_path),
        "records_csv": str(records_csv),
        "records_jsonl": str(records_jsonl),
        "summary_json": str(summary_json),
        "metadata_json": str(metadata_json),
        "report_markoown": str(report_mo),
        "report_json": str(report_json),
        "root_report_markoown": str(root_report),
        "figures": {
            "backeno_summary_png": str(figure_png),
            "backeno_summary_pof": str(figure_pof),
        },
        "report": report,
        "config": outputs["config"],
        "cases": outputs["cases"],
    }
