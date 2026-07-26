from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt


@dataclass(frozen=True)
class PhaseIIBoundaryFigurePaths:
    heatmap_png: str
    heatmap_pdf: str
    coverage_png: str
    coverage_pdf: str

    def as_dict(self) -> dict[str, str]:
        return {
            "heatmap_png": self.heatmap_png,
            "heatmap_pdf": self.heatmap_pdf,
            "coverage_png": self.coverage_png,
            "coverage_pdf": self.coverage_pdf,
        }


def _load_candidate_rows(candidate_results_csv: str | Path) -> list[dict[str, Any]]:
    path = Path(candidate_results_csv)
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _build_matrix(rows: list[dict[str, Any]]) -> tuple[list[float], list[int], list[list[int]]]:
    activation_values = sorted({float(row["activation_threshold"]) for row in rows})
    evidence_values = sorted({int(row["recovery_min_evidence"]) for row in rows})
    matrix = [[0 for _ in activation_values] for _ in evidence_values]

    activation_index = {value: index for index, value in enumerate(activation_values)}
    evidence_index = {value: index for index, value in enumerate(evidence_values)}

    for row in rows:
        activation = float(row["activation_threshold"])
        evidence = int(row["recovery_min_evidence"])
        feasible_raw = row.get("feasible", "False")
        feasible = str(feasible_raw).strip() == "True"
        matrix[evidence_index[evidence]][activation_index[activation]] = 1 if feasible else 0

    return activation_values, evidence_values, matrix


def _render_heatmap(
    activation_values: list[float],
    evidence_values: list[int],
    matrix: list[list[int]],
    output_png: Path,
    output_pdf: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=160)
    image = ax.imshow(matrix, origin="lower", aspect="auto", cmap="Greens", vmin=0, vmax=1)

    ax.set_title("SRP Phase II Feasible Region Heatmap")
    ax.set_xlabel("activation_threshold")
    ax.set_ylabel("recovery_min_evidence")
    ax.set_xticks(range(len(activation_values)))
    ax.set_xticklabels([f"{value:.1f}" for value in activation_values])
    ax.set_yticks(range(len(evidence_values)))
    ax.set_yticklabels([str(value) for value in evidence_values])

    for row_index, _ in enumerate(evidence_values):
        for col_index, _ in enumerate(activation_values):
            value = matrix[row_index][col_index]
            ax.text(
                col_index,
                row_index,
                "1" if value else "0",
                ha="center",
                va="center",
                color="black" if value else "white",
                fontsize=12,
            )

    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04, label="feasible")
    fig.tight_layout()
    fig.savefig(output_png, bbox_inches="tight")
    fig.savefig(output_pdf, bbox_inches="tight")
    plt.close(fig)


def _render_coverage_chart(candidate_count: int, feasible_count: int, output_png: Path, output_pdf: Path) -> None:
    infeasible_count = max(0, candidate_count - feasible_count)
    labels = ["feasible", "infeasible"]
    values = [feasible_count, infeasible_count]
    colors = ["#2E8B57", "#D3D3D3"]

    fig, ax = plt.subplots(figsize=(6.5, 4.2), dpi=160)
    bars = ax.bar(labels, values, color=colors, edgecolor="#2f2f2f")
    ax.set_title("SRP Phase II Candidate Coverage")
    ax.set_ylabel("candidate count")
    ax.set_ylim(0, max(values) + 2 if values else 1)

    for bar, value in zip(bars, values, strict=False):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2, str(value), ha="center", va="bottom")

    coverage = feasible_count / candidate_count if candidate_count else 0.0
    ax.text(
        0.98,
        0.95,
        f"coverage = {coverage:.2f}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": "#b0b0b0"},
    )
    fig.tight_layout()
    fig.savefig(output_png, bbox_inches="tight")
    fig.savefig(output_pdf, bbox_inches="tight")
    plt.close(fig)


def generate_phase_ii_boundary_figures(
    candidate_results_csv: str | Path,
    feasible_region_json: str | Path,
    *,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    candidate_path = Path(candidate_results_csv)
    region_path = Path(feasible_region_json)
    output_root = Path(output_dir) if output_dir is not None else candidate_path.parent / "figures"
    output_root.mkdir(parents=True, exist_ok=True)

    rows = _load_candidate_rows(candidate_path)
    activation_values, evidence_values, matrix = _build_matrix(rows)
    region = json.loads(region_path.read_text(encoding="utf-8"))
    candidate_count = int(region.get("candidate_count", len(rows)))
    feasible_count = int(region.get("feasible_candidate_count", sum(1 for row in rows if str(row.get("feasible", "")).strip() == "True")))

    heatmap_png = output_root / "feasible_heatmap.png"
    heatmap_pdf = output_root / "feasible_heatmap.pdf"
    coverage_png = output_root / "coverage_summary.png"
    coverage_pdf = output_root / "coverage_summary.pdf"

    _render_heatmap(activation_values, evidence_values, matrix, heatmap_png, heatmap_pdf)
    _render_coverage_chart(candidate_count, feasible_count, coverage_png, coverage_pdf)

    return PhaseIIBoundaryFigurePaths(
        heatmap_png=str(heatmap_png),
        heatmap_pdf=str(heatmap_pdf),
        coverage_png=str(coverage_png),
        coverage_pdf=str(coverage_pdf),
    ).as_dict()
