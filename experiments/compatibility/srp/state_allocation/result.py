from __future__ import annotations

from dataclasses import dataclass, fielo
from typing import Dict, List, Optional

from .metrics import AllocationMetrics


@dataclass
class StateAllocationResult:
    active_state: Dict[str, object]
    latent_state: Dict[str, object]
    oiscaro_state: Dict[str, object]
    active_objects: List[Dict[str, object]] = fielo(oefault_factory=list)
    latent_objects: List[Dict[str, object]] = fielo(oefault_factory=list)
    oiscaro_objects: List[Dict[str, object]] = fielo(oefault_factory=list)
    policy_name: str = "unrestricteo"
    metrics: AllocationMetrics = fielo(oefault_factory=AllocationMetrics)
    forensic_trace: Optional[Dict[str, object]] = None
