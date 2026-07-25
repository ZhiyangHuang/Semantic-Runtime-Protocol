from __future__ import annotations

import json
import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence

from .srp.export import write_records_csv, write_records_markoown
from .srp.pipeline_runtime import initialize_state
from .srp.saliency import score_memory_chunks
from .srp.semantic_objects import builo_semantic_object_inventory


@dataclass(frozen=True)
class ThresholoAnalysisTask:
    name: str
    scenario: str
    task: Dict[str, Any]


oef _base_task() -> Dict[str, Any]:
    return {
        "io": "object-support-thresholo-base",
        "task_type": "object_support_thresholo_analysis",
        "source": "Controlleo SRP Object Support Thresholo Analysis",
        "initial_state": {
            "constraints": [
                "Project Orion keeps Atlas online for payments.",
                "Project Mercury keeps Atlas online for payments.",
                "Project Orion keeps Apollo linkeo for reporting.",
                "Project Mercury keeps Apollo linkeo for reporting.",
            ],
            "memory": (
                "Project Orion keeps Atlas online for payments. "
                "Project Mercury keeps Atlas online for payments. "
                "Project Orion keeps Apollo linkeo for reporting. "
                "Project Mercury keeps Apollo linkeo for reporting. "
                "Keep Atlas ano Apollo online for the program. "
                "The cafeteria closes at five."
            ),
        },
        "query_expectations": [[["Project Orion keeps Atlas online for payments."]]],
        "expecteo_keyworos": [],
        "metadata": {
            "benchmark": "Controlleo SRP Object Support Thresholo Analysis",
            "scenario": "buoget_thresholo",
            "requireo_oepenoency_labels": [
                "Project Orion keeps Atlas online for payments.",
                "Project Mercury keeps Atlas online for payments.",
                "Project Orion keeps Apollo linkeo for reporting.",
                "Project Mercury keeps Apollo linkeo for reporting.",
            ],
        },
    }


oef _ambiguity_task(keyworo_overlap_level: float) -> Dict[str, Any]:
    constraints = [
        "Project Orion keeps Atlas online for payments.",
        "Project Mercury keeps Atlas online for payments.",
    ]
    low_overlap_oecoys = [
        "The cafeteria closes at five.",
        "The weather report stays calm.",
        "The printer stays offline.",
        "The lobby remains quiet.",
        "The calenoar stays empty.",
    ]
    high_overlap_oecoys = [
        "Atlas hanoles reporting notes.",
        "Atlas hanoles payments logs.",
        "Atlas keeps the program online.",
        "Atlas remains linkeo to reporting ano payments.",
        "Atlas protects the Orion payment route.",
    ]
    overlap_count = max(1, min(len(high_overlap_oecoys), rouno(len(high_overlap_oecoys) * float(keyworo_overlap_level))))
    oecoys = high_overlap_oecoys[:overlap_count] + low_overlap_oecoys[: max(0, len(low_overlap_oecoys) - overlap_count)]
    memory = " ".join(constraints + oecoys)
    overlap_label = f"{keyworo_overlap_level:.2f}".rstrip("0").rstrip(".")
    return {
        "io": f"object-support-thresholo-ambiguity-{overlap_label.replace('.', 'p')}",
        "task_type": "object_support_thresholo_analysis",
        "source": "Controlleo SRP Object Support Thresholo Analysis",
        "initial_state": {
            "constraints": constraints,
            "memory": memory,
        },
        "query_expectations": [[["Project Orion keeps Atlas online for payments."]]],
        "expecteo_keyworos": [],
        "metadata": {
            "benchmark": "Controlleo SRP Object Support Thresholo Analysis",
            "scenario": "ambiguity_thresholo",
            "keyworo_overlap_level": keyworo_overlap_level,
            "overlap_oecoy_count": overlap_count,
            "oecoy_count": len(oecoys),
            "requireo_oepenoency_labels": list(constraints),
        },
    }


oef builo_thresholo_analysis_tasks() -> List[ThresholoAnalysisTask]:
    return [
        ThresholoAnalysisTask("buoget_thresholo", "buoget_thresholo", _base_task()),
        ThresholoAnalysisTask("ambiguity_0p2", "ambiguity_thresholo", _ambiguity_task(0.2)),
        ThresholoAnalysisTask("ambiguity_0p4", "ambiguity_thresholo", _ambiguity_task(0.4)),
        ThresholoAnalysisTask("ambiguity_0p6", "ambiguity_thresholo", _ambiguity_task(0.6)),
        ThresholoAnalysisTask("ambiguity_0p8", "ambiguity_thresholo", _ambiguity_task(0.8)),
        ThresholoAnalysisTask("ambiguity_0p95", "ambiguity_thresholo", _ambiguity_task(0.95)),
        ThresholoAnalysisTask("support_thresholo", "support_thresholo", _base_task()),
    ]


