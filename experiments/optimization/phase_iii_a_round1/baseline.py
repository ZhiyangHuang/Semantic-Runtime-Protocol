from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from experiments.validation.phase_ii_boundary.model import FeasibleRegion

from .candidate import build_candidate_space_from_feasible_region, build_round1_candidate_space
from .evaluator import OptimizationEvaluation, evaluate_candidate
from .objective import ObjectiveWeights
from .ranking import rank_candidate_evaluations
from .report import build_optimization_report


@dataclass(frozen=True)
class PhaseIIIBaselineComparisonReport:
    report_id: str
    status: str
    summary: dict[str, Any] = field(default_factory=dict)
    baseline_report: dict[str, Any] = field(default_factory=dict)
    srp_report: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _build_full_phase_ii_grid_candidates() -> list[Any]:
    return build_round1_candidate_space(
        activation_thresholds=(0.1, 0.3, 0.5, 0.7, 0.9),
        recovery_min_evidence_values=(1, 2, 3, 4, 5),
    )


def _build_naive_grid_evaluations(weights: ObjectiveWeights) -> list[OptimizationEvaluation]:
    candidates = _build_full_phase_ii_grid_candidates()
    evaluations = [evaluate_candidate(candidate, weights=weights) for candidate in candidates]
    return rank_candidate_evaluations(evaluations)


def _build_srp_region_evaluations(
    region: FeasibleRegion,
    weights: ObjectiveWeights,
) -> list[OptimizationEvaluation]:
    candidates = build_candidate_space_from_feasible_region(region)
    evaluations = [evaluate_candidate(candidate, weights=weights) for candidate in candidates]
    return rank_candidate_evaluations(evaluations)


def write_phase_iii_a_baseline_comparison_report(
    *,
    feasible_region: FeasibleRegion,
    weights: ObjectiveWeights | None = None,
    output_dir: str | Path,
) -> dict[str, Any]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    weights = weights or ObjectiveWeights()

    baseline_evaluations = _build_naive_grid_evaluations(weights)
    srp_evaluations = _build_srp_region_evaluations(feasible_region, weights)

    baseline_report = build_optimization_report(baseline_evaluations, weights)
    srp_report = build_optimization_report(srp_evaluations, weights, feasible_region=feasible_region.as_dict())

    baseline_top = baseline_evaluations[0] if baseline_evaluations else None
    srp_top = srp_evaluations[0] if srp_evaluations else None
    top_match = False
    if baseline_top is not None and srp_top is not None:
        top_match = baseline_top.candidate.as_dict() == srp_top.candidate.as_dict()

    summary = {
        "baseline_candidate_count": len(baseline_evaluations),
        "srp_candidate_count": len(srp_evaluations),
        "baseline_top_objective_value": baseline_top.objective_value if baseline_top is not None else None,
        "srp_top_objective_value": srp_top.objective_value if srp_top is not None else None,
        "baseline_top_candidate": baseline_top.candidate.as_dict() if baseline_top is not None else None,
        "srp_top_candidate": srp_top.candidate.as_dict() if srp_top is not None else None,
        "top_match": top_match,
        "search_reduction": 1.0 - (len(srp_evaluations) / float(len(baseline_evaluations))) if baseline_evaluations else 0.0,
        "feasible_region_coverage": feasible_region.coverage,
    }

    report = PhaseIIIBaselineComparisonReport(
        report_id=f"phase_iii_a_baseline_comparison_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        status="compared",
        summary=summary,
        baseline_report=baseline_report.as_dict(),
        srp_report=srp_report.as_dict(),
    )

    report_path = output_path / "baseline_comparison_report.json"
    markdown_path = output_path / "baseline_comparison_report.md"
    report_path.write_text(json.dumps(report.as_dict(), ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    markdown_lines = [
        "# SRP Phase III-A Baseline Comparison Report",
        "",
        "This report freezes the Phase III-A baseline comparison package for SRP.",
        "It compares a naive full-grid sweep against the SRP constrained optimization path.",
        "",
        "## Summary",
        "",
        f"- baseline candidate count: `{summary['baseline_candidate_count']}`",
        f"- SRP candidate count: `{summary['srp_candidate_count']}`",
        f"- search reduction: `{summary['search_reduction']:.4f}`",
        f"- top match: `{summary['top_match']}`",
        f"- baseline top objective value: `{summary['baseline_top_objective_value']}`",
        f"- SRP top objective value: `{summary['srp_top_objective_value']}`",
        f"- feasible region coverage: `{summary['feasible_region_coverage']:.4f}`",
        "",
        "## Interpretation",
        "",
        "The baseline comparison checks whether SRP preserves the top-ranked candidate while reducing the number of evaluated candidates.",
        "This report is intended to support the paper's governed-optimization claim by contrasting SRP with a naive sweep baseline.",
        "",
        "## Relation to the Paper",
        "",
        "For the SRP optimization report, see the Phase III-A Round 1 optimization evidence package.",
    ]
    markdown_path.write_text("\n".join(markdown_lines).strip() + "\n", encoding="utf-8")

    return {
        "output_dir": str(output_path),
        "report_json": str(report_path),
        "report_markdown": str(markdown_path),
        "summary": summary,
        "baseline_report": baseline_report.as_dict(),
        "srp_report": srp_report.as_dict(),
    }
