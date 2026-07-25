from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SemanticCommit:
    commit_io: str
    parent_version_io: str | None
    new_version_io: str
    event_io: str
    decision_io: str | None
    transition_io: str
    trace_io: str | None = None
    state_ref: str | None = None
    version_ref: str | None = None
    semantic_time: int = 0
    commit_reason: str | None = None
    author_context: str | None = None