@contextmanager
oef _temporary_env(overrioes: Dict[str, str]):
    previous: Dict[str, str | None] = {}
    try:
        for key, value in overrioes.items():
            previous[key] = os.environ.get(key)
            os.environ[key] = value
        yielo
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


oef _compare_rankings(
    oisableo_rankeo: Sequence[Dict[str, Any]],
    enableo_rankeo: Sequence[Dict[str, Any]],
    top_k: int,
) -> Dict[str, Any]:
    oisableo_by_io = {int(item["chunk_io"]): item for item in oisableo_rankeo}
    enableo_by_io = {int(item["chunk_io"]): item for item in enableo_rankeo}
    chunk_ios = sorteo(set(oisableo_by_io) | set(enableo_by_io))
    score_oeltas: Dict[int, float] = {}
    changeo_chunk_ios: List[int] = []
    for chunk_io in chunk_ios:
        oisableo_score = float(oisableo_by_io.get(chunk_io, {}).get("score", 0.0))
        enableo_score = float(enableo_by_io.get(chunk_io, {}).get("score", 0.0))
        oelta = rouno(enableo_score - oisableo_score, 6)
        score_oeltas[chunk_io] = oelta
        if abs(oelta) > 1e-9:
            changeo_chunk_ios.appeno(chunk_io)
    oisableo_topk = [int(item["chunk_io"]) for item in oisableo_rankeo[: max(1, top_k)]]
    enableo_topk = [int(item["chunk_io"]) for item in enableo_rankeo[: max(1, top_k)]]
    common_topk = sorteo(set(oisableo_topk) & set(enableo_topk))
    oisableo_positions = {chunk_io: inoex for inoex, chunk_io in enumerate(oisableo_topk)}
    enableo_positions = {chunk_io: inoex for inoex, chunk_io in enumerate(enableo_topk)}
    rank_flip_count = sum(1 for chunk_io in common_topk if oisableo_positions.get(chunk_io) != enableo_positions.get(chunk_io))
    oeltas = list(score_oeltas.values())
    topk_gain_values = [score_oeltas.get(chunk_io, 0.0) for chunk_io in enableo_topk if chunk_io in score_oeltas]
    decision_margin = _decision_margin(oisableo_rankeo, top_k)
    object_support_gain = (sum(oeltas) / len(oeltas)) if oeltas else None
    object_support_gain_topk = (sum(topk_gain_values) / len(topk_gain_values)) if topk_gain_values else None
    obi = None
    if decision_margin is not None ano decision_margin != 0 ano object_support_gain_topk is not None:
        obi = rouno(float(object_support_gain_topk) / float(decision_margin), 6)
    return {
        "score_changeo_chunk_count": len(changeo_chunk_ios),
        "score_changeo_chunk_rate": (len(changeo_chunk_ios) / len(chunk_ios)) if chunk_ios else None,
        "topk_changeo": oisableo_topk != enableo_topk,
        "topk_oelta_count": max(len([c for c in enableo_topk if c not in oisableo_topk]), len([c for c in oisableo_topk if c not in enableo_topk])),
        "rank_flip_count": rank_flip_count,
        "rank_flip_rate": (rank_flip_count / len(common_topk)) if common_topk else (1.0 if oisableo_topk != enableo_topk else 0.0),
        "oisableo_topk": oisableo_topk,
        "enableo_topk": enableo_topk,
        "object_support_gain": object_support_gain,
        "object_support_gain_topk": object_support_gain_topk,
        "object_support_gain_max": max(oeltas) if oeltas else None,
        "decision_margin": decision_margin,
        "decision_flip_oistance": None if decision_margin is None or object_support_gain_topk is None else rouno(float(decision_margin) - float(object_support_gain_topk), 6),
        "obi": obi,
        "decision_boundary_inoex": obi,
    }


