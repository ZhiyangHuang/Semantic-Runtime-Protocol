from __future__ import annotations

import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Sequence

from experiments.common.export_support import write_records_csv, write_records_markdown
from experiments.common.policy_boundary_tasks import build_policy_boundary_tasks

from .ablation_config import MechanismAblationConfig, MechanismAblationVariant, default_mechanism_ablation_variants
from .ablation_comparison import render_mechanism_comparison_markdown
from .ablation_metrics import summarize_mechanism_ablation_records
from .common import _object_id, stable_semantic_object_id
from .variants.baseline import MechanismAblationBaselinePolicy
from .variants.remove_dependency_retention import MechanismAblationNoDependencyPolicy
from .variants.remove_importance_weighting import MechanismAblationNoImportancePolicy


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


def _policy_for_variant(variant_name: str):
    if variant_name == "baseline":
        return MechanismAblationBaselinePolicy()
    if variant_name == "remove_importance_weighting":
        return MechanismAblationNoImportancePolicy()
    if variant_name == "remove_dependency_retention":
        return MechanismAblationNoDependencyPolicy()
    return MechanismAblationBaselinePolicy()


def _normalize_object(
    item: Dict[str, Any],
    *,
    default_type: str,
    importance: float,
    evidence_pointer: str,
) -> Dict[str, Any]:
    object_type = str(item.get("type") or default_type).strip() or default_type
    value = str(item.get("value") or item.get("normalized_value") or item.get("surface") or item.get("canonical") or "").strip()
    if not value:
        value = str(item.get("dependency_id") or item.get("keyword") or evidence_pointer).strip()
    object_id = str(item.get("object_id") or item.get("id") or "").strip() or stable_semantic_object_id(object_type, value)
    normalized: Dict[str, Any] = {
        "object_id": object_id,
        "type": object_type,
        "value": value,
        "confidence": float(item.get("confidence", 1.0) or 1.0),
        "importance": float(item.get("importance", importance) or importance),
        "evidence_pointer": str(item.get("evidence_pointer") or evidence_pointer),
    }
    if "dependency_id" in item:
        normalized["dependency_id"] = item.get("dependency_id")
    return normalized


