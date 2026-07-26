from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class CalibrationCriteria:
    replay_equivalent: bool = True
    state_transition_equivalent: bool = True
    recovery_success: bool | None = None
    evidence_usage_consistent: bool | None = None
    max_violation_count: int = 0

    def evaluate(self, metrics: Mapping[str, Any]) -> tuple[bool, list[str]]:
        violations: list[str] = []

        if self.replay_equivalent and not bool(metrics.get("replay_equivalent", False)):
            violations.append("replay_equivalent")
        if self.state_transition_equivalent and not bool(metrics.get("state_transition_equivalent", False)):
            violations.append("state_transition_equivalence")
        if self.recovery_success is True and not bool(metrics.get("recovery_success", False)):
            violations.append("recovery_success")
        if self.evidence_usage_consistent is True and not bool(metrics.get("evidence_usage_consistent", False)):
            violations.append("evidence_usage_consistent")

        passed = len(violations) <= self.max_violation_count
        return passed, violations
