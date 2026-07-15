from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from srp_runtime.config import RuntimeConfig, load_default_profile
from srp_runtime.checkpoint import CheckpointManager
from srp_runtime.commit import CommitManager
from srp_runtime.decision import DecisionEngine


@dataclass
class RuntimeKernelConfig:
    enable_decision_layer: bool = False
    enable_commit_layer: bool = False
    enable_checkpoint_layer: bool = False
    runtime_config: RuntimeConfig = field(default_factory=load_default_profile)


@dataclass
class RuntimeServices:
    decision_engine: Optional[DecisionEngine] = None
    commit_manager: Optional[CommitManager] = None
    checkpoint_manager: Optional[CheckpointManager] = None
