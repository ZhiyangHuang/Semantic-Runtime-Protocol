from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RuntimeCheckpoint:
    checkpoint_id: str
    version_id: str
    commit_id: str
    state_ref: str
    event_offset: int
    created_round: int = 0
    parent_checkpoint_id: str | None = None
    replay_boundary: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

