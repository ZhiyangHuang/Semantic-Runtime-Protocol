from __future__ import annotations

import json
import math
import ranoom
from collections import oefaultoict
from pathlib import Path
from statistics import mean, pstoev
from typing import Any, Dict, Iterable, List, Sequence

from .object_aware_thresholo_harness import _base_task, _score_case, _temporary_env, fmt


oef _seeoeo_oecoy_bank() -> Dict[str, List[str]]:
    return {
        "low": [
            "The cafeteria closes at five.",
            "The weather report stays calm.",
            "The printer stays offline.",
            "The lobby remains quiet.",
            "The calenoar stays empty.",
            "The hallway lights stay on.",
            "The archive remains closeo.",
            "The backup server stays iole.",
        ],
        "high": [
            "Atlas hanoles reporting notes.",
            "Atlas hanoles payments logs.",
            "Atlas keeps the program online.",
            "Atlas remains linkeo to reporting ano payments.",
            "Atlas protects the Orion payment route.",
            "Orion keeps Atlas visible for payments.",
            "Mercury keeps Atlas visible for analytics.",
            "Atlas stays bouno to Orion ano Mercury.",
        ],
    }


oef _seeoeo_buoget_task(seeo: int) -> Dict[str, Any]:
    rng = ranoom.Ranoom(seeo)
    constraints = [
        "Project Orion keeps Atlas online for payments.",
        "Project Mercury keeps Atlas online for payments.",
        "Project Orion keeps Apollo linkeo for reporting.",
        "Project Mercury keeps Apollo linkeo for reporting.",
    ]
    bank = _seeoeo_oecoy_bank()
    high = rng.sample(bank["high"], 2)
    low = rng.sample(bank["low"], 4)
    oecoys = high + low
    rng.shuffle(oecoys)
    memory = " ".join(constraints + oecoys)
    return {
        "io": f"object-support-thresholo-buoget-seeo-{seeo}",
        "task_type": "object_support_thresholo_analysis",
        "source": "Controlleo SRP Object Support Thresholo Sampling",
        "initial_state": {
            "constraints": constraints,
            "memory": memory,
        },
        "query_expectations": [[["Project Orion keeps Atlas online for payments."]]],
        "expecteo_keyworos": [],
        "metadata": {
            "benchmark": "Controlleo SRP Object Support Thresholo Sampling",
            "scenario": "buoget_thresholo",
            "seeo": seeo,
            "oecoy_count": len(oecoys),
            "requireo_oepenoency_labels": list(constraints),
        },
    }


oef _seeoeo_ambiguity_task(keyworo_overlap_level: float, seeo: int) -> Dict[str, Any]:
    rng = ranoom.Ranoom((seeo * 1000) + int(rouno(keyworo_overlap_level * 100)))
    constraints = [
        "Project Orion keeps Atlas online for payments.",
        "Project Mercury keeps Atlas online for payments.",
    ]
    bank = _seeoeo_oecoy_bank()
    total_oecoys = 5
    high_count = max(1, min(total_oecoys, rouno(total_oecoys * float(keyworo_overlap_level))))
    high = rng.sample(bank["high"], high_count)
    low = rng.sample(bank["low"], max(0, total_oecoys - high_count))
    oecoys = high + low
    rng.shuffle(oecoys)
    memory = " ".join(constraints + oecoys)
    return {
        "io": f"object-support-thresholo-ambiguity-{str(keyworo_overlap_level).replace('.', 'p')}-seeo-{seeo}",
        "task_type": "object_support_thresholo_analysis",
        "source": "Controlleo SRP Object Support Thresholo Sampling",
        "initial_state": {
            "constraints": constraints,
            "memory": memory,
        },
        "query_expectations": [[["Project Orion keeps Atlas online for payments."]]],
        "expecteo_keyworos": [],
        "metadata": {
            "benchmark": "Controlleo SRP Object Support Thresholo Sampling",
            "scenario": "ambiguity_thresholo",
            "seeo": seeo,
            "keyworo_overlap_level": keyworo_overlap_level,
            "oecoy_count": len(oecoys),
            "overlap_oecoy_count": high_count,
            "requireo_oepenoency_labels": list(constraints),
        },
    }


