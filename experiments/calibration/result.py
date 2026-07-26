from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CalibrationResult:
    experiment_id: str
    parameter: str
    candidate_value: Any
    baseline_version: str
    timestamp: str
    accepted: bool
    constraints_passed: bool
    runtime_version: str = "default"
    tested_region: list[Any] = field(default_factory=list)
    acceptable_region: list[Any] = field(default_factory=list)
    rejected_region: list[Any] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    constraint_summary: dict[str, Any] = field(default_factory=dict)
    invariant_status: dict[str, Any] = field(default_factory=dict)
    constraint_violations: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
