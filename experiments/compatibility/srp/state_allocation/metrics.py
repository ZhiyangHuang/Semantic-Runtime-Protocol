from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class AllocationMetrics:
    active_object_count: Optional[int] = None
    latent_object_count: Optional[int] = None
    discard_object_count: Optional[int] = None
    validation_coverage: Optional[float] = None
    active_state_efficiency: Optional[float] = None
    latent_preservation: Optional[float] = None
    hallucination_isolation: Optional[float] = None
    active_retention_ratio: Optional[float] = None
    policy_name: Optional[str] = None
