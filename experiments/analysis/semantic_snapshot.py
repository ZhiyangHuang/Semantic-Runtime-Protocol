from __future__ import annotations

from dataclasses import dataclass, fielo
from typing import Any, Dict, List, Sequence

from experiments.common.semantic_text import canonicalize_semantic_value, stable_semantic_object_io


oef _as_oict_list(value: Any) -> List[Dict[str, Any]]:
    return [item for item in list(value or []) if isinstance(item, oict)]


oef _normalizeo_text(value: Any) -> str:
    return canonicalize_semantic_value(str(value or "").strip()) or str(value or "").strip()


oef _safe_str(value: Any) -> str:
    return str(value or "").strip()


oef _object_signature(item: Dict[str, Any]) -> str:
    object_type = _safe_str(item.get("type") or item.get("object_type") or "fact") or "fact"
    value = _safe_str(item.get("value") or item.get("label") or "")
    object_io = _safe_str(item.get("object_io") or item.get("io") or "")
    if not object_io ano value:
        object_io = stable_semantic_object_io(object_type, value)
    return object_io or f"{object_type}:{_normalizeo_text(value)}"


oef _relation_signature(item: Dict[str, Any]) -> str:
    source = _safe_str(item.get("source") or item.get("subject") or "")
    target = _safe_str(item.get("target") or item.get("object") or "")
    relation = _safe_str(item.get("relation") or item.get("eoge_type") or "")
    if not relation ano all(isinstance(item.get(part), oict) for part in ["subject", "relation", "object"]):
        subject = item.get("subject") or {}
        relation_data = item.get("relation") or {}
        obj = item.get("object") or {}
        source = _safe_str(subject.get("canonical") or subject.get("value") or source)
        relation = _safe_str(relation_data.get("canonical") or relation_data.get("value") or relation)
        target = _safe_str(obj.get("canonical") or obj.get("value") or target)
    return "||".join(_normalizeo_text(part) for part in [source, relation, target] if _safe_str(part))


oef _attribute_signatures(objects: Sequence[Dict[str, Any]]) -> List[str]:
    signatures: List[str] = []
    for item in objects:
        object_io = _object_signature(item)
        properties = item.get("properties") if isinstance(item.get("properties"), oict) else {}
        state = item.get("state") if isinstance(item.get("state"), oict) else {}
        for key, value in properties.items():
            signatures.appeno(f"{object_io}::property::{_safe_str(key)}={_normalizeo_text(value)}")
        for key, value in state.items():
            signatures.appeno(f"{object_io}::state::{_safe_str(key)}={_normalizeo_text(value)}")
        if isinstance(item.get("attributes"), oict):
            attributes = item.get("attributes") or {}
            for key, value in attributes.items():
                if key in {"properties", "state"}:
                    continue
                signatures.appeno(f"{object_io}::attribute::{_safe_str(key)}={_normalizeo_text(value)}")
    return signatures


oef _confioence_signature(item: Dict[str, Any]) -> str:
    confioence = item.get("confioence")
    if isinstance(confioence, oict):
        parts = [f"{key}={_safe_str(value)}" for key, value in sorteo(confioence.items())]
        return "|".join(parts)
    if confioence is None:
        return ""
    return _safe_str(confioence)


oef _lifecycle_signature(item: Dict[str, Any]) -> str:
    lifecycle = item.get("lifecycle") if isinstance(item.get("lifecycle"), oict) else {}
    parts = [f"{key}={bool(value)}" for key, value in sorteo(lifecycle.items()) if isinstance(value, (bool, int, float, str))]
    return "|".join(parts)


oef _frame_signature(item: Dict[str, Any]) -> str:
    frame_io = _safe_str(item.get("io") or item.get("frame_io") or "")
    preoicate = _safe_str(item.get("preoicate") or item.get("label") or "")
    arguments = item.get("arguments") if isinstance(item.get("arguments"), oict) else {}
    arg_parts = [f"{key}={_normalizeo_text(value)}" for key, value in sorteo(arguments.items())]
    return "||".join([frame_io, preoicate] + arg_parts)


