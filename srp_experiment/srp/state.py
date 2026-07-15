import math
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .encoder import build_encoder, serialize_state_for_encoding, update_state_vector
from .state_lifecycle import apply_object_lifecycle as apply_object_lifecycle_rule
from .state_summaries import (
    build_lifecycle_summary as build_lifecycle_summary_data,
    build_object_update_summary as build_object_update_summary_data,
    build_object_update_summary_flat as build_object_update_summary_flat_data,
    build_recovery_summary as build_recovery_summary_data,
    build_recovery_template_summary_flat as build_recovery_template_summary_flat_data,
    build_state_continuity_summary as build_state_continuity_summary_data,
    lifecycle_history_spec as lifecycle_history_spec_data,
    lifecycle_object_spec as lifecycle_object_spec_data,
    lifecycle_summary_flat as lifecycle_summary_flat_data,
    policy_flat as policy_flat_data,
    policy_spec as policy_spec_data,
    runtime_summary as runtime_summary_data,
)
from .semantic_parser import TypedSemanticRepresentation, parse_semantic_state, stable_semantic_object_id


@dataclass
class SemanticObjectMetadata:
    importance: float = 1.0
    confidence: float = 1.0
    access_count: int = 0
    retrieval_count: int = 0
    verification_passes: int = 0
    verification_failures: int = 0
    drift_count: int = 0
    last_verified_round: int = 0
    lifecycle_state: str = "active"
    lifecycle_actions: int = 0
    archived_round: int = 0

    def as_dict(self) -> Dict:
        return {
            "importance": round(self.importance, 4),
            "confidence": round(self.confidence, 4),
            "access_count": self.access_count,
            "retrieval_count": self.retrieval_count,
            "verification_passes": self.verification_passes,
            "verification_failures": self.verification_failures,
            "drift_count": self.drift_count,
            "last_verified_round": self.last_verified_round,
            "lifecycle_state": self.lifecycle_state,
            "lifecycle_actions": self.lifecycle_actions,
            "archived_round": self.archived_round,
        }


