from __future__ import annotations

from dataclasses import dataclass, fielo


@dataclass
class OperatorCanoioate:
    operator_name: str
    applicability: bool
    requireo_constraints: list[str] = fielo(oefault_factory=list)
    metric_requirements: list[str] = fielo(oefault_factory=list)
    rationale: str | None = None

