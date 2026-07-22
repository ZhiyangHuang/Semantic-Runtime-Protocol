from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Mapping

from .candidate import SemanticTransitionCandidate
from .decision import GovernanceDecision
from .interface import SemanticMemoryAdapter

APPROVE = "APPROVE"
REJECT = "REJECT"


def _coerce_mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    return {"value": value}


def _iter_strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Mapping):
        items: list[str] = []
        for item in value.values():
            items.extend(_iter_strings(item))
        return items
    if isinstance(value, (list, tuple, set)):
        items: list[str] = []
        for item in value:
            items.extend(_iter_strings(item))
        return items
    return [str(value)]


def _merge_patch(state: Any, patch: Any) -> Any:
    if not isinstance(patch, Mapping):
        return deepcopy(patch)
    if not isinstance(state, Mapping):
        state = {}
    merged = deepcopy(dict(state))
    for key, value in patch.items():
        current = merged.get(key)
        if isinstance(current, Mapping) and isinstance(value, Mapping):
            merged[key] = _merge_patch(current, value)
        else:
            merged[key] = deepcopy(value)
    return merged


@dataclass(frozen=True)
class RuntimeAdmissionPolicy:
    minimum_confidence: float = 0.75
    require_evidence: bool = True
    block_authority_escalation: bool = True
    enforce_transition_kind_checks: bool = True
    commit_enabled: bool = False
    mode: str = "replay"
    name: str = "runtime_integration_policy_v1"
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "minimum_confidence": self.minimum_confidence,
            "require_evidence": self.require_evidence,
            "block_authority_escalation": self.block_authority_escalation,
            "enforce_transition_kind_checks": self.enforce_transition_kind_checks,
            "commit_enabled": self.commit_enabled,
            "mode": self.mode,
            "name": self.name,
            "metadata": dict(self.metadata),
        }


@dataclass
class SemanticMemoryStore:
    state: dict[str, Any] = field(default_factory=dict)
    history: list[dict[str, Any]] = field(default_factory=list)

    def read_state(self, entity: str | None = None) -> dict[str, Any]:
        if entity is None:
            return self.snapshot()
        value = self.state.get(entity)
        if isinstance(value, Mapping):
            return deepcopy(dict(value))
        if value is None:
            return {}
        return {"value": deepcopy(value)}

    def snapshot(self) -> dict[str, Any]:
        return deepcopy(self.state)

    def propose_transition(self, candidate: SemanticTransitionCandidate) -> dict[str, Any]:
        return {
            "transition_id": candidate.transition_id,
            "subject": candidate.subject,
            "operation": candidate.operation,
            "state_before": self.read_state(candidate.subject),
            "candidate": candidate.as_dict(),
        }

    def commit_transition(self, candidate: SemanticTransitionCandidate) -> dict[str, Any]:
        patch = candidate.proposed_value
        if candidate.operation.upper() == "DELETE":
            if candidate.subject in self.state:
                self.state.pop(candidate.subject, None)
        else:
            current = self.state.get(candidate.subject)
            if isinstance(current, Mapping) and isinstance(patch, Mapping):
                self.state[candidate.subject] = _merge_patch(current, patch)
            else:
                self.state[candidate.subject] = deepcopy(patch)
        record = {
            "transition_id": candidate.transition_id,
            "subject": candidate.subject,
            "operation": candidate.operation,
            "candidate": candidate.as_dict(),
            "state": self.snapshot(),
        }
        self.history.append(record)
        return self.snapshot()

    def apply_candidate(self, candidate: SemanticTransitionCandidate) -> dict[str, Any]:
        return self.commit_transition(candidate)

    def rollback_transition(self, transition_id: str) -> dict[str, Any]:
        retained: list[dict[str, Any]] = []
        rebuilt: dict[str, Any] = {}
        for record in self.history:
            if str(record.get("transition_id")) == transition_id:
                continue
            retained.append(record)
            candidate = record.get("candidate") or {}
            subject = str(candidate.get("subject") or "")
            if not subject:
                continue
            operation = str(candidate.get("operation") or "UPDATE").upper()
            patch = candidate.get("proposed_value")
            if operation == "DELETE":
                rebuilt.pop(subject, None)
            else:
                current = rebuilt.get(subject)
                if isinstance(current, Mapping) and isinstance(patch, Mapping):
                    rebuilt[subject] = _merge_patch(current, patch)
                else:
                    rebuilt[subject] = deepcopy(patch)
        self.history = retained
        self.state = rebuilt
        return self.snapshot()

    def export_state(self) -> dict[str, Any]:
        return self.snapshot()


