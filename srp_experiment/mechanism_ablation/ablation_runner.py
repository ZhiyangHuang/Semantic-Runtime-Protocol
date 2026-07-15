from __future__ import annotations

import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Sequence

from srp_experiment.policy_boundary_analysis import build_policy_boundary_tasks
from srp_experiment.srp.export import write_records_csv, write_records_markdown
from srp_experiment.srp.pipeline import run_srp

from .ablation_config import MechanismAblationConfig, MechanismAblationVariant, default_mechanism_ablation_variants
from .ablation_comparison import render_mechanism_comparison_markdown
from .ablation_metrics import summarize_mechanism_ablation_records


@contextmanager
def _temporary_env(overrides: Dict[str, str]):
    previous: Dict[str, str | None] = {}
    try:
        for key, value in overrides.items():
            previous[key] = os.environ.get(key)
            os.environ[key] = str(value)
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _default_budgets() -> List[int]:
    return [8, 10, 12, 14, 16, 18, 20, 22, 24]


def _default_seeds() -> List[int]:
    return [0, 1, 2, 3, 4]


def run_mechanism_attribution_ablation(
    *,
    budgets: Sequence[int] | None = None,
    seeds: Sequence[int] | None = None,
    cycles: int = 1,
    variants: Sequence[MechanismAblationVariant] | None = None,
    tasks: Sequence[Any] | None = None,
) -> List[Dict[str, Any]]:
    selected_tasks = list(tasks) if tasks is not None else build_policy_boundary_tasks()
    selected_variants = list(variants) if variants is not None else default_mechanism_ablation_variants()
    selected_budgets = [int(value) for value in (budgets if budgets is not None else _default_budgets())]
    selected_seeds = [int(value) for value in (seeds if seeds is not None else _default_seeds())]
    records: List[Dict[str, Any]] = []

    for variant in selected_variants:
        for task_spec in selected_tasks:
            for budget in selected_budgets:
                for seed in selected_seeds:
                    overrides = {
                        "SRP_ACTIVE_BUDGET": str(budget),
                        "SRP_RANDOM_ALLOCATION_SEED": str(seed),
                        "SRP_EXECUTION_STATE_SOURCE": "active",
                    }
                    overrides.update(variant.env_overrides)
                    with _temporary_env(overrides):
                        task_records = run_srp(task_spec.task, cycles=cycles, client=None)
                    for record in task_records:
                        record["mechanism_ablation"] = {
                            "variant": variant.name,
                            "policy_name": variant.policy_name,
                            "removed_component": variant.removed_component,
                            "description": variant.description,
                            "benchmark": task_spec.name,
                            "budget": budget,
                            "seed": seed,
                            "cycles": cycles,
                            "semantic_unit_count": task_spec.semantic_unit_count,
                            "semantic_pressure_index": round(task_spec.semantic_unit_count / float(budget), 6) if budget else None,
                        }
                        record["mechanism_ablation_variant"] = variant.name
                        record["mechanism_ablation_policy"] = variant.policy_name
                        record["mechanism_ablation_suite"] = task_spec.name
                        record["mechanism_ablation_budget"] = budget
                        record["mechanism_ablation_seed"] = seed
                        record["mechanism_ablation_pressure_index"] = (
                            round(task_spec.semantic_unit_count / float(budget), 6) if budget else None
                        )
                        records.append(record)
    return records


def write_mechanism_attribution_outputs(records: Sequence[Dict[str, Any]], output_dir: str | Path) -> Dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    summary = summarize_mechanism_ablation_records(records)

    outputs: Dict[str, Path] = {}
    for variant_name, variant_summary in (summary.get("variants") or {}).items():
        variant_dir = output_path / variant_name
        variant_dir.mkdir(parents=True, exist_ok=True)
        variant_records = [record for record in records if str(record.get("mechanism_ablation_variant") or "unknown") == variant_name]
        jsonl_path = variant_dir / "records.jsonl"
        csv_path = variant_dir / "records.csv"
        markdown_path = variant_dir / "records.md"
        with jsonl_path.open("w", encoding="utf-8") as handle:
            for record in variant_records:
                handle.write(json.dumps(record, ensure_ascii=False))
                handle.write("\n")
        write_records_csv(variant_records, csv_path)
        write_records_markdown(variant_records, markdown_path)
        outputs[f"{variant_name}_jsonl"] = jsonl_path
        outputs[f"{variant_name}_csv"] = csv_path
        outputs[f"{variant_name}_markdown"] = markdown_path

    comparison_json = output_path / "comparison.json"
    comparison_md = output_path / "comparison.md"
    comparison_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    comparison_md.write_text(render_mechanism_comparison_markdown(summary), encoding="utf-8")
    outputs["comparison_json"] = comparison_json
    outputs["comparison_markdown"] = comparison_md
    return outputs
