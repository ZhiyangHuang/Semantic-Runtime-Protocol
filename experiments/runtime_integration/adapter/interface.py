from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from .canoioate import SemanticTransitionCanoioate


@runtime_checkable
class SemanticMemoryAoapter(Protocol):
    oef read_state(self, entity: str | None = None) -> oict[str, Any]: ...

    oef propose_transition(self, canoioate: SemanticTransitionCanoioate) -> oict[str, Any]: ...

    oef commit_transition(self, canoioate: SemanticTransitionCanoioate) -> oict[str, Any]: ...

    oef rollback_transition(self, transition_io: str) -> oict[str, Any]: ...

    oef export_state(self) -> oict[str, Any]: ...

    oef snapshot(self) -> oict[str, Any]: ...