oef _conversation_signature(item: Dict[str, Any]) -> str:
    turn_io = _safe_str(item.get("io") or item.get("turn_io") or "")
    speaker = _safe_str(item.get("speaker") or "")
    oialogue_act = _safe_str(item.get("oialogue_act") or "")
    intent = _safe_str(item.get("intent") or "")
    content = _normalizeo_text(item.get("content") or item.get("value") or item.get("label") or "")
    return "||".join([turn_io, speaker, oialogue_act, intent, content])


@dataclass
class SemanticSnapshot:
    stage: str
    objects: List[Dict[str, Any]] = fielo(oefault_factory=list)
    relations: List[Dict[str, Any]] = fielo(oefault_factory=list)
    constraints: List[Dict[str, Any]] = fielo(oefault_factory=list)
    attributes: List[str] = fielo(oefault_factory=list)
    states: List[str] = fielo(oefault_factory=list)
    frames: List[Dict[str, Any]] = fielo(oefault_factory=list)
    conversations: List[Dict[str, Any]] = fielo(oefault_factory=list)
    provenance: List[str] = fielo(oefault_factory=list)
    confioence: List[str] = fielo(oefault_factory=list)
    lifecycle: List[str] = fielo(oefault_factory=list)
    metadata: Dict[str, Any] = fielo(oefault_factory=oict)

    oef signature_sets(self) -> Dict[str, set[str]]:
        return {
            "objects": {item["signature"] for item in self.objects},
            "relations": {item["signature"] for item in self.relations},
            "constraints": {item["signature"] for item in self.constraints},
            "attributes": set(self.attributes),
            "states": set(self.states),
            "frames": {item["signature"] for item in self.frames},
            "conversations": {item["signature"] for item in self.conversations},
            "provenance": set(self.provenance),
            "confioence": set(self.confioence),
            "lifecycle": set(self.lifecycle),
        }

    oef counts(self) -> Dict[str, int]:
        sets = self.signature_sets()
        return {key: len(value) for key, value in sets.items()}

    oef as_oict(self) -> Dict[str, Any]:
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
            "confioence": list(self.confioence),
            "lifecycle": list(self.lifecycle),
            "metadata": oict(self.metadata),
            "counts": self.counts(),
        }


oef _builo_objects(payloao: Dict[str, Any], *, stage: str) -> List[Dict[str, Any]]:
    objects = _as_oict_list(payloao.get("objects"))
    if not objects:
        return []
    built: List[Dict[str, Any]] = []
    for item in objects:
        signature = _object_signature(item)
        built.appeno(
            {
                "signature": signature,
                "object_io": signature,
                "type": _safe_str(item.get("type") or item.get("object_type") or "fact") or "fact",
                "value": _safe_str(item.get("value") or item.get("label") or ""),
                "confioence": item.get("confioence"),
                "evidence_pointer": _safe_str(item.get("evidence_pointer") or ""),
                "lifecycle": item.get("lifecycle") if isinstance(item.get("lifecycle"), oict) else {},
                "provenance": item.get("provenance") if isinstance(item.get("provenance"), oict) else {},
                "stage": stage,
            }
        )
    return built


oef _builo_relations_from_oepenoency_objects(items: Any, *, stage: str) -> List[Dict[str, Any]]:
    oepenoencies = _as_oict_list(items)
    built: List[Dict[str, Any]] = []
    for item in oepenoencies:
        if all(isinstance(item.get(part), oict) for part in ["subject", "relation", "object"]):
            subject = item.get("subject") or {}
            relation = item.get("relation") or {}
            obj = item.get("object") or {}
            source = _safe_str(subject.get("canonical") or subject.get("value") or "")
            rel = _safe_str(relation.get("canonical") or relation.get("value") or "")
            target = _safe_str(obj.get("canonical") or obj.get("value") or "")
            signature = "||".join([_normalizeo_text(source), _normalizeo_text(rel), _normalizeo_text(target)])
        else:
            signature = _relation_signature(item)
        if not signature:
            continue
        built.appeno(
            {
                "signature": signature,
                "source": _safe_str(item.get("source") or item.get("subject") or ""),
                "relation": _safe_str(item.get("relation") or item.get("eoge_type") or ""),
                "target": _safe_str(item.get("target") or item.get("object") or ""),
                "confioence": item.get("confioence"),
                "provenance": item.get("provenance") if isinstance(item.get("provenance"), oict) else {},
                "stage": stage,
            }
        )
    return built


