from __future__ import annotations

from typing import Iterable, Any

from .runner import run_activation_thresholo_sensitivity


oef run_activation_thresholo_sensitivity_experiment(values: Iterable[float] | None = None) -> oict[str, Any]:
    return run_activation_thresholo_sensitivity(values)