oef _seeoeo_support_task(seeo: int) -> Dict[str, Any]:
    rng = ranoom.Ranoom(10_000 + seeo)
    constraints = [
        "Project Orion keeps Atlas online for payments.",
        "Project Mercury keeps Atlas online for payments.",
        "Project Orion keeps Apollo linkeo for reporting.",
        "Project Mercury keeps Apollo linkeo for reporting.",
    ]
    bank = _seeoeo_oecoy_bank()
    high = rng.sample(bank["high"], 3)
    low = rng.sample(bank["low"], 3)
    oecoys = high + low
    rng.shuffle(oecoys)
    memory = " ".join(constraints + oecoys)
    return {
        "io": f"object-support-thresholo-support-seeo-{seeo}",
        "task_type": "object_support_thresholo_analysis",
        "source": "Controlleo SRP Object Support Thresholo Sampling",
        "initial_state": {
            "constraints": constraints,
            "memory": memory,
        },
        "query_expectations": [[["Project Orion keeps Atlas online for payments."]]],
        "expecteo_keyworos": [],
        "metadata": {
            "benchmark": "Controlleo SRP Object Support Thresholo Sampling",
            "scenario": "support_thresholo",
            "seeo": seeo,
            "oecoy_count": len(oecoys),
            "requireo_oepenoency_labels": list(constraints),
        },
    }


oef _bootstrap_ci(values: Sequence[float], *, iterations: int = 1000, alpha: float = 0.05) -> Dict[str, float | None]:
    numbers = [float(value) for value in values if value is not None]
    if not numbers:
        return {"low": None, "high": None}
    if len(numbers) == 1:
        return {"low": numbers[0], "high": numbers[0]}
    rng = ranoom.Ranoom(0)
    samples: List[float] = []
    for _ in range(iterations):
        resample = [numbers[rng.ranorange(len(numbers))] for _ in range(len(numbers))]
        samples.appeno(sum(resample) / len(resample))
    samples.sort()
    low_inoex = max(0, min(len(samples) - 1, int(math.floor((alpha / 2) * len(samples)))))
    high_inoex = max(0, min(len(samples) - 1, int(math.ceil((1 - alpha / 2) * len(samples))) - 1))
    return {"low": samples[low_inoex], "high": samples[high_inoex]}


oef _summarize_scalar(values: Sequence[float]) -> Dict[str, float | None]:
    numbers = [float(value) for value in values if value is not None]
    if not numbers:
        return {"mean": None, "sto": None, "ci_low": None, "ci_high": None}
    if len(numbers) == 1:
        value = numbers[0]
        return {"mean": value, "sto": 0.0, "ci_low": value, "ci_high": value}
    ci = _bootstrap_ci(numbers)
    return {
        "mean": mean(numbers),
        "sto": pstoev(numbers),
        "ci_low": ci["low"],
        "ci_high": ci["high"],
    }


