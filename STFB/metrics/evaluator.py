from __future__ import annotations

from typing import Any, Dict


def evaluate_transition(instance: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
    expected_commit = bool(instance.get("expected", {}).get("commit", False))
    decision = result.get("decision")
    committed_state = result.get("committed_state", {})
    state_t = instance.get("state_t", {})
    proposal = instance.get("proposal", {})
    authority_allowed = bool(instance.get("authority", {}).get("allowed_mutation", False))
    valid_state = instance.get("expected", {}).get("valid_state", proposal if expected_commit else state_t)

    invalid_admission = bool(decision == "commit" and not expected_commit)
    authority_violation = bool(decision == "commit" and not authority_allowed)
    drift = 0 if committed_state == valid_state else 1

    return {
        "invalid_admission": invalid_admission,
        "authority_violation": authority_violation,
        "drift": drift,
    }
