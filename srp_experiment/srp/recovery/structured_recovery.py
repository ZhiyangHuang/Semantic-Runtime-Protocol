from __future__ import annotations

from ..reconstruction.policies import ConstrainedReconstructionPolicy
from .policy import RecoveryPolicy


class StructuredRecoveryPolicy(RecoveryPolicy):
    name = "structured"

    def __init__(self) -> None:
        self._delegate = ConstrainedReconstructionPolicy()

    def recover(self, package: dict, client=None, anchor_memory: str = ""):
        result = self._delegate.reconstruct(package, client=client, anchor_memory=anchor_memory)
        result.policy_name = self.name
        return result
