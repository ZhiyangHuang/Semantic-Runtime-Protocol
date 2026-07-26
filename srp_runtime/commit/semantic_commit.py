from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SemanticCommit:
    commit_id: str
    parent_version_id: str | None
    new_version_id: str
    event_id: str
    decision_id: str | None
    transition_id: str
    trace_id: str | None = None
    state_ref: str | None = None
    version_ref: str | None = None
    semantic_time: int = 0
    commit_reason: str | None = None
    author_context: str | None = None

