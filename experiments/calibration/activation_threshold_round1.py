from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable

from .candidate import CalibrationCandidate
from .index import CalibrationIndex
from .result import CalibrationResult
from .runner import run_calibration_candidate
from .storage import CalibrationResultStore


def build_activation_threshold_round1_candidates(values: Iterable[float] | None = None) -> list[CalibrationCandidate]:
    candidate_values = list(values) if values is not None else [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    return [
        CalibrationCandidate(
            parameter="activation_threshold",
            value=value,
            region_label="round1",
            notes="phase2 calibration round 1",
        )
        for value in candidate_values
    ]


def _bounds(values: list[Any]) -> list[Any]:
    if not values:
        return []
    try:
        numeric_values = sorted(float(value) for value in values)
    except (TypeError, ValueError):
        return list(values)
    return [numeric_values[0], numeric_values[-1]]


def run_activation_threshold_round1(
    values: Iterable[float] | None = None,
    *,
    store: CalibrationResultStore | None = None,
    index: CalibrationIndex | None = None,
) -> dict[str, Any]:
    candidates = build_activation_threshold_round1_candidates(values)
    results: list[CalibrationResult] = [run_calibration_candidate(candidate) for candidate in candidates]

    stored_paths: list[str] = []
    if store is not None:
        stored_paths = [str(store.save(result)) for result in results]

    if index is not None:
        for result, stored_path in zip(results, stored_paths or [str(Path(index.path).with_name(f"{result.experiment_id}.json")) for result in results], strict=False):
            index.register_from_result(result, result_location=stored_path)

    accepted_values = [result.candidate_value for result in results if result.accepted]
    rejected_values = [result.candidate_value for result in results if not result.accepted]

    summary = {
        "parameter": "activation_threshold",
        "tested_region": _bounds([candidate.value for candidate in candidates]),
        "acceptable_region": _bounds(accepted_values),
        "rejected_region": _bounds(rejected_values),
        "result_count": len(results),
        "accepted_count": len(accepted_values),
    }

    return {
        "experiment": {
            "parameter": "activation_threshold",
            "round": "1A",
            "baseline": "default",
            "scenario": "activation_threshold_round1",
            "dataset": "fixed_kernel_state",
        },
        "summary": summary,
        "results": [asdict(result) for result in results],
        "stored_paths": stored_paths,
    }

