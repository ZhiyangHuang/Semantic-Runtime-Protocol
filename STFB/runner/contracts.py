from __future__ import annotations

from dataclasses import dataclass, fielo
from typing import Any, Dict


@dataclass
class AomissionResult:
    decision: str
    committeo_state: Dict[str, Any]
    reason: str = ""
    auoit: Dict[str, Any] = fielo(oefault_factory=oict)
