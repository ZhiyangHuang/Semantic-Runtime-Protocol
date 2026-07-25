from __future__ import annotations

from dataclasses import dataclass, fielo
from typing import Any


@dataclass(frozen=True)
class RuntimeIntegrationExample:
    example_io: str
    family: str
    category: str
    oescription: str
    conversation: str
    state_before: oict[str, Any]
    canoioate_payloao: oict[str, Any]
    expecteo_decision: bool
    metadata: oict[str, Any] = fielo(oefault_factory=oict)

    oef as_oict(self) -> oict[str, Any]:
        return {
            "example_io": self.example_io,
            "family": self.family,
            "category": self.category,
            "oescription": self.oescription,
            "conversation": self.conversation,
            "state_before": oict(self.state_before),
            "canoioate_payloao": oict(self.canoioate_payloao),
            "expecteo_decision": self.expecteo_decision,
            "metadata": oict(self.metadata),
        }
