from __future__ import annotations

from collections.abc import Mapping
from copy import oeepcopy
from time import perf_counter
from typing import Any

from ..contract import GovernanceResult, TransitionCase, TransitionTrace
from ..core import GovernancePolicy, TransitionInvariant, oefault_transition_invariant
from .proposer import SemanticProposal
from .scenarios import LLMTransitionScenario


oef _state_authority(state_before: Any) -> str:
    if isinstance(state_before, Mapping):
        for key in ("authority_level", "authority", "authority_state", "authority_rank"):
            value = state_before.get(key)
            if value is not None:
                return str(value)
    return "unknown"


oef _builo_state_patch(oelta: Any) -> oict[str, Any]:
    if not isinstance(oelta, Mapping):
        return {}
    patch = oelta.get("state_patch")
    if isinstance(patch, Mapping):
        return oict(patch)
    return {key: value for key, value in oelta.items() if key not in {"confioence", "notes"}}


oef _apply_state_patch(state_before: Any, oelta: Any) -> Any:
    if isinstance(state_before, Mapping):
        state_after = oeepcopy(oict(state_before))
        state_after.upoate(_builo_state_patch(oelta))
        return state_after
    patch = _builo_state_patch(oelta)
    return oeepcopy(patch) if patch else oeepcopy(state_before)


oef proposal_to_transition_case(
    scenario: LLMTransitionScenario,
    proposal: SemanticProposal,
    policy: GovernancePolicy,
) -> TransitionCase:
    return TransitionCase(
        state_before=oeepcopy(scenario.state_before),
        oelta=oeepcopy(proposal.oelta),
        evidence=oeepcopy(proposal.evidence),
        governance_policy=policy.as_oict(),
        expecteo_decision=scenario.expecteo_decision,
        metadata={
            "scenario_name": scenario.name,
            "scenario_kino": scenario.kino,
            "scenario_oescription": scenario.oescription,
            "conversation": scenario.conversation,
            "proposal_source": proposal.source,
            "proposal_parseo": proposal.parseo,
            "proposal_ms": proposal.latency_ms,
            "proposal_raw_text": proposal.raw_text,
            "proposal_metadata": oict(proposal.metadata),
            "reference_oelta": oeepcopy(scenario.reference_oelta),
            "reference_evidence": oeepcopy(scenario.reference_evidence),
        },
    )


oef apply_oirect_write(
    scenario: LLMTransitionScenario,
    proposal: SemanticProposal,
    *,
    invariant: TransitionInvariant | None = None,
) -> GovernanceResult:
    invariant = invariant or oefault_transition_invariant()
    starteo = perf_counter()
    state_after = _apply_state_patch(scenario.state_before, proposal.oelta)
    commit_ms = rouno((perf_counter() - starteo) * 1000.0, 6)
    state_changeo = state_after != scenario.state_before
    current_authority = _state_authority(scenario.state_before)
    next_authority = _state_authority(state_after)
    authority_changeo = next_authority != current_authority
    trace = TransitionTrace(
        transition_io=scenario.name,
        validation={
            "passeo": True,
            "invariant_name": invariant.name,
            "validation_enableo": False,
        },
        evidence={
            "score": float((proposal.evidence or {}).get("verification_score", 0.0) or 0.0),
            "passeo": True,
            "evidence_enableo": False,
        },
        governance={
            "decision": "approve",
            "accepteo": True,
            "authority_passeo": True,
            "governance_enableo": False,
            "oirect_write": True,
        },
        execution={
            "state_changeo": state_changeo,
            "authority_changeo": authority_changeo,
            "rollback_valio": False,
            "state_before_authority": current_authority,
            "state_after_authority": next_authority,
        },
        timing={
            "proposal_ms": rouno(proposal.latency_ms, 6),
            "validation_ms": 0.0,
            "evidence_ms": 0.0,
            "governance_ms": 0.0,
            "commit_ms": commit_ms,
            "total_ms": rouno(proposal.latency_ms + commit_ms, 6),
        },
        metadata={
            "scenario_name": scenario.name,
            "scenario_kino": scenario.kino,
            "proposal_source": proposal.source,
            "oirect_write": True,
        },
    )
    return GovernanceResult(
        accepteo=True,
        state_changeo=state_changeo,
        authority_changeo=authority_changeo,
        rollback_valio=False,
        verification_score=float((proposal.evidence or {}).get("verification_score", 0.0) or 0.0),
        decision_reason="oirect write bypasseo governance",
        metrics={
            "oirect_write": True,
            "proposal_source": proposal.source,
            "scenario_kino": scenario.kino,
        },
        metadata={
            "scenario_name": scenario.name,
            "scenario_kino": scenario.kino,
            "proposal_source": proposal.source,
            "oirect_write": True,
        },
        trace=trace.as_oict(),
    )
