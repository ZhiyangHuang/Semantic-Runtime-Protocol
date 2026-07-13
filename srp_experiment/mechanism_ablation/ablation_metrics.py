from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, List, Sequence

from srp_experiment.policy_boundary_analysis import _boundary_gap, _derive_boundary_from_rows
from .variants.common import _object_id


def _mean(values: Iterable[float | int | None]) -> float | None:
    cleaned = [float(value) for value in values if value is not None]
    if not cleaned:
        return None
    return sum(cleaned) / len(cleaned)


def _allocation_metric_value(record: Dict[str, Any], metric_name: str) -> float | None:
    allocation = record.get("state_allocation_result") or {}
    metrics = allocation.get("metrics") or {}
    value = metrics.get(metric_name)
    return None if value is None else float(value)


def _metric_value(record: Dict[str, Any], metric_name: str) -> float | None:
    value = record.get(metric_name)
    if value is not None:
        return float(value)
    allocation = record.get("state_allocation_result") or {}
    metrics = allocation.get("metrics") or {}
    if metric_name in metrics and metrics.get(metric_name) is not None:
        return float(metrics.get(metric_name))
    return None


def _record_object_importance(record: Dict[str, Any], item: Dict[str, Any]) -> float | None:
    object_id = _object_id(item)
    runtime_metadata = record.get("runtime_metadata_snapshot") or {}
    if isinstance(runtime_metadata, dict):
        metadata = runtime_metadata.get(object_id)
        if isinstance(metadata, dict) and metadata.get("importance") is not None:
            return float(metadata.get("importance"))
    if item.get("importance") is not None:
        return float(item.get("importance"))
    return None


def _normalize_signature_value(value: object) -> str:
    text = str(value or "").strip().lower()
    while "  " in text:
        text = text.replace("  ", " ")
    return text.rstrip(".")


def _selection_signature(item: Dict[str, Any]) -> str:
    evidence_pointer = str(item.get("evidence_pointer") or "").strip()
    if evidence_pointer:
        return evidence_pointer
    object_type = str(item.get("type") or "").strip().lower()
    value = _normalize_signature_value(item.get("value"))
    return f"{object_type}|{value}"


