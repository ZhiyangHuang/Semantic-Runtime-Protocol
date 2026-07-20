from __future__ import annotations

import json
import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence

from .srp.export import write_records_csv, write_records_markdown
from .srp.pipeline_runtime import initialize_state
from .srp.saliency import score_memory_chunks
from .srp.semantic_objects import build_semantic_object_inventory


@dataclass(frozen=True)
class ThresholdAnalysisTask:
    name: str
    scenario: str
    task: Dict[str, Any]


def _base_task() -> Dict[str, Any]:
    return {
        "id": "object-support-threshold-base",
        "task_type": "object_support_threshold_analysis",
        "source": "Controlled SRP Object Support Threshold Analysis",
        "initial_state": {
            "constraints": [
                "Project Orion keeps Atlas online for payments.",
                "Project Mercury keeps Atlas online for payments.",
                "Project Orion keeps Apollo linked for reporting.",
                "Project Mercury keeps Apollo linked for reporting.",
            ],
            "memory": (
                "Project Orion keeps Atlas online for payments. "
                "Project Mercury keeps Atlas online for payments. "
                "Project Orion keeps Apollo linked for reporting. "
                "Project Mercury keeps Apollo linked for reporting. "
                "Keep Atlas and Apollo online for the program. "
                "The cafeteria closes at five."
            ),
        },
        "query_expectations": [[["Project Orion keeps Atlas online for payments."]]],
        "expected_keywords": [],
        "metadata": {
            "benchmark": "Controlled SRP Object Support Threshold Analysis",
            "scenario": "budget_threshold",
            "required_dependency_labels": [
                "Project Orion keeps Atlas online for payments.",
                "Project Mercury keeps Atlas online for payments.",
                "Project Orion keeps Apollo linked for reporting.",
                "Project Mercury keeps Apollo linked for reporting.",
            ],
        },
    }


def _ambiguity_task(keyword_overlap_level: float) -> Dict[str, Any]:
    constraints = [
        "Project Orion keeps Atlas online for payments.",
        "Project Mercury keeps Atlas online for payments.",
    ]
    low_overlap_decoys = [
        "The cafeteria closes at five.",
        "The weather report stays calm.",
        "The printer stays offline.",
        "The lobby remains quiet.",
        "The calendar stays empty.",
    ]
    high_overlap_decoys = [
        "Atlas handles reporting notes.",
        "Atlas handles payments logs.",
        "Atlas keeps the program online.",
        "Atlas remains linked to reporting and payments.",
        "Atlas protects the Orion payment route.",
    ]
    overlap_count = max(1, min(len(high_overlap_decoys), round(len(high_overlap_decoys) * float(keyword_overlap_level))))
    decoys = high_overlap_decoys[:overlap_count] + low_overlap_decoys[: max(0, len(low_overlap_decoys) - overlap_count)]
    memory = " ".join(constraints + decoys)
    overlap_label = f"{keyword_overlap_level:.2f}".rstrip("0").rstrip(".")
    return {
        "id": f"object-support-threshold-ambiguity-{overlap_label.replace('.', 'p')}",
        "task_type": "object_support_threshold_analysis",
        "source": "Controlled SRP Object Support Threshold Analysis",
        "initial_state": {
            "constraints": constraints,
            "memory": memory,
        },
        "query_expectations": [[["Project Orion keeps Atlas online for payments."]]],
        "expected_keywords": [],
        "metadata": {
            "benchmark": "Controlled SRP Object Support Threshold Analysis",
            "scenario": "ambiguity_threshold",
            "keyword_overlap_level": keyword_overlap_level,
            "overlap_decoy_count": overlap_count,
            "decoy_count": len(decoys),
            "required_dependency_labels": list(constraints),
        },
    }


def build_threshold_analysis_tasks() -> List[ThresholdAnalysisTask]:
    return [
        ThresholdAnalysisTask("budget_threshold", "budget_threshold", _base_task()),
        ThresholdAnalysisTask("ambiguity_0p2", "ambiguity_threshold", _ambiguity_task(0.2)),
        ThresholdAnalysisTask("ambiguity_0p4", "ambiguity_threshold", _ambiguity_task(0.4)),
        ThresholdAnalysisTask("ambiguity_0p6", "ambiguity_threshold", _ambiguity_task(0.6)),
        ThresholdAnalysisTask("ambiguity_0p8", "ambiguity_threshold", _ambiguity_task(0.8)),
        ThresholdAnalysisTask("ambiguity_0p95", "ambiguity_threshold", _ambiguity_task(0.95)),
        ThresholdAnalysisTask("support_threshold", "support_threshold", _base_task()),
    ]


