from __future__ import annotations

from dataclasses import asdict
from typing import Any

from experiments.validation.phase_ii_closure_validation import ValidationScenario, build_validation_scenarios


def build_round1_scenarios() -> list[ValidationScenario]:
    return build_validation_scenarios()


def describe_round1_scenarios() -> list[dict[str, Any]]:
    return [asdict(scenario) for scenario in build_round1_scenarios()]

