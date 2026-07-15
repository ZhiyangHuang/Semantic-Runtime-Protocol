from __future__ import annotations

import csv
import json
import math
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import matplotlib.pyplot as plt

from experiments.validation.phase_ii_boundary.model import FeasibleRegion

from .objective import ObjectiveWeights
from .runner import run_phase_iii_a_round1_optimization


@dataclass(frozen=True)
class ObjectiveSensitivityScenario:
    name: str
    weights: ObjectiveWeights
    description: str = ""

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self.weights)
        payload["name"] = self.name
        payload["description"] = self.description
        return payload


@dataclass(frozen=True)
class ObjectiveSensitivityScenarioResult:
    scenario: str
    candidate_count: int
    top_candidate: dict[str, Any] | None
    top_objective_value: float | None
    objective_span: float | None
    ordered_candidates: list[str] = field(default_factory=list)
    objective_values: list[float] = field(default_factory=list)
    report: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_objective_sensitivity_scenarios() -> tuple[ObjectiveSensitivityScenario, ...]:
    return (
        ObjectiveSensitivityScenario(
            name="O1_balanced",
            weights=ObjectiveWeights(0.4, 0.3, 0.2, 0.1),
            description="Balanced objective used by the Phase III-A round 1 baseline.",
        ),
        ObjectiveSensitivityScenario(
            name="O2_quality_priority",
            weights=ObjectiveWeights(0.6, 0.2, 0.1, 0.1),
            description="Quality-heavy objective that prioritizes semantic quality over resource cost.",
        ),
        ObjectiveSensitivityScenario(
            name="O3_cost_priority",
            weights=ObjectiveWeights(0.2, 0.2, 0.5, 0.1),
            description="Cost-heavy objective that emphasizes resource cost reduction.",
        ),
        ObjectiveSensitivityScenario(
            name="O4_stability_priority",
            weights=ObjectiveWeights(0.3, 0.2, 0.2, 0.3),
            description="Stability-heavy objective that increases the instability penalty weight.",
        ),
    )


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[2], text=True).strip()
    except Exception:
        return "unknown"


def _ordered_candidates(report: dict[str, Any]) -> list[dict[str, Any]]:
    evaluations = list(report.get("evaluations", []))
    evaluations.sort(key=lambda item: int(item.get("rank", 0) or 0))
    return evaluations


def _candidate_label(candidate: dict[str, Any]) -> str:
    label = str(candidate.get("label", "") or "").strip()
    if label:
        return label
    return f"a{candidate.get('activation_threshold')}_r{candidate.get('recovery_min_evidence')}"


def _rank_map(order: list[str]) -> dict[str, int]:
    return {candidate_label: index + 1 for index, candidate_label in enumerate(order)}


def _spearman_rho(reference_order: list[str], comparison_order: list[str]) -> float:
    if len(reference_order) <= 1:
        return 1.0
    reference_ranks = _rank_map(reference_order)
    comparison_ranks = _rank_map(comparison_order)
    labels = [label for label in reference_order if label in comparison_ranks]
    if not labels:
        return 0.0
    n = len(labels)
    sum_squared_diffs = sum((reference_ranks[label] - comparison_ranks[label]) ** 2 for label in labels)
    return round(1.0 - (6.0 * sum_squared_diffs) / (n * (n * n - 1)), 6) if n > 1 else 1.0


def _kendall_tau(reference_order: list[str], comparison_order: list[str]) -> float:
    reference_ranks = _rank_map(reference_order)
    comparison_ranks = _rank_map(comparison_order)
    labels = [label for label in reference_order if label in comparison_ranks]
    n = len(labels)
    if n <= 1:
        return 1.0

    concordant = 0
    discordant = 0
    for left_index in range(n):
        for right_index in range(left_index + 1, n):
            left_label = labels[left_index]
            right_label = labels[right_index]
            reference_sign = reference_ranks[left_label] - reference_ranks[right_label]
            comparison_sign = comparison_ranks[left_label] - comparison_ranks[right_label]
            if reference_sign * comparison_sign > 0:
                concordant += 1
            elif reference_sign * comparison_sign < 0:
                discordant += 1
    total_pairs = concordant + discordant
    if total_pairs == 0:
        return 1.0
    return round((concordant - discordant) / total_pairs, 6)


def _topk_overlap(reference_order: list[str], comparison_order: list[str], k: int) -> dict[str, Any]:
    reference_top = reference_order[:k]
    comparison_top = comparison_order[:k]
    overlap = len(set(reference_top) & set(comparison_top))
    return {
        "k": k,
        "overlap_count": overlap,
        "overlap_rate": overlap / float(min(k, len(reference_order), len(comparison_order))) if reference_order and comparison_order else 0.0,
        "reference_top": reference_top,
        "comparison_top": comparison_top,
    }