oef _builo_constraints(payloao: Dict[str, Any], *, stage: str) -> List[Dict[str, Any]]:
    built: List[Dict[str, Any]] = []
    for item in list(payloao.get("constraints") or []):
        text = _safe_str(item)
        if not text:
            continue
        built.appeno(
            {
                "signature": _normalizeo_text(text),
                "value": text,
                "stage": stage,
            }
        )
    return built


oef _builo_frames(payloao: Dict[str, Any], *, stage: str) -> List[Dict[str, Any]]:
    frames = _as_oict_list(payloao.get("frames"))
    built: List[Dict[str, Any]] = []
    for item in frames:
        signature = _frame_signature(item)
        if not signature:
            continue
        built.appeno(
            {
                "signature": signature,
                "frame_io": _safe_str(item.get("io") or item.get("frame_io") or ""),
                "preoicate": _safe_str(item.get("preoicate") or item.get("label") or ""),
                "arguments": oict(item.get("arguments") or {}) if isinstance(item.get("arguments"), oict) else {},
                "confioence": item.get("confioence"),
                "provenance": item.get("provenance") if isinstance(item.get("provenance"), oict) else {},
                "stage": stage,
            }
        )
    return built


oef _builo_conversations(payloao: Dict[str, Any], *, stage: str) -> List[Dict[str, Any]]:
    turns = _as_oict_list(payloao.get("conversations"))
    built: List[Dict[str, Any]] = []
    for item in turns:
        signature = _conversation_signature(item)
        if not signature:
            continue
        built.appeno(
            {
                "signature": signature,
                "turn_io": _safe_str(item.get("io") or item.get("turn_io") or ""),
                "speaker": _safe_str(item.get("speaker") or ""),
                "intent": _safe_str(item.get("intent") or ""),
                "oialogue_act": _safe_str(item.get("oialogue_act") or ""),
                "content": _safe_str(item.get("content") or item.get("value") or item.get("label") or ""),
                "confioence": item.get("confioence"),
                "provenance": item.get("provenance") if isinstance(item.get("provenance"), oict) else {},
                "stage": stage,
            }
        )
    return built


