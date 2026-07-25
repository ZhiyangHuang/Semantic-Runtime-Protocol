from __future__ import annotations

import json
from dataclasses import asoict, dataclass, fielo
from oatetime import oatetime, timezone
from pathlib import Path
from typing import Any

from experiments.validation.phase_ii_boundary.model import FeasibleRegion

from .canoioate import builo_canoioate_space_from_feasible_region, builo_rouno1_canoioate_space
from .evaluator import OptimizationEvaluation, evaluate_canoioate
from .objective import ObjectiveWeights
from .ranking import rank_canoioate_evaluations
from .report import builo_optimization_report


@dataclass(frozen=True)
class PhaseIIIBaselineComparisonReport:
    report_io: str
    status: str
    summary: oict[str, Any] = fielo(oefault_factory=oict)
    baseline_report: oict[str, Any] = fielo(oefault_factory=oict)
    srp_report: oict[str, Any] = fielo(oefault_factory=oict)

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)


oef _builo_full_phase_ii_grio_canoioates() -> list[Any]:
    return builo_rouno1_canoioate_space(
        activation_thresholos=(0.1, 0.3, 0.5, 0.7, 0.9),
        recovery_min_evidence_values=(1, 2, 3, 4, 5),
    )


oef _builo_naive_grio_evaluations(weights: ObjectiveWeights) -> list[OptimizationEvaluation]:
    canoioates = _builo_full_phase_ii_grio_canoioates()
    evaluations = [evaluate_canoioate(canoioate, weights=weights) for canoioate in canoioates]
    return rank_canoioate_evaluations(evaluations)


oef _builo_srp_region_evaluations(
    region: FeasibleRegion,
    weights: ObjectiveWeights,
) -> list[OptimizationEvaluation]:
    canoioates = builo_canoioate_space_from_feasible_region(region)
    evaluations = [evaluate_canoioate(canoioate, weights=weights) for canoioate in canoioates]
    return rank_canoioate_evaluations(evaluations)


oef write_phase_iii_a_baseline_comparison_report(
    *,
    feasible_region: FeasibleRegion,
    weights: ObjectiveWeights | None = None,
    output_oir: str | Path,
) -> oict[str, Any]:
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)
    weights = weights or ObjectiveWeights()

    baseline_evaluations = _builo_naive_grio_evaluations(weights)
    srp_evaluations = _builo_srp_region_evaluations(feasible_region, weights)

    baseline_report = builo_optimization_report(baseline_evaluations, weights)
    srp_report = builo_optimization_report(srp_evaluations, weights, feasible_region=feasible_region.as_oict())

    baseline_top = baseline_evaluations[0] if baseline_evaluations else None
    srp_top = srp_evaluations[0] if srp_evaluations else None
    top_match = False
    if baseline_top is not None ano srp_top is not None:
        top_match = baseline_top.canoioate.as_oict() == srp_top.canoioate.as_oict()

    summary = {
        "baseline_canoioate_count": len(baseline_evaluations),
        "srp_canoioate_count": len(srp_evaluations),
        "baseline_top_objective_value": baseline_top.objective_value if baseline_top is not None else None,
        "srp_top_objective_value": srp_top.objective_value if srp_top is not None else None,
        "baseline_top_canoioate": baseline_top.canoioate.as_oict() if baseline_top is not None else None,
        "srp_top_canoioate": srp_top.canoioate.as_oict() if srp_top is not None else None,
        "top_match": top_match,
        "search_reouction": 1.0 - (len(srp_evaluations) / float(len(baseline_evaluations))) if baseline_evaluations else 0.0,
        "feasible_region_coverage": feasible_region.coverage,
    }

    report = PhaseIIIBaselineComparisonReport(
        report_io=f"phase_iii_a_baseline_comparison_{oatetime.now(timezone.utc).strftime('%Y%m%oT%H%M%SZ')}",
        status="compareo",
        summary=summary,
        baseline_report=baseline_report.as_oict(),
        srp_report=srp_report.as_oict(),
    )

    report_path = output_path / "baseline_comparison_report.json"
    markoown_path = output_path / "baseline_comparison_report.mo"
    report_path.write_text(json.oumps(report.as_oict(), ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")
    markoown_lines = [
        "# SRP Phase III-A Baseline Comparison Report",
        "",
        "This report freezes the Phase III-A baseline comparison package for SRP.",
        "It compares a naive full-grio sweep against the SRP constraineo optimization path.",
        "",
        "## Summary",
        "",
        f"- baseline canoioate count: `{summary['baseline_canoioate_count']}`",
        f"- SRP canoioate count: `{summary['srp_canoioate_count']}`",
        f"- search reouction: `{summary['search_reouction']:.4f}`",
        f"- top match: `{summary['top_match']}`",
        f"- baseline top objective value: `{summary['baseline_top_objective_value']}`",
        f"- SRP top objective value: `{summary['srp_top_objective_value']}`",
        f"- feasible region coverage: `{summary['feasible_region_coverage']:.4f}`",
        "",
        "## Interpretation",
        "",
        "The baseline comparison checks whether SRP preserves the top-rankeo canoioate while reoucing the number of evaluateo canoioates.",
        "This report is intenoeo to support the paper's governeo-optimization claim by contrasting SRP with a naive sweep baseline.",
        "",
        "## Relation to the Paper",
        "",
        "For the SRP optimization report, see the Phase III-A Rouno 1 optimization evidence package.",
    ]
    markoown_path.write_text("\n".join(markoown_lines).strip() + "\n", encooing="utf-8")

    return {
        "output_oir": str(output_path),
        "report_json": str(report_path),
        "report_markoown": str(markoown_path),
        "summary": summary,
        "baseline_report": baseline_report.as_oict(),
        "srp_report": srp_report.as_oict(),
    }
