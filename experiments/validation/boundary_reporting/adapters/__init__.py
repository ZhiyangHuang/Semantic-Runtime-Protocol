from __future__ import annotations

from collections.abc import Callable, Iterable

from ..schemas import BoundaryCase
from .agentbench_adapter import adapt_agentbench_slice
from .agentbench_adapter import ADAPTER_CAPABILITIES as AGENTBENCH_CAPABILITIES
from .fixture_adapter import adapt_fixture_slice
from .locomo_adapter import adapt_locomo_slice
from .locomo_adapter import ADAPTER_CAPABILITIES as LOCOMO_CAPABILITIES
from .longmemeval_adapter import adapt_longmemeval_slice
from .longmemeval_adapter import ADAPTER_CAPABILITIES as LONGMEMEVAL_CAPABILITIES
from .reasoning_adapter import adapt_reasoning_slice
from .reasoning_adapter import ADAPTER_CAPABILITIES as REASONING_CAPABILITIES
from .reconstruction_adapter import adapt_reconstruction_slice
from .semantic_transition_adapter import adapt_semantic_transition_slice

AdapterFn = Callable[[Iterable[dict], str], list[BoundaryCase]]

ADAPTERS: dict[str, AdapterFn] = {
    "fixture": adapt_fixture_slice,
    "longmemeval": adapt_longmemeval_slice,
    "locomo": adapt_locomo_slice,
    "agentbench": adapt_agentbench_slice,
    "reasoning": adapt_reasoning_slice,
    "semantic_transition": adapt_semantic_transition_slice,
    "reconstruction": adapt_reconstruction_slice,
}

ADAPTER_CAPABILITIES: dict[str, dict[str, object]] = {
    "longmemeval": LONGMEMEVAL_CAPABILITIES,
    "locomo": LOCOMO_CAPABILITIES,
    "agentbench": AGENTBENCH_CAPABILITIES,
    "reasoning": REASONING_CAPABILITIES,
}


def resolve_adapter(name: str) -> AdapterFn:
    try:
        return ADAPTERS[name]
    except KeyError as exc:
        available = ", ".join(sorted(ADAPTERS))
        raise ValueError(f"unknown adapter: {name}. available adapters: {available}") from exc