@contextmanager
def _temporary_env(overrides: Dict[str, str]):
    previous: Dict[str, str | None] = {}
    try:
        for key, value in overrides.items():
            previous[key] = os.environ.get(key)
            os.environ[key] = value
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _compare_rankings(
    disabled_ranked: Sequence[Dict[str, Any]],
    enabled_ranked: Sequence[Dict[str, Any]],
    top_k: int,
) -> Dict[str, Any]:
    disabled_by_id = {int(item["chunk_id"]): item for item in disabled_ranked}
    enabled_by_id = {int(item["chunk_id"]): item for item in enabled_ranked}
    chunk_ids = sorted(set(disabled_by_id) | set(enabled_by_id))
    score_deltas: Dict[int, float] = {}
    changed_chunk_ids: List[int] = []
    for chunk_id in chunk_ids:
        disabled_score = float(disabled_by_id.get(chunk_id, {}).get("score", 0.0))
        enabled_score = float(enabled_by_id.get(chunk_id, {}).get("score", 0.0))
        delta = round(enabled_score - disabled_score, 6)
        score_deltas[chunk_id] = delta
        if abs(delta) > 1e-9:
            changed_chunk_ids.append(chunk_id)
    disabled_topk = [int(item["chunk_id"]) for item in disabled_ranked[: max(1, top_k)]]
    enabled_topk = [int(item["chunk_id"]) for item in enabled_ranked[: max(1, top_k)]]
    common_topk = sorted(set(disabled_topk) & set(enabled_topk))
    disabled_positions = {chunk_id: index for index, chunk_id in enumerate(disabled_topk)}
    enabled_positions = {chunk_id: index for index, chunk_id in enumerate(enabled_topk)}
    rank_flip_count = sum(1 for chunk_id in common_topk if disabled_positions.get(chunk_id) != enabled_positions.get(chunk_id))
    deltas = list(score_deltas.values())
    topk_gain_values = [score_deltas.get(chunk_id, 0.0) for chunk_id in enabled_topk if chunk_id in score_deltas]
    decision_margin = _decision_margin(disabled_ranked, top_k)
    object_support_gain = (sum(deltas) / len(deltas)) if deltas else None
    object_support_gain_topk = (sum(topk_gain_values) / len(topk_gain_values)) if topk_gain_values else None
    dbi = None
    if decision_margin is not None and decision_margin != 0 and object_support_gain_topk is not None:
        dbi = round(float(object_support_gain_topk) / float(decision_margin), 6)
    return {
        "score_changed_chunk_count": len(changed_chunk_ids),
        "score_changed_chunk_rate": (len(changed_chunk_ids) / len(chunk_ids)) if chunk_ids else None,
        "topk_changed": disabled_topk != enabled_topk,
        "topk_delta_count": max(len([c for c in enabled_topk if c not in disabled_topk]), len([c for c in disabled_topk if c not in enabled_topk])),
        "rank_flip_count": rank_flip_count,
        "rank_flip_rate": (rank_flip_count / len(common_topk)) if common_topk else (1.0 if disabled_topk != enabled_topk else 0.0),
        "disabled_topk": disabled_topk,
        "enabled_topk": enabled_topk,
        "object_support_gain": object_support_gain,
        "object_support_gain_topk": object_support_gain_topk,
        "object_support_gain_max": max(deltas) if deltas else None,
        "decision_margin": decision_margin,
        "decision_flip_distance": None if decision_margin is None or object_support_gain_topk is None else round(float(decision_margin) - float(object_support_gain_topk), 6),
        "dbi": dbi,
        "decision_boundary_index": dbi,
    }


