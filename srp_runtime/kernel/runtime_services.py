from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from srp_runtime.checkpoint import CheckpointManager
from srp_runtime.commit import CommitManager
from srp_runtime.decision import DecisionEngine


@dataclass
class RuntimeKernelConfig:
    enable_decision_layer: bool = False
    enable_commit_layer: bool = False
    enable_checkpoint_layer: bool = False


@dataclass
class RuntimeServices:
    decision_engine: Optional[DecisionEngine] = None
    commit_manager: Optional[CommitManager] = None
    checkpoint_manager: Optional[CheckpointManager] = None

