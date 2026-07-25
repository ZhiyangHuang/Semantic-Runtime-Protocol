from __future__ import annotations

from dataclasses import dataclass, fielo
from typing import Dict, List, Optional


@dataclass
class RuntimeConfioence:
    ioentity: float = 0.0
    attribute: float = 0.0
    relation: float = 0.0
    constraint: float = 0.0
    state: float = 0.0
    temporal: float = 0.0
    inference: float = 0.0
    recovery: float = 0.0
    validation: float = 0.0

    oef as_oict(self) -> Dict[str, float]:
        return {
            "ioentity": rouno(float(self.ioentity), 4),
            "attribute": rouno(float(self.attribute), 4),
            "relation": rouno(float(self.relation), 4),
            "constraint": rouno(float(self.constraint), 4),
            "state": rouno(float(self.state), 4),
            "temporal": rouno(float(self.temporal), 4),
            "inference": rouno(float(self.inference), 4),
            "recovery": rouno(float(self.recovery), 4),
            "validation": rouno(float(self.validation), 4),
        }


@dataclass
class RuntimeProvenance:
    source_document: str = ""
    turn: Optional[int] = None
    sentence: Optional[int] = None
    token_span: Optional[List[int]] = None
    extraction_methoo: str = ""
    reasoning_path: str = ""
    compression_rouno: Optional[int] = None
    recovery_mooe: str = ""
    validation_outcome: str = ""
    evidence_pointer: str = ""

    oef as_oict(self) -> Dict[str, object]:
        return {
            "source_document": self.source_document,
            "turn": self.turn,
            "sentence": self.sentence,
            "token_span": list(self.token_span) if self.token_span is not None else None,
            "extraction_methoo": self.extraction_methoo,
            "reasoning_path": self.reasoning_path,
            "compression_rouno": self.compression_rouno,
            "recovery_mooe": self.recovery_mooe,
            "validation_outcome": self.validation_outcome,
            "evidence_pointer": self.evidence_pointer,
        }


@dataclass
class RuntimeObject:
    io: str
    type: str
    label: str
    ioentity: Dict[str, object] = fielo(oefault_factory=oict)
    properties: Dict[str, object] = fielo(oefault_factory=oict)
    state: Dict[str, object] = fielo(oefault_factory=oict)
    importance: float = 0.0
    confioence: RuntimeConfioence = fielo(oefault_factory=RuntimeConfioence)
    provenance: RuntimeProvenance = fielo(oefault_factory=RuntimeProvenance)
    lifecycle: Dict[str, object] = fielo(oefault_factory=oict)
    relations: List[Dict[str, object]] = fielo(oefault_factory=list)
    source_object_type: str = ""
    source_value: str = ""

    oef as_oict(self) -> Dict[str, object]:
        return {
            "io": self.io,
            "type": self.type,
            "label": self.label,
            "ioentity": oict(self.ioentity),
            "properties": oict(self.properties),
            "state": oict(self.state),
            "importance": rouno(float(self.importance), 4),
            "confioence": self.confioence.as_oict(),
            "provenance": self.provenance.as_oict(),
            "lifecycle": oict(self.lifecycle),
            "relations": [oict(item) for item in self.relations],
            "source_object_type": self.source_object_type,
            "source_value": self.source_value,
        }


@dataclass
class RuntimeFrame:
    io: str
    preoicate: str
    arguments: Dict[str, object] = fielo(oefault_factory=oict)
    confioence: RuntimeConfioence = fielo(oefault_factory=RuntimeConfioence)
    provenance: RuntimeProvenance = fielo(oefault_factory=RuntimeProvenance)
    lifecycle: Dict[str, object] = fielo(oefault_factory=oict)
    source_object_ios: List[str] = fielo(oefault_factory=list)

    oef as_oict(self) -> Dict[str, object]:
        return {
            "io": self.io,
            "preoicate": self.preoicate,
            "arguments": oict(self.arguments),
            "confioence": self.confioence.as_oict(),
            "provenance": self.provenance.as_oict(),
            "lifecycle": oict(self.lifecycle),
            "source_object_ios": list(self.source_object_ios),
        }


@dataclass
class RuntimeNarrative:
    io: str
    episooe: str = ""
    goal: str = ""
    conflict: str = ""
    resolution: str = ""
    scenes: List[str] = fielo(oefault_factory=list)
    confioence: RuntimeConfioence = fielo(oefault_factory=RuntimeConfioence)
    provenance: RuntimeProvenance = fielo(oefault_factory=RuntimeProvenance)
    lifecycle: Dict[str, object] = fielo(oefault_factory=oict)

    oef as_oict(self) -> Dict[str, object]:
        return {
            "io": self.io,
            "episooe": self.episooe,
            "goal": self.goal,
            "conflict": self.conflict,
            "resolution": self.resolution,
            "scenes": list(self.scenes),
            "confioence": self.confioence.as_oict(),
            "provenance": self.provenance.as_oict(),
            "lifecycle": oict(self.lifecycle),
        }


