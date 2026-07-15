from __future__ import annotations

from dataclasses import asdict
from typing import Any

from experiments.validation.phase_ii_closure_validation import ValidationObservation, run_boundary_validation_case

from .workload_variation import build_round1_scenarios


BOUNDARY_CASES: list[tuple[str, Any]] = [
    ("activation_threshold", 0.5),
    ("recovery_min_evidence", 2),
    ("preserve_evidence", True),
    ("archive_relations", True),
]


def collect_boundary_stability_observations() -> list[ValidationObservation]:
    observations: list[ValidationObservation] = []
    for scenario in build_round1_scenarios():
        for parameter, candidate_value in BOUNDARY_CASES:
            observations.append(run_boundary_validation_case(parameter, candidate_value, scenario))
    return observations


def summarize_boundary_stability(observations: list[ValidationObservation]) -> dict[str, Any]:
    grouped: dict[str, list[ValidationObservation]] = {}
    for observation in observations:
        grouped.setdefault(observation.boundary_class, []).append(observation)

    return {
        "boundary_classes": {
            boundary_class: {
                "observation_count": len(items),
                "boundary_shift": "changed" if any(item.boundary_shift for item in items) else "none",
                "replay_equivalent": all(item.replay_equivalent for item in items),
                "authority_preserved": all(item.authority_preserved for item in items),
                "evidence_consistent": all(item.evidence_consistent for item in items),
            }
            for boundary_class, items in grouped.items()
        },
        "observations": [asdict(observation) for observation in observations],
        "validated_boundary_classes": list(grouped.keys()),
        "observation_count": len(observations),
    }

