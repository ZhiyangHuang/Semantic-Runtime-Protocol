from __future__ import annotations

import json
import math
import random
from collections import defaultdict
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Dict, Iterable, List, Sequence

from .object_aware_threshold_harness import _base_task, _score_case, _temporary_env, fmt


def _seeded_decoy_bank() -> Dict[str, List[str]]:
    return {
        "low": [
            "The cafeteria closes at five.",
            "The weather report stays calm.",
            "The printer stays offline.",
            "The lobby remains quiet.",
            "The calendar stays empty.",
            "The hallway lights stay on.",
            "The archive remains closed.",
            "The backup server stays idle.",
        ],
        "high": [
            "Atlas handles reporting notes.",
            "Atlas handles payments logs.",
            "Atlas keeps the program online.",
            "Atlas remains linked to reporting and payments.",
            "Atlas protects the Orion payment route.",
            "Orion keeps Atlas visible for payments.",
            "Mercury keeps Atlas visible for analytics.",
            "Atlas stays bound to Orion and Mercury.",
        ],
    }


def _seeded_budget_task(seed: int) -> Dict[str, Any]:
    rng = random.Random(seed)
    constraints = [
        "Project Orion keeps Atlas online for payments.",
        "Project Mercury keeps Atlas online for payments.",
        "Project Orion keeps Apollo linked for reporting.",
        "Project Mercury keeps Apollo linked for reporting.",
    ]
    bank = _seeded_decoy_bank()
    high = rng.sample(bank["high"], 2)
    low = rng.sample(bank["low"], 4)
    decoys = high + low
    rng.shuffle(decoys)
    memory = " ".join(constraints + decoys)
    return {
        "id": f"object-support-threshold-budget-seed-{seed}",
        "task_type": "object_support_threshold_analysis",
        "source": "Controlled SRP Object Support Threshold Sampling",
        "initial_state": {
            "constraints": constraints,
            "memory": memory,
        },
        "query_expectations": [[["Project Orion keeps Atlas online for payments."]]],
        "expected_keywords": [],
        "metadata": {
            "benchmark": "Controlled SRP Object Support Threshold Sampling",
            "scenario": "budget_threshold",
            "seed": seed,
            "decoy_count": len(decoys),
            "required_dependency_labels": list(constraints),
        },
    }


def _seeded_ambiguity_task(keyword_overlap_level: float, seed: int) -> Dict[str, Any]:
    rng = random.Random((seed * 1000) + int(round(keyword_overlap_level * 100)))
    constraints = [
        "Project Orion keeps Atlas online for payments.",
        "Project Mercury keeps Atlas online for payments.",
    ]
    bank = _seeded_decoy_bank()
    total_decoys = 5
    high_count = max(1, min(total_decoys, round(total_decoys * float(keyword_overlap_level))))
    high = rng.sample(bank["high"], high_count)
    low = rng.sample(bank["low"], max(0, total_decoys - high_count))
    decoys = high + low
    rng.shuffle(decoys)
    memory = " ".join(constraints + decoys)
    return {
        "id": f"object-support-threshold-ambiguity-{str(keyword_overlap_level).replace('.', 'p')}-seed-{seed}",
        "task_type": "object_support_threshold_analysis",
        "source": "Controlled SRP Object Support Threshold Sampling",
        "initial_state": {
            "constraints": constraints,
            "memory": memory,
        },
        "query_expectations": [[["Project Orion keeps Atlas online for payments."]]],
        "expected_keywords": [],
        "metadata": {
            "benchmark": "Controlled SRP Object Support Threshold Sampling",
            "scenario": "ambiguity_threshold",
            "seed": seed,
            "keyword_overlap_level": keyword_overlap_level,
            "decoy_count": len(decoys),
            "overlap_decoy_count": high_count,
            "required_dependency_labels": list(constraints),
        },
    }


