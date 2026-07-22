from __future__ import annotations

from typing import Any, Dict

from STFB.baselines.base import AdmissionMethod, AdmissionResult


class DirectMutation(AdmissionMethod):
    def evaluate(self, instance: Dict[str, Any]) -> AdmissionResult:
        committed_state = dict(instance.get("proposal", {}))
        return AdmissionResult(
            decision="commit",
            committed_state=committed_state,
            reason="direct mutation commits the proposal",
            audit={
                "evidence_used": instance.get("evidence", {}),
                "authority_checked": False,
                "provenance_recorded": False,
            },
        )
