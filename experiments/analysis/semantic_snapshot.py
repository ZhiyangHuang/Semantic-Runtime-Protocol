from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Sequence

from experiments.common.semantic_text import canonicalize_semantic_value, stable_semantic_object_id


def _as_dict_list(value: Any) -> List[Dict[str, Any]]:
    return [item for item in list(value or []) if isinstance(item, dict)]


def _normalized_text(value: Any) -> str:
    return canonicalize_semantic_value(str(value or "").strip()) or str(value or "").strip()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _object_signature(item: Dict[str, Any]) -> str:
    object_type = _safe_str(item.get("type") or item.get("object_type") or "fact") or "fact"
    value = _safe_str(item.get("value") or item.get("label") or "")
    object_id = _safe_str(item.get("object_id") or item.get("id") or "")
    if not object_id and value:
        object_id = stable_semantic_object_id(object_type, value)
    return object_id or f"{object_type}:{_normalized_text(value)}"


def _relation_signature(item: Dict[str, Any]) -> str:
    source = _safe_str(item.get("source") or item.get("subject") or "")
    target = _safe_str(item.get("target") or item.get("object") or "")
    relation = _safe_str(item.get("relation") or item.get("edge_type") or "")
    if not relation and all(isinstance(item.get(part), dict) for part in ["subject", "relation", "object"]):
        subject = item.get("subject") or {}
        relation_data = item.get("relation") or {}
        obj = item.get("object") or {}
        source = _safe_str(subject.get("canonical") or subject.get("value") or source)
        relation = _safe_str(relation_data.get("canonical") or relation_data.get("value") or relation)
        target = _safe_str(obj.get("canonical") or obj.get("value") or target)
    return "||".join(_normalized_text(part) for part in [source, relation, target] if _safe_str(part))


def _attribute_signatures(objects: Sequence[Dict[str, Any]]) -> List[str]:
    signatures: List[str] = []
    for item in objects:
        object_id = _object_signature(item)
        properties = item.get("properties") if isinstance(item.get("properties"), dict) else {}
        state = item.get("state") if isinstance(item.get("state"), dict) else {}
        for key, value in properties.items():
            signatures.append(f"{object_id}::property::{_safe_str(key)}={_normalized_text(value)}")
        for key, value in state.items():
            signatures.append(f"{object_id}::state::{_safe_str(key)}={_normalized_text(value)}")
        if isinstance(item.get("attributes"), dict):
            attributes = item.get("attributes") or {}
            for key, value in attributes.items():
                if key in {"properties", "state"}:
                    continue
                signatures.append(f"{object_id}::attribute::{_safe_str(key)}={_normalized_text(value)}")
    return signatures


def _confidence_signature(item: Dict[str, Any]) -> str:
    confidence = item.get("confidence")
    if isinstance(confidence, dict):
        parts = [f"{key}={_safe_str(value)}" for key, value in sorted(confidence.items())]
        return "|".join(parts)
    if confidence is None:
        return ""
    return _safe_str(confidence)


def _lifecycle_signature(item: Dict[str, Any]) -> str:
    lifecycle = item.get("lifecycle") if isinstance(item.get("lifecycle"), dict) else {}
    parts = [f"{key}={bool(value)}" for key, value in sorted(lifecycle.items()) if isinstance(value, (bool, int, float, str))]
    return "|".join(parts)


def _frame_signature(item: Dict[str, Any]) -> str:
    frame_id = _safe_str(item.get("id") or item.get("frame_id") or "")
    predicate = _safe_str(item.get("predicate") or item.get("label") or "")
    arguments = item.get("arguments") if isinstance(item.get("arguments"), dict) else {}
    arg_parts = [f"{key}={_normalized_text(value)}" for key, value in sorted(arguments.items())]
    return "||".join([frame_id, predicate] + arg_parts)


def _conversation_signature(item: Dict[str, Any]) -> str:
    turn_id = _safe_str(item.get("id") or item.get("turn_id") or "")
    speaker = _safe_str(item.get("speaker") or "")
    dialogue_act = _safe_str(item.get("dialogue_act") or "")
    intent = _safe_str(item.get("intent") or "")
    content = _normalized_text(item.get("content") or item.get("value") or item.get("label") or "")
    return "||".join([turn_id, speaker, dialogue_act, intent, content])