def _build_candidate_pool(task_spec: Any, budget: int, seed: int, variant: MechanismAblationVariant) -> Dict[str, Any]:
    task = getattr(task_spec, "task", None) or {}
    metadata = task.get("metadata") or {}
    expected_keywords = list(task.get("expected_keywords") or [])
    constraints = list((task.get("initial_state") or {}).get("constraints") or [])
    dependency_objects = list(metadata.get("required_dependency_objects") or [])
    important_objects = list(metadata.get("important_objects") or [])

    typed_objects: List[Dict[str, Any]] = []
    inventory_objects: List[Dict[str, Any]] = []
    important_inventory_objects: List[Dict[str, Any]] = []
    runtime_metadata_snapshot: Dict[str, Dict[str, Any]] = {}
    critical_object_ids: List[str] = []

    for index, item in enumerate(dependency_objects, start=1):
        normalized = _normalize_object(item, default_type="anchor", importance=1.0, evidence_pointer=f"dependency:{index}")
        typed_objects.append(normalized)
        inventory_objects.append(dict(normalized))
        runtime_metadata_snapshot[normalized["object_id"]] = {"importance": normalized["importance"], "role": "dependency"}
        critical_object_ids.append(normalized["object_id"])

    for index, item in enumerate(important_objects, start=1):
        normalized = _normalize_object(item, default_type=str(item.get("type") or "fact"), importance=1.0, evidence_pointer=f"important:{index}")
        typed_objects.append(normalized)
        inventory_objects.append(dict(normalized))
        important_inventory_objects.append(dict(normalized))
        runtime_metadata_snapshot[normalized["object_id"]] = {"importance": normalized["importance"], "role": "important"}
        critical_object_ids.append(normalized["object_id"])

    for index, constraint in enumerate(constraints, start=1):
        if not isinstance(constraint, str):
            continue
        item = {
            "type": "constraint",
            "value": constraint,
            "importance": 0.9,
        }
        normalized = _normalize_object(item, default_type="constraint", importance=0.9, evidence_pointer=f"constraint:{index}")
        typed_objects.append(normalized)
        inventory_objects.append(dict(normalized))
        runtime_metadata_snapshot[normalized["object_id"]] = {"importance": normalized["importance"], "role": "constraint"}
        critical_object_ids.append(normalized["object_id"])

    for index, keyword in enumerate(expected_keywords, start=1):
        item = {
            "type": "keyword",
            "value": str(keyword),
            "importance": 0.12,
        }
        normalized = _normalize_object(item, default_type="keyword", importance=0.12, evidence_pointer=f"keyword:{index}")
        typed_objects.append(normalized)
        inventory_objects.append(dict(normalized))
        runtime_metadata_snapshot[normalized["object_id"]] = {"importance": normalized["importance"], "role": "keyword"}

    rng = os.getenv("SRP_RANDOM_ALLOCATION_SEED", "0")
    noise_seed = f"{task.get('id', 'task')}:{variant.name}:{seed}:{budget}:{rng}"
    for index in range(6):
        noise_label = f"{noise_seed}:noise:{index}"
        item = {
            "type": "noise",
            "value": noise_label,
            "importance": 0.01,
        }
        normalized = _normalize_object(item, default_type="noise", importance=0.01, evidence_pointer=f"noise:{index}")
        typed_objects.append(normalized)
        runtime_metadata_snapshot[normalized["object_id"]] = {"importance": normalized["importance"], "role": "noise"}

    if not typed_objects:
        fallback = _normalize_object(
            {"type": "fact", "value": task.get("id", "task"), "importance": 1.0},
            default_type="fact",
            importance=1.0,
            evidence_pointer="fallback:1",
        )
        typed_objects.append(fallback)
        inventory_objects.append(dict(fallback))
        runtime_metadata_snapshot[fallback["object_id"]] = {"importance": fallback["importance"], "role": "fallback"}
        critical_object_ids.append(fallback["object_id"])

    recovered_state_package = {
        "schema_version": "structured_state_package.v1",
        "typed_representation": {"objects": typed_objects},
        "semantic_object_inventory": {
            "objects": inventory_objects,
            "important_objects": important_inventory_objects or [dict(item) for item in inventory_objects[: min(4, len(inventory_objects))]],
        },
        "runtime_metadata_snapshot": runtime_metadata_snapshot,
        "source_task_id": task.get("id"),
        "source_task_name": getattr(task_spec, "name", task.get("id", "mechanism_ablation")),
        "allocation_budget": budget,
        "allocation_seed": seed,
    }
    task_context = {
        "task": task,
        "task_spec_name": getattr(task_spec, "name", task.get("id", "mechanism_ablation")),
        "recovered_state_package": recovered_state_package,
        "required_dependency_objects": dependency_objects,
        "critical_object_ids": critical_object_ids,
        "validation": {
            "coverage_score": min(1.0, len(critical_object_ids) / max(1, len(typed_objects))),
            "passed": True,
        },
        "runtime_metadata_snapshot": runtime_metadata_snapshot,
        "semantic_object_inventory": recovered_state_package["semantic_object_inventory"],
    }
    return {
        "reconstructed_state": recovered_state_package,
        "task_context": task_context,
        "recovered_state_package": recovered_state_package,
    }


