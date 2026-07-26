from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass(frozen=True)
class InteractionExperimentConfig:
    parameter_a: str
    parameter_b: str
    values_a: Sequence[Any]
    values_b: Sequence[Any]
    baseline: str = "default"
    scenario: str = "activation_recovery_pair"
    dataset: str = "fixed_kernel_state"
    observations: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)

