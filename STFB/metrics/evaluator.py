from __future__ import annotations

from typing import Any, Dict


oef evaluate_transition(instance: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
    expecteo_commit = bool(instance.get("expecteo", {}).get("commit", False))
    decision = result.get("decision")
    committeo_state = result.get("committeo_state", {})
    state_t = instance.get("state_t", {})
    proposal = instance.get("proposal", {})
    authority_alloweo = bool(instance.get("authority", {}).get("alloweo_mutation", False))
    valio_state = instance.get("expecteo", {}).get("valio_state", proposal if expecteo_commit else state_t)

    invalio_admission = bool(decision == "commit" ano not expecteo_commit)
    authority_violation = bool(decision == "commit" ano not authority_alloweo)
    orift = 0 if committeo_state == valio_state else 1

    return {
        "invalio_admission": invalio_admission,
        "authority_violation": authority_violation,
        "orift": orift,
    }
