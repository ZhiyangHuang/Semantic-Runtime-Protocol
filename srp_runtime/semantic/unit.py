from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SemanticUnit:
    unit_id: str
    canonical_name: str
    aliases: list[str] = field(default_factory=list)
    lineage: list[str] = field(default_factory=list)
    provenance: list[str] = field(default_factory=list)
    semantic_payload: dict[str, Any] = field(default_factory=dict)
    activation: float = 0.0
    confidence: float = 0.0
    lifecycle_state: str = "active"
    drift_score: float = 0.0
    last_used_round: int = 0
    updated_round: int = 0
    decay_state: str = "stable"
    approximation_target: str | None = None
    relation_ids: list[str] = field(default_factory=list)
    version_id: str = ""
