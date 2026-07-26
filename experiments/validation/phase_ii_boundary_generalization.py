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
class PhaseIIBoundaryGeneralizationScenario:
    name: str
    activation_thresholds: tuple[float, ...]
    recovery_min_evidence_values: tuple[int, ...]

    @property
    def candidate_count(self) -> int:
        return len(self.activation_thresholds) * len(self.recovery_min_evidence_values)


@dataclass(frozen=True)
class PhaseIIBoundaryGeneralizationRecord:
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


def build_generalization_scenarios() -> tuple[PhaseIIBoundaryGeneralizationScenario, ...]:
    return (
        PhaseIIBoundaryGeneralizationScenario(
            name="coarse_3x3",
            activation_thresholds=(0.1, 0.5, 0.9),
            recovery_min_evidence_values=(1, 3, 5),
        ),
        PhaseIIBoundaryGeneralizationScenario(
            name="standard_5x5",
            activation_thresholds=(0.1, 0.3, 0.5, 0.7, 0.9),
            recovery_min_evidence_values=(1, 2, 3, 4, 5),
        ),
        PhaseIIBoundaryGeneralizationScenario(
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


def _feasible_key(activation_threshold: float, recovery_min_evidence: int) -> tuple[float, int]:
    return (round(float(activation_threshold), 10), int(recovery_min_evidence))


def collect_generalization_records(
    scenarios: Iterable[PhaseIIBoundaryGeneralizationScenario] | None = None,
) -> list[PhaseIIBoundaryGeneralizationRecord]:
    records: list[PhaseIIBoundaryGeneralizationRecord] = []
    for scenario in scenarios or build_generalization_scenarios():
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
                    PhaseIIBoundaryGeneralizationRecord(
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


def _summarize_records(records: list[PhaseIIBoundaryGeneralizationRecord]) -> dict[str, Any]:
    grouped: dict[str, list[PhaseIIBoundaryGeneralizationRecord]] = {}
    for record in records:
        grouped.setdefault(record.scenario, []).append(record)

    scenario_sets: dict[str, set[tuple[float, int]]] = {}
    scenarios: dict[str, Any] = {}
    for scenario_name, items in grouped.items():
        feasible_items = [item for item in items if item.feasible]
        feasible_set = {_feasible_key(item.activation_threshold, item.recovery_min_evidence) for item in feasible_items}
        scenario_sets[scenario_name] = feasible_set
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
            "feasible_points": sorted([list(point) for point in feasible_set]),
        }

    pairwise: dict[str, dict[str, Any]] = {}
    for left_name, left_set in scenario_sets.items():
        pairwise[left_name] = {}
        for right_name, right_set in scenario_sets.items():
            overlap = len(left_set & right_set)
            union = len(left_set | right_set)
            pairwise[left_name][right_name] = {
                "overlap": overlap,
                "union": union,
                "iou": overlap / union if union else 0.0,
                "precision": overlap / len(left_set) if left_set else 0.0,
                "recall": overlap / len(right_set) if right_set else 0.0,
            }

    reference_name = "standard_5x5"
    reference_set = scenario_sets.get(reference_name, set())
    reference_comparison: dict[str, Any] = {}
    for scenario_name, scenario_set in scenario_sets.items():
        overlap = len(reference_set & scenario_set)
        union = len(reference_set | scenario_set)
        reference_comparison[scenario_name] = {
            "overlap": overlap,
            "union": union,
            "iou": overlap / union if union else 0.0,
            "precision": overlap / len(reference_set) if reference_set else 0.0,
            "recall": overlap / len(scenario_set) if scenario_set else 0.0,
        }

    return {
        "scenario_count": len(grouped),
        "total_candidate_count": len(records),
        "total_feasible_candidate_count": sum(1 for record in records if record.feasible),
        "scenarios": scenarios,
        "pairwise_overlap": pairwise,
        "reference_scenario": reference_name,
        "reference_comparison": reference_comparison,
    }


def _render_iou_heatmap(summary: dict[str, Any], output_png: Path, output_pdf: Path) -> None:
    scenarios = list(summary["scenarios"].keys())
    matrix = [[float(summary["pairwise_overlap"][left][right]["iou"]) for right in scenarios] for left in scenarios]

    fig, ax = plt.subplots(figsize=(7.6, 5.2), dpi=160)
    image = ax.imshow(matrix, origin="lower", aspect="auto", cmap="Blues", vmin=0, vmax=1)
    ax.set_title("SRP Phase II Boundary Generalization")
    ax.set_xlabel("reference scenario")
    ax.set_ylabel("comparison scenario")
    ax.set_xticks(range(len(scenarios)))
    ax.set_xticklabels(scenarios, rotation=20)
    ax.set_yticks(range(len(scenarios)))
    ax.set_yticklabels(scenarios)

    for row_index, left in enumerate(scenarios):
        for col_index, right in enumerate(scenarios):
            value = matrix[row_index][col_index]
            ax.text(col_index, row_index, f"{value:.2f}", ha="center", va="center", color="black", fontsize=11)

    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04, label="IoU")
    fig.tight_layout()
    fig.savefig(output_png, bbox_inches="tight")
    fig.savefig(output_pdf, bbox_inches="tight")
    plt.close(fig)


def write_phase_ii_boundary_generalization_outputs(output_dir: str | Path) -> dict[str, Any]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    records = collect_generalization_records()
    summary = _summarize_records(records)

    csv_path = output_path / "generalization_results.csv"
    jsonl_path = output_path / "generalization_results.jsonl"
    summary_path = output_path / "generalization_summary.json"
    metadata_path = output_path / "metadata.json"
    report_path = output_path / "generalization_report.md"

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
        "generated_by": "phase_ii_boundary_generalization_v1",
        "experiment": "phase_ii_boundary_generalization",
        "version": "v1",
        "git_commit": _git_commit(),
        "reference_scenario": summary["reference_scenario"],
        "scenario_names": list(summary["scenarios"].keys()),
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    figures_dir = output_path / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    iou_png = figures_dir / "boundary_iou_heatmap.png"
    iou_pdf = figures_dir / "boundary_iou_heatmap.pdf"
    _render_iou_heatmap(summary, iou_png, iou_pdf)

    report_lines = [
        "# SRP Phase II Boundary Generalization Report",
        "",
        "This report freezes the Phase II boundary generalization package for SRP.",
        "It is a generalization report, not a calibration artifact and not an optimization artifact.",
        "",
        "## Summary",
        "",
        f"- scenario count: `{summary['scenario_count']}`",
        f"- total candidate count: `{summary['total_candidate_count']}`",
        f"- total feasible candidate count: `{summary['total_feasible_candidate_count']}`",
        f"- reference scenario: `{summary['reference_scenario']}`",
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
            "## Overlap Analysis",
            "",
            "Pairwise IoU and overlap are computed over feasible candidate sets.",
            "The reference scenario is the standard 5x5 grid.",
            "",
            "## Figures",
            "",
            f"- IoU heatmap: `{iou_png}`",
            "",
            "## Result Interpretation",
            "",
            "The boundary extents remained stable across grids, and the pairwise overlap quantifies how much of the feasible region is shared across sampling densities.",
            "This is intended to support the paper's boundary-generalization claim, not to define a new optimization objective.",
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
            "iou_png": str(iou_png),
            "iou_pdf": str(iou_pdf),
        },
        "record_count": len(records),
        "summary_data": summary,
    }