@dataclass
class SemanticSnapshot:
    stage: str
    objects: List[Dict[str, Any]] = field(default_factory=list)
    relations: List[Dict[str, Any]] = field(default_factory=list)
    constraints: List[Dict[str, Any]] = field(default_factory=list)
    attributes: List[str] = field(default_factory=list)
    states: List[str] = field(default_factory=list)
    frames: List[Dict[str, Any]] = field(default_factory=list)
    conversations: List[Dict[str, Any]] = field(default_factory=list)
    provenance: List[str] = field(default_factory=list)
    confidence: List[str] = field(default_factory=list)
    lifecycle: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def signature_sets(self) -> Dict[str, set[str]]:
        return {
            "objects": {item["signature"] for item in self.objects},
            "relations": {item["signature"] for item in self.relations},
            "constraints": {item["signature"] for item in self.constraints},
            "attributes": set(self.attributes),
            "states": set(self.states),
            "frames": {item["signature"] for item in self.frames},
            "conversations": {item["signature"] for item in self.conversations},
            "provenance": set(self.provenance),
            "confidence": set(self.confidence),
            "lifecycle": set(self.lifecycle),
        }

    def counts(self) -> Dict[str, int]:
        sets = self.signature_sets()
        return {key: len(value) for key, value in sets.items()}

    def as_dict(self) -> Dict[str, Any]:
        return {
            "stage": self.stage,
            "objects": list(self.objects),
            "relations": list(self.relations),
            "constraints": list(self.constraints),
            "attributes": list(self.attributes),
            "states": list(self.states),
            "frames": list(self.frames),
            "conversations": list(self.conversations),
            "provenance": list(self.provenance),
            "confidence": list(self.confidence),
            "lifecycle": list(self.lifecycle),
            "metadata": dict(self.metadata),
            "counts": self.counts(),
        }


def _build_objects(payload: Dict[str, Any], *, stage: str) -> List[Dict[str, Any]]:
    objects = _as_dict_list(payload.get("objects"))
    if not objects:
        return []
    built: List[Dict[str, Any]] = []
    for item in objects:
        signature = _object_signature(item)
        built.append(
            {
                "signature": signature,
                "object_id": signature,
                "type": _safe_str(item.get("type") or item.get("object_type") or "fact") or "fact",
                "value": _safe_str(item.get("value") or item.get("label") or ""),
                "confidence": item.get("confidence"),
                "evidence_pointer": _safe_str(item.get("evidence_pointer") or ""),
                "lifecycle": item.get("lifecycle") if isinstance(item.get("lifecycle"), dict) else {},
                "provenance": item.get("provenance") if isinstance(item.get("provenance"), dict) else {},
                "stage": stage,
            }
        )
    return built


def _build_relations_from_dependency_objects(items: Any, *, stage: str) -> List[Dict[str, Any]]:
    dependencies = _as_dict_list(items)
    built: List[Dict[str, Any]] = []
    for item in dependencies:
        if all(isinstance(item.get(part), dict) for part in ["subject", "relation", "object"]):
            subject = item.get("subject") or {}
            relation = item.get("relation") or {}
            obj = item.get("object") or {}
            source = _safe_str(subject.get("canonical") or subject.get("value") or "")
            rel = _safe_str(relation.get("canonical") or relation.get("value") or "")
            target = _safe_str(obj.get("canonical") or obj.get("value") or "")
            signature = "||".join([_normalized_text(source), _normalized_text(rel), _normalized_text(target)])
        else:
            signature = _relation_signature(item)
        if not signature:
            continue
        built.append(
            {
                "signature": signature,
                "source": _safe_str(item.get("source") or item.get("subject") or ""),
                "relation": _safe_str(item.get("relation") or item.get("edge_type") or ""),
                "target": _safe_str(item.get("target") or item.get("object") or ""),
                "confidence": item.get("confidence"),
                "provenance": item.get("provenance") if isinstance(item.get("provenance"), dict) else {},
                "stage": stage,
            }
        )
    return built


