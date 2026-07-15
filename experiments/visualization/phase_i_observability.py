from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import csv

import matplotlib.pyplot as plt


@dataclass(frozen=True)
class PhaseIObservabilityFigurePaths:
    observation_frequency_png: str
    observation_frequency_pdf: str
    drift_histogram_png: str
    drift_histogram_pdf: str

    def as_dict(self) -> dict[str, str]:
        return {
            "observation_frequency_png": self.observation_frequency_png,
            "observation_frequency_pdf": self.observation_frequency_pdf,
            "drift_histogram_png": self.drift_histogram_png,
            "drift_histogram_pdf": self.drift_histogram_pdf,
        }


def _load_rows(csv_path: str | Path) -> list[dict[str, Any]]:
    path = Path(csv_path)
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _render_observation_frequency(rows: list[dict[str, Any]], output_png: Path, output_pdf: Path) -> None:
    counts: dict[str, int] = {}
    for row in rows:
        parameter = str(row.get("parameter", "unknown"))
        counts[parameter] = counts.get(parameter, 0) + 1

    ordered = sorted(counts.items(), key=lambda item: item[0])
    labels = [item[0] for item in ordered]
    values = [item[1] for item in ordered]

    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=160)
    bars = ax.bar(labels, values, color="#4C78A8", edgecolor="#2f2f2f")
    ax.set_title("SRP Phase I Observation Frequency")
    ax.set_ylabel("observation count")
    ax.set_ylim(0, max(values) + 10 if values else 1)
    ax.tick_params(axis="x", rotation=20)

    for bar, value in zip(bars, values, strict=False):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, str(value), ha="center", va="bottom")

    fig.tight_layout()
    fig.savefig(output_png, bbox_inches="tight")
    fig.savefig(output_pdf, bbox_inches="tight")
    plt.close(fig)


def _render_drift_histogram(rows: list[dict[str, Any]], output_png: Path, output_pdf: Path) -> None:
    drift_values = [float(row.get("parameter_drift", 0.0) or 0.0) for row in rows]
    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=160)
    ax.hist(drift_values, bins=min(12, max(4, len(set(drift_values)))), color="#72B7B2", edgecolor="#2f2f2f")
    ax.set_title("SRP Phase I Parameter Drift Distribution")
    ax.set_xlabel("parameter drift")
    ax.set_ylabel("count")
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_png, bbox_inches="tight")
    fig.savefig(output_pdf, bbox_inches="tight")
    plt.close(fig)


def generate_phase_i_observability_figures(
    observability_csv: str | Path,
    *,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    csv_path = Path(observability_csv)
    output_root = Path(output_dir) if output_dir is not None else csv_path.parent / "figures"
    output_root.mkdir(parents=True, exist_ok=True)

    rows = _load_rows(csv_path)

    observation_frequency_png = output_root / "observation_frequency.png"
    observation_frequency_pdf = output_root / "observation_frequency.pdf"
    drift_histogram_png = output_root / "parameter_drift_histogram.png"
    drift_histogram_pdf = output_root / "parameter_drift_histogram.pdf"

    _render_observation_frequency(rows, observation_frequency_png, observation_frequency_pdf)
    _render_drift_histogram(rows, drift_histogram_png, drift_histogram_pdf)

    return PhaseIObservabilityFigurePaths(
        observation_frequency_png=str(observation_frequency_png),
        observation_frequency_pdf=str(observation_frequency_pdf),
        drift_histogram_png=str(drift_histogram_png),
        drift_histogram_pdf=str(drift_histogram_pdf),
    ).as_dict()