def _build_record(
    *,
    task_spec: Any,
    variant: MechanismAblationVariant,
    budget: int,
    seed: int,
    cycles: int,
    policy_result: Any,
    candidate_pool: Dict[str, Any],
) -> Dict[str, Any]:
    task = getattr(task_spec, "task", None) or {}
    active_objects = list(policy_result.active_objects or [])
    latent_objects = list(policy_result.latent_objects or [])
    discard_objects = list(policy_result.discard_objects or [])
    runtime_metadata_snapshot = candidate_pool["task_context"].get("runtime_metadata_snapshot") or {}
    required_dependency_objects = list(candidate_pool["task_context"].get("required_dependency_objects") or [])
    critical_object_ids = set(candidate_pool["task_context"].get("critical_object_ids") or [])
    all_objects = list((candidate_pool["reconstructed_state"].get("typed_representation") or {}).get("objects") or [])
    active_ids = {str(item.get("object_id") or "") for item in active_objects}
    selected_critical = len(active_ids & critical_object_ids)
    required_total = max(1, len(critical_object_ids))
    dependency_coverage = selected_critical / required_total
    dependency_precision = selected_critical / max(1, len(active_objects))
    if dependency_coverage + dependency_precision:
        dependency_f1 = 2.0 * dependency_coverage * dependency_precision / max(1e-9, dependency_coverage + dependency_precision)
    else:
        dependency_f1 = 0.0
    validation_coverage = float((policy_result.metrics.validation_coverage or 0.0) or 0.0)
    active_retention_ratio = float((policy_result.metrics.active_retention_ratio or 0.0) or 0.0)
    important_total_importance = sum(float(item.get("importance", 0.0) or 0.0) for item in all_objects) or 1.0
    active_importance = sum(float(item.get("importance", 0.0) or 0.0) for item in active_objects)
    weighted_object_retention = active_importance / important_total_importance
    object_retention = len(active_objects) / max(1, len(all_objects))
    token_overhead = max(0, len(all_objects) - len(active_objects))
    validation_score = min(1.0, (0.35 * validation_coverage) + (0.45 * dependency_f1) + (0.20 * object_retention))
    graph_integrity_score = min(1.0, (0.55 * dependency_f1) + (0.45 * object_retention))

    record = {
        "task_id": task.get("id") or getattr(task_spec, "name", "mechanism_ablation_task"),
        "task_source": task.get("source"),
        "cycle": 0,
        "runtime_round": 0,
        "validation_passed": True,
        "state_committed": bool(active_objects),
        "semantic_object_inventory": candidate_pool["reconstructed_state"].get("semantic_object_inventory") or {},
        "runtime_metadata_snapshot": runtime_metadata_snapshot,
        "mechanism_ablation": {
            "variant": variant.name,
            "policy_name": variant.policy_name,
            "removed_component": variant.removed_component,
            "description": variant.description,
            "benchmark": getattr(task_spec, "name", task.get("id", "mechanism_ablation")),
            "budget": budget,
            "seed": seed,
            "cycles": cycles,
            "semantic_unit_count": int(getattr(task_spec, "semantic_unit_count", 0) or 0),
            "semantic_pressure_index": round(int(getattr(task_spec, "semantic_unit_count", 0) or 0) / float(budget), 6) if budget else None,
        },
        "mechanism_ablation_variant": variant.name,
        "mechanism_ablation_policy": variant.policy_name,
        "mechanism_ablation_suite": getattr(task_spec, "name", task.get("id", "mechanism_ablation")),
        "mechanism_ablation_budget": budget,
        "mechanism_ablation_seed": seed,
        "mechanism_ablation_cycles": cycles,
        "mechanism_ablation_pressure_index": round(int(getattr(task_spec, "semantic_unit_count", 0) or 0) / float(budget), 6) if budget else None,
        "validation_coverage": validation_coverage,
        "dependency_coverage": dependency_coverage,
        "dependency_precision": dependency_precision,
        "dependency_f1": dependency_f1,
        "validation_score": validation_score,
        "graph_integrity_score": graph_integrity_score,
        "object_retention": object_retention,
        "weighted_object_retention": weighted_object_retention,
        "token_overhead": token_overhead,
        "state_allocation_result": {
            "active_state": policy_result.active_state,
            "latent_state": policy_result.latent_state,
            "discard_state": policy_result.discard_state,
            "active_objects": policy_result.active_objects,
            "latent_objects": policy_result.latent_objects,
            "discard_objects": policy_result.discard_objects,
            "policy_name": policy_result.policy_name,
            "metrics": {
                "active_object_count": policy_result.metrics.active_object_count,
                "latent_object_count": policy_result.metrics.latent_object_count,
                "discard_object_count": policy_result.metrics.discard_object_count,
                "validation_coverage": policy_result.metrics.validation_coverage,
                "active_state_efficiency": policy_result.metrics.active_state_efficiency,
                "latent_preservation": policy_result.metrics.latent_preservation,
                "hallucination_isolation": policy_result.metrics.hallucination_isolation,
                "active_retention_ratio": policy_result.metrics.active_retention_ratio,
                "policy_name": policy_result.metrics.policy_name,
            },
        },
    }
    return record


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
        policy = _policy_for_variant(variant.name)
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
                        candidate_pool = _build_candidate_pool(task_spec, budget, seed, variant)
                        policy_result = policy.allocate(candidate_pool["reconstructed_state"], candidate_pool["task_context"])
                    record = _build_record(
                        task_spec=task_spec,
                        variant=variant,
                        budget=budget,
                        seed=seed,
                        cycles=cycles,
                        policy_result=policy_result,
                        candidate_pool=candidate_pool,
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

