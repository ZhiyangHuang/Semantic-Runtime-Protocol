from __future__ import annotations

import re
from typing import Dict, Iterable, List, Tuple

from ..semantic_parser import canonicalize_semantic_value, stable_semantic_object_id
from ..state import SemanticState
from .model import (
    RuntimeConfidence,
    RuntimeConversationTurn,
    RuntimeFrame,
    RuntimeNarrative,
    RuntimeObject,
    RuntimeProvenance,
    RuntimeRepresentation,
)


_EVENT_VERBS = {
    "buy",
    "bought",
    "open",
    "opened",
    "close",
    "closed",
    "move",
    "moved",
    "give",
    "gave",
    "ask",
    "asked",
    "answer",
    "answered",
    "work",
    "worked",
    "own",
    "owns",
    "have",
    "has",
    "need",
    "needed",
    "pick",
    "picked",
    "find",
    "found",
    "repair",
    "repaired",
}

_STATE_TERMS = {"locked", "unlocked", "pending", "active", "verified", "archived", "recovered"}

_CONFLICT_TERMS = {"but", "however", "cannot", "can't", "unable", "instead"}
_RESOLUTION_TERMS = {"so", "therefore", "thus", "finally", "resolved", "success"}
_GOAL_TERMS = {"want", "needs", "need", "goal", "plan", "aim", "trying"}


def _split_sentences(text: str) -> List[str]:
    normalized = " ".join(str(text or "").strip().split())
    if not normalized:
        return []
    parts = re.split(r"[.!?]+", normalized)
    return [part.strip(" ,;") for part in parts if part.strip(" ,;")]


def _sentence_turn(sentence: str) -> Tuple[str, str]:
    speaker_match = re.match(r"^(user|assistant|system|speaker)\s*:\s*(.+)$", sentence, re.IGNORECASE)
    if speaker_match:
        return speaker_match.group(1).lower(), speaker_match.group(2).strip()
    return "source", sentence.strip()


def _infer_runtime_type(object_type: str, value: str) -> str:
    normalized = canonicalize_semantic_value(value)
    object_type = str(object_type or "fact").strip().lower()
    if object_type == "constraint":
        return "Constraint"
    if object_type == "question":
        return "Question"
    if object_type == "answer":
        return "Answer"
    if object_type == "anchor":
        return "Observation"
    if object_type == "event":
        return "Event"
    if object_type == "state":
        return "State"
    if object_type == "goal":
        return "Goal"
    if object_type == "inference":
        return "Inference"
    if any(term in normalized.split() for term in _STATE_TERMS):
        return "State"
    if any(verb in normalized.split() for verb in _EVENT_VERBS):
        return "Event"
    return "Observation" if object_type == "fact" else object_type.title()


def _build_confidence(base: float, *, kind: str) -> RuntimeConfidence:
    base = max(0.0, min(1.0, float(base)))
    kind = kind.lower()
    if kind == "constraint":
        return RuntimeConfidence(
            identity=base,
            attribute=base,
            relation=min(1.0, base + 0.05),
            constraint=min(1.0, base + 0.15),
            state=base,
            temporal=base * 0.8,
            inference=base * 0.7,
            recovery=base,
            validation=base,
        )
    if kind == "event":
        return RuntimeConfidence(
            identity=base,
            attribute=base,
            relation=min(1.0, base + 0.1),
            constraint=base * 0.85,
            state=min(1.0, base + 0.05),
            temporal=min(1.0, base + 0.08),
            inference=base * 0.75,
            recovery=base,
            validation=base,
        )
    return RuntimeConfidence(
        identity=base,
        attribute=base,
        relation=base,
        constraint=base * 0.9,
        state=base,
        temporal=base * 0.8,
        inference=base * 0.8,
        recovery=base,
        validation=base,
    )


def _build_provenance(
    *,
    source_document: str,
    sentence_index: int | None,
    extraction_method: str,
    evidence_pointer: str,
    recovery_mode: str = "",
) -> RuntimeProvenance:
    return RuntimeProvenance(
        source_document=source_document,
        sentence=sentence_index,
        extraction_method=extraction_method,
        reasoning_path="direct_extraction",
        compression_round=0,
        recovery_mode=recovery_mode,
        validation_outcome="unvalidated",
        evidence_pointer=evidence_pointer,
    )


