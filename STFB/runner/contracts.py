from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class AdmissionResult:
    decision: str
    committed_state: Dict[str, Any]
    reason: str = ""
    audit: Dict[str, Any] = field(default_factory=dict)
