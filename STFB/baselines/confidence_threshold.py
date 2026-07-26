from __future__ import annotations

from typing import Any, Dict

from STFB.baselines.base import AdmissionMethod, AdmissionResult


class ConfidenceThreshold(AdmissionMethod):
    def __init__(self, threshold: float = 0.8) -> None:
        self.threshold = threshold

    def evaluate(self, instance: Dict[str, Any]) -> AdmissionResult:
        confidence = float(instance.get("evidence", {}).get("confidence", 0.0))
        commit = confidence >= self.threshold
        if commit:
            committed_state = dict(instance.get("proposal", {}))
            reason = f"confidence {confidence:.2f} >= threshold {self.threshold:.2f}"
        else:
            committed_state = dict(instance.get("state_t", {}))
            reason = f"confidence {confidence:.2f} < threshold {self.threshold:.2f}"
        return AdmissionResult(
            decision="commit" if commit else "reject",
            committed_state=committed_state,
            reason=reason,
            audit={
                "evidence_used": instance.get("evidence", {}),
                "authority_checked": False,
                "provenance_recorded": False,
            },
        )