def _render_rank_correlation_heatmap(matrix: list[list[float]], labels: list[str], output_png: Path, output_pdf: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.8, 5.4), dpi=160)
    image = ax.imshow(matrix, origin="lower", aspect="auto", cmap="PuBu", vmin=-1, vmax=1)
    ax.set_title("SRP Phase III-A Objective Sensitivity")
    ax.set_xlabel("comparison scenario")
    ax.set_ylabel("reference scenario")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=20)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)

    for row_index, reference in enumerate(labels):
        for col_index, comparison in enumerate(labels):
            ax.text(col_index, row_index, f"{matrix[row_index][col_index]:.2f}", ha="center", va="center", fontsize=11)

    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04, label="Spearman rho")
    fig.tight_layout()
    fig.savefig(output_png, bbox_inches="tight")
    fig.savefig(output_pdf, bbox_inches="tight")
    plt.close(fig)


def _render_top_objective_bar(results: list[ObjectiveSensitivityScenarioResult], output_png: Path, output_pdf: Path) -> None:
    labels = [result.scenario for result in results]
    values = [float(result.top_objective_value or 0.0) for result in results]

    fig, ax = plt.subplots(figsize=(7.6, 4.6), dpi=160)
    bars = ax.bar(labels, values, color=["#4C78A8", "#F58518", "#54A24B", "#B279A2"], edgecolor="#2f2f2f")
    ax.set_title("SRP Phase III-A Top Objective per Weight Setting")
    ax.set_ylabel("top objective value")
    ax.tick_params(axis="x", rotation=20)
    ax.set_ylim(0, max(values) + 0.1 if values else 1.0)

    for bar, value in zip(bars, values, strict=False):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01, f"{value:.2f}", ha="center", va="bottom")

    fig.tight_layout()
    fig.savefig(output_png, bbox_inches="tight")
    fig.savefig(output_pdf, bbox_inches="tight")
    plt.close(fig)


def _scenario_result(
    scenario: ObjectiveSensitivityScenario,
    feasible_region: FeasibleRegion,
) -> ObjectiveSensitivityScenarioResult:
    optimization_output = run_phase_iii_a_round1_optimization(
        weights=scenario.weights,
        feasible_region=feasible_region,
    )
    report = dict(optimization_output["report"])
    ordered_evaluations = _ordered_candidates(report)
    ordered_candidates = [_candidate_label(item["candidate"]) for item in ordered_evaluations]
    objective_values = [float(item.get("objective_value", 0.0) or 0.0) for item in ordered_evaluations]
    top_candidate = ordered_evaluations[0]["candidate"] if ordered_evaluations else None
    top_objective_value = float(ordered_evaluations[0]["objective_value"]) if ordered_evaluations else None
    objective_span = report["summary"].get("objective_span")
    return ObjectiveSensitivityScenarioResult(
        scenario=scenario.name,
        candidate_count=int(report["summary"].get("candidate_count", 0) or 0),
        top_candidate=top_candidate,
        top_objective_value=top_objective_value,
        objective_span=float(objective_span) if objective_span is not None else None,
        ordered_candidates=ordered_candidates,
        objective_values=objective_values,
        report=report,
    )


