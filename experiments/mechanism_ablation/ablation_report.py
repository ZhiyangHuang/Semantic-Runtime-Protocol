from __future__ import annotations

from typing import Any, Dict, List


def _fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}".rstrip("0").rstrip(".")
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _table(headers: List[str], rows: List[List[Any]]) -> List[str]:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(_fmt(cell) for cell in row) + " |")
    return lines


def render_mechanism_ablation_markdown(summary: Dict[str, Any]) -> str:
    lines: List[str] = ["# SRP Mechanism Attribution / Ablation", ""]
    lines.append(f"- `records`: {_fmt(summary.get('records'))}")
    lines.append("")
    comparison = summary.get("comparison") or {}
    if comparison:
        lines.append("## Baseline vs Ablated")
        rows = []
        for benchmark_name in sorted(comparison.keys()):
            item = comparison.get(benchmark_name) or {}
            rows.append(
                [
                    benchmark_name,
                    item.get("allocation_boundary_shift", {}).get("budget_shift"),
                    item.get("dependency_boundary_shift", {}).get("budget_shift"),
                    item.get("dependency_f1_boundary_shift", {}).get("budget_shift"),
                    item.get("validation_boundary_shift", {}).get("budget_shift"),
                ]
            )
        lines.extend(_table(["Benchmark", "Allocation Shift", "Dependency Shift", "Dependency-F1 Shift", "Validation Shift"], rows))
        lines.append("")
    for variant_name in sorted((summary.get("variants") or {}).keys()):
        variant = (summary.get("variants") or {}).get(variant_name) or {}
        lines.append(f"## {variant_name}")
        lines.append(f"- `records`: {_fmt(variant.get('records'))}")
        lines.append("")
        for benchmark_name in sorted((variant.get("benchmarks") or {}).keys()):
            benchmark = (variant.get("benchmarks") or {}).get(benchmark_name) or {}
            lines.append(f"### {benchmark_name}")
            lines.append(f"- `semantic_unit_count`: {_fmt(benchmark.get('semantic_unit_count'))}")
            lines.append(f"- `baseline_budget`: {_fmt(benchmark.get('baseline_budget'))}")
            lines.append(f"- `allocation_boundary`: {_fmt((benchmark.get('allocation_boundary') or {}).get('boundary_upper_budget'))} -> {_fmt((benchmark.get('allocation_boundary') or {}).get('boundary_lower_budget'))}")
            lines.append(f"- `dependency_boundary`: {_fmt((benchmark.get('dependency_boundary') or {}).get('boundary_upper_budget'))} -> {_fmt((benchmark.get('dependency_boundary') or {}).get('boundary_lower_budget'))}")
            lines.append(f"- `dependency_f1_boundary`: {_fmt((benchmark.get('dependency_f1_boundary') or {}).get('boundary_upper_budget'))} -> {_fmt((benchmark.get('dependency_f1_boundary') or {}).get('boundary_lower_budget'))}")
            lines.append(f"- `validation_boundary`: {_fmt((benchmark.get('validation_boundary') or {}).get('boundary_upper_budget'))} -> {_fmt((benchmark.get('validation_boundary') or {}).get('boundary_lower_budget'))}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"