def _build_constraints(payload: Dict[str, Any], *, stage: str) -> List[Dict[str, Any]]:
    built: List[Dict[str, Any]] = []
    for item in list(payload.get("constraints") or []):
        text = _safe_str(item)
        if not text:
            continue
        built.append(
            {
                "signature": _normalized_text(text),
                "value": text,
                "stage": stage,
            }
        )
    return built


def _build_frames(payload: Dict[str, Any], *, stage: str) -> List[Dict[str, Any]]:
    frames = _as_dict_list(payload.get("frames"))
    built: List[Dict[str, Any]] = []
    for item in frames:
        signature = _frame_signature(item)
        if not signature:
            continue
        built.append(
            {
                "signature": signature,
                "frame_id": _safe_str(item.get("id") or item.get("frame_id") or ""),
                "predicate": _safe_str(item.get("predicate") or item.get("label") or ""),
                "arguments": dict(item.get("arguments") or {}) if isinstance(item.get("arguments"), dict) else {},
                "confidence": item.get("confidence"),
                "provenance": item.get("provenance") if isinstance(item.get("provenance"), dict) else {},
                "stage": stage,
            }
        )
    return built


def _build_conversations(payload: Dict[str, Any], *, stage: str) -> List[Dict[str, Any]]:
    turns = _as_dict_list(payload.get("conversations"))
    built: List[Dict[str, Any]] = []
    for item in turns:
        signature = _conversation_signature(item)
        if not signature:
            continue
        built.append(
            {
                "signature": signature,
                "turn_id": _safe_str(item.get("id") or item.get("turn_id") or ""),
                "speaker": _safe_str(item.get("speaker") or ""),
                "intent": _safe_str(item.get("intent") or ""),
                "dialogue_act": _safe_str(item.get("dialogue_act") or ""),
                "content": _safe_str(item.get("content") or item.get("value") or item.get("label") or ""),
                "confidence": item.get("confidence"),
                "provenance": item.get("provenance") if isinstance(item.get("provenance"), dict) else {},
                "stage": stage,
            }
        )
    return built


def _build_from_graph(graph: Dict[str, Any], *, stage: str) -> SemanticSnapshot:
    nodes = _as_dict_list(graph.get("nodes"))
    edges = _as_dict_list(graph.get("edges"))
    objects: List[Dict[str, Any]] = []
    relations: List[Dict[str, Any]] = []
    constraints: List[Dict[str, Any]] = []
    frames: List[Dict[str, Any]] = []
    conversations: List[Dict[str, Any]] = []
    for node in nodes:
        node_type = _safe_str(node.get("type") or "")
        node_id = _safe_str(node.get("id") or node.get("node_id") or "")
        label = _safe_str(node.get("label") or "")
        if not label and isinstance(node.get("identity"), dict):
            label = _safe_str((node.get("identity") or {}).get("canonical_name") or "")
        signature = node_id or f"{node_type}:{_normalized_text(label)}"
        if node_type in {"frame"}:
            frames.append(
                {
                    "signature": signature,
                    "frame_id": node_id,
                    "predicate": label,
                    "arguments": dict(node.get("arguments") or {}),
                    "confidence": node.get("confidence"),
                    "provenance": node.get("provenance") if isinstance(node.get("provenance"), dict) else {},
                    "stage": stage,
                }
            )
            continue
        if node_type in {"conversation_turn"}:
            conversations.append(
                {
                    "signature": signature,
                    "turn_id": node_id,
                    "speaker": _safe_str(node.get("speaker") or ""),
                    "intent": _safe_str(node.get("intent") or ""),
                    "dialogue_act": _safe_str(node.get("dialogue_act") or ""),
                    "content": label,
                    "confidence": node.get("confidence"),
                    "provenance": node.get("provenance") if isinstance(node.get("provenance"), dict) else {},
                    "stage": stage,
                }
            )
            continue
        if node_type.startswith("contract_"):
            constraints.append({"signature": signature, "value": label, "stage": stage})
            continue
        objects.append(
            {
                "signature": signature,
                "object_id": signature,
                "type": node_type or "object",
                "value": label,
                "confidence": node.get("confidence"),
                "evidence_pointer": _safe_str((node.get("provenance") or {}).get("evidence_pointer") if isinstance(node.get("provenance"), dict) else ""),
                "lifecycle": node.get("lifecycle") if isinstance(node.get("lifecycle"), dict) else {},
                "provenance": node.get("provenance") if isinstance(node.get("provenance"), dict) else {},
                "stage": stage,
            }
        )
    for edge in edges:
        source = _safe_str(edge.get("source") or "")
        target = _safe_str(edge.get("target") or "")
        relation = _safe_str(edge.get("relation") or "")
        if not relation:
            continue
        relations.append(
            {
                "signature": "||".join([_normalized_text(source), _normalized_text(relation), _normalized_text(target)]),
                "source": source,
                "relation": relation,
                "target": target,
                "confidence": edge.get("confidence"),
                "provenance": edge.get("provenance") if isinstance(edge.get("provenance"), dict) else {},
                "stage": stage,
            }
        )
    attributes = _attribute_signatures(objects)
    states = []
    for item in objects:
        state = item.get("state") if isinstance(item.get("state"), dict) else {}
        for key, value in state.items():
            states.append(f"{item['signature']}::state::{_safe_str(key)}={_normalized_text(value)}")
    provenance = [item["signature"] for item in objects if item.get("provenance")] + [item["signature"] for item in relations if item.get("provenance")]
    confidence = [_confidence_signature(item) for item in objects if _confidence_signature(item)] + [_confidence_signature(item) for item in relations if _confidence_signature(item)]
    lifecycle = [_lifecycle_signature(item) for item in objects if _lifecycle_signature(item)]
    return SemanticSnapshot(
        stage=stage,
        objects=objects,
        relations=relations,
        constraints=constraints,
        attributes=attributes,
        states=states,
        frames=frames,
        conversations=conversations,
        provenance=provenance,
        confidence=confidence,
        lifecycle=lifecycle,
        metadata={"graph_schema_version": graph.get("schema_version")},
    )


