from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass(frozen=True)
class SensitivityExperimentConfig:
    parameter: str
    values: Sequence[Any]
    baseline: str = "default"
    scenario: str = "activation_update"
    dataset: str = "fixed_kernel_state"
    cycles: int = 1
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