def _decision_margin(ranked: Sequence[Dict[str, Any]], top_k: int) -> float | None:
    effective_top_k = max(1, min(int(top_k), len(ranked)))
    if len(ranked) <= effective_top_k:
        return None
    cutoff_score = float(ranked[effective_top_k - 1].get("score", 0.0))
    next_score = float(ranked[effective_top_k].get("score", 0.0))
    return round(cutoff_score - next_score, 6)


def _score_case(task: Dict[str, Any], top_k: int, support_scale: float) -> Dict[str, Any]:
    state = initialize_state(task, encoder=None)
    inventory = build_semantic_object_inventory(state)
    disabled_ranked = score_memory_chunks(
        state.memory,
        state.constraints,
        expected_keywords=task.get("expected_keywords", []),
        semantic_object_inventory=None,
    )
    with _temporary_env({"SRP_OBJECT_SUPPORT_SCALE": str(support_scale)}):
        enabled_ranked = score_memory_chunks(
            state.memory,
            state.constraints,
            expected_keywords=task.get("expected_keywords", []),
            semantic_object_inventory=inventory,
        )
    comparison = _compare_rankings(disabled_ranked, enabled_ranked, top_k)
    metadata = task.get("metadata", {})
    comparison.update(
        {
            "schema_version": "object_support_threshold_case.v1",
            "task_id": task.get("id"),
            "scenario": metadata.get("scenario"),
            "keyword_overlap_level": metadata.get("keyword_overlap_level"),
            "decoy_count": metadata.get("decoy_count"),
            "overlap_decoy_count": metadata.get("overlap_decoy_count"),
            "top_k": top_k,
            "support_scale": support_scale,
            "chunk_count": len(disabled_ranked),
            "object_count": inventory.get("object_count"),
            "important_object_count": len(inventory.get("important_objects", [])),
            "decision_margin_disabled": _decision_margin(disabled_ranked, top_k),
            "decision_margin_enabled": _decision_margin(enabled_ranked, top_k),
        }
    )
    return comparison


def _build_rq2_1_budget_threshold() -> Dict[str, Any]:
    task = _base_task()
    top_k_values = [12, 10, 8, 6, 4, 2, 1]
    sweeps = [_score_case(task, top_k=value, support_scale=1.0) for value in top_k_values]
    first_changed = next((sweep["top_k"] for sweep in sweeps if sweep["topk_changed"]), None)
    return {
        "schema_version": "object_support_threshold_budget.v1",
        "research_question": "RQ2.1 Budget Threshold",
        "task_id": task.get("id"),
        "scenario": task.get("metadata", {}).get("scenario"),
        "top_k_values": top_k_values,
        "first_changed_top_k": first_changed,
        "sweeps": sweeps,
        "dbi_mean": _mean([sweep.get("dbi") for sweep in sweeps]),
        "decision_boundary_index_mean": _mean([sweep.get("dbi") for sweep in sweeps]),
        "decision_flip_distance_mean": _mean([sweep.get("decision_flip_distance") for sweep in sweeps]),
    }


def _build_rq2_2_ambiguity_threshold() -> Dict[str, Any]:
    overlap_levels = [0.2, 0.4, 0.6, 0.8, 0.95]
    tasks = [_ambiguity_task(level) for level in overlap_levels]
    sweeps = [_score_case(task, top_k=4, support_scale=1.0) for task in tasks]
    first_changed = next((sweep["task_id"] for sweep in sweeps if sweep["topk_changed"]), None)
    return {
        "schema_version": "object_support_threshold_ambiguity.v1",
        "research_question": "RQ2.2 Ambiguity Threshold",
        "keyword_overlap_levels": overlap_levels,
        "first_changed_keyword_overlap_level": first_changed,
        "sweeps": sweeps,
        "dbi_mean": _mean([sweep.get("dbi") for sweep in sweeps]),
        "decision_boundary_index_mean": _mean([sweep.get("dbi") for sweep in sweeps]),
        "decision_flip_distance_mean": _mean([sweep.get("decision_flip_distance") for sweep in sweeps]),
    }