class SemanticRuntimeAdapter:
    def __init__(
        self,
        *,
        policy: RuntimeAdmissionPolicy | None = None,
        store: SemanticMemoryAdapter | None = None,
    ) -> None:
        self.policy = policy or RuntimeAdmissionPolicy()
        self.store = store or SemanticMemoryStore()

    def evaluate(self, candidate: SemanticTransitionCandidate) -> GovernanceDecision:
        return self.process(candidate)

    def process(self, candidate: SemanticTransitionCandidate) -> GovernanceDecision:
        started = perf_counter()
        state_before = self.store.snapshot()
        proposal_view = self.store.propose_transition(candidate)

        validation_started = perf_counter()
        validation_score = 1.0 if candidate.subject and candidate.operation.upper() in {"ADD", "UPDATE", "DELETE"} else 0.0
        validation_ms = (perf_counter() - validation_started) * 1000.0

        evidence_started = perf_counter()
        evidence_score = float(candidate.confidence if candidate.evidence else 0.0)
        evidence_ms = (perf_counter() - evidence_started) * 1000.0

        governance_started = perf_counter()
        violated_rules: list[str] = []
        transition_kind = str(candidate.metadata.get("transition_kind") or "unknown")
        if self.policy.require_evidence and not candidate.evidence:
            violated_rules.append("missing_evidence")
        if evidence_score < self.policy.minimum_confidence:
            violated_rules.append("low_confidence")
        if self.policy.enforce_transition_kind_checks and transition_kind in {"unsupported", "contradictory", "authority_injection"}:
            violated_rules.append(transition_kind)
        if self.policy.block_authority_escalation and _contains_authority_escalation(candidate):
            violated_rules.append("authority_escalation")
        accepted = validation_score >= 1.0 and not violated_rules
        governance_ms = (perf_counter() - governance_started) * 1000.0

        commit_ms = 0.0
        state_changed = False
        authority_changed = False
        state_after = deepcopy(state_before)
        if accepted and self.policy.commit_enabled:
            commit_started = perf_counter()
            state_after = self.store.commit_transition(candidate)
            commit_ms = (perf_counter() - commit_started) * 1000.0
            state_changed = state_after != state_before
            authority_changed = _authority_label(state_after) != _authority_label(state_before)

        total_ms = (perf_counter() - started) * 1000.0
        trace = {
            "transition_id": candidate.transition_id,
            "validation": {
                "passed": validation_score >= 1.0,
                "score": validation_score,
                "mode": self.policy.mode,
            },
            "evidence": {
                "score": evidence_score,
                "passed": evidence_score >= self.policy.minimum_confidence and bool(candidate.evidence),
            },
            "governance": {
                "decision": APPROVE if accepted else REJECT,
                "accepted": accepted,
                "violated_rules": list(violated_rules),
            },
            "execution": {
                "state_changed": state_changed,
                "authority_changed": authority_changed,
                "state_before": state_before,
                "state_after": state_after,
            },
            "timing": {
                "proposal_ms": float(candidate.metadata.get("proposal_ms", 0.0) or 0.0),
                "validation_ms": round(validation_ms, 6),
                "evidence_ms": round(evidence_ms, 6),
                "governance_ms": round(governance_ms, 6),
                "commit_ms": round(commit_ms, 6),
                "total_ms": round(total_ms, 6),
            },
            "metadata": {
                "mode": self.policy.mode,
                "policy": self.policy.as_dict(),
                "candidate_metadata": dict(candidate.metadata),
                "proposal_view": proposal_view,
            },
        }

        return GovernanceDecision(
            id=candidate.transition_id,
            decision=APPROVE if accepted else REJECT,
            accepted=accepted,
            validation_score=validation_score,
            evidence_score=evidence_score,
            violated_rules=violated_rules,
            governance_trace=trace,
            latency_ms=round(total_ms, 6),
            metadata={
                "state_changed": state_changed,
                "authority_changed": authority_changed,
                "mode": self.policy.mode,
                "policy": self.policy.as_dict(),
            },
        )


def _authority_label(state: Any) -> str:
    if isinstance(state, Mapping):
        for key in ("authority_level", "authority", "authority_state", "authority_rank"):
            value = state.get(key)
            if value is not None:
                return str(value)
    return "unknown"


def _contains_authority_escalation(candidate: SemanticTransitionCandidate) -> bool:
    if str(candidate.subject).lower() in {"authority", "authority_level", "role", "user_role"}:
        return True
    for value in _iter_strings(candidate.proposed_value):
        if value.lower() in {"admin", "root", "superuser", "owner"}:
            return True
    for evidence in candidate.evidence:
        for value in _iter_strings(evidence):
            if value.lower() in {"admin", "root", "superuser", "owner"}:
                return True
    return False