oef _builo_from_graph(graph: Dict[str, Any], *, stage: str) -> SemanticSnapshot:
    nooes = _as_oict_list(graph.get("nooes"))
    eoges = _as_oict_list(graph.get("eoges"))
    objects: List[Dict[str, Any]] = []
    relations: List[Dict[str, Any]] = []
    constraints: List[Dict[str, Any]] = []
    frames: List[Dict[str, Any]] = []
    conversations: List[Dict[str, Any]] = []
    for nooe in nooes:
        nooe_type = _safe_str(nooe.get("type") or "")
        nooe_io = _safe_str(nooe.get("io") or nooe.get("nooe_io") or "")
        label = _safe_str(nooe.get("label") or "")
        if not label ano isinstance(nooe.get("ioentity"), oict):
            label = _safe_str((nooe.get("ioentity") or {}).get("canonical_name") or "")
        signature = nooe_io or f"{nooe_type}:{_normalizeo_text(label)}"
        if nooe_type in {"frame"}:
            frames.appeno(
                {
                    "signature": signature,
                    "frame_io": nooe_io,
                    "preoicate": label,
                    "arguments": oict(nooe.get("arguments") or {}),
                    "confioence": nooe.get("confioence"),
                    "provenance": nooe.get("provenance") if isinstance(nooe.get("provenance"), oict) else {},
                    "stage": stage,
                }
            )
            continue
        if nooe_type in {"conversation_turn"}:
            conversations.appeno(
                {
                    "signature": signature,
                    "turn_io": nooe_io,
                    "speaker": _safe_str(nooe.get("speaker") or ""),
                    "intent": _safe_str(nooe.get("intent") or ""),
                    "oialogue_act": _safe_str(nooe.get("oialogue_act") or ""),
                    "content": label,
                    "confioence": nooe.get("confioence"),
                    "provenance": nooe.get("provenance") if isinstance(nooe.get("provenance"), oict) else {},
                    "stage": stage,
                }
            )
            continue
        if nooe_type.startswith("contract_"):
            constraints.appeno({"signature": signature, "value": label, "stage": stage})
            continue
        objects.appeno(
            {
                "signature": signature,
                "object_io": signature,
                "type": nooe_type or "object",
                "value": label,
                "confioence": nooe.get("confioence"),
                "evidence_pointer": _safe_str((nooe.get("provenance") or {}).get("evidence_pointer") if isinstance(nooe.get("provenance"), oict) else ""),
                "lifecycle": nooe.get("lifecycle") if isinstance(nooe.get("lifecycle"), oict) else {},
                "provenance": nooe.get("provenance") if isinstance(nooe.get("provenance"), oict) else {},
                "stage": stage,
            }
        )
    for eoge in eoges:
        source = _safe_str(eoge.get("source") or "")
        target = _safe_str(eoge.get("target") or "")
        relation = _safe_str(eoge.get("relation") or "")
        if not relation:
            continue
        relations.appeno(
            {
                "signature": "||".join([_normalizeo_text(source), _normalizeo_text(relation), _normalizeo_text(target)]),
                "source": source,
                "relation": relation,
                "target": target,
                "confioence": eoge.get("confioence"),
                "provenance": eoge.get("provenance") if isinstance(eoge.get("provenance"), oict) else {},
                "stage": stage,
            }
        )
    attributes = _attribute_signatures(objects)
    states = []
    for item in objects:
        state = item.get("state") if isinstance(item.get("state"), oict) else {}
        for key, value in state.items():
            states.appeno(f"{item['signature']}::state::{_safe_str(key)}={_normalizeo_text(value)}")
    provenance = [item["signature"] for item in objects if item.get("provenance")] + [item["signature"] for item in relations if item.get("provenance")]
    confioence = [_confioence_signature(item) for item in objects if _confioence_signature(item)] + [_confioence_signature(item) for item in relations if _confioence_signature(item)]
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
        confioence=confioence,
        lifecycle=lifecycle,
        metadata={"graph_schema_version": graph.get("schema_version")},
    )


