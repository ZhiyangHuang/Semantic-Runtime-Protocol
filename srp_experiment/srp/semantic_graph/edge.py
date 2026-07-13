from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class SemanticGraphEdge:
    edge_id: str
    source: str
    target: str
    relation: str
    strength: float = 1.0
    confidence: float = 1.0
    evidence_pointer: str = ""
    attributes: Dict[str, object] = field(default_factory=dict)
    lifecycle: Dict[str, object] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, object]:
        return {
            "edge_id": self.edge_id,
            "source": self.source,
            "target": self.target,
            "relation": self.relation,
            "strength": round(float(self.strength), 4),
            "confidence": round(float(self.confidence), 4),
            "evidence_pointer": self.evidence_pointer,
            "attributes": dict(self.attributes),
            "lifecycle": dict(self.lifecycle),
        }
