from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CalibrationCandidate:
    parameter: str
    value: Any
    region_label: str | None = None
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "parameter": self.parameter,
            "value": self.value,
            "region_label": self.region_label,
            "notes": self.notes,
            "metadata": dict(self.metadata),
        }

