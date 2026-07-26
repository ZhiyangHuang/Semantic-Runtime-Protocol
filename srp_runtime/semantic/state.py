from __future__ import annotations

from dataclasses import dataclass, field
import copy
from typing import Any

from .graph import SemanticGraph
from .unit import SemanticUnit


@dataclass
class SemanticState:
    state_id: str
    units: dict[str, SemanticUnit] = field(default_factory=dict)
    graph: SemanticGraph = field(default_factory=SemanticGraph)
    version_id: str = ""
    timestamp_round: int = 0

    def snapshot(self) -> "SemanticState":
        return copy.deepcopy(self)

    def state_ref(self) -> str:
        version_part = self.version_id if self.version_id else str(self.timestamp_round)
        return f"{self.state_id}:{version_part}"


@dataclass(frozen=True)
class SemanticStateView:
    state_id: str
    version_id: str
    timestamp_round: int
    unit_ids: list[str] = field(default_factory=list)
    graph_summary: dict[str, Any] = field(default_factory=dict)