def write_phase_iii_a_objective_sensitivity_outputs(
    *,
    feasible_region: FeasibleRegion,
    output_dir: str | Path,
    scenarios: Iterable[ObjectiveSensitivityScenario] | None = None,
) -> dict[str, Any]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    scenario_list = tuple(scenarios) if scenarios is not None else build_objective_sensitivity_scenarios()

    scenario_results = [_scenario_result(scenario, feasible_region) for scenario in scenario_list]
    reference_result = next((result for result in scenario_results if result.scenario == "O1_balanced"), scenario_results[0])
    scenario_names = [result.scenario for result in scenario_results]

    pairwise: dict[str, dict[str, Any]] = {}
    for left in scenario_results:
        pairwise[left.scenario] = {}
        for right in scenario_results:
            pairwise[left.scenario][right.scenario] = {
                "spearman_rho": _spearman_rho(left.ordered_candidates, right.ordered_candidates),
                "kendall_tau": _kendall_tau(left.ordered_candidates, right.ordered_candidates),
                "top1_match": (left.ordered_candidates[:1] == right.ordered_candidates[:1]),
                "top3_overlap": _topk_overlap(left.ordered_candidates, right.ordered_candidates, 3),
                "top5_overlap": _topk_overlap(left.ordered_candidates, right.ordered_candidates, 5),
            }

    reference_pairwise = pairwise[reference_result.scenario]

    summary = {
        "scenario_count": len(scenario_results),
        "scenario_names": scenario_names,
        "reference_scenario": reference_result.scenario,
        "feasible_region_coverage": feasible_region.coverage,
        "candidate_count": reference_result.candidate_count,
        "scenario_summaries": {
            result.scenario: {
                "candidate_count": result.candidate_count,
                "top_candidate": result.top_candidate,
                "top_objective_value": result.top_objective_value,
                "objective_span": result.objective_span,
                "ordered_candidates": result.ordered_candidates,
            }
            for result in scenario_results
        },
        "pairwise_comparison": pairwise,
        "reference_comparison": reference_pairwise,
    }

    rankings_csv = output_path / "objective_rankings.csv"
    rankings_jsonl = output_path / "objective_rankings.jsonl"
    summary_path = output_path / "objective_sensitivity_summary.json"
    metadata_path = output_path / "metadata.json"
    report_path = output_path / "objective_sensitivity_report.md"

    ranking_rows: list[dict[str, Any]] = []
    for result in scenario_results:
        for rank, evaluation in enumerate(result.report.get("evaluations", []), start=1):
            ranking_rows.append(
                {
                    "scenario": result.scenario,
                    "rank": rank,
                    "candidate_label": _candidate_label(evaluation["candidate"]),
                    "activation_threshold": evaluation["candidate"]["activation_threshold"],
                    "recovery_min_evidence": evaluation["candidate"]["recovery_min_evidence"],
                    "objective_value": evaluation["objective_value"],
                }
            )

    with rankings_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(ranking_rows[0].keys()) if ranking_rows else [])
        writer.writeheader()
        for row in ranking_rows:
            writer.writerow(row)

    with rankings_jsonl.open("w", encoding="utf-8") as handle:
        for row in ranking_rows:
            handle.write(json.dumps(row, ensure_ascii=False, default=str))
            handle.write("\n")

    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "phase_iii_a_objective_sensitivity_v1",
        "experiment": "phase_iii_a_objective_sensitivity",
        "version": "v1",
        "git_commit": _git_commit(),
        "scenario_names": scenario_names,
        "feasible_region_coverage": feasible_region.coverage,
        "feasible_region_candidate_count": feasible_region.candidate_count,
        "feasible_region_feasible_candidate_count": feasible_region.feasible_candidate_count,
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    figures_dir = output_path / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    corr_png = figures_dir / "rank_correlation_heatmap.png"
    corr_pdf = figures_dir / "rank_correlation_heatmap.pdf"
    top_png = figures_dir / "top_objective_bar.png"
    top_pdf = figures_dir / "top_objective_bar.pdf"

    matrix = [[pairwise[left][right]["spearman_rho"] for right in scenario_names] for left in scenario_names]
    _render_rank_correlation_heatmap(matrix, scenario_names, corr_png, corr_pdf)
    _render_top_objective_bar(scenario_results, top_png, top_pdf)

    report_lines = [
        "# SRP Phase III-A Objective Sensitivity Report",
        "",
        "This report freezes the Phase III-A objective sensitivity package for SRP.",
        "It is a sensitivity report, not a calibration artifact and not an optimization artifact.",
        "",
        "## Purpose",
        "",
        "The objective sensitivity study compares how different objective weights change the ranking of the same feasible-region candidates.",
        "",
        "## Experimental Boundary",
        "",
        f"- feasible region coverage: `{feasible_region.coverage:.4f}`",
        f"- candidate count: `{feasible_region.candidate_count}`",
        f"- feasible candidate count: `{feasible_region.feasible_candidate_count}`",
        "",
        "## Scenario Summary",
        "",
    ]
    for result in scenario_results:
        report_lines.extend(
            [
                f"### {result.scenario}",
                "",
                f"- top candidate: `{result.top_candidate}`",
                f"- top objective value: `{result.top_objective_value}`",
                f"- objective span: `{result.objective_span}`",
                f"- candidate count: `{result.candidate_count}`",
                "",
            ]
        )

    report_lines.extend(
        [
            "## Stability Analysis",
            "",
            "The study reports Top-1 match, Top-3 overlap, Top-5 overlap, Spearman rho, and Kendall tau between objective settings.",
            "The main expectation is not invariant Top-1 results, but controlled sensitivity of rankings to the declared objective.",
            "This is objective decoupling rather than boundary drift: the feasible set does not change, but the ranking order within that fixed set does.",
            "In the current feasible region, recovery success and instability penalty are constant across candidates, so the observed ranking shifts are primarily driven by semantic-quality and resource-cost tradeoffs.",
            "",
            "## Figures",
            "",
            f"- rank correlation heatmap: `{corr_png}`",
            f"- top objective bar chart: `{top_png}`",
            "",
            "## Relation to the Paper",
            "",
            "This study supports the paper's governed-optimization claim by showing that the feasible region is fixed while the ranking depends on the objective weights.",
        ]
    )
    report_path.write_text("\n".join(report_lines).strip() + "\n", encoding="utf-8")

    return {
        "output_dir": str(output_path),
        "rankings_csv": str(rankings_csv),
        "rankings_jsonl": str(rankings_jsonl),
        "summary": str(summary_path),
        "metadata": str(metadata_path),
        "report": str(report_path),
        "figures": {
            "rank_correlation_heatmap_png": str(corr_png),
            "rank_correlation_heatmap_pdf": str(corr_pdf),
            "top_objective_bar_png": str(top_png),
            "top_objective_bar_pdf": str(top_pdf),
        },
        "summary_data": summary,
        "scenario_results": [result.as_dict() for result in scenario_results],
    }
