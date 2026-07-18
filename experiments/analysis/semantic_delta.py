from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .semantic_snapshot import SemanticSnapshot


def _sorted_list(values: set[str]) -> List[str]:
    return sorted(values)


@dataclass
class SemanticDelta:
    from_stage: str
    to_stage: str
    removed_objects: List[str] = field(default_factory=list)
    added_objects: List[str] = field(default_factory=list)
    removed_relations: List[str] = field(default_factory=list)
    added_relations: List[str] = field(default_factory=list)
    removed_constraints: List[str] = field(default_factory=list)
    added_constraints: List[str] = field(default_factory=list)
    removed_attributes: List[str] = field(default_factory=list)
    added_attributes: List[str] = field(default_factory=list)
    removed_states: List[str] = field(default_factory=list)
    added_states: List[str] = field(default_factory=list)
    removed_frames: List[str] = field(default_factory=list)
    added_frames: List[str] = field(default_factory=list)
    removed_conversations: List[str] = field(default_factory=list)
    added_conversations: List[str] = field(default_factory=list)
    removed_provenance: List[str] = field(default_factory=list)
    added_provenance: List[str] = field(default_factory=list)
    removed_confidence: List[str] = field(default_factory=list)
    added_confidence: List[str] = field(default_factory=list)
    removed_lifecycle: List[str] = field(default_factory=list)
    added_lifecycle: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "from_stage": self.from_stage,
            "to_stage": self.to_stage,
            "removed_objects": list(self.removed_objects),
            "added_objects": list(self.added_objects),
            "removed_relations": list(self.removed_relations),
            "added_relations": list(self.added_relations),
            "removed_constraints": list(self.removed_constraints),
            "added_constraints": list(self.added_constraints),
            "removed_attributes": list(self.removed_attributes),
            "added_attributes": list(self.added_attributes),
            "removed_states": list(self.removed_states),
            "added_states": list(self.added_states),
            "removed_frames": list(self.removed_frames),
            "added_frames": list(self.added_frames),
            "removed_conversations": list(self.removed_conversations),
            "added_conversations": list(self.added_conversations),
            "removed_provenance": list(self.removed_provenance),
            "added_provenance": list(self.added_provenance),
            "removed_confidence": list(self.removed_confidence),
            "added_confidence": list(self.added_confidence),
            "removed_lifecycle": list(self.removed_lifecycle),
            "added_lifecycle": list(self.added_lifecycle),
            "object_loss_count": len(self.removed_objects),
            "object_gain_count": len(self.added_objects),
            "relation_loss_count": len(self.removed_relations),
            "relation_gain_count": len(self.added_relations),
            "constraint_loss_count": len(self.removed_constraints),
            "constraint_gain_count": len(self.added_constraints),
            "frame_loss_count": len(self.removed_frames),
            "frame_gain_count": len(self.added_frames),
            "provenance_loss_count": len(self.removed_provenance),
            "provenance_gain_count": len(self.added_provenance),
            "confidence_loss_count": len(self.removed_confidence),
            "confidence_gain_count": len(self.added_confidence),
            "lifecycle_loss_count": len(self.removed_lifecycle),
            "lifecycle_gain_count": len(self.added_lifecycle),
        }


def build_semantic_delta(from_snapshot: SemanticSnapshot, to_snapshot: SemanticSnapshot) -> SemanticDelta:
    left = from_snapshot.signature_sets()
    right = to_snapshot.signature_sets()
    return SemanticDelta(
        from_stage=from_snapshot.stage,
        to_stage=to_snapshot.stage,
        removed_objects=_sorted_list(left["objects"] - right["objects"]),
        added_objects=_sorted_list(right["objects"] - left["objects"]),
        removed_relations=_sorted_list(left["relations"] - right["relations"]),
        added_relations=_sorted_list(right["relations"] - left["relations"]),
        removed_constraints=_sorted_list(left["constraints"] - right["constraints"]),
        added_constraints=_sorted_list(right["constraints"] - left["constraints"]),
        removed_attributes=_sorted_list(left["attributes"] - right["attributes"]),
        added_attributes=_sorted_list(right["attributes"] - left["attributes"]),
        removed_states=_sorted_list(left["states"] - right["states"]),
        added_states=_sorted_list(right["states"] - left["states"]),
        removed_frames=_sorted_list(left["frames"] - right["frames"]),
        added_frames=_sorted_list(right["frames"] - left["frames"]),
        removed_conversations=_sorted_list(left["conversations"] - right["conversations"]),
        added_conversations=_sorted_list(right["conversations"] - left["conversations"]),
        removed_provenance=_sorted_list(left["provenance"] - right["provenance"]),
        added_provenance=_sorted_list(right["provenance"] - left["provenance"]),
        removed_confidence=_sorted_list(left["confidence"] - right["confidence"]),
        added_confidence=_sorted_list(right["confidence"] - left["confidence"]),
        removed_lifecycle=_sorted_list(left["lifecycle"] - right["lifecycle"]),
        added_lifecycle=_sorted_list(right["lifecycle"] - left["lifecycle"]),
    )