def _make_object(
    semantic_object: Dict[str, object],
    *,
    sentence_index: int,
    source_document: str,
    anchor_memory: str,
    importance: float,
) -> RuntimeObject:
    source_type = str(semantic_object.get("type", "fact")).strip() or "fact"
    label = str(semantic_object.get("value", "")).strip()
    object_id = str(semantic_object.get("object_id") or semantic_object.get("id") or "").strip() or stable_semantic_object_id(source_type, label)
    runtime_type = _infer_runtime_type(source_type, label)
    canonical = canonicalize_semantic_value(label)
    metadata = semantic_object.get("metadata") if isinstance(semantic_object.get("metadata"), dict) else {}
    state = {}
    if runtime_type == "State":
        state["current"] = canonical or label
    if runtime_type == "Goal":
        state["target"] = canonical or label
    if runtime_type == "Constraint":
        state["rule"] = canonical or label
    provenance = _build_provenance(
        source_document=source_document,
        sentence_index=sentence_index,
        extraction_method=str(metadata.get("extraction_method", "rule_based_runtime_extractor")),
        evidence_pointer=str(semantic_object.get("evidence_pointer", "")),
    )
    lifecycle = {
        "extracted": True,
        "canonicalized": True,
        "merged": False,
        "compressed": False,
        "recovered": False,
        "validated": False,
        "updated": False,
        "archived": False,
    }
    relations: List[Dict[str, object]] = []
    if runtime_type in {"Event", "State", "Constraint"}:
        relations.append(
            {
                "relation": "derived_from",
                "target": provenance.evidence_pointer or object_id,
                "confidence": round(float(semantic_object.get("confidence", 0.0) or 0.0), 4),
                "provenance": provenance.as_dict(),
            }
        )
    return RuntimeObject(
        id=object_id,
        type=runtime_type,
        label=label,
        identity={
            "canonical_name": canonical or label,
            "aliases": [label] if canonical and canonical != label else [],
            "entity_key": object_id,
        },
        properties={
            "source_type": source_type,
            "raw_value": label,
            "anchor_memory": anchor_memory,
        },
        state=state,
        importance=float(importance),
        confidence=_build_confidence(float(semantic_object.get("confidence", 0.0) or 0.0), kind=runtime_type),
        provenance=provenance,
        lifecycle=lifecycle,
        relations=relations,
        source_object_type=source_type,
        source_value=label,
    )


def _extract_frames(sentences: Iterable[str], source_document: str) -> List[RuntimeFrame]:
    frames: List[RuntimeFrame] = []
    verb_pattern = re.compile(
        r"^(?P<subject>[\w'-]+(?:\s+[\w'-]+)*)\s+"
        r"(?P<verb>bought|buy|buys|opened|open|closes|closed|moves|moved|gave|give|gives|asked|ask|asks|works|worked|owns|own|has|have|needed|need|picked|pick|finds|found|repaired|repair)\s+"
        r"(?P<object>.+)$",
        re.IGNORECASE,
    )
    for index, sentence in enumerate(sentences, start=1):
        match = verb_pattern.match(sentence)
        if match is None:
            continue
        subject = match.group("subject").strip()
        verb = match.group("verb").strip().lower()
        obj = match.group("object").strip()
        arguments = {
            "agent": subject,
            "patient": obj,
        }
        lowered = sentence.lower()
        if " to " in lowered and verb in {"gave", "give", "gives", "bought", "buy", "buys"}:
            recipient = sentence.split(" to ", 1)[1].strip()
            arguments["recipient"] = recipient
        if " at " in lowered:
            arguments["location"] = sentence.split(" at ", 1)[1].strip()
        if " on " in lowered and "time" not in arguments:
            arguments["time"] = sentence.split(" on ", 1)[1].strip()
        provenance = _build_provenance(
            source_document=source_document,
            sentence_index=index,
            extraction_method="rule_based_frame_extractor",
            evidence_pointer=f"memory:{index}",
        )
        frames.append(
            RuntimeFrame(
                id=f"frame:{index}",
                predicate=verb,
                arguments=arguments,
                confidence=_build_confidence(0.72, kind="event"),
                provenance=provenance,
                lifecycle={
                    "extracted": True,
                    "canonicalized": True,
                    "merged": False,
                    "compressed": False,
                    "recovered": False,
                    "validated": False,
                    "updated": False,
                    "archived": False,
                },
                source_object_ids=[],
            )
        )
    return frames


def _build_narrative(sentences: List[str], source_document: str) -> List[RuntimeNarrative]:
    goal = next((sentence for sentence in sentences if any(term in sentence.lower() for term in _GOAL_TERMS)), "")
    conflict = next((sentence for sentence in sentences if any(term in sentence.lower() for term in _CONFLICT_TERMS)), "")
    resolution = next((sentence for sentence in sentences if any(term in sentence.lower() for term in _RESOLUTION_TERMS)), "")
    if not any([goal, conflict, resolution]):
        return []
    episode = " -> ".join(part for part in [goal, conflict, resolution] if part)
    provenance = _build_provenance(
        source_document=source_document,
        sentence_index=1 if sentences else None,
        extraction_method="rule_based_narrative_extractor",
        evidence_pointer="memory:episode",
    )
    return [
        RuntimeNarrative(
            id="narrative:1",
            episode=episode,
            goal=goal,
            conflict=conflict,
            resolution=resolution,
            scenes=list(sentences[:5]),
            confidence=_build_confidence(0.6, kind="event"),
            provenance=provenance,
            lifecycle={
                "extracted": True,
                "canonicalized": True,
                "merged": False,
                "compressed": False,
                "recovered": False,
                "validated": False,
                "updated": False,
                "archived": False,
            },
        )
    ]