def _inventory_object_lookup(record: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    allocation = record.get("state_allocation_result") or {}
    active_state = allocation.get("active_state") or {}
    inventory = active_state.get("semantic_object_inventory") or record.get("semantic_object_inventory") or {}
    objects = inventory.get("objects") or []
    lookup: Dict[str, Dict[str, Any]] = {}
    for item in objects:
        if not isinstance(item, dict):
            continue
        key = f"{str(item.get('type') or '').strip().lower()}|{_normalize_signature_value(item.get('value'))}"
        lookup[key] = item
    return lookup


def _selected_importance_mean(record: Dict[str, Any], selection_key: str) -> float | None:
    allocation = record.get("state_allocation_result") or {}
    items = allocation.get(selection_key) or []
    lookup = _inventory_object_lookup(record)
    values: List[float] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        key = f"{str(item.get('type') or '').strip().lower()}|{_normalize_signature_value(item.get('value'))}"
        inventory_item = lookup.get(key)
        if not inventory_item:
            continue
        importance = _record_object_importance(record, inventory_item)
        if importance is not None:
            values.append(float(importance))
    return _mean(values)


def _important_capture_rate(record: Dict[str, Any], selection_key: str) -> float | None:
    allocation = record.get("state_allocation_result") or {}
    items = allocation.get(selection_key) or []
    important_lookup = {
        f"{str(item.get('type') or '').strip().lower()}|{_normalize_signature_value(item.get('value'))}"
        for item in ((allocation.get("active_state") or {}).get("important_objects") or [])
        if isinstance(item, dict)
    }
    if not items:
        return None
    selected = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        key = f"{str(item.get('type') or '').strip().lower()}|{_normalize_signature_value(item.get('value'))}"
        if key in important_lookup:
            selected += 1
    return selected / len(items)


def _selection_overlap_diagnostics(
    baseline_record: Dict[str, Any],
    ablated_record: Dict[str, Any],
) -> Dict[str, Any]:
    baseline_items = ((baseline_record.get("state_allocation_result") or {}).get("active_objects") or [])
    ablated_items = ((ablated_record.get("state_allocation_result") or {}).get("active_objects") or [])
    baseline_signatures = [_selection_signature(item) for item in baseline_items if isinstance(item, dict)]
    ablated_signatures = [_selection_signature(item) for item in ablated_items if isinstance(item, dict)]
    baseline_set = set(baseline_signatures)
    ablated_set = set(ablated_signatures)
    intersection = baseline_set & ablated_set
    union = baseline_set | ablated_set

    baseline_rank = {signature: index for index, signature in enumerate(baseline_signatures)}
    ablated_rank = {signature: index for index, signature in enumerate(ablated_signatures)}
    rank_shifts = [abs(baseline_rank[signature] - ablated_rank[signature]) for signature in intersection if signature in baseline_rank and signature in ablated_rank]

    return {
        "selection_overlap_jaccard": (len(intersection) / len(union)) if union else None,
        "selection_rank_shift_mean": _mean(rank_shifts),
        "baseline_selected_importance_mean": _selected_importance_mean(baseline_record, "active_objects"),
        "ablated_selected_importance_mean": _selected_importance_mean(ablated_record, "active_objects"),
        "selected_importance_mean_delta": _delta(
            _selected_importance_mean(baseline_record, "active_objects"),
            _selected_importance_mean(ablated_record, "active_objects"),
        ),
        "baseline_active_important_capture_rate": _important_capture_rate(baseline_record, "active_objects"),
        "ablated_active_important_capture_rate": _important_capture_rate(ablated_record, "active_objects"),
        "active_important_capture_rate_delta": _delta(
            _important_capture_rate(baseline_record, "active_objects"),
            _important_capture_rate(ablated_record, "active_objects"),
        ),
    }


def _importance_mean_for_items(records: Sequence[Dict[str, Any]], key: str) -> float | None:
    values: List[float | int | None] = []
    for record in records:
        allocation = record.get("state_allocation_result") or {}
        items = allocation.get(key) or []
        for item in items:
            if isinstance(item, dict):
                values.append(_record_object_importance(record, item))
    return _mean(values)


def summarize_variant_records(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "records": len(records),
        "benchmarks": {},
    }
    benchmark_names = sorted({str(record.get("mechanism_ablation_suite") or "unknown") for record in records})
    for benchmark_name in benchmark_names:
        benchmark_records = [record for record in records if str(record.get("mechanism_ablation_suite") or "unknown") == benchmark_name]
        if not benchmark_records:
            continue
        pressure_indices = [record.get("mechanism_ablation_pressure_index") for record in benchmark_records if record.get("mechanism_ablation_pressure_index") is not None]
        semantic_unit_count = next(
            (
                int((record.get("mechanism_ablation") or {}).get("semantic_unit_count"))
                for record in benchmark_records
                if (record.get("mechanism_ablation") or {}).get("semantic_unit_count") is not None
            ),
            None,
        )
        by_budget: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        for record in benchmark_records:
            budget = int(record.get("mechanism_ablation_budget") or 0)
            by_budget[budget].append(record)

        budget_rows: List[Dict[str, Any]] = []
        for budget in sorted(by_budget):
            budget_records = by_budget[budget]
            allocation_metrics = {
                "active_object_count": _mean(_allocation_metric_value(record, "active_object_count") for record in budget_records),
                "active_state_efficiency": _mean(_allocation_metric_value(record, "active_state_efficiency") for record in budget_records),
                "active_retention_ratio": _mean(_allocation_metric_value(record, "active_retention_ratio") for record in budget_records),
                "latent_preservation": _mean(_allocation_metric_value(record, "latent_preservation") for record in budget_records),
                "hallucination_isolation": _mean(_allocation_metric_value(record, "hallucination_isolation") for record in budget_records),
            }
            metrics = {
                "validation_coverage": _mean(_metric_value(record, "validation_coverage") for record in budget_records),
                "dependency_coverage": _mean(_metric_value(record, "dependency_coverage") for record in budget_records),
                "dependency_precision": _mean(_metric_value(record, "dependency_precision") for record in budget_records),
                "dependency_f1": _mean(_metric_value(record, "dependency_f1") for record in budget_records),
                "validation_score": _mean(_metric_value(record, "validation_score") for record in budget_records),
                "graph_integrity_score": _mean(_metric_value(record, "graph_integrity_score") for record in budget_records),
                "object_retention": _mean(_metric_value(record, "object_retention") for record in budget_records),
                "weighted_object_retention": _mean(_metric_value(record, "weighted_object_retention") for record in budget_records),
                "token_overhead": _mean(_metric_value(record, "token_overhead") for record in budget_records),
            }
            metrics.update(allocation_metrics)
            row = {
                "budget": budget,
                "records": len(budget_records),
                "semantic_unit_count": semantic_unit_count,
                "semantic_pressure_index": _mean(
                    float((record.get("mechanism_ablation") or {}).get("semantic_pressure_index"))
                    for record in budget_records
                    if (record.get("mechanism_ablation") or {}).get("semantic_pressure_index") is not None
                ),
                "allocation_metrics": allocation_metrics,
                "metrics": metrics,
            }
            budget_rows.append(row)

        baseline_metrics = budget_rows[-1]["metrics"] if budget_rows else {}
        for row in budget_rows:
            metrics = row["metrics"]
            row["deltas"] = {
                "validation_coverage": _delta(metrics.get("validation_coverage"), baseline_metrics.get("validation_coverage")),
                "dependency_coverage": _delta(metrics.get("dependency_coverage"), baseline_metrics.get("dependency_coverage")),
                "dependency_f1": _delta(metrics.get("dependency_f1"), baseline_metrics.get("dependency_f1")),
                "graph_integrity_score": _delta(metrics.get("graph_integrity_score"), baseline_metrics.get("graph_integrity_score")),
                "object_retention": _delta(metrics.get("object_retention"), baseline_metrics.get("object_retention")),
                "weighted_object_retention": _delta(metrics.get("weighted_object_retention"), baseline_metrics.get("weighted_object_retention")),
            }

        allocation_boundary = _derive_boundary_from_rows(
            budget_rows,
            metric_names=["active_retention_ratio", "active_state_efficiency", "active_object_count", "latent_preservation", "hallucination_isolation"],
        )
        dependency_boundary = _derive_boundary_from_rows(
            budget_rows,
            metric_names=["dependency_coverage", "dependency_precision", "dependency_f1"],
        )
        dependency_f1_boundary = _derive_boundary_from_rows(
            budget_rows,
            metric_names=["dependency_f1"],
            mode="adjacent",
        )
        validation_boundary = _derive_boundary_from_rows(
            budget_rows,
            metric_names=[
                "validation_score",
                "validation_coverage",
                "graph_integrity_score",
                "object_retention",
                "weighted_object_retention",
            ],
        )
        importance_activation = {
            "active_importance_mean": _importance_mean_for_items(benchmark_records, "active_objects"),
            "latent_importance_mean": _importance_mean_for_items(benchmark_records, "latent_objects"),
            "discard_importance_mean": _importance_mean_for_items(benchmark_records, "discard_objects"),
        }
        importance_activation["active_vs_discard_gap"] = _delta(
            importance_activation.get("active_importance_mean"),
            importance_activation.get("discard_importance_mean"),
        )
        importance_activation["active_vs_latent_gap"] = _delta(
            importance_activation.get("active_importance_mean"),
            importance_activation.get("latent_importance_mean"),
        )
        boundary_gap = {
            "allocation_to_dependency": _boundary_gap(allocation_boundary, dependency_boundary),
            "dependency_to_dependency_f1": _boundary_gap(dependency_boundary, dependency_f1_boundary),
            "dependency_f1_to_validation": _boundary_gap(dependency_f1_boundary, validation_boundary),
            "allocation_to_validation": _boundary_gap(allocation_boundary, validation_boundary),
        }
        summary["benchmarks"][benchmark_name] = {
            "records": len(benchmark_records),
            "semantic_unit_count": semantic_unit_count,
            "semantic_pressure_index_mean": _mean(float(value) for value in pressure_indices if value is not None) if pressure_indices else None,
            "budgets": budget_rows,
            "allocation_boundary": allocation_boundary,
            "dependency_boundary": dependency_boundary,
            "dependency_f1_boundary": dependency_f1_boundary,
            "validation_boundary": validation_boundary,
            "boundary_gap": boundary_gap,
            "importance_activation": importance_activation,
            "boundary": allocation_boundary,
            "baseline_budget": allocation_boundary.get("baseline_budget"),
        }
    return summary


def compare_variant_summaries(baseline_summary: Dict[str, Any], ablated_summary: Dict[str, Any]) -> Dict[str, Any]:
    comparison: Dict[str, Any] = {}
    benchmark_names = sorted(set(baseline_summary.get("benchmarks", {}).keys()) | set(ablated_summary.get("benchmarks", {}).keys()))
    for benchmark_name in benchmark_names:
        baseline = baseline_summary.get("benchmarks", {}).get(benchmark_name) or {}
        ablated = ablated_summary.get("benchmarks", {}).get(benchmark_name) or {}
        comparison[benchmark_name] = {
            "allocation_boundary_shift": _boundary_shift(baseline.get("allocation_boundary"), ablated.get("allocation_boundary")),
            "dependency_boundary_shift": _boundary_shift(baseline.get("dependency_boundary"), ablated.get("dependency_boundary")),
            "dependency_f1_boundary_shift": _boundary_shift(baseline.get("dependency_f1_boundary"), ablated.get("dependency_f1_boundary")),
            "validation_boundary_shift": _boundary_shift(baseline.get("validation_boundary"), ablated.get("validation_boundary")),
            "boundary_gap_shift": {
                "allocation_to_dependency": _gap_shift(baseline.get("boundary_gap"), ablated.get("boundary_gap"), "allocation_to_dependency"),
                "dependency_to_dependency_f1": _gap_shift(baseline.get("boundary_gap"), ablated.get("boundary_gap"), "dependency_to_dependency_f1"),
                "dependency_f1_to_validation": _gap_shift(baseline.get("boundary_gap"), ablated.get("boundary_gap"), "dependency_f1_to_validation"),
                "allocation_to_validation": _gap_shift(baseline.get("boundary_gap"), ablated.get("boundary_gap"), "allocation_to_validation"),
            },
            "budget_delta_table": _budget_delta_table(baseline, ablated),
        }
    return comparison


def _delta(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return left - right


def _boundary_midpoint(boundary: Dict[str, Any] | None) -> float | None:
    if not boundary:
        return None
    upper = boundary.get("boundary_upper_budget")
    lower = boundary.get("boundary_lower_budget")
    if upper is None or lower is None:
        return None
    return (float(upper) + float(lower)) / 2.0


def _boundary_shift(left_boundary: Dict[str, Any] | None, right_boundary: Dict[str, Any] | None) -> Dict[str, Any]:
    left_midpoint = _boundary_midpoint(left_boundary)
    right_midpoint = _boundary_midpoint(right_boundary)
    return {
        "baseline_midpoint_budget": left_midpoint,
        "ablated_midpoint_budget": right_midpoint,
        "budget_shift": None if left_midpoint is None or right_midpoint is None else left_midpoint - right_midpoint,
        "baseline_transition_detected": bool(left_boundary and left_boundary.get("transition_detected")),
        "ablated_transition_detected": bool(right_boundary and right_boundary.get("transition_detected")),
    }


def _gap_shift(left_gap: Dict[str, Any] | None, right_gap: Dict[str, Any] | None, key: str) -> Dict[str, Any]:
    left = (left_gap or {}).get(key) or {}
    right = (right_gap or {}).get(key) or {}
    left_budget = left.get("mean_budget_gap")
    right_budget = right.get("mean_budget_gap")
    left_pressure = left.get("mean_pressure_gap")
    right_pressure = right.get("mean_pressure_gap")
    return {
        "baseline_budget_gap": left_budget,
        "ablated_budget_gap": right_budget,
        "budget_gap_shift": _delta(left_budget, right_budget),
        "baseline_pressure_gap": left_pressure,
        "ablated_pressure_gap": right_pressure,
        "pressure_gap_shift": _delta(left_pressure, right_pressure),
    }


def _budget_delta_table(baseline: Dict[str, Any], ablated: Dict[str, Any]) -> List[Dict[str, Any]]:
    baseline_rows = {int(row.get("budget") or 0): row for row in baseline.get("budgets", [])}
    ablated_rows = {int(row.get("budget") or 0): row for row in ablated.get("budgets", [])}
    budgets = sorted(set(baseline_rows.keys()) | set(ablated_rows.keys()))
    rows: List[Dict[str, Any]] = []
    for budget in budgets:
        base_metrics = (baseline_rows.get(budget) or {}).get("metrics") or {}
        ablated_metrics = (ablated_rows.get(budget) or {}).get("metrics") or {}
        rows.append(
            {
                "budget": budget,
                "baseline_validation_score": base_metrics.get("validation_score"),
                "ablated_validation_score": ablated_metrics.get("validation_score"),
                "delta_validation_score": _delta(base_metrics.get("validation_score"), ablated_metrics.get("validation_score")),
                "baseline_dependency_coverage": base_metrics.get("dependency_coverage"),
                "ablated_dependency_coverage": ablated_metrics.get("dependency_coverage"),
                "delta_dependency_coverage": _delta(base_metrics.get("dependency_coverage"), ablated_metrics.get("dependency_coverage")),
                "baseline_dependency_f1": base_metrics.get("dependency_f1"),
                "ablated_dependency_f1": ablated_metrics.get("dependency_f1"),
                "delta_dependency_f1": _delta(base_metrics.get("dependency_f1"), ablated_metrics.get("dependency_f1")),
                "baseline_active_retention_ratio": base_metrics.get("active_retention_ratio"),
                "ablated_active_retention_ratio": ablated_metrics.get("active_retention_ratio"),
                "delta_active_retention_ratio": _delta(base_metrics.get("active_retention_ratio"), ablated_metrics.get("active_retention_ratio")),
            }
        )
    return rows


def summarize_mechanism_ablation_records(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "records": len(records),
        "variants": {},
        "comparisons": {},
        "comparison": {},
    }
    variant_names = sorted({str(record.get("mechanism_ablation_variant") or "unknown") for record in records})
    for variant_name in variant_names:
        variant_records = [record for record in records if str(record.get("mechanism_ablation_variant") or "unknown") == variant_name]
        summary["variants"][variant_name] = summarize_variant_records(variant_records)

    if "baseline" in summary["variants"]:
        baseline_records = [record for record in records if str(record.get("mechanism_ablation_variant") or "unknown") == "baseline"]
        from .ablation_comparison import build_mechanism_comparison

        for variant_name, variant_summary in summary["variants"].items():
            if variant_name == "baseline":
                continue
            summary["comparisons"][variant_name] = build_mechanism_comparison(
                summary["variants"]["baseline"],
                variant_summary,
            )
            variant_records = [record for record in records if str(record.get("mechanism_ablation_variant") or "unknown") == variant_name]
            pairwise_summary: Dict[str, Dict[str, List[Dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
            baseline_index: Dict[tuple[str, int, int, int], Dict[str, Any]] = {}
            variant_index: Dict[tuple[str, int, int, int], Dict[str, Any]] = {}
            for record in baseline_records:
                key = (
                    str(record.get("mechanism_ablation_suite") or "unknown"),
                    int(record.get("mechanism_ablation_budget") or 0),
                    int(record.get("mechanism_ablation_seed") or 0),
                    int(record.get("mechanism_ablation_cycles") or 0),
                )
                baseline_index[key] = record
            for record in variant_records:
                key = (
                    str(record.get("mechanism_ablation_suite") or "unknown"),
                    int(record.get("mechanism_ablation_budget") or 0),
                    int(record.get("mechanism_ablation_seed") or 0),
                    int(record.get("mechanism_ablation_cycles") or 0),
                )
                variant_index[key] = record

            for key in sorted(set(baseline_index.keys()) & set(variant_index.keys())):
                benchmark_name = key[0]
                diag = _selection_overlap_diagnostics(baseline_index[key], variant_index[key])
                pairwise_summary[benchmark_name]["records"].append(diag)

            for benchmark_name, buckets in pairwise_summary.items():
                diagnostics = buckets.get("records") or []
                summary["comparisons"][variant_name].setdefault(benchmark_name, {})
                summary["comparisons"][variant_name][benchmark_name]["selection_diagnostics"] = {
                    "selection_overlap_jaccard": _mean(item.get("selection_overlap_jaccard") for item in diagnostics),
                    "selection_rank_shift_mean": _mean(item.get("selection_rank_shift_mean") for item in diagnostics),
                    "baseline_selected_importance_mean": _mean(item.get("baseline_selected_importance_mean") for item in diagnostics),
                    "ablated_selected_importance_mean": _mean(item.get("ablated_selected_importance_mean") for item in diagnostics),
                    "selected_importance_mean_delta": _mean(item.get("selected_importance_mean_delta") for item in diagnostics),
                    "baseline_active_important_capture_rate": _mean(item.get("baseline_active_important_capture_rate") for item in diagnostics),
                    "ablated_active_important_capture_rate": _mean(item.get("ablated_active_important_capture_rate") for item in diagnostics),
                    "active_important_capture_rate_delta": _mean(item.get("active_important_capture_rate_delta") for item in diagnostics),
                }
        if summary["comparisons"]:
            summary["comparison"] = summary["comparisons"].get("remove_dependency_retention") or next(
                iter(summary["comparisons"].values())
            )
    return summary
