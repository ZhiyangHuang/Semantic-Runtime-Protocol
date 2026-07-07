import math
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .encoder import build_encoder, serialize_state_for_encoding, update_state_vector
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
        return {
            "schema_version": "policy_spec.v1",
            "lifecycle": {
                "lifecycle_retained_importance": {
                    "type": "float",
                    "default": 0.35,
                    "meaning": "Minimum importance for an object to be eligible for retention.",
                },
                "lifecycle_retained_passes": {
                    "type": "int",
                    "default": 2,
                    "meaning": "Minimum verification passes for an object to be considered active enough for retention.",
                },
                "lifecycle_archived_importance": {
                    "type": "float",
                    "default": 0.3,
                    "meaning": "Importance threshold below which risky objects may be archived.",
                },
                "lifecycle_archived_drift_count": {
                    "type": "int",
                    "default": 2,
                    "meaning": "Minimum drift count that marks an object as archival-risky.",
                },
                "lifecycle_archived_failure_count": {
                    "type": "int",
                    "default": 2,
                    "meaning": "Minimum failure count that marks an object as archival-risky.",
                },
                "lifecycle_decayed_floor": {
                    "type": "float",
                    "default": 0.05,
                    "meaning": "Lower bound applied when decaying importance.",
                },
                "lifecycle_decayed_multiplier": {
                    "type": "float",
                    "default": 0.92,
                    "meaning": "Multiplier applied to importance during decay.",
                },
            },
        }

    def policy_flat(self) -> Dict[str, object]:
        return {
            "schema_version": "policy_spec_flat.v1",
            "lifecycle_retained_importance": 0.35,
            "lifecycle_retained_passes": 2,
            "lifecycle_archived_importance": 0.3,
            "lifecycle_archived_drift_count": 2,
            "lifecycle_archived_failure_count": 2,
            "lifecycle_decayed_floor": 0.05,
            "lifecycle_decayed_multiplier": 0.92,
        }

    def lifecycle_object_spec(self) -> Dict[str, object]:
        return {
            "schema_version": "lifecycle_object_spec.v1",
            "columns": {
                "object_count": {"type": "int", "meaning": "Total number of tracked semantic objects."},
                "high_importance_count": {"type": "int", "meaning": "Count of objects whose importance is at least 0.8."},
                "drifting_object_count": {"type": "int", "meaning": "Count of objects with at least one drift event."},
                "high_risk_object_count": {"type": "int", "meaning": "Count of objects with more failures than passes and nonzero drift."},
                "high_importance_object_ids": {"type": "list[str]", "meaning": "Top important object ids, truncated for compact logging."},
                "drifting_object_ids": {"type": "list[str]", "meaning": "Objects that have drifted at least once."},
                "high_risk_object_ids": {"type": "list[str]", "meaning": "Objects that are both failure-heavy and drifting."},
                "top_drifting_object_ids": {"type": "list[str]", "meaning": "Objects sorted by drift risk, highest first."},
                "top_stable_object_ids": {"type": "list[str]", "meaning": "Objects sorted by verification stability, highest first."},
                "lifecycle_state_counts": {"type": "dict[str,int]", "meaning": "Counts of active/retained/decayed/archived states."},
            },
        }

    def lifecycle_history_spec(self) -> Dict[str, object]:
        return {
            "schema_version": "lifecycle_history_spec.v1",
            "columns": {
                "first_round_id": {"type": "int|None", "meaning": "First round observed in history."},
                "latest_round_id": {"type": "int|None", "meaning": "Most recent round observed in history."},
                "coverage_mean": {"type": "float|None", "meaning": "Mean coverage across verification records."},
                "drift_mean": {"type": "float|None", "meaning": "Mean drift across verification records."},
                "alignment_mean": {"type": "float|None", "meaning": "Mean alignment across verification records."},
                "coverage_delta": {"type": "float", "meaning": "Change from first to last coverage value."},
                "drift_delta": {"type": "float", "meaning": "Change from first to last drift value."},
                "alignment_delta": {"type": "float", "meaning": "Change from first to last alignment value."},
                "last_passed": {"type": "bool|None", "meaning": "Whether the latest verification record passed."},
            },
        }

    def lifecycle_summary_flat(self, summary: Optional[Dict[str, object]] = None) -> Dict[str, object]:
        summary = summary or self.lifecycle_summary or {}
        global_history = summary.get("global_history", {})
        per_object = summary.get("per_object", {})
        flat = {
            "schema_version": "lifecycle_summary_flat.v1",
            "history_length": summary.get("history_length"),
            "round_id": summary.get("round_id"),
        }
        for key, value in global_history.items():
            flat[f"global_history_{key}"] = value
        for key, value in per_object.items():
            flat[f"per_object_{key}"] = value
        return flat

    def build_recovery_template_summary_flat(self, summary: Optional[Dict[str, object]] = None) -> Dict[str, object]:
        summary = summary or self.recovery_template_summary or {}
        return {
            "schema_version": "recovery_template_summary_flat.v1",
            "recovery_template_version": summary.get("schema_version"),
            "recover_template_sections": list(summary.get("sections", [])),
            "recover_prompt_word_count": summary.get("prompt_word_count"),
            "anchor_memory_word_count": summary.get("anchor_memory_word_count"),
        }

    def build_object_update_summary(self, validation: Dict, committed: bool) -> Dict[str, object]:
        alignment = validation.get("object_alignment", {})
        updates = []
        for group in alignment.values():
            for match in group.get("matches", []):
                source_id = match.get("source_object_id")
                if not source_id:
                    continue
                similarity = float(match.get("similarity", 0.0))
                action = "pass" if similarity >= 0.5 else "drift"
                metadata = self.runtime_metadata.get(source_id)
                updates.append(
                    {
                        "source_object_id": source_id,
                        "object_type": match.get("object_type", "unknown"),
                        "similarity": round(similarity, 4),
                        "action": action,
                        "committed": committed,
                        "lifecycle_state": metadata.lifecycle_state if metadata else None,
                        "importance": round(metadata.importance, 4) if metadata else None,
                        "confidence": round(metadata.confidence, 4) if metadata else None,
                        "verification_passes": metadata.verification_passes if metadata else None,
                        "verification_failures": metadata.verification_failures if metadata else None,
                        "drift_count": metadata.drift_count if metadata else None,
                    }
                )
        return {
            "schema_version": "object_update_summary.v1",
            "round_id": self.round_id,
            "committed": committed,
            "update_count": len(updates),
            "updates": updates[:20],
        }

    def build_object_update_summary_flat(self, summary: Optional[Dict[str, object]] = None) -> Dict[str, object]:
        summary = summary or self.object_update_summary or {}
        updates = list(summary.get("updates", []))
        action_counts: Dict[str, int] = {}
        lifecycle_counts: Dict[str, int] = {}
        object_types: Dict[str, int] = {}
        similarities: List[float] = []
        for update in updates:
            action = str(update.get("action", "unknown"))
            action_counts[action] = action_counts.get(action, 0) + 1
            lifecycle_state = str(update.get("lifecycle_state", "unknown"))
            lifecycle_counts[lifecycle_state] = lifecycle_counts.get(lifecycle_state, 0) + 1
            object_type = str(update.get("object_type", "unknown"))
            object_types[object_type] = object_types.get(object_type, 0) + 1
            if update.get("similarity") is not None:
                try:
                    similarities.append(float(update.get("similarity")))
                except (TypeError, ValueError):
                    pass
        mean_similarity = (sum(similarities) / len(similarities)) if similarities else None
        return {
            "schema_version": "object_update_summary_flat.v1",
            "round_id": summary.get("round_id"),
            "committed": summary.get("committed"),
            "update_count": summary.get("update_count"),
            "update_count_pass": action_counts.get("pass", 0),
            "update_count_drift": action_counts.get("drift", 0),
            "update_count_unknown": action_counts.get("unknown", 0),
            "update_action_counts": action_counts,
            "update_lifecycle_counts": lifecycle_counts,
            "update_object_type_counts": object_types,
            "update_mean_similarity": round(mean_similarity, 4) if mean_similarity is not None else None,
            "updates_joined": "|".join(
                f"{str(item.get('source_object_id'))}:{str(item.get('action', 'unknown'))}:{item.get('similarity', '')}"
                for item in updates
                if item.get("source_object_id")
            ),
        }

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
        retained_importance = self._policy_float("lifecycle_retained_importance", 0.35)
        retained_passes = self._policy_int("lifecycle_retained_passes", 2)
        archived_importance = self._policy_float("lifecycle_archived_importance", 0.3)
        archived_drift_count = self._policy_int("lifecycle_archived_drift_count", 2)
        archived_failure_count = self._policy_int("lifecycle_archived_failure_count", 2)
        decayed_floor = self._policy_float("lifecycle_decayed_floor", 0.05)
        decayed_multiplier = self._policy_float("lifecycle_decayed_multiplier", 0.92)
        retained = 0
        decayed = 0
        archived = 0
        for metadata in self.runtime_metadata.values():
            previous_state = metadata.lifecycle_state
            stable = metadata.verification_passes > metadata.verification_failures and metadata.drift_count == 0
            active = metadata.importance >= retained_importance or metadata.verification_passes >= retained_passes
            risky = metadata.drift_count >= archived_drift_count or metadata.verification_failures >= archived_failure_count
            if active and stable:
                metadata.lifecycle_state = "retained"
                retained += 1
            elif risky and metadata.importance < archived_importance:
                metadata.lifecycle_state = "archived"
                metadata.archived_round = self.round_id
                metadata.importance = 0.0
                metadata.confidence = min(metadata.confidence, 0.25)
                archived += 1
            else:
                metadata.lifecycle_state = "decayed"
                metadata.importance = max(decayed_floor, metadata.importance * decayed_multiplier)
                decayed += 1
            if metadata.lifecycle_state != previous_state:
                metadata.lifecycle_actions += 1
        return {
            "retained": retained,
            "decayed": decayed,
            "archived": archived,
        }

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
        object_count = len(self.ensure_typed_representation().objects)
        high_importance_count = sum(1 for metadata in self.runtime_metadata.values() if metadata.importance >= 0.8)
        importance_values = [metadata.importance for metadata in self.runtime_metadata.values()]
        mean_importance = (sum(importance_values) / len(importance_values)) if importance_values else None
        return {
            "object_count": object_count,
            "high_importance_count": high_importance_count,
            "mean_importance": round(mean_importance, 4) if mean_importance is not None else None,
            "history_length": len(self.history),
        }

    def build_lifecycle_summary(self) -> Dict[str, object]:
        history_length = len(self.history)
        object_items = list(self.runtime_metadata.items())
        object_count = len(object_items)
        lifecycle_state_counts = {
            "active": sum(1 for _, metadata in object_items if metadata.lifecycle_state == "active"),
            "retained": sum(1 for _, metadata in object_items if metadata.lifecycle_state == "retained"),
            "decayed": sum(1 for _, metadata in object_items if metadata.lifecycle_state == "decayed"),
            "archived": sum(1 for _, metadata in object_items if metadata.lifecycle_state == "archived"),
        }
        high_importance_objects = [object_id for object_id, metadata in object_items if metadata.importance >= 0.8]
        drifting_objects = [object_id for object_id, metadata in object_items if metadata.drift_count > 0]
        high_risk_objects = [
            object_id
            for object_id, metadata in object_items
            if metadata.verification_failures > metadata.verification_passes and metadata.drift_count > 0
        ]
        top_drifting_objects = [
            object_id
            for object_id, metadata in sorted(
                object_items,
                key=lambda item: (
                    item[1].drift_count,
                    item[1].verification_failures,
                    item[1].importance,
                    item[0],
                ),
                reverse=True,
            )
            if metadata.drift_count > 0
        ][:5]
        top_stable_objects = [
            object_id
            for object_id, _ in sorted(
                object_items,
                key=lambda item: (
                    item[1].verification_passes,
                    item[1].importance,
                    -item[1].drift_count,
                    item[0],
                ),
                reverse=True,
            )
        ][:5]
        coverage_values = [record.coverage for record in self.history]
        drift_values = [record.drift for record in self.history]
        alignment_values = [record.alignment_score for record in self.history]
        history_trend = {
            "first_round_id": self.history[0].round_id if self.history else None,
            "latest_round_id": self.history[-1].round_id if self.history else self.round_id,
            "coverage_mean": round(sum(coverage_values) / len(coverage_values), 4) if coverage_values else None,
            "drift_mean": round(sum(drift_values) / len(drift_values), 4) if drift_values else None,
            "alignment_mean": round(sum(alignment_values) / len(alignment_values), 4) if alignment_values else None,
            "coverage_delta": round(coverage_values[-1] - coverage_values[0], 4) if len(coverage_values) >= 2 else 0.0,
            "drift_delta": round(drift_values[-1] - drift_values[0], 4) if len(drift_values) >= 2 else 0.0,
            "alignment_delta": round(alignment_values[-1] - alignment_values[0], 4) if len(alignment_values) >= 2 else 0.0,
            "last_passed": self.history[-1].passed if self.history else None,
        }
        object_lifecycle = {
            "object_count": object_count,
            "high_importance_count": len(high_importance_objects),
            "drifting_object_count": len(drifting_objects),
            "high_risk_object_count": len(high_risk_objects),
            "high_importance_object_ids": high_importance_objects[:5],
            "drifting_object_ids": drifting_objects[:5],
            "high_risk_object_ids": high_risk_objects[:5],
            "top_drifting_object_ids": top_drifting_objects,
            "top_stable_object_ids": top_stable_objects,
            "lifecycle_state_counts": lifecycle_state_counts,
        }
        return {
            "schema_version": "lifecycle_summary.v1",
            "global_history": history_trend,
            "global_history_spec": self.lifecycle_history_spec(),
            "per_object": object_lifecycle,
            "per_object_spec": self.lifecycle_object_spec(),
            "policy_spec": self.policy_spec(),
            "policy_flat": self.policy_flat(),
            "history_length": history_length,
            "round_id": self.round_id,
        }

    def build_recovery_summary(self, source_package: Dict, anchor_memory: str = "") -> Dict[str, object]:
        source_constraints = [str(item).strip() for item in source_package.get("constraints", []) if str(item).strip()]
        source_global_vocab = [str(item).strip() for item in source_package.get("global_vocab", []) if str(item).strip()]
        source_local_vocab = [str(item).strip() for item in source_package.get("local_vocab", []) if str(item).strip()]
        source_memory = str(source_package.get("memory", "")).strip()
        source_runtime_summary = source_package.get("runtime_summary", {}) if isinstance(source_package.get("runtime_summary", {}), dict) else {}
        source_selection = source_package.get("selected_chunk_ids", [])
        current_summary = self.runtime_summary()
        source_constraint_set = {item.lower() for item in source_constraints}
        recovered_constraint_set = {item.lower() for item in self.constraints if str(item).strip()}
        source_vocab_set = {item.lower() for item in source_global_vocab + source_local_vocab}
        recovered_vocab_set = {item.lower() for item in self.global_vocabulary + self.local_vocabulary if str(item).strip()}
        constraint_union = source_constraint_set | recovered_constraint_set
        vocab_union = source_vocab_set | recovered_vocab_set
        constraint_overlap_rate = (len(source_constraint_set & recovered_constraint_set) / len(constraint_union)) if constraint_union else 1.0
        vocab_overlap_rate = (len(source_vocab_set & recovered_vocab_set) / len(vocab_union)) if vocab_union else 1.0
        history_continuity_ok = len(self.history) >= source_runtime_summary.get("history_length", 0)
        return {
            "schema_version": "recovery_summary.v1",
            "source_memory_length": len(source_memory.split()),
            "recovered_memory_length": len(self.memory.split()),
            "source_constraint_count": len(source_constraints),
            "recovered_constraint_count": len(self.constraints),
            "source_global_vocab_count": len(source_global_vocab),
            "recovered_global_vocab_count": len(self.global_vocabulary),
            "source_local_vocab_count": len(source_local_vocab),
            "recovered_local_vocab_count": len(self.local_vocabulary),
            "source_selected_chunk_ids": list(source_selection) if isinstance(source_selection, list) else [],
            "recovered_round_id": self.round_id,
            "recovered_history_length": len(self.history),
            "recovered_runtime_summary": current_summary,
            "source_runtime_summary": source_runtime_summary,
            "anchor_memory_length": len(str(anchor_memory).split()) if anchor_memory else 0,
            "memory_delta": len(self.memory.split()) - len(source_memory.split()),
            "constraint_overlap_rate": round(constraint_overlap_rate, 4),
            "vocab_overlap_rate": round(vocab_overlap_rate, 4),
            "history_continuity_ok": history_continuity_ok,
        }

    def build_state_continuity_summary(self, source_package: Dict, anchor_memory: str = "") -> Dict[str, object]:
        runtime_summary = self.runtime_summary()
        recovery_summary = self.build_recovery_summary(source_package, anchor_memory=anchor_memory)
        return {
            "schema_version": "state_continuity_summary.v1",
            "runtime": runtime_summary,
            "recovery": recovery_summary,
            "round_id": self.round_id,
            "history_length": len(self.history),
            "history_continuity_ok": recovery_summary.get("history_continuity_ok", False),
            "constraint_overlap_rate": recovery_summary.get("constraint_overlap_rate"),
            "vocab_overlap_rate": recovery_summary.get("vocab_overlap_rate"),
            "memory_delta": recovery_summary.get("memory_delta"),
        }

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
            "lifecycle_summary": lifecycle_summary,
            "object_update_summary": self.object_update_summary,
            "object_update_summary_flat": self.object_update_summary_flat,
            "runtime_summary": self.runtime_summary(),
            "policy_flat": self.policy_flat(),
            "typed_representation": self.ensure_typed_representation().as_dict(),
        }