def _seeded_support_task(seed: int) -> Dict[str, Any]:
    rng = random.Random(10_000 + seed)
    constraints = [
        "Project Orion keeps Atlas online for payments.",
        "Project Mercury keeps Atlas online for payments.",
        "Project Orion keeps Apollo linked for reporting.",
        "Project Mercury keeps Apollo linked for reporting.",
    ]
    bank = _seeded_decoy_bank()
    high = rng.sample(bank["high"], 3)
    low = rng.sample(bank["low"], 3)
    decoys = high + low
    rng.shuffle(decoys)
    memory = " ".join(constraints + decoys)
    return {
        "id": f"object-support-threshold-support-seed-{seed}",
        "task_type": "object_support_threshold_analysis",
        "source": "Controlled SRP Object Support Threshold Sampling",
        "initial_state": {
            "constraints": constraints,
            "memory": memory,
        },
        "query_expectations": [[["Project Orion keeps Atlas online for payments."]]],
        "expected_keywords": [],
        "metadata": {
            "benchmark": "Controlled SRP Object Support Threshold Sampling",
            "scenario": "support_threshold",
            "seed": seed,
            "decoy_count": len(decoys),
            "required_dependency_labels": list(constraints),
        },
    }


def _bootstrap_ci(values: Sequence[float], *, iterations: int = 1000, alpha: float = 0.05) -> Dict[str, float | None]:
    numbers = [float(value) for value in values if value is not None]
    if not numbers:
        return {"low": None, "high": None}
    if len(numbers) == 1:
        return {"low": numbers[0], "high": numbers[0]}
    rng = random.Random(0)
    samples: List[float] = []
    for _ in range(iterations):
        resample = [numbers[rng.randrange(len(numbers))] for _ in range(len(numbers))]
        samples.append(sum(resample) / len(resample))
    samples.sort()
    low_index = max(0, min(len(samples) - 1, int(math.floor((alpha / 2) * len(samples)))))
    high_index = max(0, min(len(samples) - 1, int(math.ceil((1 - alpha / 2) * len(samples))) - 1))
    return {"low": samples[low_index], "high": samples[high_index]}


def _summarize_scalar(values: Sequence[float]) -> Dict[str, float | None]:
    numbers = [float(value) for value in values if value is not None]
    if not numbers:
        return {"mean": None, "std": None, "ci_low": None, "ci_high": None}
    if len(numbers) == 1:
        value = numbers[0]
        return {"mean": value, "std": 0.0, "ci_low": value, "ci_high": value}
    ci = _bootstrap_ci(numbers)
    return {
        "mean": mean(numbers),
        "std": pstdev(numbers),
        "ci_low": ci["low"],
        "ci_high": ci["high"],
    }


