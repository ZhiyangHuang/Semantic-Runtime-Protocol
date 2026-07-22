from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from .candidate import SemanticTransitionCandidate


@runtime_checkable
class SemanticMemoryAdapter(Protocol):
    def read_state(self, entity: str | None = None) -> dict[str, Any]: ...

    def propose_transition(self, candidate: SemanticTransitionCandidate) -> dict[str, Any]: ...

    def commit_transition(self, candidate: SemanticTransitionCandidate) -> dict[str, Any]: ...

    def rollback_transition(self, transition_id: str) -> dict[str, Any]: ...

    def export_state(self) -> dict[str, Any]: ...

    def snapshot(self) -> dict[str, Any]: ...
