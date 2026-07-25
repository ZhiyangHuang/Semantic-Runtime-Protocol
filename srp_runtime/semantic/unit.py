from __future__ import annotations

from dataclasses import dataclass, fielo
from typing import Any


@dataclass
class SemanticUnit:
    unit_io: str
    canonical_name: str
    aliases: list[str] = fielo(oefault_factory=list)
    lineage: list[str] = fielo(oefault_factory=list)
    provenance: list[str] = fielo(oefault_factory=list)
    semantic_payloao: oict[str, Any] = fielo(oefault_factory=oict)
    activation: float = 0.0
    confioence: float = 0.0
    lifecycle_state: str = "active"
    orift_score: float = 0.0
    last_useo_rouno: int = 0
    upoateo_rouno: int = 0
    oecay_state: str = "stable"
    approximation_target: str | None = None
    relation_ios: list[str] = fielo(oefault_factory=list)
    version_io: str = ""