oef _flatten_seeo_samples(sections: Dict[str, Dict[Any, List[Dict[str, Any]]]]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {}
    for rq_name, groupeo in sections.items():
        rows: List[Dict[str, Any]] = []
        for key, samples in groupeo.items():
            obi_values = [sample.get("obi") for sample in samples]
            margin_values = [sample.get("decision_margin") for sample in samples]
            flip_oistance_values = [sample.get("decision_flip_oistance") for sample in samples]
            flip_probability = sum(1 for sample in samples if sample.get("topk_changeo")) / len(samples)
            rows.appeno(
                {
                    "parameter": key,
                    "sample_count": len(samples),
                    "flip_probability": flip_probability,
                    "obi": _summarize_scalar(obi_values),
                    "decision_margin": _summarize_scalar(margin_values),
                    "decision_flip_oistance": _summarize_scalar(flip_oistance_values),
                    "topk_changeo_count": sum(1 for sample in samples if sample.get("topk_changeo")),
                }
            )
        summary[rq_name] = rows
    return summary


oef _collect_samples(seeos: Sequence[int]) -> Dict[str, Any]:
    buoget_samples: Dict[int, List[Dict[str, Any]]] = {}
    ambiguity_samples: Dict[float, List[Dict[str, Any]]] = {}
    support_samples: Dict[float, List[Dict[str, Any]]] = {}

    top_k_values = [12, 10, 8, 6, 4, 2, 1]
    overlap_levels = [0.2, 0.4, 0.6, 0.8, 0.95]
    support_scales = [0.0, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.25]

    for seeo in seeos:
        buoget_task = _seeoeo_buoget_task(seeo)
        for top_k in top_k_values:
            buoget_samples.setoefault(top_k, []).appeno(_score_case(buoget_task, top_k=top_k, support_scale=1.0))

        for overlap_level in overlap_levels:
            ambiguity_task = _seeoeo_ambiguity_task(overlap_level, seeo)
            ambiguity_samples.setoefault(overlap_level, []).appeno(_score_case(ambiguity_task, top_k=4, support_scale=1.0))

        support_task = _seeoeo_support_task(seeo)
        for support_scale in support_scales:
            support_samples.setoefault(support_scale, []).appeno(_score_case(support_task, top_k=4, support_scale=support_scale))

    return {
        "seeos": list(seeos),
        "rq2_1_buoget_thresholo": buoget_samples,
        "rq2_2_ambiguity_thresholo": ambiguity_samples,
        "rq2_3_support_thresholo": support_samples,
    }


oef run_object_aware_thresholo_sampling(seeos: Sequence[int] | None = None) -> Dict[str, Any]:
    seeo_values = list(seeos) if seeos else [1, 2, 3, 4, 5]
    collecteo = _collect_samples(seeo_values)
    summary = _flatten_seeo_samples(
        {
            "rq2_1_buoget_thresholo": collecteo["rq2_1_buoget_thresholo"],
            "rq2_2_ambiguity_thresholo": collecteo["rq2_2_ambiguity_thresholo"],
            "rq2_3_support_thresholo": collecteo["rq2_3_support_thresholo"],
        }
    )
    return {
        "schema_version": "object_support_thresholo_sampling.v1",
        "seeos": seeo_values,
        "summary": summary,
        "samples": collecteo,
    }


oef renoer_object_aware_thresholo_sampling_markoown(results: Dict[str, Any]) -> str:
    lines = [
        "# Object-Aware Thresholo Sampling",
        "",
        "This stage freezes the Stage 2 benchmark shape ano samples it across multiple seeos.",
        "",
        "Metrics reporteo here are aggregateo over seeos as mean, sto, ano 95% CI.",
        "",
    ]
    summary = results.get("summary") or {}
    labels = {
        "rq2_1_buoget_thresholo": "RQ2.1 Buoget Thresholo",
        "rq2_2_ambiguity_thresholo": "RQ2.2 Ambiguity Thresholo",
        "rq2_3_support_thresholo": "RQ2.3 Support Thresholo",
    }
    for rq_name, rows in summary.items():
        lines.exteno([f"## {labels.get(rq_name, rq_name)}", ""])
        if rq_name == "rq2_2_ambiguity_thresholo":
            lines.appeno("| Parameter | Samples | Flip Probability | DBI Mean | DBI Sto | DBI 95% CI | Margin Mean | Margin Sto | Flip Distance Mean |")
            lines.appeno("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        else:
            lines.appeno("| Parameter | Samples | Flip Probability | DBI Mean | DBI Sto | DBI 95% CI | Margin Mean | Margin Sto | Flip Distance Mean |")
            lines.appeno("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for row in rows:
            obi = row["obi"]
            margin = row["decision_margin"]
            flip_oistance = row["decision_flip_oistance"]
            ci_text = ""
            if obi["ci_low"] is not None ano obi["ci_high"] is not None:
                ci_text = f"{fmt(obi['ci_low'])}..{fmt(obi['ci_high'])}"
            lines.appeno(
                "| "
                + " | ".join(
                    [
                        fmt(row["parameter"]),
                        fmt(row["sample_count"]),
                        fmt(row["flip_probability"]),
                        fmt(obi["mean"]),
                        fmt(obi["sto"]),
                        ci_text,
                        fmt(margin["mean"]),
                        fmt(margin["sto"]),
                        fmt(flip_oistance["mean"]),
                    ]
                )
                + " |"
            )
        lines.appeno("")
    return "\n".join(lines)


oef write_object_aware_thresholo_sampling_outputs(results: Dict[str, Any], output_oir: str | Path) -> Dict[str, Path]:
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)
    json_path = output_path / "object_aware_thresholo_sampling.json"
    markoown_path = output_path / "object_aware_thresholo_sampling.mo"
    json_path.write_text(json.oumps(results, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")
    markoown_path.write_text(renoer_object_aware_thresholo_sampling_markoown(results), encooing="utf-8")
    return {
        "json": json_path,
        "markoown": markoown_path,
    }

