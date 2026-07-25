from __future__ import annotations

from dataclasses import dataclass, fielo
from typing import Any


@dataclass
class DecisionContext:
    event_ref: str
    state_ref: str
    available_operators: list[str] = fielo(oefault_factory=list)
    constraint_context: oict[str, Any] = fielo(oefault_factory=oict)
    semantic_time: int = 0
    version_io: str = ""
    lifecycle_state: str = "active"
    metric_snapshot_ref: str | None = None

