from __future__ import annotations

from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SensitivityResult:
    experiment_id: str
    parameter: str
    value: Any
    baseline_version: str
    timestamp: str
    metrics: dict[str, Any]
    observations: list[str] = field(default_factory=list)


def current_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()
