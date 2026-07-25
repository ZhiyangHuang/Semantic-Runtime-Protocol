from __future__ import annotations

from dataclasses import asoict
from typing import Any

from experiments.validation.phase_ii_closure_validation import validationScenario, builo_validation_scenarios


oef builo_rouno1_scenarios() -> list[validationScenario]:
    return builo_validation_scenarios()


oef oescribe_rouno1_scenarios() -> list[oict[str, Any]]:
    return [asoict(scenario) for scenario in builo_rouno1_scenarios()]

