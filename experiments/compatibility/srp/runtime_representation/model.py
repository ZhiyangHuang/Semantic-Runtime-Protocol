from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RuntimeConfidence:
    identity: float = 0.0
    attribute: float = 0.0
    relation: float = 0.0
    constraint: float = 0.0
    state: float = 0.0
    temporal: float = 0.0
    inference: float = 0.0
    recovery: float = 0.0
    validation: float = 0.0

    def as_dict(self) -> Dict[str, float]:
        return {
            "identity": round(float(self.identity), 4),
            "attribute": round(float(self.attribute), 4),
            "relation": round(float(self.relation), 4),
            "constraint": round(float(self.constraint), 4),
            "state": round(float(self.state), 4),
            "temporal": round(float(self.temporal), 4),
            "inference": round(float(self.inference), 4),
            "recovery": round(float(self.recovery), 4),
            "validation": round(float(self.validation), 4),
        }


@dataclass
class RuntimeProvenance:
    source_document: str = ""
    turn: Optional[int] = None
    sentence: Optional[int] = None
    token_span: Optional[List[int]] = None
    extraction_method: str = ""
    reasoning_path: str = ""
    compression_round: Optional[int] = None
    recovery_mode: str = ""
    validation_outcome: str = ""
    evidence_pointer: str = ""

    def as_dict(self) -> Dict[str, object]:
        return {
            "source_document": self.source_document,
            "turn": self.turn,
            "sentence": self.sentence,
            "token_span": list(self.token_span) if self.token_span is not None else None,
            "extraction_method": self.extraction_method,
            "reasoning_path": self.reasoning_path,
            "compression_round": self.compression_round,
            "recovery_mode": self.recovery_mode,
            "validation_outcome": self.validation_outcome,
            "evidence_pointer": self.evidence_pointer,
        }


@dataclass
class RuntimeObject:
    id: str
    type: str
    label: str
    identity: Dict[str, object] = field(default_factory=dict)
    properties: Dict[str, object] = field(default_factory=dict)
    state: Dict[str, object] = field(default_factory=dict)
    importance: float = 0.0
    confidence: RuntimeConfidence = field(default_factory=RuntimeConfidence)
    provenance: RuntimeProvenance = field(default_factory=RuntimeProvenance)
    lifecycle: Dict[str, object] = field(default_factory=dict)
    relations: List[Dict[str, object]] = field(default_factory=list)
    source_object_type: str = ""
    source_value: str = ""

    def as_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "identity": dict(self.identity),
            "properties": dict(self.properties),
            "state": dict(self.state),
            "importance": round(float(self.importance), 4),
            "confidence": self.confidence.as_dict(),
            "provenance": self.provenance.as_dict(),
            "lifecycle": dict(self.lifecycle),
            "relations": [dict(item) for item in self.relations],
            "source_object_type": self.source_object_type,
            "source_value": self.source_value,
        }


@dataclass
class RuntimeFrame:
    id: str
    predicate: str
    arguments: Dict[str, object] = field(default_factory=dict)
    confidence: RuntimeConfidence = field(default_factory=RuntimeConfidence)
    provenance: RuntimeProvenance = field(default_factory=RuntimeProvenance)
    lifecycle: Dict[str, object] = field(default_factory=dict)
    source_object_ids: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "predicate": self.predicate,
            "arguments": dict(self.arguments),
            "confidence": self.confidence.as_dict(),
            "provenance": self.provenance.as_dict(),
            "lifecycle": dict(self.lifecycle),
            "source_object_ids": list(self.source_object_ids),
        }


@dataclass
class RuntimeNarrative:
    id: str
    episode: str = ""
    goal: str = ""
    conflict: str = ""
    resolution: str = ""
    scenes: List[str] = field(default_factory=list)
    confidence: RuntimeConfidence = field(default_factory=RuntimeConfidence)
    provenance: RuntimeProvenance = field(default_factory=RuntimeProvenance)
    lifecycle: Dict[str, object] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "episode": self.episode,
            "goal": self.goal,
            "conflict": self.conflict,
            "resolution": self.resolution,
            "scenes": list(self.scenes),
            "confidence": self.confidence.as_dict(),
            "provenance": self.provenance.as_dict(),
            "lifecycle": dict(self.lifecycle),
        }


@dataclass
class RuntimeConversationTurn:
    id: str
    speaker: str = ""
    listener: str = ""
    dialogue_act: str = ""
    intent: str = ""
    content: str = ""
    reference: str = ""
    confidence: RuntimeConfidence = field(default_factory=RuntimeConfidence)
    provenance: RuntimeProvenance = field(default_factory=RuntimeProvenance)
    lifecycle: Dict[str, object] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "speaker": self.speaker,
            "listener": self.listener,
            "dialogue_act": self.dialogue_act,
            "intent": self.intent,
            "content": self.content,
            "reference": self.reference,
            "confidence": self.confidence.as_dict(),
            "provenance": self.provenance.as_dict(),
            "lifecycle": dict(self.lifecycle),
        }


