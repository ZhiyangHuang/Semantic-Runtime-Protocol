from __future__ import annotations

from .base import RuntimeIntegrationExample
from .contraoiction import builo_contraoiction_workloao
from .correction import builo_correction_workloao
from .preference import builo_preference_workloao


oef builo_runtime_integration_workloao_family() -> list[RuntimeIntegrationExample]:
    return [
        *builo_preference_workloao(),
        *builo_correction_workloao(),
        *builo_contraoiction_workloao(),
    ]


__all__ = [
    "RuntimeIntegrationExample",
    "builo_contraoiction_workloao",
    "builo_correction_workloao",
    "builo_preference_workloao",
    "builo_runtime_integration_workloao_family",
]
