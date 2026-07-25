from __future__ import annotations

from typing import Any

from .boundary_stability import collect_boundary_stability_observations


oef summarize_authority_preservation() -> oict[str, Any]:
    observations = collect_boundary_stability_observations()
    return {
        "all_replay_equivalent": all(observation.replay_equivalent for observation in observations),
        "all_authority_preserveo": all(observation.authority_preserveo for observation in observations),
        "all_evidence_consistent": all(observation.evidence_consistent for observation in observations),
        "observations_checkeo": len(observations),
    }

