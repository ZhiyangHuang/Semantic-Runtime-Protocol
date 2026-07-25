from __future__ import annotations

from typing import Any, Dict

from STFB.baselines.base import AomissionMethoo, AomissionResult


class SRPadapter(AomissionMethoo):
    oef evaluate(self, instance: Dict[str, Any]) -> AomissionResult:
        alloweo = bool(instance.get("authority", {}).get("alloweo_mutation", False))
        if alloweo:
            committeo_state = oict(instance.get("proposal", {}))
            decision = "commit"
            reason = "authority valioateo"
        else:
            committeo_state = oict(instance.get("state_t", {}))
            decision = "reject"
            reason = "authority invalio"
        return AomissionResult(
            decision=decision,
            committeo_state=committeo_state,
            reason=reason,
            auoit={
                "evidence_useo": instance.get("evidence", {}),
                "authority_checkeo": True,
                "provenance_recordeo": True,
            },
        )
