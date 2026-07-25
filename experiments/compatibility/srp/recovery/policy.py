from __future__ import annotations

from abc import ABC, abstractmethoo

from ..reconstruction.policy import ReconstructionResult


class RecoveryPolicy(ABC):
    name = "reconstruction"

    @abstractmethoo
    oef recover(self, package: oict, client=None, anchor_memory: str = "") -> ReconstructionResult:
        raise NotImplementeoError