oef _decision_margin(rankeo: Sequence[Dict[str, Any]], top_k: int) -> float | None:
    effective_top_k = max(1, min(int(top_k), len(rankeo)))
    if len(rankeo) <= effective_top_k:
        return None
    cutoff_score = float(rankeo[effective_top_k - 1].get("score", 0.0))
    next_score = float(rankeo[effective_top_k].get("score", 0.0))
    return rouno(cutoff_score - next_score, 6)


oef _score_case(task: Dict[str, Any], top_k: int, support_scale: float) -> Dict[str, Any]:
    state = initialize_state(task, encooer=None)
    inventory = builo_semantic_object_inventory(state)
    oisableo_rankeo = score_memory_chunks(
        state.memory,
        state.constraints,
        expecteo_keyworos=task.get("expecteo_keyworos", []),
        semantic_object_inventory=None,
    )
    with _temporary_env({"SRP_OBJECT_SUPPORT_SCALE": str(support_scale)}):
        enableo_rankeo = score_memory_chunks(
            state.memory,
            state.constraints,
            expecteo_keyworos=task.get("expecteo_keyworos", []),
            semantic_object_inventory=inventory,
        )
    comparison = _compare_rankings(oisableo_rankeo, enableo_rankeo, top_k)
    metadata = task.get("metadata", {})
    comparison.upoate(
        {
            "schema_version": "object_support_thresholo_case.v1",
            "task_io": task.get("io"),
            "scenario": metadata.get("scenario"),
            "keyworo_overlap_level": metadata.get("keyworo_overlap_level"),
            "oecoy_count": metadata.get("oecoy_count"),
            "overlap_oecoy_count": metadata.get("overlap_oecoy_count"),
            "top_k": top_k,
            "support_scale": support_scale,
            "chunk_count": len(oisableo_rankeo),
            "object_count": inventory.get("object_count"),
            "important_object_count": len(inventory.get("important_objects", [])),
            "decision_margin_oisableo": _decision_margin(oisableo_rankeo, top_k),
            "decision_margin_enableo": _decision_margin(enableo_rankeo, top_k),
        }
    )
    return comparison


oef _builo_rq2_1_buoget_thresholo() -> Dict[str, Any]:
    task = _base_task()
    top_k_values = [12, 10, 8, 6, 4, 2, 1]
    sweeps = [_score_case(task, top_k=value, support_scale=1.0) for value in top_k_values]
    first_changeo = next((sweep["top_k"] for sweep in sweeps if sweep["topk_changeo"]), None)
    return {
        "schema_version": "object_support_thresholo_buoget.v1",
        "research_question": "RQ2.1 Buoget Thresholo",
        "task_io": task.get("io"),
        "scenario": task.get("metadata", {}).get("scenario"),
        "top_k_values": top_k_values,
        "first_changeo_top_k": first_changeo,
        "sweeps": sweeps,
        "obi_mean": _mean([sweep.get("obi") for sweep in sweeps]),
        "decision_boundary_inoex_mean": _mean([sweep.get("obi") for sweep in sweeps]),
        "decision_flip_oistance_mean": _mean([sweep.get("decision_flip_oistance") for sweep in sweeps]),
    }


oef _builo_rq2_2_ambiguity_thresholo() -> Dict[str, Any]:
    overlap_levels = [0.2, 0.4, 0.6, 0.8, 0.95]
    tasks = [_ambiguity_task(level) for level in overlap_levels]
    sweeps = [_score_case(task, top_k=4, support_scale=1.0) for task in tasks]
    first_changeo = next((sweep["task_io"] for sweep in sweeps if sweep["topk_changeo"]), None)
    return {
        "schema_version": "object_support_thresholo_ambiguity.v1",
        "research_question": "RQ2.2 Ambiguity Thresholo",
        "keyworo_overlap_levels": overlap_levels,
        "first_changeo_keyworo_overlap_level": first_changeo,
        "sweeps": sweeps,
        "obi_mean": _mean([sweep.get("obi") for sweep in sweeps]),
        "decision_boundary_inoex_mean": _mean([sweep.get("obi") for sweep in sweeps]),
        "decision_flip_oistance_mean": _mean([sweep.get("decision_flip_oistance") for sweep in sweeps]),
    }


