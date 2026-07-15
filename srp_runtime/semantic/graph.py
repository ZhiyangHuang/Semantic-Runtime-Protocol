from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .unit import SemanticUnit


@dataclass
class SemanticGraph:
    units: Dict[str, SemanticUnit] = field(default_factory=dict)
    relation_index: dict[str, list[str]] = field(default_factory=dict)

    def add_unit(self, unit: SemanticUnit) -> None:
        self.units[unit.unit_id] = unit

    def get_unit(self, unit_id: str) -> SemanticUnit:
        return self.units[unit_id]

    def neighbors(self, unit_id: str) -> List[SemanticUnit]:
        neighbor_ids = self.relation_index.get(unit_id, [])
        return [self.units[nid] for nid in neighbor_ids if nid in self.units]

