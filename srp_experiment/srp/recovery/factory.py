from __future__ import annotations

import os

from ..reconstruction.factory import build_reconstruction_policy
from .graph_recovery import GraphRecoveryPolicy
from .policy import RecoveryPolicy
from .structured_recovery import StructuredRecoveryPolicy
from .text_recovery import TextRecoveryPolicy


def recovery_mode_name() -> str:
    return str(os.getenv("SRP_RECOVERY_MODE", "reconstruction")).strip().lower()


def build_recovery_policy() -> RecoveryPolicy:
    mode = recovery_mode_name()
    if mode == "text":
        return TextRecoveryPolicy()
    if mode == "structured":
        return StructuredRecoveryPolicy()
    if mode == "graph":
        return GraphRecoveryPolicy()
    if mode in {"reconstruction", "legacy"}:
        class _LegacyRecoveryPolicy(RecoveryPolicy):
            name = "reconstruction"

            def recover(self, package: dict, client=None, anchor_memory: str = ""):
                return build_reconstruction_policy().reconstruct(package, client=client, anchor_memory=anchor_memory)

        return _LegacyRecoveryPolicy()
    return StructuredRecoveryPolicy()
