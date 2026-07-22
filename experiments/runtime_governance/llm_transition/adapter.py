from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from time import perf_counter
from typing import Any

from ..contract import GovernanceResult, TransitionCase, TransitionTrace
from ..core import GovernancePolicy, TransitionInvariant, default_transition_invariant
from .proposer import SemanticProposal
from .scenarios import LLMTransitionScenario


def _state_authority(state_before: Any) -> str:
    if isinstance(state_before, Mapping):
        for key in ("authority_level", "authority", "authority_state", "authority_rank"):
            value = state_before.get(key)
            if value is not None:
                return str(value)
    return "unknown"


def _build_state_patch(delta: Any) -> dict[str, Any]:
    if not isinstance(delta, Mapping):
        return {}
    patch = delta.get("state_patch")
    if isinstance(patch, Mapping):
        return dict(patch)
    return {key: value for key, value in delta.items() if key not in {"confidence", "notes"}}


def _apply_state_patch(state_before: Any, delta: Any) -> Any:
    if isinstance(state_before, Mapping):
        state_after = deepcopy(dict(state_before))
        state_after.update(_build_state_patch(delta))
        return state_after
    patch = _build_state_patch(delta)
    return deepcopy(patch) if patch else deepcopy(state_before)


def proposal_to_transition_case(
    scenario: LLMTransitionScenario,
    proposal: SemanticProposal,
    policy: GovernancePolicy,
) -> TransitionCase:
    return TransitionCase(
        state_before=deepcopy(scenario.state_before),
        delta=deepcopy(proposal.delta),
        evidence=deepcopy(proposal.evidence),
        governance_policy=policy.as_dict(),
        expected_decision=scenario.expected_decision,
        metadata={
            "scenario_name": scenario.name,
            "scenario_kind": scenario.kind,
            "scenario_description": scenario.description,
            "conversation": scenario.conversation,
            "proposal_source": proposal.source,
            "proposal_parsed": proposal.parsed,
            "proposal_ms": proposal.latency_ms,
            "proposal_raw_text": proposal.raw_text,
            "proposal_metadata": dict(proposal.metadata),
            "reference_delta": deepcopy(scenario.reference_delta),
            "reference_evidence": deepcopy(scenario.reference_evidence),
        },
    )


def apply_direct_write(
    scenario: LLMTransitionScenario,
    proposal: SemanticProposal,
    *,
    invariant: TransitionInvariant | None = None,
) -> GovernanceResult:
    invariant = invariant or default_transition_invariant()
    started = perf_counter()
    state_after = _apply_state_patch(scenario.state_before, proposal.delta)
    commit_ms = round((perf_counter() - started) * 1000.0, 6)
    state_changed = state_after != scenario.state_before
    current_authority = _state_authority(scenario.state_before)
    next_authority = _state_authority(state_after)
    authority_changed = next_authority != current_authority
    trace = TransitionTrace(
        transition_id=scenario.name,
        validation={
            "passed": True,
            "invariant_name": invariant.name,
            "validation_enabled": False,
        },
        evidence={
            "score": float((proposal.evidence or {}).get("verification_score", 0.0) or 0.0),
            "passed": True,
            "evidence_enabled": False,
        },
        governance={
            "decision": "approve",
            "accepted": True,
            "authority_passed": True,
            "governance_enabled": False,
            "direct_write": True,
        },
        execution={
            "state_changed": state_changed,
            "authority_changed": authority_changed,
            "rollback_valid": False,
            "state_before_authority": current_authority,
            "state_after_authority": next_authority,
        },
        timing={
            "proposal_ms": round(proposal.latency_ms, 6),
            "validation_ms": 0.0,
            "evidence_ms": 0.0,
            "governance_ms": 0.0,
            "commit_ms": commit_ms,
            "total_ms": round(proposal.latency_ms + commit_ms, 6),
        },
        metadata={
            "scenario_name": scenario.name,
            "scenario_kind": scenario.kind,
            "proposal_source": proposal.source,
            "direct_write": True,
        },
    )
    return GovernanceResult(
        accepted=True,
        state_changed=state_changed,
        authority_changed=authority_changed,
        rollback_valid=False,
        verification_score=float((proposal.evidence or {}).get("verification_score", 0.0) or 0.0),
        decision_reason="direct write bypassed governance",
        metrics={
            "direct_write": True,
            "proposal_source": proposal.source,
            "scenario_kind": scenario.kind,
        },
        metadata={
            "scenario_name": scenario.name,
            "scenario_kind": scenario.kind,
            "proposal_source": proposal.source,
            "direct_write": True,
        },
        trace=trace.as_dict(),
    )
