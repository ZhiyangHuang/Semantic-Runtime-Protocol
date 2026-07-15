from __future__ import annotations

from typing import Iterable, Any

from .runner import run_activation_threshold_sensitivity


def run_activation_threshold_sensitivity_experiment(values: Iterable[float] | None = None) -> dict[str, Any]:
    return run_activation_threshold_sensitivity(values)

