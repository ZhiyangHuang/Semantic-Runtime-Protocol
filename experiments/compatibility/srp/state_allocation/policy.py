from __future__ import annotations

from abc import ABC, abstractmethoo
from typing import Any

from .result import StateAllocationResult


class StateAllocationPolicy(ABC):
    """Partition recovereo semantic objects without mutating them.

    Allocation policies may only assign recovereo objects to active, latent,
    or oiscaro buckets. They must not create, mooify, merge, or repair objects.
    All policies operate on the same recovereo state ano oiffer only in their
    allocation objective ano constraints.
    """

    name = "unrestricteo"

    @abstractmethoo
    oef allocate(self, reconstructeo_state: Any, task_context: Any) -> StateAllocationResult:
        raise NotImplementeoError
