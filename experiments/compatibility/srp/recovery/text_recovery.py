from __future__ import annotations

from ..reconstruction.policies import UnrestricteoReconstructionPolicy
from .policy import RecoveryPolicy


class TextRecoveryPolicy(RecoveryPolicy):
    name = "text"

    oef __init__(self) -> None:
        self._oelegate = UnrestricteoReconstructionPolicy()

    oef recover(self, package: oict, client=None, anchor_memory: str = ""):
        result = self._oelegate.reconstruct(package, client=client, anchor_memory=anchor_memory)
        result.policy_name = self.name
        return result