def _build_from_runtime_representation(representation: Dict[str, Any], *, stage: str) -> SemanticSnapshot:
    objects = _as_dict_list(representation.get("objects"))
    frames = _as_dict_list(representation.get("frames"))
    narratives = _as_dict_list(representation.get("narratives"))
    conversations = _as_dict_list(representation.get("conversations"))

    built_objects: List[Dict[str, Any]] = []
    for item in objects:
        signature = _safe_str(item.get("id") or item.get("object_id") or "")
        if not signature:
            signature = _object_signature(item)
        built_objects.append(
            {
                "signature": signature,
                "object_id": signature,
                "type": _safe_str(item.get("type") or "object"),
                "value": _safe_str(item.get("label") or item.get("value") or ""),
                "confidence": item.get("confidence"),
                "evidence_pointer": _safe_str((item.get("provenance") or {}).get("evidence_pointer") if isinstance(item.get("provenance"), dict) else ""),
                "lifecycle": item.get("lifecycle") if isinstance(item.get("lifecycle"), dict) else {},
                "provenance": item.get("provenance") if isinstance(item.get("provenance"), dict) else {},
                "state": item.get("state") if isinstance(item.get("state"), dict) else {},
                "properties": item.get("properties") if isinstance(item.get("properties"), dict) else {},
                "relations": list(item.get("relations") or []) if isinstance(item.get("relations"), list) else [],
                "stage": stage,
            }
        )

    built_frames = _build_frames({"frames": frames}, stage=stage)
    built_narratives = []
    for item in narratives:
        signature = _safe_str(item.get("id") or "")
        if not signature:
            signature = _normalized_text(item.get("episode") or item.get("goal") or item.get("conflict") or item.get("resolution") or "")
        built_narratives.append(
            {
                "signature": signature,
                "narrative_id": _safe_str(item.get("id") or ""),
                "episode": _safe_str(item.get("episode") or ""),
                "goal": _safe_str(item.get("goal") or ""),
                "conflict": _safe_str(item.get("conflict") or ""),
                "resolution": _safe_str(item.get("resolution") or ""),
                "confidence": item.get("confidence"),
                "provenance": item.get("provenance") if isinstance(item.get("provenance"), dict) else {},
                "stage": stage,
            }
        )
    built_conversations = _build_conversations({"conversations": conversations}, stage=stage)

    relations: List[Dict[str, Any]] = []
    for item in built_objects:
        for relation in item.get("relations", []) if isinstance(item.get("relations"), list) else []:
            relation = relation if isinstance(relation, dict) else {}
            relation_signature = _relation_signature(relation)
            if relation_signature:
                relations.append(
                    {
                        "signature": relation_signature,
                        "source": item["signature"],
                        "relation": _safe_str(relation.get("relation") or ""),
                        "target": _safe_str(relation.get("target") or ""),
                        "confidence": relation.get("confidence"),
                        "provenance": relation.get("provenance") if isinstance(relation.get("provenance"), dict) else {},
                        "stage": stage,
                    }
                )

    attributes = _attribute_signatures(built_objects)
    states = []
    for item in built_objects:
        state = item.get("state") if isinstance(item.get("state"), dict) else {}
        for key, value in state.items():
            states.append(f"{item['signature']}::state::{_safe_str(key)}={_normalized_text(value)}")
    provenance = [item["signature"] for item in built_objects if item.get("provenance")] + [item["signature"] for item in built_frames if item.get("provenance")] + [item["signature"] for item in built_narratives if item.get("provenance")] + [item["signature"] for item in built_conversations if item.get("provenance")]
    confidence = [_confidence_signature(item) for item in built_objects if _confidence_signature(item)] + [_confidence_signature(item) for item in built_frames if _confidence_signature(item)] + [_confidence_signature(item) for item in built_narratives if _confidence_signature(item)] + [_confidence_signature(item) for item in built_conversations if _confidence_signature(item)]
    lifecycle = [_lifecycle_signature(item) for item in built_objects if _lifecycle_signature(item)] + [_lifecycle_signature(item) for item in built_frames if _lifecycle_signature(item)] + [_lifecycle_signature(item) for item in built_narratives if _lifecycle_signature(item)] + [_lifecycle_signature(item) for item in built_conversations if _lifecycle_signature(item)]

    return SemanticSnapshot(
        stage=stage,
        objects=built_objects,
        relations=relations,
        constraints=[],
        attributes=attributes,
        states=states,
        frames=built_frames,
        conversations=built_conversations,
        provenance=provenance,
        confidence=confidence,
        lifecycle=lifecycle,
        metadata={"schema_version": representation.get("schema_version")},
    )


