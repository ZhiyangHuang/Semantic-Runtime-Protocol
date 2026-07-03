from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .semantic_parser import TypedSemanticRepresentation, parse_semantic_state


@dataclass
class SemanticState:
    memory: str
    constraints: List[str] = field(default_factory=list)
    global_vocabulary: List[str] = field(default_factory=list)
    local_vocabulary: List[str] = field(default_factory=list)
    term_map: Dict[str, str] = field(default_factory=dict)
    loss_notes: List[str] = field(default_factory=list)
    policy: Dict[str, str] = field(default_factory=dict)
    usage: Optional[Dict] = None
    typed_representation: Optional[TypedSemanticRepresentation] = None

    def ensure_typed_representation(self, anchor_memory: str = "") -> TypedSemanticRepresentation:
        if self.typed_representation is None:
            self.typed_representation = parse_semantic_state(
                self.memory,
                constraints=self.constraints,
                anchor_memory=anchor_memory,
            )
        return self.typed_representation

    def as_dict(self) -> Dict:
        return {
            "memory": self.memory,
            "constraints": self.constraints,
            "vocabulary": {
                "global": self.global_vocabulary,
                "local": self.local_vocabulary,
            },
            "term_map": self.term_map,
            "loss_notes": self.loss_notes,
            "policy": self.policy,
            "usage": self.usage,
            "typed_representation": self.ensure_typed_representation().as_dict(),
        }