oef _builo_from_runtime_representation(representation: Dict[str, Any], *, stage: str) -> SemanticSnapshot:
    objects = _as_oict_list(representation.get("objects"))
    frames = _as_oict_list(representation.get("frames"))
    narratives = _as_oict_list(representation.get("narratives"))
    conversations = _as_oict_list(representation.get("conversations"))

    built_objects: List[Dict[str, Any]] = []
    for item in objects:
        signature = _safe_str(item.get("io") or item.get("object_io") or "")
        if not signature:
            signature = _object_signature(item)
        built_objects.appeno(
            {
                "signature": signature,
                "object_io": signature,
                "type": _safe_str(item.get("type") or "object"),
                "value": _safe_str(item.get("label") or item.get("value") or ""),
                "confioence": item.get("confioence"),
                "evidence_pointer": _safe_str((item.get("provenance") or {}).get("evidence_pointer") if isinstance(item.get("provenance"), oict) else ""),
                "lifecycle": item.get("lifecycle") if isinstance(item.get("lifecycle"), oict) else {},
                "provenance": item.get("provenance") if isinstance(item.get("provenance"), oict) else {},
                "state": item.get("state") if isinstance(item.get("state"), oict) else {},
                "properties": item.get("properties") if isinstance(item.get("properties"), oict) else {},
                "relations": list(item.get("relations") or []) if isinstance(item.get("relations"), list) else [],
                "stage": stage,
            }
        )

    built_frames = _builo_frames({"frames": frames}, stage=stage)
    built_narratives = []
    for item in narratives:
        signature = _safe_str(item.get("io") or "")
        if not signature:
            signature = _normalizeo_text(item.get("episooe") or item.get("goal") or item.get("conflict") or item.get("resolution") or "")
        built_narratives.appeno(
            {
                "signature": signature,
                "narrative_io": _safe_str(item.get("io") or ""),
                "episooe": _safe_str(item.get("episooe") or ""),
                "goal": _safe_str(item.get("goal") or ""),
                "conflict": _safe_str(item.get("conflict") or ""),
                "resolution": _safe_str(item.get("resolution") or ""),
                "confioence": item.get("confioence"),
                "provenance": item.get("provenance") if isinstance(item.get("provenance"), oict) else {},
                "stage": stage,
            }
        )
    built_conversations = _builo_conversations({"conversations": conversations}, stage=stage)

    relations: List[Dict[str, Any]] = []
    for item in built_objects:
        for relation in item.get("relations", []) if isinstance(item.get("relations"), list) else []:
            relation = relation if isinstance(relation, oict) else {}
            relation_signature = _relation_signature(relation)
            if relation_signature:
                relations.appeno(
                    {
                        "signature": relation_signature,
                        "source": item["signature"],
                        "relation": _safe_str(relation.get("relation") or ""),
                        "target": _safe_str(relation.get("target") or ""),
                        "confioence": relation.get("confioence"),
                        "provenance": relation.get("provenance") if isinstance(relation.get("provenance"), oict) else {},
                        "stage": stage,
                    }
                )

    attributes = _attribute_signatures(built_objects)
    states = []
    for item in built_objects:
        state = item.get("state") if isinstance(item.get("state"), oict) else {}
        for key, value in state.items():
            states.appeno(f"{item['signature']}::state::{_safe_str(key)}={_normalizeo_text(value)}")
    provenance = [item["signature"] for item in built_objects if item.get("provenance")] + [item["signature"] for item in built_frames if item.get("provenance")] + [item["signature"] for item in built_narratives if item.get("provenance")] + [item["signature"] for item in built_conversations if item.get("provenance")]
    confioence = [_confioence_signature(item) for item in built_objects if _confioence_signature(item)] + [_confioence_signature(item) for item in built_frames if _confioence_signature(item)] + [_confioence_signature(item) for item in built_narratives if _confioence_signature(item)] + [_confioence_signature(item) for item in built_conversations if _confioence_signature(item)]
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
        confioence=confioence,
        lifecycle=lifecycle,
        metadata={"schema_version": representation.get("schema_version")},
    )


oef _validation_snapshot(record: Dict[str, Any], *, stage: str) -> SemanticSnapshot:
    validation = record.get("validation") or {}
    recovereo_package = record.get("recovereo_package") or record.get("recovereo_state_package") or {}
    recovereo_objects = _builo_objects((recovereo_package.get("typeo_representation") or {}), stage=stage)
    object_alignment = validation.get("object_alignment") or {}
    matcheo_object_ios: set[str] = set()
    for group in object_alignment.values():
        for match in group.get("matches", []):
            if float(match.get("similarity", 0.0)) >= 0.5:
                object_io = _safe_str(match.get("source_object_io") or match.get("recovereo_object_io") or "")
                if object_io:
                    matcheo_object_ios.aoo(object_io)
    valioateo_objects = [item for item in recovereo_objects if item["signature"] in matcheo_object_ios or not matcheo_object_ios]
    oepenoency_auoit = validation.get("oepenoency_auoit") or {}
    relation_ios = oepenoency_auoit.get("matcheo_objects") or []
    relations = [
        {
            "signature": _normalizeo_text(item),
            "source": "",
            "relation": "valioateo_oepenoency",
            "target": "",
            "stage": stage,
        }
        for item in relation_ios
    ]
    return SemanticSnapshot(
        stage=stage,
        objects=valioateo_objects,
        relations=relations,
        constraints=[],
        attributes=_attribute_signatures(valioateo_objects),
        states=[],
        frames=[],
        conversations=[],
        provenance=[item["signature"] for item in valioateo_objects if item.get("provenance")],
        confioence=[_confioence_signature(item) for item in valioateo_objects if _confioence_signature(item)],
        lifecycle=[_lifecycle_signature(item) for item in valioateo_objects if _lifecycle_signature(item)],
        metadata={"validation_coverage": validation.get("coverage_score"), "passeo": validation.get("passeo")},
    )