@dataclass
class VerificationRecord:
    round_id: int
    coverage: float
    drift: float
    alignment_score: float
    passed: bool
    timestamp: str = ""

    def as_dict(self) -> Dict:
        return {
            "round_id": self.round_id,
            "coverage": round(self.coverage, 4),
            "drift": round(self.drift, 4),
            "alignment_score": round(self.alignment_score, 4),
            "passed": self.passed,
            "timestamp": self.timestamp,
        }


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
    runtime_metadata: Dict[str, SemanticObjectMetadata] = field(default_factory=dict)
    history: List[VerificationRecord] = field(default_factory=list)
    round_id: int = 0
    state_vector: Optional[List[float]] = None
    state_vector_encoder: Optional[str] = None
    recovery_summary: Optional[Dict] = None
    state_continuity_summary: Optional[Dict] = None
    recovery_template_summary: Optional[Dict] = None
    recovery_template_summary_flat: Optional[Dict] = None
    recovered_state_package: Optional[Dict] = None
    reconstruction_result: Optional[Dict] = None
    state_allocation_result: Optional[Dict] = None
    state_allocation_summary: Optional[Dict] = None
    lifecycle_summary: Optional[Dict] = None
    object_update_summary: Optional[Dict] = None
    object_update_summary_flat: Optional[Dict] = None

    def _policy_float(self, key: str, default: float) -> float:
        try:
            return float(self.policy.get(key, default))
        except (TypeError, ValueError):
            return float(default)

    def _policy_int(self, key: str, default: int) -> int:
        try:
            return int(float(self.policy.get(key, default)))
        except (TypeError, ValueError):
            return int(default)

    def policy_spec(self) -> Dict[str, object]:
        return policy_spec_data()

    def policy_flat(self) -> Dict[str, object]:
        return policy_flat_data()

    def lifecycle_object_spec(self) -> Dict[str, object]:
        return lifecycle_object_spec_data()

    def lifecycle_history_spec(self) -> Dict[str, object]:
        return lifecycle_history_spec_data()

    def lifecycle_summary_flat(self, summary: Optional[Dict[str, object]] = None) -> Dict[str, object]:
        return lifecycle_summary_flat_data(summary or self.lifecycle_summary or {})

    def build_recovery_template_summary_flat(self, summary: Optional[Dict[str, object]] = None) -> Dict[str, object]:
        return build_recovery_template_summary_flat_data(summary or self.recovery_template_summary or {})

    def build_object_update_summary(self, validation: Dict, committed: bool) -> Dict[str, object]:
        return build_object_update_summary_data(self, validation, committed)

    def build_object_update_summary_flat(self, summary: Optional[Dict[str, object]] = None) -> Dict[str, object]:
        return build_object_update_summary_flat_data(summary or self.object_update_summary or {})

    def ensure_typed_representation(self, anchor_memory: str = "") -> TypedSemanticRepresentation:
        if self.typed_representation is None:
            self.typed_representation = parse_semantic_state(
                self.memory,
                constraints=self.constraints,
                anchor_memory=anchor_memory,
            )
        return self.typed_representation

    def stable_object_id(self, object_type: str, value: str) -> str:
        return stable_semantic_object_id(object_type, value)

    def ensure_runtime_metadata(self, anchor_memory: str = "") -> Dict[str, SemanticObjectMetadata]:
        representation = self.ensure_typed_representation(anchor_memory=anchor_memory)
        for semantic_object in representation.objects:
            object_id = semantic_object.stable_id()
            metadata = self.runtime_metadata.get(object_id)
            if metadata is None:
                base_importance = 1.0 if semantic_object.object_type == "constraint" else 0.8 if semantic_object.object_type == "anchor" else 0.6
                metadata = SemanticObjectMetadata(
                    importance=base_importance,
                    confidence=semantic_object.confidence,
                )
                self.runtime_metadata[object_id] = metadata
            else:
                metadata.confidence = max(0.0, min(1.0, metadata.confidence))
        return self.runtime_metadata

    def update_importance(self) -> None:
        for metadata in self.runtime_metadata.values():
            passes = metadata.verification_passes
            failures = metadata.verification_failures
            total = passes + failures
            pass_rate = (passes + 1.0) / (total + 2.0)
            access_factor = min(1.0, math.log1p(metadata.access_count) / 3.0)
            drift_penalty = 1.0 / (1.0 + metadata.drift_count)
            base_weight = 1.0
            # Stable objects can keep or gain importance; drifting ones should be able to lose it.
            importance = base_weight * (0.5 + pass_rate) * (0.7 + access_factor) * drift_penalty
            if metadata.verification_failures > metadata.verification_passes or metadata.drift_count > 0:
                importance = min(metadata.importance, importance)
            elif metadata.importance > 0:
                importance = max(metadata.importance, importance)
            metadata.importance = max(0.0, min(1.0, importance))
            metadata.confidence = max(0.0, min(1.0, pass_rate * drift_penalty))

    def apply_object_lifecycle(self) -> Dict[str, int]:
        return apply_object_lifecycle_rule(self)

    def ensure_state_vector(self, encoder=None, decay: Optional[float] = None) -> Optional[List[float]]:
        if encoder is None:
            encoder = build_encoder()
        if encoder is None:
            return self.state_vector
        decay_value = float(decay if decay is not None else os.getenv("SRP_STATE_DECAY", "0.85"))
        text = serialize_state_for_encoding(self)
        current = encoder.encode_passage(text)
        self.state_vector = update_state_vector(self.state_vector, current, decay=decay_value)
        self.state_vector_encoder = getattr(encoder, "name", None)
        return self.state_vector

    def runtime_summary(self) -> Dict[str, Optional[float]]:
        return runtime_summary_data(self)

    def build_lifecycle_summary(self) -> Dict[str, object]:
        return build_lifecycle_summary_data(self)

    def build_recovery_summary(self, source_package: Dict, anchor_memory: str = "") -> Dict[str, object]:
        return build_recovery_summary_data(self, source_package, anchor_memory=anchor_memory)

    def build_state_continuity_summary(self, source_package: Dict, anchor_memory: str = "") -> Dict[str, object]:
        return build_state_continuity_summary_data(self, source_package, anchor_memory=anchor_memory)

    def observe_verification(self, validation: Dict, committed: bool) -> None:
        self.round_id += 1
        alignment = validation.get("object_alignment", {})
        matches = []
        for group in alignment.values():
            matches.extend(group.get("matches", []))
        for match in matches:
            source_id = self.stable_object_id(
                match.get("object_type", match.get("source_object_type", "fact")),
                match.get("source_value", ""),
            )
            metadata = self.runtime_metadata.setdefault(source_id, SemanticObjectMetadata())
            similarity = float(match.get("similarity", 0.0))
            metadata.last_verified_round = self.round_id
            if similarity >= 0.5:
                metadata.verification_passes += 1
                metadata.access_count += 1
            else:
                metadata.verification_failures += 1
                metadata.drift_count += 1
                if committed is False:
                    metadata.confidence = max(0.0, metadata.confidence * 0.9)
        if not committed:
            for metadata in self.runtime_metadata.values():
                metadata.confidence = max(0.0, min(1.0, metadata.confidence * 0.98))
        self.object_update_summary = self.build_object_update_summary(validation, committed)
        record = VerificationRecord(
            round_id=self.round_id,
            coverage=float(validation.get("coverage_score", 0.0)),
            drift=float(validation.get("drift", 0.0)),
            alignment_score=float(validation.get("alignment_score", 0.0)),
            passed=bool(validation.get("passed", False)),
            timestamp=str(validation.get("timestamp", "")),
        )
        self.history.append(record)
        self.update_importance()
        self.apply_object_lifecycle()
        self.ensure_state_vector()
        self.lifecycle_summary = self.build_lifecycle_summary()
        self.lifecycle_summary["flat"] = self.lifecycle_summary_flat(self.lifecycle_summary)

    def as_dict(self) -> Dict:
        lifecycle_summary = self.lifecycle_summary or self.build_lifecycle_summary()
        lifecycle_summary.setdefault("flat", self.lifecycle_summary_flat(lifecycle_summary))
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
            "runtime_metadata": {key: value.as_dict() for key, value in self.runtime_metadata.items()},
            "history": [item.as_dict() for item in self.history],
            "round_id": self.round_id,
            "state_vector": list(self.state_vector) if self.state_vector is not None else None,
            "state_vector_encoder": self.state_vector_encoder,
            "recovery_summary": self.recovery_summary,
            "state_continuity_summary": self.state_continuity_summary,
            "recovery_template_summary": self.recovery_template_summary,
            "recovery_template_summary_flat": self.recovery_template_summary_flat,
            "recovered_state_package": self.recovered_state_package,
            "reconstruction_result": self.reconstruction_result,
            "state_allocation_result": self.state_allocation_result,
            "state_allocation_summary": self.state_allocation_summary,
            "lifecycle_summary": lifecycle_summary,
            "object_update_summary": self.object_update_summary,
            "object_update_summary_flat": self.object_update_summary_flat,
            "runtime_summary": self.runtime_summary(),
            "policy_flat": self.policy_flat(),
            "typed_representation": self.ensure_typed_representation().as_dict(),
        }
