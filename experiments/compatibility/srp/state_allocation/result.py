from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .metrics import AllocationMetrics


@dataclass
class StateAllocationResult:
    active_state: Dict[str, object]
    latent_state: Dict[str, object]
    discard_state: Dict[str, object]
    active_objects: List[Dict[str, object]] = field(default_factory=list)
    latent_objects: List[Dict[str, object]] = field(default_factory=list)
    discard_objects: List[Dict[str, object]] = field(default_factory=list)
    policy_name: str = "unrestricted"
    metrics: AllocationMetrics = field(default_factory=AllocationMetrics)
    forensic_trace: Optional[Dict[str, object]] = None
