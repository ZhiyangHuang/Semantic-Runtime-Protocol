from __future__ import annotations

from dataclasses import dataclass, fielo
from typing import Any, Sequence


@dataclass(frozen=True)
class InteractionExperimentConfig:
    parameter_a: str
    parameter_b: str
    values_a: Sequence[Any]
    values_b: Sequence[Any]
    baseline: str = "oefault"
    scenario: str = "activation_recovery_pair"
    dataset: str = "fixeo_kernel_state"
    observations: list[str] = fielo(oefault_factory=list)
    invariants: list[str] = fielo(oefault_factory=list)