def _build_conversation(sentences: List[str], source_document: str) -> List[RuntimeConversationTurn]:
    turns: List[RuntimeConversationTurn] = []
    turn_index = 0
    for sentence in sentences:
        speaker, content = _sentence_turn(sentence)
        if speaker == "source" and not any(prefix in sentence.lower() for prefix in ["user:", "assistant:", "system:"]):
            continue
        turn_index += 1
        intent = "statement"
        dialogue_act = "inform"
        if "?" in sentence:
            intent = "question"
            dialogue_act = "ask"
        if any(term in sentence.lower() for term in ["correction", "actually", "meant"]):
            intent = "correction"
            dialogue_act = "correct"
        provenance = _build_provenance(
            source_document=source_document,
            sentence_index=turn_index,
            extraction_method="rule_based_conversation_extractor",
            evidence_pointer=f"turn:{turn_index}",
        )
        turns.append(
            RuntimeConversationTurn(
                id=f"turn:{turn_index}",
                speaker=speaker,
                listener="assistant" if speaker == "user" else "user",
                dialogue_act=dialogue_act,
                intent=intent,
                content=content,
                reference="",
                confidence=_build_confidence(0.65, kind="event"),
                provenance=provenance,
                lifecycle={
                    "extracted": True,
                    "canonicalized": True,
                    "merged": False,
                    "compressed": False,
                    "recovered": False,
                    "validated": False,
                    "updated": False,
                    "archived": False,
                },
            )
        )
    return turns


def build_runtime_representation_v2(state: SemanticState, *, anchor_memory: str = "") -> RuntimeRepresentation:
    representation = state.ensure_typed_representation(anchor_memory=anchor_memory)
    runtime_metadata = state.ensure_runtime_metadata(anchor_memory=anchor_memory)
    source_document = "semantic_state"
    runtime_objects: List[RuntimeObject] = []
    for index, semantic_object in enumerate(representation.objects, start=1):
        object_id = semantic_object.stable_id()
        metadata = runtime_metadata.get(object_id)
        importance = float(metadata.importance if metadata is not None else (1.0 if semantic_object.object_type == "constraint" else 0.6))
        runtime_objects.append(
            _make_object(
                semantic_object.as_dict() | {"object_id": object_id},
                sentence_index=index,
                source_document=source_document,
                anchor_memory=anchor_memory,
                importance=importance,
            )
        )

    sentences = _split_sentences(state.memory)
    frames = _extract_frames(sentences, source_document)
    narratives = _build_narrative(sentences, source_document)
    conversations = _build_conversation(sentences, source_document)

    provenance_count = sum(1 for item in runtime_objects if item.provenance.source_document)
    provenance_count += sum(1 for item in frames if item.provenance.source_document)
    provenance_count += sum(1 for item in narratives if item.provenance.source_document)
    provenance_count += sum(1 for item in conversations if item.provenance.source_document)
    total_items = len(runtime_objects) + len(frames) + len(narratives) + len(conversations)
    provenance_completeness = round(provenance_count / total_items, 6) if total_items else 0.0

    graph_nodes = len(runtime_objects) + len(frames) + len(narratives) + len(conversations)
    graph_edges = sum(len(obj.relations) for obj in runtime_objects)
    graph_edges += sum(len(frame.arguments) for frame in frames)

    summary = {
        "schema_version": "srr.v2.summary",
        "object_count": len(runtime_objects),
        "frame_count": len(frames),
        "narrative_count": len(narratives),
        "conversation_count": len(conversations),
        "graph_node_count": graph_nodes,
        "graph_edge_count": graph_edges,
        "provenance_completeness": provenance_completeness,
        "lifecycle_coverage": 1.0 if runtime_objects else 0.0,
        "confidence_mean": round(
            sum(item.confidence.identity for item in runtime_objects) / len(runtime_objects), 6
        )
        if runtime_objects
        else 0.0,
    }

    metadata = {
        "source_document": source_document,
        "anchor_memory": anchor_memory,
        "runtime_layers": ["graph", "frame", "narrative", "conversation", "state", "provenance", "confidence"],
    }

    return RuntimeRepresentation(
        schema_version="srr.v2",
        objects=runtime_objects,
        frames=frames,
        narratives=narratives,
        conversations=conversations,
        metadata=metadata,
        summary=summary,
    )
