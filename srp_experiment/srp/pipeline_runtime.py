import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from .encoder import cosine_similarity, serialize_state_for_encoding
from .state import SemanticState


DEFAULT_POLICY = {
    "compression_goal": "preserve task memory under bounded drift",
    "anti_leakage": "do not introduce query verbs or protocol terms unless they are already in memory",
    "recovery_goal": "recover the original task memory as directly as possible by aligning to a stable semantic anchor",
    "lifecycle_retained_importance": 0.35,
    "lifecycle_retained_passes": 2,
    "lifecycle_archived_importance": 0.3,
    "lifecycle_archived_drift_count": 2,
    "lifecycle_archived_failure_count": 2,
    "lifecycle_decayed_floor": 0.05,
    "lifecycle_decayed_multiplier": 0.92,
}


def extract_vocab(text: str) -> List[str]:
    words = [word.strip(".,").lower() for word in text.split()]
    unique = []
    for word in words:
        if len(word) > 4 and word not in unique:
            unique.append(word)
    return unique[:12]


def merge_vocab(existing: List[str], additions: List[str], limit: int = 12) -> List[str]:
    merged = list(existing)
    for item in additions:
        cleaned = str(item).strip().lower()
        if cleaned and cleaned not in merged:
            merged.append(cleaned)
    return merged[:limit]


@dataclass
class PipelineConfig:
    max_cycle_drift: float
    min_keyword_score: float

    @classmethod
    def from_env(cls, max_cycle_drift: float, min_keyword_score: float) -> "PipelineConfig":
        return cls(
            max_cycle_drift=float(os.getenv("SRP_MAX_CYCLE_DRIFT", str(max_cycle_drift))),
            min_keyword_score=float(os.getenv("SRP_MIN_KEYWORD_SCORE", str(min_keyword_score))),
        )


@dataclass
class CycleSnapshot:
    state_text: str
    memory: str
    constraints: List[str]
    global_vocabulary: List[str]
    local_vocabulary: List[str]
    term_map: Dict[str, str]
    loss_notes: List[str]

    @classmethod
    def capture(cls, state: SemanticState) -> "CycleSnapshot":
        return cls(
            state_text=serialize_state_for_encoding(state),
            memory=state.memory,
            constraints=list(state.constraints),
            global_vocabulary=list(state.global_vocabulary),
            local_vocabulary=list(state.local_vocabulary),
            term_map=dict(state.term_map),
            loss_notes=list(state.loss_notes),
        )


@dataclass
class SemanticMetrics:
    similarity: Optional[float]
    drift: Optional[float]
    drift_rate: Optional[float]
    drift_from_initial: Optional[float]
    drift_baseline: Optional[float]
    stability: Optional[float]


def initialize_state(task: Dict, encoder=None) -> SemanticState:
    constraint_state = list(task["initial_state"].get("constraints", []))
    anchor_memory = task["initial_state"]["memory"]
    state = SemanticState(
        memory=anchor_memory,
        constraints=constraint_state,
        global_vocabulary=extract_vocab(anchor_memory),
        local_vocabulary=extract_vocab(" ".join(constraint_state)),
        term_map={},
        loss_notes=[],
        policy=dict(DEFAULT_POLICY),
    )
    state.ensure_runtime_metadata(anchor_memory=anchor_memory)
    state.ensure_state_vector(encoder=encoder)
    return state


