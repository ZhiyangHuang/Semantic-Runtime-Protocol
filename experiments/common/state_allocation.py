from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


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


class StateAllocationPolicy(ABC):
    """Partition recovered semantic objects without mutating them.

    Allocation policies may only assign recovered objects to active, latent,
    or discard buckets. They must not create, modify, merge, or repair objects.
    All policies operate on the same recovered state and differ only in their
    allocation objective and constraints.
    """

    name = "unrestricted"

    @abstractmethod
    def allocate(self, reconstructed_state: Any, task_context: Any) -> StateAllocationResult:
        raise NotImplementedError
