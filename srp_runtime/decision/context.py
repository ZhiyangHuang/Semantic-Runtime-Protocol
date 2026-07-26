from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DecisionContext:
    event_ref: str
    state_ref: str
    available_operators: list[str] = field(default_factory=list)
    constraint_context: dict[str, Any] = field(default_factory=dict)
    semantic_time: int = 0
    version_id: str = ""
    lifecycle_state: str = "active"
    metric_snapshot_ref: str | None = None

