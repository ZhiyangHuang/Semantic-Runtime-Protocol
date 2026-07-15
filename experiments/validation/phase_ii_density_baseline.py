from __future__ import annotations

import csv
import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

import matplotlib.pyplot as plt

from experiments.sensitivity.interaction.runner import run_activation_recovery_cell


@dataclass(frozen=True)
class PhaseIIDensityScenario:
    name: str
    activation_thresholds: tuple[float, ...]
    recovery_min_evidence_values: tuple[int, ...]

    @property
    def candidate_count(self) -> int:
        return len(self.activation_thresholds) * len(self.recovery_min_evidence_values)


@dataclass(frozen=True)
class PhaseIIDensityRecord:
    scenario: str
    activation_threshold: float
    recovery_min_evidence: int
    replay_equivalent: bool
    state_transition_equivalence: bool
    authority_preserved: bool
    recovery_success: bool
    boundary_consistency_score: float
    feasible: bool
    metrics: dict[str, Any] = field(default_factory=dict)
    observations: list[str] = field(default_factory=list)


def build_density_scenarios() -> tuple[PhaseIIDensityScenario, ...]:
    return (
        PhaseIIDensityScenario(
            name="coarse_3x3",
            activation_thresholds=(0.1, 0.5, 0.9),
            recovery_min_evidence_values=(1, 3, 5),
        ),
        PhaseIIDensityScenario(
            name="standard_5x5",
            activation_thresholds=(0.1, 0.3, 0.5, 0.7, 0.9),
            recovery_min_evidence_values=(1, 2, 3, 4, 5),
        ),
        PhaseIIDensityScenario(
            name="dense_9x9",
            activation_thresholds=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9),
            recovery_min_evidence_values=(1, 2, 3, 4, 5, 6, 7, 8, 9),
        ),
    )


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[2], text=True).strip()
    except Exception:
        return "unknown"


def _boundary_consistency_flag(metrics: dict[str, Any]) -> bool:
    return bool(metrics.get("replay_equivalent", False)) and bool(metrics.get("state_transition_equivalence", False))


def collect_density_baseline_records(
    scenarios: Iterable[PhaseIIDensityScenario] | None = None,
) -> list[PhaseIIDensityRecord]:
    records: list[PhaseIIDensityRecord] = []
    for scenario in scenarios or build_density_scenarios():
        for activation_threshold in scenario.activation_thresholds:
            for recovery_min_evidence in scenario.recovery_min_evidence_values:
                result = run_activation_recovery_cell(activation_threshold, recovery_min_evidence)
                metrics = dict(result.get("metrics", {}))
                replay_equivalent = bool(metrics.get("replay_equivalent", False))
                state_transition_equivalence = bool(metrics.get("state_transition_equivalence", False))
                recovery_success = bool(metrics.get("recovery_success", False))
                authority_preserved = replay_equivalent and state_transition_equivalence
                feasible = replay_equivalent and state_transition_equivalence and authority_preserved and recovery_success
                records.append(
                    PhaseIIDensityRecord(
                        scenario=scenario.name,
                        activation_threshold=activation_threshold,
                        recovery_min_evidence=recovery_min_evidence,
                        replay_equivalent=replay_equivalent,
                        state_transition_equivalence=state_transition_equivalence,
                        authority_preserved=authority_preserved,
                        recovery_success=recovery_success,
                        boundary_consistency_score=float(metrics.get("boundary_consistency_score", 0.0) or 0.0),
                        feasible=feasible,
                        metrics=metrics,
                        observations=list(result.get("observations", [])),
                    )
                )
    return records


def _summarize_records(records: list[PhaseIIDensityRecord]) -> dict[str, Any]:
    grouped: dict[str, list[PhaseIIDensityRecord]] = {}
    for record in records:
        grouped.setdefault(record.scenario, []).append(record)

    scenarios: dict[str, Any] = {}
    for scenario_name, items in grouped.items():
        feasible_items = [item for item in items if item.feasible]
        activation_values = [item.activation_threshold for item in feasible_items]
        evidence_values = [item.recovery_min_evidence for item in feasible_items]
        scenarios[scenario_name] = {
            "candidate_count": len(items),
            "feasible_candidate_count": len(feasible_items),
            "coverage": len(feasible_items) / len(items) if items else 0.0,
            "activation_threshold": {
                "min": min(activation_values) if activation_values else None,
                "max": max(activation_values) if activation_values else None,
            },
            "recovery_min_evidence": {
                "min": min(evidence_values) if evidence_values else None,
                "max": max(evidence_values) if evidence_values else None,
            },
            "mean_boundary_consistency_score": mean([item.boundary_consistency_score for item in items]) if items else 0.0,
        }

    reference = scenarios.get("dense_9x9", {})
    return {
        "scenario_count": len(grouped),
        "total_candidate_count": len(records),
        "total_feasible_candidate_count": sum(1 for record in records if record.feasible),
        "scenarios": scenarios,
        "reference_scenario": reference,
    }


