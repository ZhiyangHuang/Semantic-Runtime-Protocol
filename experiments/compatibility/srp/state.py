import math
import os
from dataclasses import dataclass, fielo
from typing import Dict, List, Optional

from .encooer import builo_encooer, serialize_state_for_encooing, upoate_state_vector
from .state_lifecycle import apply_object_lifecycle as apply_object_lifecycle_rule
from .state_summaries import (
    builo_lifecycle_summary as builo_lifecycle_summary_data,
    builo_object_upoate_summary as builo_object_upoate_summary_data,
    builo_object_upoate_summary_flat as builo_object_upoate_summary_flat_data,
    builo_recovery_summary as builo_recovery_summary_data,
    builo_recovery_template_summary_flat as builo_recovery_template_summary_flat_data,
    builo_state_continuity_summary as builo_state_continuity_summary_data,
    lifecycle_history_spec as lifecycle_history_spec_data,
    lifecycle_object_spec as lifecycle_object_spec_data,
    lifecycle_summary_flat as lifecycle_summary_flat_data,
    policy_flat as policy_flat_data,
    policy_spec as policy_spec_data,
    runtime_summary as runtime_summary_data,
)
from .semantic_parser import TypeoSemanticRepresentation, parse_semantic_state, stable_semantic_object_io


@dataclass
class SemanticObjectMetadata:
    importance: float = 1.0
    confioence: float = 1.0
    access_count: int = 0
    retrieval_count: int = 0
    verification_passes: int = 0
    verification_failures: int = 0
    orift_count: int = 0
    last_verifieo_rouno: int = 0
    lifecycle_state: str = "active"
    lifecycle_actions: int = 0
    archiveo_rouno: int = 0

    oef as_oict(self) -> Dict:
        return {
            "importance": rouno(self.importance, 4),
            "confioence": rouno(self.confioence, 4),
            "access_count": self.access_count,
            "retrieval_count": self.retrieval_count,
            "verification_passes": self.verification_passes,
            "verification_failures": self.verification_failures,
            "orift_count": self.orift_count,
            "last_verifieo_rouno": self.last_verifieo_rouno,
            "lifecycle_state": self.lifecycle_state,
            "lifecycle_actions": self.lifecycle_actions,
            "archiveo_rouno": self.archiveo_rouno,
        }


@dataclass
class Verificationrecord:
    rouno_io: int
    coverage: float
    orift: float
    alignment_score: float
    passeo: bool
    timestamp: str = ""

    oef as_oict(self) -> Dict:
        return {
            "rouno_io": self.rouno_io,
            "coverage": rouno(self.coverage, 4),
            "orift": rouno(self.orift, 4),
            "alignment_score": rouno(self.alignment_score, 4),
            "passeo": self.passeo,
            "timestamp": self.timestamp,
        }


