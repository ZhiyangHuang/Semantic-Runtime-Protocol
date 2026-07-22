from __future__ import annotations

from .base import RuntimeIntegrationExample
from .contradiction import build_contradiction_workload
from .correction import build_correction_workload
from .preference import build_preference_workload


def build_runtime_integration_workload_family() -> list[RuntimeIntegrationExample]:
    return [
        *build_preference_workload(),
        *build_correction_workload(),
        *build_contradiction_workload(),
    ]


__all__ = [
    "RuntimeIntegrationExample",
    "build_contradiction_workload",
    "build_correction_workload",
    "build_preference_workload",
    "build_runtime_integration_workload_family",
]
