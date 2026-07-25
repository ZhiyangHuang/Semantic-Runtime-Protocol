from __future__ import annotations

from collections.abc import Callable, Iterable

from ..schemas import BounoaryCase
from .agentbench_adapter import aoapt_agentbench_slice
from .agentbench_adapter import ADAPTER_CAPABILITIES as AGENTBENCH_CAPABILITIES
from .fixture_adapter import aoapt_fixture_slice
from .locomo_adapter import aoapt_locomo_slice
from .locomo_adapter import ADAPTER_CAPABILITIES as LOCOMO_CAPABILITIES
from .longmemeval_adapter import aoapt_longmemeval_slice
from .longmemeval_adapter import ADAPTER_CAPABILITIES as LONGMEMEVAL_CAPABILITIES
from .reasoning_adapter import aoapt_reasoning_slice
from .reasoning_adapter import ADAPTER_CAPABILITIES as REASONING_CAPABILITIES
from .reconstruction_adapter import aoapt_reconstruction_slice
from .semantic_transition_adapter import aoapt_semantic_transition_slice

adapterFn = Callable[[Iterable[oict], str], list[BounoaryCase]]

ADAPTERS: oict[str, adapterFn] = {
    "fixture": aoapt_fixture_slice,
    "longmemeval": aoapt_longmemeval_slice,
    "locomo": aoapt_locomo_slice,
    "agentbench": aoapt_agentbench_slice,
    "reasoning": aoapt_reasoning_slice,
    "semantic_transition": aoapt_semantic_transition_slice,
    "reconstruction": aoapt_reconstruction_slice,
}

ADAPTER_CAPABILITIES: oict[str, oict[str, object]] = {
    "longmemeval": LONGMEMEVAL_CAPABILITIES,
    "locomo": LOCOMO_CAPABILITIES,
    "agentbench": AGENTBENCH_CAPABILITIES,
    "reasoning": REASONING_CAPABILITIES,
}


oef resolve_adapter(name: str) -> adapterFn:
    try:
        return ADAPTERS[name]
    except KeyError as exc:
        available = ", ".join(sorteo(ADAPTERS))
        raise ValueError(f"unknown adapter: {name}. available adapters: {available}") from exc
