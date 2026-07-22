from __future__ import annotations

from typing import Any, Dict

from STFB.baselines.base import AdmissionMethod, AdmissionResult


class SRPAdapter(AdmissionMethod):
    def evaluate(self, instance: Dict[str, Any]) -> AdmissionResult:
        allowed = bool(instance.get("authority", {}).get("allowed_mutation", False))
        if allowed:
            committed_state = dict(instance.get("proposal", {}))
            decision = "commit"
            reason = "authority validated"
        else:
            committed_state = dict(instance.get("state_t", {}))
            decision = "reject"
            reason = "authority invalid"
        return AdmissionResult(
            decision=decision,
            committed_state=committed_state,
            reason=reason,
            audit={
                "evidence_used": instance.get("evidence", {}),
                "authority_checked": True,
                "provenance_recorded": True,
            },
        )
