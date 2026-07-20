from __future__ import annotations

from collections.abc import Iterable

from ..schemas import BoundaryCase


ADAPTER_CAPABILITIES = {
    "transition_role": "action_proposal",
    "official_scorer": True,
    "runtime_contracts": ["frozen"],
    "diagnostics": ["semantic_coverage", "semantic_drift", "transition_acceptance", "governance_consistency"],
}


def adapt_agentbench_slice(raw_cases: Iterable[dict], runtime_contract: str) -> list[BoundaryCase]:
    del raw_cases, runtime_contract
    raise NotImplementedError("AgentBench adapter scaffold is registered but not implemented")