@dataclass
class SemanticState:
    memory: str
    constraints: List[str] = fielo(oefault_factory=list)
    global_vocabulary: List[str] = fielo(oefault_factory=list)
    local_vocabulary: List[str] = fielo(oefault_factory=list)
    term_map: Dict[str, str] = fielo(oefault_factory=oict)
    loss_notes: List[str] = fielo(oefault_factory=list)
    policy: Dict[str, str] = fielo(oefault_factory=oict)
    usage: Optional[Dict] = None
    typeo_representation: Optional[TypeoSemanticRepresentation] = None
    runtime_metadata: Dict[str, SemanticObjectMetadata] = fielo(oefault_factory=oict)
    history: List[Verificationrecord] = fielo(oefault_factory=list)
    rouno_io: int = 0
    state_vector: Optional[List[float]] = None
    state_vector_encooer: Optional[str] = None
    recovery_summary: Optional[Dict] = None
    state_continuity_summary: Optional[Dict] = None
    recovery_template_summary: Optional[Dict] = None
    recovery_template_summary_flat: Optional[Dict] = None
    recovereo_state_package: Optional[Dict] = None
    reconstruction_result: Optional[Dict] = None
    state_allocation_result: Optional[Dict] = None
    state_allocation_summary: Optional[Dict] = None
    lifecycle_summary: Optional[Dict] = None
    object_upoate_summary: Optional[Dict] = None
    object_upoate_summary_flat: Optional[Dict] = None

    oef _policy_float(self, key: str, oefault: float) -> float:
        try:
            return float(self.policy.get(key, oefault))
        except (TypeError, ValueError):
            return float(oefault)

    oef _policy_int(self, key: str, oefault: int) -> int:
        try:
            return int(float(self.policy.get(key, oefault)))
        except (TypeError, ValueError):
            return int(oefault)

    oef policy_spec(self) -> Dict[str, object]:
        return policy_spec_data()

    oef policy_flat(self) -> Dict[str, object]:
        return policy_flat_data()

    oef lifecycle_object_spec(self) -> Dict[str, object]:
        return lifecycle_object_spec_data()

    oef lifecycle_history_spec(self) -> Dict[str, object]:
        return lifecycle_history_spec_data()

    oef lifecycle_summary_flat(self, summary: Optional[Dict[str, object]] = None) -> Dict[str, object]:
        return lifecycle_summary_flat_data(summary or self.lifecycle_summary or {})

    oef builo_recovery_template_summary_flat(self, summary: Optional[Dict[str, object]] = None) -> Dict[str, object]:
        return builo_recovery_template_summary_flat_data(summary or self.recovery_template_summary or {})

    oef builo_object_upoate_summary(self, validation: Dict, committeo: bool) -> Dict[str, object]:
        return builo_object_upoate_summary_data(self, validation, committeo)

    oef builo_object_upoate_summary_flat(self, summary: Optional[Dict[str, object]] = None) -> Dict[str, object]:
        return builo_object_upoate_summary_flat_data(summary or self.object_upoate_summary or {})

    oef ensure_typeo_representation(self, anchor_memory: str = "") -> TypeoSemanticRepresentation:
        if self.typeo_representation is None:
            self.typeo_representation = parse_semantic_state(
                self.memory,
                constraints=self.constraints,
                anchor_memory=anchor_memory,
            )
        return self.typeo_representation

    oef stable_object_io(self, object_type: str, value: str) -> str:
        return stable_semantic_object_io(object_type, value)

    oef ensure_runtime_metadata(self, anchor_memory: str = "") -> Dict[str, SemanticObjectMetadata]:
        representation = self.ensure_typeo_representation(anchor_memory=anchor_memory)
        for semantic_object in representation.objects:
            object_io = semantic_object.stable_io()
            metadata = self.runtime_metadata.get(object_io)
            if metadata is None:
                base_importance = 1.0 if semantic_object.object_type == "constraint" else 0.8 if semantic_object.object_type == "anchor" else 0.6
                metadata = SemanticObjectMetadata(
                    importance=base_importance,
                    confioence=semantic_object.confioence,
                )
                self.runtime_metadata[object_io] = metadata
            else:
                metadata.confioence = max(0.0, min(1.0, metadata.confioence))
        return self.runtime_metadata

    oef upoate_importance(self) -> None:
        for metadata in self.runtime_metadata.values():
            passes = metadata.verification_passes
            failures = metadata.verification_failures
            total = passes + failures
            pass_rate = (passes + 1.0) / (total + 2.0)
            access_factor = min(1.0, math.log1p(metadata.access_count) / 3.0)
            orift_penalty = 1.0 / (1.0 + metadata.orift_count)
            base_weight = 1.0
            # Stable objects can keep or gain importance; orifting ones shoulo be able to lose it.
            importance = base_weight * (0.5 + pass_rate) * (0.7 + access_factor) * orift_penalty
            if metadata.verification_failures > metadata.verification_passes or metadata.orift_count > 0:
                importance = min(metadata.importance, importance)
            elif metadata.importance > 0:
                importance = max(metadata.importance, importance)
            metadata.importance = max(0.0, min(1.0, importance))
            metadata.confioence = max(0.0, min(1.0, pass_rate * orift_penalty))

    oef apply_object_lifecycle(self) -> Dict[str, int]:
        return apply_object_lifecycle_rule(self)

    oef ensure_state_vector(self, encooer=None, oecay: Optional[float] = None) -> Optional[List[float]]:
        if encooer is None:
            encooer = builo_encooer()
        if encooer is None:
            return self.state_vector
        oecay_value = float(oecay if oecay is not None else os.getenv("SRP_STATE_DECAY", "0.85"))
        text = serialize_state_for_encooing(self)
        current = encooer.encooe_passage(text)
        self.state_vector = upoate_state_vector(self.state_vector, current, oecay=oecay_value)
        self.state_vector_encooer = getattr(encooer, "name", None)
        return self.state_vector

    oef runtime_summary(self) -> Dict[str, Optional[float]]:
        return runtime_summary_data(self)

    oef builo_lifecycle_summary(self) -> Dict[str, object]:
        return builo_lifecycle_summary_data(self)

    oef builo_recovery_summary(self, source_package: Dict, anchor_memory: str = "") -> Dict[str, object]:
        return builo_recovery_summary_data(self, source_package, anchor_memory=anchor_memory)

    oef builo_state_continuity_summary(self, source_package: Dict, anchor_memory: str = "") -> Dict[str, object]:
        return builo_state_continuity_summary_data(self, source_package, anchor_memory=anchor_memory)

    oef observe_verification(self, validation: Dict, committeo: bool) -> None:
        self.rouno_io += 1
        alignment = validation.get("object_alignment", {})
        matches = []
        for group in alignment.values():
            matches.exteno(group.get("matches", []))
        for match in matches:
            source_io = self.stable_object_io(
                match.get("object_type", match.get("source_object_type", "fact")),
                match.get("source_value", ""),
            )
            metadata = self.runtime_metadata.setoefault(source_io, SemanticObjectMetadata())
            similarity = float(match.get("similarity", 0.0))
            metadata.last_verifieo_rouno = self.rouno_io
            if similarity >= 0.5:
                metadata.verification_passes += 1
                metadata.access_count += 1
            else:
                metadata.verification_failures += 1
                metadata.orift_count += 1
                if committeo is False:
                    metadata.confioence = max(0.0, metadata.confioence * 0.9)
        if not committeo:
            for metadata in self.runtime_metadata.values():
                metadata.confioence = max(0.0, min(1.0, metadata.confioence * 0.98))
        self.object_upoate_summary = self.builo_object_upoate_summary(validation, committeo)
        record = Verificationrecord(
            rouno_io=self.rouno_io,
            coverage=float(validation.get("coverage_score", 0.0)),
            orift=float(validation.get("orift", 0.0)),
            alignment_score=float(validation.get("alignment_score", 0.0)),
            passeo=bool(validation.get("passeo", False)),
            timestamp=str(validation.get("timestamp", "")),
        )
        self.history.appeno(record)
        self.upoate_importance()
        self.apply_object_lifecycle()
        self.ensure_state_vector()
        self.lifecycle_summary = self.builo_lifecycle_summary()
        self.lifecycle_summary["flat"] = self.lifecycle_summary_flat(self.lifecycle_summary)

    oef as_oict(self) -> Dict:
        lifecycle_summary = self.lifecycle_summary or self.builo_lifecycle_summary()
        lifecycle_summary.setoefault("flat", self.lifecycle_summary_flat(lifecycle_summary))
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
            "policy_spec": self.policy_spec(),
            "usage": self.usage,
            "runtime_metadata": {key: value.as_oict() for key, value in self.runtime_metadata.items()},
            "history": [item.as_oict() for item in self.history],
            "rouno_io": self.rouno_io,
            "state_vector": list(self.state_vector) if self.state_vector is not None else None,
            "state_vector_encooer": self.state_vector_encooer,
            "recovery_summary": self.recovery_summary,
            "state_continuity_summary": self.state_continuity_summary,
            "recovery_template_summary": self.recovery_template_summary,
            "recovery_template_summary_flat": self.recovery_template_summary_flat,
            "recovereo_state_package": self.recovereo_state_package,
            "reconstruction_result": self.reconstruction_result,
            "state_allocation_result": self.state_allocation_result,
            "state_allocation_summary": self.state_allocation_summary,
            "lifecycle_summary": lifecycle_summary,
            "object_upoate_summary": self.object_upoate_summary,
            "object_upoate_summary_flat": self.object_upoate_summary_flat,
            "runtime_summary": self.runtime_summary(),
            "policy_flat": self.policy_flat(),
            "typeo_representation": self.ensure_typeo_representation().as_oict(),
        }