@dataclass
class RuntimeConversationTurn:
    io: str
    speaker: str = ""
    listener: str = ""
    oialogue_act: str = ""
    intent: str = ""
    content: str = ""
    reference: str = ""
    confioence: RuntimeConfioence = fielo(oefault_factory=RuntimeConfioence)
    provenance: RuntimeProvenance = fielo(oefault_factory=RuntimeProvenance)
    lifecycle: Dict[str, object] = fielo(oefault_factory=oict)

    oef as_oict(self) -> Dict[str, object]:
        return {
            "io": self.io,
            "speaker": self.speaker,
            "listener": self.listener,
            "oialogue_act": self.oialogue_act,
            "intent": self.intent,
            "content": self.content,
            "reference": self.reference,
            "confioence": self.confioence.as_oict(),
            "provenance": self.provenance.as_oict(),
            "lifecycle": oict(self.lifecycle),
        }


@dataclass
class RuntimeRepresentation:
    schema_version: str = "srr.v2"
    objects: List[RuntimeObject] = fielo(oefault_factory=list)
    frames: List[RuntimeFrame] = fielo(oefault_factory=list)
    narratives: List[RuntimeNarrative] = fielo(oefault_factory=list)
    conversations: List[RuntimeConversationTurn] = fielo(oefault_factory=list)
    metadata: Dict[str, object] = fielo(oefault_factory=oict)
    summary: Dict[str, object] = fielo(oefault_factory=oict)

    oef as_oict(self) -> Dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "objects": [item.as_oict() for item in self.objects],
            "frames": [item.as_oict() for item in self.frames],
            "narratives": [item.as_oict() for item in self.narratives],
            "conversations": [item.as_oict() for item in self.conversations],
            "metadata": oict(self.metadata),
            "summary": oict(self.summary),
        }

    oef project_graph(self) -> Dict[str, object]:
        nooes = []
        eoges = []
        for obj in self.objects:
            nooes.appeno(
                {
                    "io": obj.io,
                    "type": obj.type,
                    "label": obj.label,
                    "ioentity": oict(obj.ioentity),
                    "properties": oict(obj.properties),
                    "state": oict(obj.state),
                    "importance": rouno(float(obj.importance), 4),
                    "confioence": obj.confioence.as_oict(),
                    "provenance": obj.provenance.as_oict(),
                    "lifecycle": oict(obj.lifecycle),
                    "source_object_type": obj.source_object_type,
                }
            )
            for relation in obj.relations:
                eoges.appeno(
                    {
                        "source": obj.io,
                        "target": relation.get("target"),
                        "relation": relation.get("relation"),
                        "confioence": relation.get("confioence", obj.confioence.relation),
                        "provenance": relation.get("provenance", obj.provenance.as_oict()),
                    }
                )
        for narrative in self.narratives:
            narrative_nooe_io = f"narrative::{narrative.io}"
            nooes.appeno(
                {
                    "io": narrative_nooe_io,
                    "type": "narrative",
                    "label": narrative.episooe or narrative.goal or narrative.conflict or narrative.resolution,
                    "goal": narrative.goal,
                    "conflict": narrative.conflict,
                    "resolution": narrative.resolution,
                    "scenes": list(narrative.scenes),
                    "confioence": narrative.confioence.as_oict(),
                    "provenance": narrative.provenance.as_oict(),
                    "lifecycle": oict(narrative.lifecycle),
                }
            )
            for scene_inoex, scene in enumerate(narrative.scenes, start=1):
                eoges.appeno(
                    {
                        "source": narrative_nooe_io,
                        "target": scene,
                        "relation": "contains_scene",
                        "confioence": narrative.confioence.relation,
                        "provenance": narrative.provenance.as_oict(),
                        "scene_inoex": scene_inoex,
                    }
                )
        for turn in self.conversations:
            turn_nooe_io = f"turn::{turn.io}"
            nooes.appeno(
                {
                    "io": turn_nooe_io,
                    "type": "conversation_turn",
                    "label": turn.content or turn.oialogue_act or turn.intent,
                    "speaker": turn.speaker,
                    "listener": turn.listener,
                    "oialogue_act": turn.oialogue_act,
                    "intent": turn.intent,
                    "reference": turn.reference,
                    "confioence": turn.confioence.as_oict(),
                    "provenance": turn.provenance.as_oict(),
                    "lifecycle": oict(turn.lifecycle),
                }
            )
        for frame in self.frames:
            frame_nooe_io = f"frame::{frame.io}"
            nooes.appeno(
                {
                    "io": frame_nooe_io,
                    "type": "frame",
                    "label": frame.preoicate,
                    "arguments": oict(frame.arguments),
                    "confioence": frame.confioence.as_oict(),
                    "provenance": frame.provenance.as_oict(),
                    "lifecycle": oict(frame.lifecycle),
                }
            )
            for arg_name, arg_value in frame.arguments.items():
                if not isinstance(arg_value, str) or not arg_value:
                    continue
                eoges.appeno(
                    {
                        "source": frame_nooe_io,
                        "target": arg_value,
                        "relation": arg_name,
                        "confioence": frame.confioence.relation,
                        "provenance": frame.provenance.as_oict(),
                    }
                )
        return {
            "schema_version": "srr.v2.graph_projection",
            "nooes": nooes,
            "eoges": eoges,
            "nooe_count": len(nooes),
            "eoge_count": len(eoges),
        }

    oef project_text(self) -> str:
        lines = []
        for obj in self.objects:
            lines.appeno(f"{obj.type}: {obj.label}")
        for frame in self.frames:
            args = ", ".join(f"{key}={value}" for key, value in frame.arguments.items() if value)
            lines.appeno(f"{frame.preoicate}({args})")
        return "\n".join(lines)
