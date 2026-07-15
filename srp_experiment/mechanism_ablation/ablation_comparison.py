from __future__ import annotations

from typing import Any, Dict, List

from .ablation_metrics import compare_variant_summaries


def _abs_or_none(value: float | None) -> float | None:
    if value is None:
        return None
    return abs(float(value))


def _sum_abs(values: List[float | None]) -> float | None:
    cleaned = [abs(float(value)) for value in values if value is not None]
    if not cleaned:
        return None
    return sum(cleaned)


def _attribution_score(entry: Dict[str, Any]) -> float | None:
    boundary_shift = entry.get("boundary_shift") or {}
    metric_delta = entry.get("metric_delta_summary") or {}
    target_effect = _sum_abs(
        [
            boundary_shift.get("dependency_boundary_shift", {}).get("budget_shift"),
            boundary_shift.get("dependency_f1_boundary_shift", {}).get("budget_shift"),
        ]
    )
    if target_effect is None:
        target_effect = _sum_abs(
            [
                metric_delta.get("dependency_coverage"),
                metric_delta.get("dependency_f1"),
            ]
        )
    collateral_effect = _sum_abs(
        [
            boundary_shift.get("allocation_boundary_shift", {}).get("budget_shift"),
            boundary_shift.get("validation_boundary_shift", {}).get("budget_shift"),
        ]
    )
    if collateral_effect is None:
        collateral_effect = _sum_abs(
            [
                metric_delta.get("active_retention_ratio"),
                metric_delta.get("validation_score"),
            ]
        )
    if target_effect is None and collateral_effect is None:
        return None
    target_effect = target_effect or 0.0
    collateral_effect = collateral_effect or 0.0
    denominator = target_effect + collateral_effect
    if denominator <= 0:
        return None
    return target_effect / denominator


def build_mechanism_comparison(baseline_summary: Dict[str, Any], ablated_summary: Dict[str, Any]) -> Dict[str, Any]:
    comparison = compare_variant_summaries(baseline_summary, ablated_summary)
    enriched: Dict[str, Any] = {}
    for benchmark_name, entry in comparison.items():
        budgets = entry.get("budget_delta_table") or []
        metric_delta_summary = {
            "validation_score": _sum_delta(budgets, "delta_validation_score"),
            "dependency_coverage": _sum_delta(budgets, "delta_dependency_coverage"),
            "dependency_f1": _sum_delta(budgets, "delta_dependency_f1"),
            "active_retention_ratio": _sum_delta(budgets, "delta_active_retention_ratio"),
        }
        enriched[benchmark_name] = {
            **entry,
            "metric_delta_summary": metric_delta_summary,
            "target_effect": _sum_abs(
                [
                    entry.get("dependency_boundary_shift", {}).get("budget_shift"),
                    entry.get("dependency_f1_boundary_shift", {}).get("budget_shift"),
                ]
            ),
            "collateral_effect": _sum_abs(
                [
                    entry.get("allocation_boundary_shift", {}).get("budget_shift"),
                    entry.get("validation_boundary_shift", {}).get("budget_shift"),
                ]
            ),
        }
        enriched[benchmark_name]["attribution_score"] = _attribution_score(enriched[benchmark_name])
    return enriched


def _sum_delta(rows: List[Dict[str, Any]], key: str) -> float | None:
    values = [row.get(key) for row in rows if row.get(key) is not None]
    if not values:
        return None
    return sum(float(value) for value in values) / len(values)


