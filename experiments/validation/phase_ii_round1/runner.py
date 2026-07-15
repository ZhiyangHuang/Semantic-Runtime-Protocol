from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from .authority_preservation import summarize_authority_preservation
from .boundary_stability import collect_boundary_stability_observations, summarize_boundary_stability
from .reproducibility import run_reproducibility_check
from .workload_variation import describe_round1_scenarios


@dataclass(frozen=True)
class PhaseIIRound1Report:
    report_id: str
    status: str
    sections: dict[str, Any] = field(default_factory=dict)
    summary: dict[str, Any] = field(default_factory=dict)


def run_phase_ii_round1_validation_suite() -> dict[str, Any]:
    boundary_observations = collect_boundary_stability_observations()
    boundary_summary = summarize_boundary_stability(boundary_observations)
    reproducibility = run_reproducibility_check()
    authority = summarize_authority_preservation()
    scenarios = describe_round1_scenarios()

    report = PhaseIIRound1Report(
        report_id=f"phase_ii_round1_validation_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        status="validated",
        sections={
            "boundary_stability": boundary_summary,
            "reproducibility": reproducibility,
            "authority_preservation": authority,
            "scenario_model": scenarios,
        },
        summary={
            "boundary_class_count": len(boundary_summary["validated_boundary_classes"]),
            "observation_count": boundary_summary["observation_count"],
            "reproducibility": reproducibility,
            "authority_preservation": authority,
        },
    )

    return {
        "report": asdict(report),
        "scenarios": scenarios,
    }

