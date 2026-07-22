from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from time import perf_counter
from typing import Any

from ..contract import GovernanceResult, TransitionCase, TransitionTrace
from .policies import GovernanceDecision, GovernancePolicy, TransitionInvariant, default_transition_invariant

_RESERVED_DELTA_KEYS = {
    "state_patch",
    "updates",
    "patch",
    "requested_authority",
    "authority_update",
    "authority_level",
    "violates_invariant",
    "invariant_violation",
    "optimization_pressure",
    "confidence",
    "score",
    "evidence_score",
}


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    return {"value": value}


def _state_authority(state_before: Any) -> str:
    if isinstance(state_before, Mapping):
        for key in ("authority_level", "authority", "authority_state", "authority_rank"):
            value = state_before.get(key)
            if value is not None:
                return str(value)
    return "unknown"


def _transition_id(case: TransitionCase) -> str:
    if isinstance(case.metadata, Mapping):
        for key in ("transition_id", "case_id", "source_case_id", "id"):
            value = case.metadata.get(key)
            if value is not None:
                return str(value)
    if isinstance(case.state_before, Mapping):
        for key in ("transition_id", "case_id", "id"):
            value = case.state_before.get(key)
            if value is not None:
                return str(value)
    return "unknown"


def _proposal_latency_ms(case: TransitionCase) -> float:
    if not isinstance(case.metadata, Mapping):
        return 0.0
    for key in ("proposal_ms", "proposal_latency_ms"):
        value = case.metadata.get(key)
        if value is not None:
            try:
                return round(float(value), 6)
            except (TypeError, ValueError):
                continue
    timing = case.metadata.get("timing")
    if isinstance(timing, Mapping):
        value = timing.get("proposal_ms")
        if value is not None:
            try:
                return round(float(value), 6)
            except (TypeError, ValueError):
                return 0.0
    return 0.0


def _requested_authority(delta: Any) -> str | None:
    if isinstance(delta, Mapping):
        for key in ("requested_authority", "authority_update", "authority_level"):
            value = delta.get(key)
            if value is not None:
                return str(value)
    return None


def _evidence_score(evidence: Any) -> float:
    if evidence is None:
        return 0.0
    if isinstance(evidence, bool):
        return 1.0 if evidence else 0.0
    if isinstance(evidence, (int, float)):
        value = float(evidence)
        if value < 0:
            return 0.0
        if value > 1:
            return 1.0
        return value
    if isinstance(evidence, Mapping):
        for key in ("verification_score", "evidence_score", "confidence", "score", "support"):
            value = evidence.get(key)
            if value is not None:
                try:
                    parsed = float(value)
                except (TypeError, ValueError):
                    continue
                if parsed < 0:
                    return 0.0
                if parsed > 1:
                    return 1.0
                return parsed
        if evidence.get("high_confidence") is True:
            return 1.0
        if evidence.get("low_confidence") is True:
            return 0.0
    if isinstance(evidence, (list, tuple, set)):
        return 1.0 if evidence else 0.0
    return 0.0


def _build_state_patch(delta: Any) -> dict[str, Any]:
    if not isinstance(delta, Mapping):
        return {}
    for key in ("state_patch", "updates", "patch"):
        value = delta.get(key)
        if isinstance(value, Mapping):
            return dict(value)
    patch = {key: value for key, value in delta.items() if key not in _RESERVED_DELTA_KEYS}
    return patch


def _apply_patch(state_before: Any, delta: Any) -> Any:
    if isinstance(state_before, Mapping):
        state_after = deepcopy(dict(state_before))
        patch = _build_state_patch(delta)
        state_after.update(patch)
        if isinstance(delta, Mapping):
            requested_authority = delta.get("authority_update")
            if requested_authority is not None:
                state_after["authority_level"] = requested_authority
        return state_after
    patch = _build_state_patch(delta)
    if not patch:
        return deepcopy(state_before)
    return deepcopy(patch)


def _validation_passed(case: TransitionCase, policy: GovernancePolicy, invariant: TransitionInvariant) -> bool:
    if not policy.enable_validation:
        return True
    return invariant.validate(case.state_before, case.delta)


def _evidence_passed(case: TransitionCase, policy: GovernancePolicy) -> tuple[float, bool]:
    score = _evidence_score(case.evidence)
    if not policy.enable_evidence:
        return score, True
    return score, score >= policy.evidence_threshold