def render_mechanism_comparison_markdown(summary: Dict[str, Any]) -> str:
    lines: List[str] = ["# SRP Mechanism Attribution / Comparison", ""]
    lines.append(f"- `records`: {summary.get('records')}")
    lines.append("")
    comparisons = summary.get("comparisons") or {}
    if not comparisons and summary.get("comparison"):
        comparisons = {"remove_dependency_retention": summary.get("comparison") or {}}

    for variant_name in sorted(comparisons.keys()):
        lines.append(f"## Baseline vs {variant_name}")
        comparison = comparisons.get(variant_name) or {}
        for benchmark_name in sorted(comparison.keys()):
            entry = comparison[benchmark_name] or {}
            lines.append(f"### {benchmark_name}")
            lines.append("| Boundary | Baseline | Ablated | Delta |")
            lines.append("| --- | --- | --- | --- |")
            for key, label in [
                ("allocation_boundary_shift", "allocation"),
                ("dependency_boundary_shift", "dependency"),
                ("dependency_f1_boundary_shift", "dependency_f1"),
                ("validation_boundary_shift", "validation"),
            ]:
                shift = entry.get(key) or {}
                lines.append(
                    f"| {label} | {_fmt(shift.get('baseline_midpoint_budget'))} | {_fmt(shift.get('ablated_midpoint_budget'))} | {_fmt(shift.get('budget_shift'))} |"
                )
            lines.append("")
            lines.append("| Metric | Mean Delta |")
            lines.append("| --- | --- |")
            for metric_name, delta in (entry.get("metric_delta_summary") or {}).items():
                lines.append(f"| {metric_name} | {_fmt(delta)} |")
            lines.append("")
            lines.append(f"- `target_effect`: {_fmt(entry.get('target_effect'))}")
            lines.append(f"- `collateral_effect`: {_fmt(entry.get('collateral_effect'))}")
            lines.append(f"- `attribution_score`: {_fmt(entry.get('attribution_score'))}")
            lines.append("")
            lines.append("| Importance Activation | Value |")
            lines.append("| --- | --- |")
            baseline_variant = (summary.get("variants") or {}).get("baseline") or {}
            baseline_benchmark = (baseline_variant.get("benchmarks") or {}).get(benchmark_name) or {}
            ablated_variant = None
            for name, variant_summary in (summary.get("variants") or {}).items():
                if name == "baseline":
                    continue
                if benchmark_name in (variant_summary.get("benchmarks") or {}):
                    ablated_variant = variant_summary
                    break
            ablated_benchmark = (ablated_variant.get("benchmarks") or {}).get(benchmark_name) if ablated_variant else {}
            for label, value in [
                ("baseline_active_importance_mean", (baseline_benchmark.get("importance_activation") or {}).get("active_importance_mean")),
                ("baseline_discard_importance_mean", (baseline_benchmark.get("importance_activation") or {}).get("discard_importance_mean")),
                ("ablated_active_importance_mean", (ablated_benchmark.get("importance_activation") or {}).get("active_importance_mean")),
                ("ablated_discard_importance_mean", (ablated_benchmark.get("importance_activation") or {}).get("discard_importance_mean")),
            ]:
                lines.append(f"| {label} | {_fmt(value)} |")
            selection_diagnostics = entry.get("selection_diagnostics") or {}
            if selection_diagnostics:
                lines.append("")
                lines.append("| Selection Diagnostic | Value |")
                lines.append("| --- | --- |")
                for label, value in [
                    ("selection_overlap_jaccard", selection_diagnostics.get("selection_overlap_jaccard")),
                    ("selection_rank_shift_mean", selection_diagnostics.get("selection_rank_shift_mean")),
                    ("baseline_selected_importance_mean", selection_diagnostics.get("baseline_selected_importance_mean")),
                    ("ablated_selected_importance_mean", selection_diagnostics.get("ablated_selected_importance_mean")),
                    ("selected_importance_mean_delta", selection_diagnostics.get("selected_importance_mean_delta")),
                    ("baseline_active_important_capture_rate", selection_diagnostics.get("baseline_active_important_capture_rate")),
                    ("ablated_active_important_capture_rate", selection_diagnostics.get("ablated_active_important_capture_rate")),
                    ("active_important_capture_rate_delta", selection_diagnostics.get("active_important_capture_rate_delta")),
                ]:
                    lines.append(f"| {label} | {_fmt(value)} |")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}".rstrip("0").rstrip(".")
    return str(value)
