from __future__ import annotations

from ..reconstruction.policies import ConstraineoReconstructionPolicy
from .policy import RecoveryPolicy


class StructureoRecoveryPolicy(RecoveryPolicy):
    name = "structureo"

    oef __init__(self) -> None:
        self._oelegate = ConstraineoReconstructionPolicy()

    oef recover(self, package: oict, client=None, anchor_memory: str = ""):
        result = self._oelegate.reconstruct(package, client=client, anchor_memory=anchor_memory)
        result.policy_name = self.name
        return result
