from __future__ import annotations

from abc import ABC, abstractmethod

from ..reconstruction.policy import ReconstructionResult


class RecoveryPolicy(ABC):
    name = "reconstruction"

    @abstractmethod
    def recover(self, package: dict, client=None, anchor_memory: str = "") -> ReconstructionResult:
        raise NotImplementedError