def _authority_passed(
    case: TransitionCase,
    policy: GovernancePolicy,
    evidence_passed: bool,
    validation_passed: bool,
) -> bool:
    if not policy.enable_governance:
        return True
    if not validation_passed:
        return False
    if not policy.enable_evidence and policy.require_authority:
        requested = _requested_authority(case.delta)
        current = _state_authority(case.state_before)
        return requested is None or requested == current

    requested = _requested_authority(case.delta)
    current = _state_authority(case.state_before)
    authority_ok = requested is None or requested == current
    if policy.evidence_controls_authority and requested is not None:
        authority_ok = authority_ok or evidence_passed
    if policy.require_authority and requested is not None and not authority_ok:
        return False
    return authority_ok


def execute_transition(
    case: TransitionCase,
    policy: GovernancePolicy,
    invariant: TransitionInvariant | None = None,
) -> GovernanceResult:
    invariant = invariant or policy.invariant or default_transition_invariant()
    transition_id = _transition_id(case)
    total_started = perf_counter()

    validation_started = perf_counter()
    validation_passed = _validation_passed(case, policy, invariant)
    validation_ms = round((perf_counter() - validation_started) * 1000.0, 6)

    evidence_started = perf_counter()
    evidence_score, evidence_passed = _evidence_passed(case, policy)
    evidence_ms = round((perf_counter() - evidence_started) * 1000.0, 6)

    governance_started = perf_counter()
    authority_passed = _authority_passed(case, policy, evidence_passed, validation_passed)

    if not policy.enable_governance:
        accepted = True
        decision = GovernanceDecision.APPROVE
        reason = "governance bypassed by policy"
    elif validation_passed and evidence_passed and authority_passed:
        accepted = True
        decision = GovernanceDecision.APPROVE
        reason = "transition admitted"
    else:
        accepted = False
        decision = GovernanceDecision.REJECT
        reason = "transition rejected"
    governance_ms = round((perf_counter() - governance_started) * 1000.0, 6)

    commit_started = perf_counter()
    state_after = _apply_patch(case.state_before, case.delta) if accepted else deepcopy(case.state_before)
    commit_ms = round((perf_counter() - commit_started) * 1000.0, 6)
    total_ms = round((perf_counter() - total_started) * 1000.0, 6)

    state_changed = state_after != case.state_before
    current_authority = _state_authority(case.state_before)
    next_authority = _state_authority(state_after)
    authority_changed = next_authority != current_authority
    rollback_valid = not accepted and not state_changed
    if accepted and policy.enable_governance and not policy.evidence_controls_authority:
        rollback_valid = True

    verification_score = round(
        (0.5 if validation_passed else 0.0) + (0.5 * evidence_score),
        6,
    )
    if accepted:
        verification_score = max(verification_score, 1.0 if validation_passed and evidence_passed else verification_score)

    trace = TransitionTrace(
        transition_id=transition_id,
        validation={
            "passed": validation_passed,
            "invariant_name": invariant.name,
            "validation_enabled": policy.enable_validation,
        },
        evidence={
            "score": evidence_score,
            "passed": evidence_passed,
            "evidence_enabled": policy.enable_evidence,
        },
        governance={
            "decision": "approve" if accepted else "reject",
            "accepted": accepted,
            "authority_passed": authority_passed,
            "governance_enabled": policy.enable_governance,
            "evidence_controls_authority": policy.evidence_controls_authority,
        },
        execution={
            "state_changed": state_changed,
            "authority_changed": authority_changed,
            "rollback_valid": rollback_valid,
            "state_before_authority": current_authority,
            "state_after_authority": next_authority,
        },
        timing={
            "proposal_ms": _proposal_latency_ms(case),
            "validation_ms": validation_ms,
            "evidence_ms": evidence_ms,
            "governance_ms": governance_ms,
            "commit_ms": commit_ms,
            "total_ms": total_ms,
        },
        metadata={
            "policy_name": policy.name,
            "expected_decision": case.expected_decision,
            "decision_reason": reason,
        },
    )

    return GovernanceResult(
        accepted=accepted,
        state_changed=state_changed,
        authority_changed=authority_changed,
        rollback_valid=rollback_valid,
        verification_score=verification_score,
        decision_reason=reason if decision is None else f"{reason} ({decision.value})",
        metrics={
            "validation_passed": validation_passed,
            "evidence_score": evidence_score,
            "evidence_passed": evidence_passed,
            "authority_passed": authority_passed,
            "state_before_authority": current_authority,
            "state_after_authority": next_authority,
        },
        metadata={
            "policy_name": policy.name,
            "invariant_name": invariant.name,
            "expected_decision": case.expected_decision,
        },
        trace=trace.as_dict(),
    )
