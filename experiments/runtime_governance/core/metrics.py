from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Any, Iterable, Sequence


@dataclass(frozen=True)
class GovernanceMetrics:
    invalid_accept_rate: float
    state_corruption_rate: float
    authority_escalation_rate: float
    rollback_success_rate: float
    verification_delta: float
    accepted_rate: float
    rejected_rate: float

    def as_dict(self) -> dict[str, float]:
        return {
            "invalid_accept_rate": self.invalid_accept_rate,
            "state_corruption_rate": self.state_corruption_rate,
            "authority_escalation_rate": self.authority_escalation_rate,
            "rollback_success_rate": self.rollback_success_rate,
            "verification_delta": self.verification_delta,
            "accepted_rate": self.accepted_rate,
            "rejected_rate": self.rejected_rate,
        }


@dataclass(frozen=True)
class GovernanceLatencySummary:
    mean_ms: dict[str, float]
    p95_ms: dict[str, float]
    max_ms: dict[str, float]
    sample_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "mean_ms": dict(self.mean_ms),
            "p95_ms": dict(self.p95_ms),
            "max_ms": dict(self.max_ms),
            "sample_count": self.sample_count,
        }


def _record_expected_decision(record: dict[str, Any]) -> bool | None:
    if "expected_decision" in record:
        value = record.get("expected_decision")
        return None if value is None else bool(value)
    case = record.get("case") or {}
    if isinstance(case, dict) and "expected_decision" in case:
        value = case.get("expected_decision")
        return None if value is None else bool(value)
    metadata = record.get("metadata") or {}
    if isinstance(metadata, dict) and "expected_decision" in metadata:
        value = metadata.get("expected_decision")
        return None if value is None else bool(value)
    return None


def summarize_governance_results(records: Sequence[dict[str, Any]]) -> GovernanceMetrics:
    selected = list(records)
    if not selected:
        return GovernanceMetrics(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    expected_decisions = [_record_expected_decision(record) for record in selected]
    accepted = [bool((record.get("result") or {}).get("accepted", False)) for record in selected]
    state_changed = [bool((record.get("result") or {}).get("state_changed", False)) for record in selected]
    authority_changed = [bool((record.get("result") or {}).get("authority_changed", False)) for record in selected]
    rollback_valid = [bool((record.get("result") or {}).get("rollback_valid", False)) for record in selected]
    verification_scores = [float((record.get("result") or {}).get("verification_score", 0.0) or 0.0) for record in selected]

    invalid_mask = [decision is False for decision in expected_decisions]
    valid_mask = [decision is True for decision in expected_decisions]
    invalid_total = sum(invalid_mask)
    valid_total = sum(valid_mask)
    accepted_invalid = sum(1 for is_invalid, is_accepted in zip(invalid_mask, accepted) if is_invalid and is_accepted)
    state_corruption = sum(1 for is_invalid, changed in zip(invalid_mask, state_changed) if is_invalid and changed)
    authority_escalation = sum(1 for is_invalid, changed in zip(invalid_mask, authority_changed) if is_invalid and changed)
    rollback_success = sum(
        1
        for is_invalid, is_accepted, rollback_ok in zip(invalid_mask, accepted, rollback_valid)
        if is_invalid and (not is_accepted) and rollback_ok
    )
    accepted_total = sum(accepted)
    rejected_total = len(selected) - accepted_total

    valid_verification = [score for score, is_valid in zip(verification_scores, valid_mask) if is_valid]
    invalid_verification = [score for score, is_invalid in zip(verification_scores, invalid_mask) if is_invalid]
    verification_delta = (mean(valid_verification) - mean(invalid_verification)) if valid_verification and invalid_verification else 0.0

    return GovernanceMetrics(
        invalid_accept_rate=accepted_invalid / float(invalid_total) if invalid_total else 0.0,
        state_corruption_rate=state_corruption / float(invalid_total) if invalid_total else 0.0,
        authority_escalation_rate=authority_escalation / float(invalid_total) if invalid_total else 0.0,
        rollback_success_rate=rollback_success / float(invalid_total) if invalid_total else 0.0,
        verification_delta=verification_delta,
        accepted_rate=accepted_total / float(len(selected)),
        rejected_rate=rejected_total / float(len(selected)),
    )


def summarize_governance_latencies(records: Sequence[dict[str, Any]]) -> GovernanceLatencySummary:
    selected = list(records)
    if not selected:
        return GovernanceLatencySummary(mean_ms={}, p95_ms={}, max_ms={}, sample_count=0)

    timing_keys = ("proposal_ms", "validation_ms", "evidence_ms", "governance_ms", "commit_ms", "total_ms")
    per_key: dict[str, list[float]] = {key: [] for key in timing_keys}

    for record in selected:
        trace = ((record.get("result") or {}).get("trace") or {})
        timing = trace.get("timing") or {}
        if not isinstance(timing, dict):
            continue
        for key in timing_keys:
            value = timing.get(key)
            if value is None:
                continue
            try:
                per_key[key].append(float(value))
            except (TypeError, ValueError):
                continue

    def _p95(values: list[float]) -> float:
        if not values:
            return 0.0
        ordered = sorted(values)
        index = max(0, min(len(ordered) - 1, int(round(0.95 * (len(ordered) - 1)))))
        return ordered[index]

    def _max(values: list[float]) -> float:
        return max(values) if values else 0.0

    mean_ms = {key: (mean(values) if values else 0.0) for key, values in per_key.items()}
    p95_ms = {key: _p95(values) for key, values in per_key.items()}
    max_ms = {key: _max(values) for key, values in per_key.items()}
    return GovernanceLatencySummary(mean_ms=mean_ms, p95_ms=p95_ms, max_ms=max_ms, sample_count=len(selected))