def _render_coverage_bar(summary: dict[str, Any], output_png: Path, output_pdf: Path) -> None:
    scenarios = summary["scenarios"]
    labels = list(scenarios.keys())
    coverage_values = [float(scenarios[label]["coverage"]) for label in labels]
    candidate_counts = [int(scenarios[label]["candidate_count"]) for label in labels]

    fig, ax = plt.subplots(figsize=(8.2, 4.8), dpi=160)
    bars = ax.bar(labels, coverage_values, color=["#4C78A8", "#72B7B2", "#54A24B"], edgecolor="#2f2f2f")
    ax.set_title("SRP Phase II Sampling Density Baseline")
    ax.set_ylabel("feasible coverage")
    ax.set_ylim(0, 1.0)
    ax.tick_params(axis="x", rotation=20)

    for bar, coverage, candidate_count in zip(bars, coverage_values, candidate_counts, strict=False):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.03,
            f"{coverage:.2f}\n(n={candidate_count})",
            ha="center",
            va="bottom",
        )

    fig.tight_layout()
    fig.savefig(output_png, bbox_inches="tight")
    fig.savefig(output_pdf, bbox_inches="tight")
    plt.close(fig)


def write_phase_ii_density_baseline_outputs(output_dir: str | Path) -> dict[str, Any]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    records = collect_density_baseline_records()
    summary = _summarize_records(records)

    csv_path = output_path / "density_results.csv"
    jsonl_path = output_path / "density_results.jsonl"
    summary_path = output_path / "density_summary.json"
    metadata_path = output_path / "metadata.json"
    report_path = output_path / "density_report.md"

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(records[0]).keys()) if records else [])
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))

    with jsonl_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(asdict(record), ensure_ascii=False, default=str))
            handle.write("\n")

    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "phase_ii_density_baseline_v1",
        "experiment": "phase_ii_density_baseline",
        "version": "v1",
        "git_commit": _git_commit(),
        "scenario_names": list(summary["scenarios"].keys()),
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    figures_dir = output_path / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    coverage_png = figures_dir / "density_coverage.png"
    coverage_pdf = figures_dir / "density_coverage.pdf"
    _render_coverage_bar(summary, coverage_png, coverage_pdf)

    report_lines = [
        "# SRP Phase II Sampling Density Baseline",
        "",
        "This report freezes the Phase II sampling-density baseline package for SRP.",
        "It is a baseline report, not a calibration artifact and not an optimization artifact.",
        "",
        "## Summary",
        "",
        f"- scenario count: `{summary['scenario_count']}`",
        f"- total candidate count: `{summary['total_candidate_count']}`",
        f"- total feasible candidate count: `{summary['total_feasible_candidate_count']}`",
        "",
    ]
    for scenario_name, scenario_summary in summary["scenarios"].items():
        report_lines.extend(
            [
                f"### {scenario_name}",
                "",
                f"- candidate count: `{scenario_summary['candidate_count']}`",
                f"- feasible candidate count: `{scenario_summary['feasible_candidate_count']}`",
                f"- coverage: `{scenario_summary['coverage']:.4f}`",
                f"- activation_threshold range: `{scenario_summary['activation_threshold']['min']}` to `{scenario_summary['activation_threshold']['max']}`",
                f"- recovery_min_evidence range: `{scenario_summary['recovery_min_evidence']['min']}` to `{scenario_summary['recovery_min_evidence']['max']}`",
                f"- mean boundary consistency score: `{scenario_summary['mean_boundary_consistency_score']:.4f}`",
                "",
            ]
        )
    report_lines.extend(
        [
            "## Interpretation",
            "",
            "The sampling-density baseline compares coarse, standard, and dense candidate grids.",
            "It is intended to show whether the validated feasible region remains stable as sampling density increases.",
            "",
            "## Figures",
            "",
            f"- coverage comparison: `{coverage_png}`",
            "",
            "## Relation to the Paper",
            "",
            "This baseline supports the paper's boundary-validation claim by checking that the feasible region is not an artifact of a single grid resolution.",
        ]
    )
    report_path.write_text("\n".join(report_lines).strip() + "\n", encoding="utf-8")

    return {
        "output_dir": str(output_path),
        "csv": str(csv_path),
        "jsonl": str(jsonl_path),
        "summary": str(summary_path),
        "metadata": str(metadata_path),
        "report": str(report_path),
        "figures": {
            "coverage_png": str(coverage_png),
            "coverage_pdf": str(coverage_pdf),
        },
        "record_count": len(records),
        "summary_data": summary,
    }