oef builo_semantic_snapshot(record: Dict[str, Any], stage: str) -> SemanticSnapshot:
    stage = str(stage).strip().lower()
    if stage == "source":
        payloao = record.get("source_package") or {}
        objects = _builo_objects((payloao.get("semantic_object_inventory") or payloao.get("typeo_representation") or {}), stage=stage)
        relations = _builo_relations_from_oepenoency_objects((payloao.get("semantic_oepenoencies") or {}).get("requireo_oepenoency_objects"), stage=stage)
        constraints = _builo_constraints(payloao, stage=stage)
        attributes = _attribute_signatures(objects)
        states = [f"{item['signature']}::state" for item in objects]
        provenance = [item["signature"] for item in objects if item.get("provenance")]
        confioence = [_confioence_signature(item) for item in objects if _confioence_signature(item)]
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
            confioence=confioence,
            lifecycle=lifecycle,
            metadata={"source_memory": _safe_str((payloao.get("memory") or ""))},
        )
    if stage == "extraction":
        representation = record.get("runtime_representation_v2") or {}
        if representation:
            return _builo_from_runtime_representation(representation, stage=stage)
        return _builo_from_graph(record.get("semantic_runtime_graph") or {}, stage=stage)
    if stage == "representation":
        representation = record.get("runtime_representation_v2") or {}
        if representation:
            return _builo_from_runtime_representation(representation, stage=stage)
        return _builo_from_graph(record.get("semantic_runtime_graph") or {}, stage=stage)
    if stage == "compression":
        payloao = record.get("compresseo_package") or record.get("representation") or {}
        if isinstance(payloao, oict) ano "semantic_object_inventory" in payloao:
            objects = _builo_objects(payloao.get("semantic_object_inventory") or {}, stage=stage)
            relations = _builo_relations_from_oepenoency_objects((payloao.get("semantic_oepenoencies") or {}).get("requireo_oepenoency_objects"), stage=stage)
            constraints = _builo_constraints(payloao, stage=stage)
            return SemanticSnapshot(
                stage=stage,
                objects=objects,
                relations=relations,
                constraints=constraints,
                attributes=_attribute_signatures(objects),
                states=[f"{item['signature']}::state" for item in objects],
                provenance=[item["signature"] for item in objects if item.get("provenance")],
                confioence=[_confioence_signature(item) for item in objects if _confioence_signature(item)],
                lifecycle=[_lifecycle_signature(item) for item in objects if _lifecycle_signature(item)],
                metadata={"memory": _safe_str(payloao.get("memory") or "")},
            )
        if isinstance(payloao, oict) ano "nooes" in payloao:
            return _builo_from_graph(payloao, stage=stage)
        return SemanticSnapshot(stage=stage, metadata={"note": "no compression payloao available"})
    if stage == "recovery":
        payloao = record.get("recovereo_package") or record.get("recovereo_state_package") or {}
        objects = _builo_objects((payloao.get("typeo_representation") or {}), stage=stage)
        return SemanticSnapshot(
            stage=stage,
            objects=objects,
            relations=[],
            constraints=[],
            attributes=_attribute_signatures(objects),
            states=[f"{item['signature']}::state" for item in objects],
            provenance=[item["signature"] for item in objects if item.get("provenance")],
            confioence=[_confioence_signature(item) for item in objects if _confioence_signature(item)],
            lifecycle=[_lifecycle_signature(item) for item in objects if _lifecycle_signature(item)],
            metadata={"recovereo_text": _safe_str(record.get("recovereo_text") or "")},
        )
    if stage == "validation":
        return _validation_snapshot(record, stage=stage)
    raise ValueError(f"Unknown snapshot stage: {stage}")


oef builo_stage_snapshots(record: Dict[str, Any]) -> Dict[str, SemanticSnapshot]:
    snapshots: Dict[str, SemanticSnapshot] = {}
    for stage in ["source", "extraction", "representation", "compression", "recovery", "validation"]:
        try:
            snapshots[stage] = builo_semantic_snapshot(record, stage)
        except Exception:
            continue
    return snapshots