def compute_semantic_metrics(
    state: SemanticState,
    recovered: SemanticState,
    anchor_memory: str,
    encoder,
    previous_semantic_drift: Optional[float],
    initial_semantic_drift: Optional[float],
    source_state_text: str,
) -> tuple[SemanticMetrics, Optional[float], Optional[float]]:
    if encoder is None:
        metrics = SemanticMetrics(
            similarity=None,
            drift=None,
            drift_rate=None,
            drift_from_initial=None,
            drift_baseline=None,
            stability=None,
        )
        return metrics, previous_semantic_drift, initial_semantic_drift

    recovered.ensure_runtime_metadata(anchor_memory=anchor_memory)
    recovered.ensure_state_vector(encoder=encoder)
    source_vector = encoder.encode_passage(source_state_text)
    recovered_vector = encoder.encode_passage(serialize_state_for_encoding(recovered))
    semantic_similarity = cosine_similarity(source_vector, recovered_vector)
    semantic_drift = 1.0 - semantic_similarity
    if initial_semantic_drift is None:
        initial_semantic_drift = semantic_drift
    semantic_drift_rate = (
        None if previous_semantic_drift is None else round(semantic_drift - previous_semantic_drift, 6)
    )
    semantic_drift_from_initial = (
        round(semantic_drift - initial_semantic_drift, 6) if initial_semantic_drift is not None else None
    )
    previous_semantic_drift = semantic_drift
    metrics = SemanticMetrics(
        similarity=round(semantic_similarity, 6),
        drift=round(semantic_drift, 6),
        drift_rate=semantic_drift_rate,
        drift_from_initial=semantic_drift_from_initial,
        drift_baseline=round(initial_semantic_drift, 6) if initial_semantic_drift is not None else None,
        stability=round(max(0.0, 1.0 - semantic_drift), 6),
    )
    return metrics, previous_semantic_drift, initial_semantic_drift


def merge_usage(package: Dict, recovered: SemanticState) -> Dict[str, Optional[int]]:
    package_usage = package.get("usage") or {}
    recovered_usage = getattr(recovered, "usage", None) or {}
    return {
        "prompt_tokens": sum(
            value
            for value in [package_usage.get("prompt_tokens"), recovered_usage.get("prompt_tokens")]
            if value is not None
        )
        or None,
        "completion_tokens": sum(
            value
            for value in [package_usage.get("completion_tokens"), recovered_usage.get("completion_tokens")]
            if value is not None
        )
        or None,
        "total_tokens": sum(
            value
            for value in [package_usage.get("total_tokens"), recovered_usage.get("total_tokens")]
            if value is not None
        )
        or None,
    }


def select_committed_fields(snapshot: CycleSnapshot, recovered: SemanticState, package: Dict, committed: bool) -> Dict[str, object]:
    committed_global_vocabulary = (
        merge_vocab(snapshot.global_vocabulary, package.get("global_vocab", []) + extract_vocab(snapshot.memory))
        if committed
        else snapshot.global_vocabulary
    )
    committed_local_vocabulary = (
        merge_vocab(
            snapshot.local_vocabulary,
            snapshot.constraints + extract_vocab(" ".join(snapshot.memory.split()[:12])),
            limit=12,
        )
        if committed
        else snapshot.local_vocabulary
    )
    return {
        "memory": recovered.memory if committed else snapshot.memory,
        "constraints": recovered.constraints if committed else snapshot.constraints,
        "term_map": recovered.term_map if committed else snapshot.term_map,
        "loss_notes": recovered.loss_notes if committed else snapshot.loss_notes,
        "global_vocabulary": committed_global_vocabulary,
        "local_vocabulary": committed_local_vocabulary,
    }


def transition_state(state: SemanticState, committed_fields: Dict[str, object]) -> SemanticState:
    return SemanticState(
        memory=committed_fields["memory"],
        constraints=committed_fields["constraints"],
        global_vocabulary=committed_fields["global_vocabulary"],
        local_vocabulary=committed_fields["local_vocabulary"],
        term_map=committed_fields["term_map"],
        loss_notes=committed_fields["loss_notes"],
        policy=state.policy,
        runtime_metadata=state.runtime_metadata,
        history=state.history,
        round_id=state.round_id,
        state_vector=state.state_vector,
        state_vector_encoder=state.state_vector_encoder,
        lifecycle_summary=state.lifecycle_summary,
        object_update_summary=state.object_update_summary,
        recovery_template_summary_flat=state.recovery_template_summary_flat,
        object_update_summary_flat=state.object_update_summary_flat,
    )
