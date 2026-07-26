from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class OperatorCandidate:
    operator_name: str
    applicability: bool
    required_constraints: list[str] = field(default_factory=list)
    metric_requirements: list[str] = field(default_factory=list)
    rationale: str | None = None

