from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .result import StateAllocationResult


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