def _build_rq2_3_support_threshold() -> Dict[str, Any]:
    task = _base_task()
    support_scales = [0.0, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.25]
    sweeps = [_score_case(task, top_k=4, support_scale=scale) for scale in support_scales]
    first_changed = next((sweep["support_scale"] for sweep in sweeps if sweep["topk_changed"]), None)
    return {
        "schema_version": "object_support_threshold_support.v1",
        "research_question": "RQ2.3 Support Threshold",
        "support_scales": support_scales,
        "first_changed_support_scale": first_changed,
        "sweeps": sweeps,
        "dbi_mean": _mean([sweep.get("dbi") for sweep in sweeps]),
        "decision_boundary_index_mean": _mean([sweep.get("dbi") for sweep in sweeps]),
        "decision_flip_distance_mean": _mean([sweep.get("decision_flip_distance") for sweep in sweeps]),
    }


def _mean(values: Sequence[Any]) -> float | None:
    numbers = [float(value) for value in values if value is not None]
    if not numbers:
        return None
    return sum(numbers) / len(numbers)


def run_object_aware_threshold_analysis() -> Dict[str, Any]:
    return {
        "rq2_1_budget_threshold": _build_rq2_1_budget_threshold(),
        "rq2_2_ambiguity_threshold": _build_rq2_2_ambiguity_threshold(),
        "rq2_3_support_threshold": _build_rq2_3_support_threshold(),
    }


def render_object_aware_threshold_analysis_markdown(results: Dict[str, Any]) -> str:
    lines = [
        "# Object-Aware Compression Threshold Analysis",
        "",
        "Stage 2 is split into three single-variable research questions:",
        "",
        "- RQ2.1 Budget Threshold",
        "- RQ2.2 Ambiguity Threshold",
        "- RQ2.3 Support Threshold",
        "- Decoy count is held fixed within each RQ until a later difficulty sweep",
        "",
    ]
    for key, section in results.items():
        lines.extend([f"## {section.get('research_question')}", ""])
        if key == "rq2_1_budget_threshold":
            lines.extend(
                [
                    "| Top-k | Top-k Changed | Rank Flip Rate | Decision Margin | DBI | Flip Distance |",
                    "| --- | --- | --- | --- | --- | --- |",
                ]
            )
        elif key == "rq2_2_ambiguity_threshold":
            lines.extend(
                [
                    "| Keyword Overlap | Decoy Count | Top-k Changed | Rank Flip Rate | Decision Margin | DBI | Flip Distance |",
                    "| --- | --- | --- | --- | --- | --- | --- |",
                ]
            )
        else:
            lines.extend(
                [
                    "| Support Scale | Top-k Changed | Rank Flip Rate | Decision Margin | DBI | Flip Distance |",
                    "| --- | --- | --- | --- | --- | --- |",
                ]
            )
        for sweep in section.get("sweeps") or []:
            if key == "rq2_1_budget_threshold":
                row = [
                    str(sweep.get("top_k")),
                    str(sweep.get("topk_changed")),
                    fmt(sweep.get("rank_flip_rate")),
                    fmt(sweep.get("decision_margin")),
                    fmt(sweep.get("dbi")),
                    fmt(sweep.get("decision_flip_distance")),
                ]
            elif key == "rq2_2_ambiguity_threshold":
                row = [
                    fmt(sweep.get("keyword_overlap_level")),
                    str(sweep.get("decoy_count")),
                    str(sweep.get("topk_changed")),
                    fmt(sweep.get("rank_flip_rate")),
                    fmt(sweep.get("decision_margin")),
                    fmt(sweep.get("dbi")),
                    fmt(sweep.get("decision_flip_distance")),
                ]
            else:
                row = [
                    fmt(sweep.get("support_scale")),
                    str(sweep.get("topk_changed")),
                    fmt(sweep.get("rank_flip_rate")),
                    fmt(sweep.get("decision_margin")),
                    fmt(sweep.get("dbi")),
                    fmt(sweep.get("decision_flip_distance")),
                ]
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")
    return "\n".join(lines)


def fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}".rstrip("0").rstrip(".")
    return str(value)


def write_object_aware_threshold_analysis_outputs(results: Dict[str, Any], output_dir: str | Path) -> Dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    json_path = output_path / "object_aware_threshold_analysis.json"
    markdown_path = output_path / "object_aware_threshold_analysis.md"
    json_path.write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    markdown_path.write_text(render_object_aware_threshold_analysis_markdown(results), encoding="utf-8")
    return {
        "json": json_path,
        "markdown": markdown_path,
    }

