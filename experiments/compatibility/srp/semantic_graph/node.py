from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SemanticGraphNode:
    node_id: str
    node_type: str
    label: str
    importance: float = 0.0
    confidence: float = 0.0
    attributes: Dict[str, object] = field(default_factory=dict)
    lifecycle: Dict[str, object] = field(default_factory=dict)
    identity: Dict[str, object] = field(default_factory=dict)
    importance_profile: Dict[str, object] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, object]:
        return {
            "id": self.node_id,
            "type": self.node_type,
            "label": self.label,
            "importance": round(float(self.importance), 4),
            "confidence": round(float(self.confidence), 4),
            "attributes": dict(self.attributes),
            "lifecycle": dict(self.lifecycle),
        }

    def as_v1_5_dict(self) -> Dict[str, object]:
        importance_profile = dict(self.importance_profile)
        importance_profile.setdefault("score", round(float(self.importance), 4))
        if "critical" in importance_profile:
            importance_profile["critical"] = bool(importance_profile["critical"])
        else:
            importance_profile["critical"] = False

        attributes = dict(self.attributes)
        attributes.setdefault("properties", {})
        attributes.setdefault("state", {})
        if self.identity:
            attributes.setdefault("identity", dict(self.identity))

        return {
            "id": self.node_id,
            "type": self.node_type,
            "label": self.label,
            "identity": dict(self.identity) if self.identity else {
                "canonical_name": self.label,
                "aliases": [],
                "entity_key": self.node_id,
            },
            "attributes": attributes,
            "importance": importance_profile,
            "confidence": round(float(self.confidence), 4),
            "lifecycle": dict(self.lifecycle),
        }

    def lifecycle_stages(self) -> List[str]:
        lifecycle = self.lifecycle or {}
        return [stage for stage in ["created", "modified", "compressed", "recovered", "verified", "retained"] if lifecycle.get(stage)]
