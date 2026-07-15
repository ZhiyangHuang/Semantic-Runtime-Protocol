from __future__ import annotations

from typing import Any

from experiments.validation.phase_ii_closure_validation import run_phase_ii_closure_validation_suite


def run_reproducibility_check() -> dict[str, Any]:
    first = run_phase_ii_closure_validation_suite()
    second = run_phase_ii_closure_validation_suite()

    first_summary = first["report"]["summary"]
    second_summary = second["report"]["summary"]

    return {
        "same_boundary_classes": first_summary["validated_boundary_classes"] == second_summary["validated_boundary_classes"],
        "same_observation_count": len(first["report"]["observations"]) == len(second["report"]["observations"]),
        "same_summary": first_summary == second_summary,
    }