def _validation_snapshot(record: Dict[str, Any], *, stage: str) -> SemanticSnapshot:
    validation = record.get("validation") or {}
    recovered_package = record.get("recovered_package") or record.get("recovered_state_package") or {}
    recovered_objects = _build_objects((recovered_package.get("typed_representation") or {}), stage=stage)
    object_alignment = validation.get("object_alignment") or {}
    matched_object_ids: set[str] = set()
    for group in object_alignment.values():
        for match in group.get("matches", []):
            if float(match.get("similarity", 0.0)) >= 0.5:
                object_id = _safe_str(match.get("source_object_id") or match.get("recovered_object_id") or "")
                if object_id:
                    matched_object_ids.add(object_id)
    validated_objects = [item for item in recovered_objects if item["signature"] in matched_object_ids or not matched_object_ids]
    dependency_audit = validation.get("dependency_audit") or {}
    relation_ids = dependency_audit.get("matched_objects") or []
    relations = [
        {
            "signature": _normalized_text(item),
            "source": "",
            "relation": "validated_dependency",
            "target": "",
            "stage": stage,
        }
        for item in relation_ids
    ]
    return SemanticSnapshot(
        stage=stage,
        objects=validated_objects,
        relations=relations,
        constraints=[],
        attributes=_attribute_signatures(validated_objects),
        states=[],
        frames=[],
        conversations=[],
        provenance=[item["signature"] for item in validated_objects if item.get("provenance")],
        confidence=[_confidence_signature(item) for item in validated_objects if _confidence_signature(item)],
        lifecycle=[_lifecycle_signature(item) for item in validated_objects if _lifecycle_signature(item)],
        metadata={"validation_coverage": validation.get("coverage_score"), "passed": validation.get("passed")},
    )


