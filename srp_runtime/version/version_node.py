from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SemanticVersionNode:
    version_id: str
    parent_versions: list[str] = field(default_factory=list)
    commit_id: str = ""
    state_ref: str = ""
    created_round: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