@dataclass
class RuntimeRepresentation:
    schema_version: str = "srr.v2"
    objects: List[RuntimeObject] = field(default_factory=list)
    frames: List[RuntimeFrame] = field(default_factory=list)
    narratives: List[RuntimeNarrative] = field(default_factory=list)
    conversations: List[RuntimeConversationTurn] = field(default_factory=list)
    metadata: Dict[str, object] = field(default_factory=dict)
    summary: Dict[str, object] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "objects": [item.as_dict() for item in self.objects],
            "frames": [item.as_dict() for item in self.frames],
            "narratives": [item.as_dict() for item in self.narratives],
            "conversations": [item.as_dict() for item in self.conversations],
            "metadata": dict(self.metadata),
            "summary": dict(self.summary),
        }

    def project_graph(self) -> Dict[str, object]:
        nodes = []
        edges = []
        for obj in self.objects:
            nodes.append(
                {
                    "id": obj.id,
                    "type": obj.type,
                    "label": obj.label,
                    "identity": dict(obj.identity),
                    "properties": dict(obj.properties),
                    "state": dict(obj.state),
                    "importance": round(float(obj.importance), 4),
                    "confidence": obj.confidence.as_dict(),
                    "provenance": obj.provenance.as_dict(),
                    "lifecycle": dict(obj.lifecycle),
                    "source_object_type": obj.source_object_type,
                }
            )
            for relation in obj.relations:
                edges.append(
                    {
                        "source": obj.id,
                        "target": relation.get("target"),
                        "relation": relation.get("relation"),
                        "confidence": relation.get("confidence", obj.confidence.relation),
                        "provenance": relation.get("provenance", obj.provenance.as_dict()),
                    }
                )
        for narrative in self.narratives:
            narrative_node_id = f"narrative::{narrative.id}"
            nodes.append(
                {
                    "id": narrative_node_id,
                    "type": "narrative",
                    "label": narrative.episode or narrative.goal or narrative.conflict or narrative.resolution,
                    "goal": narrative.goal,
                    "conflict": narrative.conflict,
                    "resolution": narrative.resolution,
                    "scenes": list(narrative.scenes),
                    "confidence": narrative.confidence.as_dict(),
                    "provenance": narrative.provenance.as_dict(),
                    "lifecycle": dict(narrative.lifecycle),
                }
            )
            for scene_index, scene in enumerate(narrative.scenes, start=1):
                edges.append(
                    {
                        "source": narrative_node_id,
                        "target": scene,
                        "relation": "contains_scene",
                        "confidence": narrative.confidence.relation,
                        "provenance": narrative.provenance.as_dict(),
                        "scene_index": scene_index,
                    }
                )
        for turn in self.conversations:
            turn_node_id = f"turn::{turn.id}"
            nodes.append(
                {
                    "id": turn_node_id,
                    "type": "conversation_turn",
                    "label": turn.content or turn.dialogue_act or turn.intent,
                    "speaker": turn.speaker,
                    "listener": turn.listener,
                    "dialogue_act": turn.dialogue_act,
                    "intent": turn.intent,
                    "reference": turn.reference,
                    "confidence": turn.confidence.as_dict(),
                    "provenance": turn.provenance.as_dict(),
                    "lifecycle": dict(turn.lifecycle),
                }
            )
        for frame in self.frames:
            frame_node_id = f"frame::{frame.id}"
            nodes.append(
                {
                    "id": frame_node_id,
                    "type": "frame",
                    "label": frame.predicate,
                    "arguments": dict(frame.arguments),
                    "confidence": frame.confidence.as_dict(),
                    "provenance": frame.provenance.as_dict(),
                    "lifecycle": dict(frame.lifecycle),
                }
            )
            for arg_name, arg_value in frame.arguments.items():
                if not isinstance(arg_value, str) or not arg_value:
                    continue
                edges.append(
                    {
                        "source": frame_node_id,
                        "target": arg_value,
                        "relation": arg_name,
                        "confidence": frame.confidence.relation,
                        "provenance": frame.provenance.as_dict(),
                    }
                )
        return {
            "schema_version": "srr.v2.graph_projection",
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges),
        }

    def project_text(self) -> str:
        lines = []
        for obj in self.objects:
            lines.append(f"{obj.type}: {obj.label}")
        for frame in self.frames:
            args = ", ".join(f"{key}={value}" for key, value in frame.arguments.items() if value)
            lines.append(f"{frame.predicate}({args})")
        return "\n".join(lines)