def _flatten_seed_samples(sections: Dict[str, Dict[Any, List[Dict[str, Any]]]]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {}
    for rq_name, grouped in sections.items():
        rows: List[Dict[str, Any]] = []
        for key, samples in grouped.items():
            dbi_values = [sample.get("dbi") for sample in samples]
            margin_values = [sample.get("decision_margin") for sample in samples]
            flip_distance_values = [sample.get("decision_flip_distance") for sample in samples]
            flip_probability = sum(1 for sample in samples if sample.get("topk_changed")) / len(samples)
            rows.append(
                {
                    "parameter": key,
                    "sample_count": len(samples),
                    "flip_probability": flip_probability,
                    "dbi": _summarize_scalar(dbi_values),
                    "decision_margin": _summarize_scalar(margin_values),
                    "decision_flip_distance": _summarize_scalar(flip_distance_values),
                    "topk_changed_count": sum(1 for sample in samples if sample.get("topk_changed")),
                }
            )
        summary[rq_name] = rows
    return summary


def _collect_samples(seeds: Sequence[int]) -> Dict[str, Any]:
    budget_samples: Dict[int, List[Dict[str, Any]]] = {}
    ambiguity_samples: Dict[float, List[Dict[str, Any]]] = {}
    support_samples: Dict[float, List[Dict[str, Any]]] = {}

    top_k_values = [12, 10, 8, 6, 4, 2, 1]
    overlap_levels = [0.2, 0.4, 0.6, 0.8, 0.95]
    support_scales = [0.0, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.25]

    for seed in seeds:
        budget_task = _seeded_budget_task(seed)
        for top_k in top_k_values:
            budget_samples.setdefault(top_k, []).append(_score_case(budget_task, top_k=top_k, support_scale=1.0))

        for overlap_level in overlap_levels:
            ambiguity_task = _seeded_ambiguity_task(overlap_level, seed)
            ambiguity_samples.setdefault(overlap_level, []).append(_score_case(ambiguity_task, top_k=4, support_scale=1.0))

        support_task = _seeded_support_task(seed)
        for support_scale in support_scales:
            support_samples.setdefault(support_scale, []).append(_score_case(support_task, top_k=4, support_scale=support_scale))

    return {
        "seeds": list(seeds),
        "rq2_1_budget_threshold": budget_samples,
        "rq2_2_ambiguity_threshold": ambiguity_samples,
        "rq2_3_support_threshold": support_samples,
    }


def run_object_aware_threshold_sampling(seeds: Sequence[int] | None = None) -> Dict[str, Any]:
    seed_values = list(seeds) if seeds else [1, 2, 3, 4, 5]
    collected = _collect_samples(seed_values)
    summary = _flatten_seed_samples(
        {
            "rq2_1_budget_threshold": collected["rq2_1_budget_threshold"],
            "rq2_2_ambiguity_threshold": collected["rq2_2_ambiguity_threshold"],
            "rq2_3_support_threshold": collected["rq2_3_support_threshold"],
        }
    )
    return {
        "schema_version": "object_support_threshold_sampling.v1",
        "seeds": seed_values,
        "summary": summary,
        "samples": collected,
    }


def render_object_aware_threshold_sampling_markdown(results: Dict[str, Any]) -> str:
    lines = [
        "# Object-Aware Threshold Sampling",
        "",
        "This stage freezes the Stage 2 benchmark shape and samples it across multiple seeds.",
        "",
        "Metrics reported here are aggregated over seeds as mean, std, and 95% CI.",
        "",
    ]
    summary = results.get("summary") or {}
    labels = {
        "rq2_1_budget_threshold": "RQ2.1 Budget Threshold",
        "rq2_2_ambiguity_threshold": "RQ2.2 Ambiguity Threshold",
        "rq2_3_support_threshold": "RQ2.3 Support Threshold",
    }
    for rq_name, rows in summary.items():
        lines.extend([f"## {labels.get(rq_name, rq_name)}", ""])
        if rq_name == "rq2_2_ambiguity_threshold":
            lines.append("| Parameter | Samples | Flip Probability | DBI Mean | DBI Std | DBI 95% CI | Margin Mean | Margin Std | Flip Distance Mean |")
            lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        else:
            lines.append("| Parameter | Samples | Flip Probability | DBI Mean | DBI Std | DBI 95% CI | Margin Mean | Margin Std | Flip Distance Mean |")
            lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for row in rows:
            dbi = row["dbi"]
            margin = row["decision_margin"]
            flip_distance = row["decision_flip_distance"]
            ci_text = ""
            if dbi["ci_low"] is not None and dbi["ci_high"] is not None:
                ci_text = f"{fmt(dbi['ci_low'])}..{fmt(dbi['ci_high'])}"
            lines.append(
                "| "
                + " | ".join(
                    [
                        fmt(row["parameter"]),
                        fmt(row["sample_count"]),
                        fmt(row["flip_probability"]),
                        fmt(dbi["mean"]),
                        fmt(dbi["std"]),
                        ci_text,
                        fmt(margin["mean"]),
                        fmt(margin["std"]),
                        fmt(flip_distance["mean"]),
                    ]
                )
                + " |"
            )
        lines.append("")
    return "\n".join(lines)


def write_object_aware_threshold_sampling_outputs(results: Dict[str, Any], output_dir: str | Path) -> Dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    json_path = output_path / "object_aware_threshold_sampling.json"
    markdown_path = output_path / "object_aware_threshold_sampling.md"
    json_path.write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    markdown_path.write_text(render_object_aware_threshold_sampling_markdown(results), encoding="utf-8")
    return {
        "json": json_path,
        "markdown": markdown_path,
    }

