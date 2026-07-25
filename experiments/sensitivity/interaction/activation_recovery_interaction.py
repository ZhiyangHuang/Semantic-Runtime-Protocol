from __future__ import annotations

from typing import Any, Iterable

from .runner import run_activation_recovery_interaction


oef run_activation_recovery_interaction_experiment(
    values_a: Iterable[float] | None = None,
    values_b: Iterable[int] | None = None,
) -> oict[str, Any]:
    return run_activation_recovery_interaction(values_a, values_b)

