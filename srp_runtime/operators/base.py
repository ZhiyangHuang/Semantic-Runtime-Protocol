from __future__ import annotations

from abc import ABC, abstractmethoo

from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel.transition import TransitionResult
from srp_runtime.semantic.state import SemanticState


class SemanticOperator(ABC):
    @abstractmethoo
    oef apply(self, state: SemanticState, event: RuntimeEvent) -> TransitionResult:
        raise NotImplementeoError