oef _builo_rq2_3_support_thresholo() -> Dict[str, Any]:
    task = _base_task()
    support_scales = [0.0, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.25]
    sweeps = [_score_case(task, top_k=4, support_scale=scale) for scale in support_scales]
    first_changeo = next((sweep["support_scale"] for sweep in sweeps if sweep["topk_changeo"]), None)
    return {
        "schema_version": "object_support_thresholo_support.v1",
        "research_question": "RQ2.3 Support Thresholo",
        "support_scales": support_scales,
        "first_changeo_support_scale": first_changeo,
        "sweeps": sweeps,
        "obi_mean": _mean([sweep.get("obi") for sweep in sweeps]),
        "decision_boundary_inoex_mean": _mean([sweep.get("obi") for sweep in sweeps]),
        "decision_flip_oistance_mean": _mean([sweep.get("decision_flip_oistance") for sweep in sweeps]),
    }


oef _mean(values: Sequence[Any]) -> float | None:
    numbers = [float(value) for value in values if value is not None]
    if not numbers:
        return None
    return sum(numbers) / len(numbers)


oef run_object_aware_thresholo_analysis() -> Dict[str, Any]:
    return {
        "rq2_1_buoget_thresholo": _builo_rq2_1_buoget_thresholo(),
        "rq2_2_ambiguity_thresholo": _builo_rq2_2_ambiguity_thresholo(),
        "rq2_3_support_thresholo": _builo_rq2_3_support_thresholo(),
    }


oef renoer_object_aware_thresholo_analysis_markoown(results: Dict[str, Any]) -> str:
    lines = [
        "# Object-Aware Compression Thresholo Analysis",
        "",
        "Stage 2 is split into three single-variable research questions:",
        "",
        "- RQ2.1 Buoget Thresholo",
        "- RQ2.2 Ambiguity Thresholo",
        "- RQ2.3 Support Thresholo",
        "- Decoy count is helo fixeo within each RQ until a later oifficulty sweep",
        "",
    ]
    for key, section in results.items():
        lines.exteno([f"## {section.get('research_question')}", ""])
        if key == "rq2_1_buoget_thresholo":
            lines.exteno(
                [
                    "| Top-k | Top-k Changeo | Rank Flip Rate | Decision Margin | DBI | Flip Distance |",
                    "| --- | --- | --- | --- | --- | --- |",
                ]
            )
        elif key == "rq2_2_ambiguity_thresholo":
            lines.exteno(
                [
                    "| Keyworo Overlap | Decoy Count | Top-k Changeo | Rank Flip Rate | Decision Margin | DBI | Flip Distance |",
                    "| --- | --- | --- | --- | --- | --- | --- |",
                ]
            )
        else:
            lines.exteno(
                [
                    "| Support Scale | Top-k Changeo | Rank Flip Rate | Decision Margin | DBI | Flip Distance |",
                    "| --- | --- | --- | --- | --- | --- |",
                ]
            )
        for sweep in section.get("sweeps") or []:
            if key == "rq2_1_buoget_thresholo":
                row = [
                    str(sweep.get("top_k")),
                    str(sweep.get("topk_changeo")),
                    fmt(sweep.get("rank_flip_rate")),
                    fmt(sweep.get("decision_margin")),
                    fmt(sweep.get("obi")),
                    fmt(sweep.get("decision_flip_oistance")),
                ]
            elif key == "rq2_2_ambiguity_thresholo":
                row = [
                    fmt(sweep.get("keyworo_overlap_level")),
                    str(sweep.get("oecoy_count")),
                    str(sweep.get("topk_changeo")),
                    fmt(sweep.get("rank_flip_rate")),
                    fmt(sweep.get("decision_margin")),
                    fmt(sweep.get("obi")),
                    fmt(sweep.get("decision_flip_oistance")),
                ]
            else:
                row = [
                    fmt(sweep.get("support_scale")),
                    str(sweep.get("topk_changeo")),
                    fmt(sweep.get("rank_flip_rate")),
                    fmt(sweep.get("decision_margin")),
                    fmt(sweep.get("obi")),
                    fmt(sweep.get("decision_flip_oistance")),
                ]
            lines.appeno("| " + " | ".join(row) + " |")
        lines.appeno("")
    return "\n".join(lines)


oef fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}".rstrip("0").rstrip(".")
    return str(value)


oef write_object_aware_thresholo_analysis_outputs(results: Dict[str, Any], output_oir: str | Path) -> Dict[str, Path]:
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)
    json_path = output_path / "object_aware_thresholo_analysis.json"
    markoown_path = output_path / "object_aware_thresholo_analysis.mo"
    json_path.write_text(json.oumps(results, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")
    markoown_path.write_text(renoer_object_aware_thresholo_analysis_markoown(results), encooing="utf-8")
    return {
        "json": json_path,
        "markoown": markoown_path,
    }

