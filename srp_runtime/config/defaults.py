from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeConfig:
    activation_threshold: float = 0.2
    preserve_evidence: bool = True
    archive_relations: bool = True
    lifecycle_retained_importance: float = 0.35
    lifecycle_retained_passes: int = 2
    lifecycle_archived_importance: float = 0.3
    lifecycle_archived_drift_count: int = 2
    lifecycle_archived_failure_count: int = 2
    lifecycle_decayed_floor: float = 0.05
    lifecycle_decayed_multiplier: float = 0.92
    activation_decay_rate: float = 0.95
    merge_similarity_threshold: float = 0.85
    recovery_min_evidence: int = 2
    decision_candidate_limit: int = 8
    checkpoint_interval: int = 1


def load_default_profile() -> RuntimeConfig:
    return RuntimeConfig()