def build_semantic_snapshot(record: Dict[str, Any], stage: str) -> SemanticSnapshot:
    stage = str(stage).strip().lower()
    if stage == "source":
        payload = record.get("source_package") or {}
        objects = _build_objects((payload.get("semantic_object_inventory") or payload.get("typed_representation") or {}), stage=stage)
        relations = _build_relations_from_dependency_objects((payload.get("semantic_dependencies") or {}).get("required_dependency_objects"), stage=stage)
        constraints = _build_constraints(payload, stage=stage)
        attributes = _attribute_signatures(objects)
        states = [f"{item['signature']}::state" for item in objects]
        provenance = [item["signature"] for item in objects if item.get("provenance")]
        confidence = [_confidence_signature(item) for item in objects if _confidence_signature(item)]
        lifecycle = [_lifecycle_signature(item) for item in objects if _lifecycle_signature(item)]
        return SemanticSnapshot(
            stage=stage,
            objects=objects,
            relations=relations,
            constraints=constraints,
            attributes=attributes,
            states=states,
            frames=[],
            conversations=[],
            provenance=provenance,
            confidence=confidence,
            lifecycle=lifecycle,
            metadata={"source_memory": _safe_str((payload.get("memory") or ""))},
        )
    if stage == "extraction":
        representation = record.get("runtime_representation_v2") or {}
        if representation:
            return _build_from_runtime_representation(representation, stage=stage)
        return _build_from_graph(record.get("semantic_runtime_graph") or {}, stage=stage)
    if stage == "representation":
        representation = record.get("runtime_representation_v2") or {}
        if representation:
            return _build_from_runtime_representation(representation, stage=stage)
        return _build_from_graph(record.get("semantic_runtime_graph") or {}, stage=stage)
    if stage == "compression":
        payload = record.get("compressed_package") or record.get("representation") or {}
        if isinstance(payload, dict) and "semantic_object_inventory" in payload:
            objects = _build_objects(payload.get("semantic_object_inventory") or {}, stage=stage)
            relations = _build_relations_from_dependency_objects((payload.get("semantic_dependencies") or {}).get("required_dependency_objects"), stage=stage)
            constraints = _build_constraints(payload, stage=stage)
            return SemanticSnapshot(
                stage=stage,
                objects=objects,
                relations=relations,
                constraints=constraints,
                attributes=_attribute_signatures(objects),
                states=[f"{item['signature']}::state" for item in objects],
                provenance=[item["signature"] for item in objects if item.get("provenance")],
                confidence=[_confidence_signature(item) for item in objects if _confidence_signature(item)],
                lifecycle=[_lifecycle_signature(item) for item in objects if _lifecycle_signature(item)],
                metadata={"memory": _safe_str(payload.get("memory") or "")},
            )
        if isinstance(payload, dict) and "nodes" in payload:
            return _build_from_graph(payload, stage=stage)
        return SemanticSnapshot(stage=stage, metadata={"note": "no compression payload available"})
    if stage == "recovery":
        payload = record.get("recovered_package") or record.get("recovered_state_package") or {}
        objects = _build_objects((payload.get("typed_representation") or {}), stage=stage)
        return SemanticSnapshot(
            stage=stage,
            objects=objects,
            relations=[],
            constraints=[],
            attributes=_attribute_signatures(objects),
            states=[f"{item['signature']}::state" for item in objects],
            provenance=[item["signature"] for item in objects if item.get("provenance")],
            confidence=[_confidence_signature(item) for item in objects if _confidence_signature(item)],
            lifecycle=[_lifecycle_signature(item) for item in objects if _lifecycle_signature(item)],
            metadata={"recovered_text": _safe_str(record.get("recovered_text") or "")},
        )
    if stage == "validation":
        return _validation_snapshot(record, stage=stage)
    raise ValueError(f"Unknown snapshot stage: {stage}")


def build_stage_snapshots(record: Dict[str, Any]) -> Dict[str, SemanticSnapshot]:
    snapshots: Dict[str, SemanticSnapshot] = {}
    for stage in ["source", "extraction", "representation", "compression", "recovery", "validation"]:
        try:
            snapshots[stage] = build_semantic_snapshot(record, stage)
        except Exception:
            continue
    return snapshots
