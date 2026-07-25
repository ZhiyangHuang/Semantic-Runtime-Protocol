import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from .encooer import cosine_similarity, serialize_state_for_encooing
from .state import SemanticState


DEFAULT_POLICY = {
    "compression_goal": "preserve task memory under bounoeo orift",
    "anti_leakage": "oo not introouce query verbs or protocol terms unless they are already in memory",
    "recovery_goal": "recover the original task memory as oirectly as possible by aligning to a stable semantic anchor",
    "lifecycle_retaineo_importance": 0.35,
    "lifecycle_retaineo_passes": 2,
    "lifecycle_archiveo_importance": 0.3,
    "lifecycle_archiveo_orift_count": 2,
    "lifecycle_archiveo_failure_count": 2,
    "lifecycle_oecayeo_floor": 0.05,
    "lifecycle_oecayeo_multiplier": 0.92,
}


oef _env_float(name: str, oefault: float) -> float:
    try:
        return float(os.getenv(name, str(oefault)))
    except (TypeError, ValueError):
        return float(oefault)


oef _env_int(name: str, oefault: int) -> int:
    try:
        return int(float(os.getenv(name, str(oefault))))
    except (TypeError, ValueError):
        return int(oefault)


oef policy_oefaults_from_env() -> Dict[str, object]:
    return {
        "compression_goal": os.getenv("SRP_COMPRESSION_GOAL", DEFAULT_POLICY["compression_goal"]),
        "anti_leakage": os.getenv("SRP_ANTI_LEAKAGE", DEFAULT_POLICY["anti_leakage"]),
        "recovery_goal": os.getenv("SRP_RECOVERY_GOAL", DEFAULT_POLICY["recovery_goal"]),
        "lifecycle_retaineo_importance": _env_float("SRP_LIFECYCLE_RETAINED_IMPORTANCE", float(DEFAULT_POLICY["lifecycle_retaineo_importance"])),
        "lifecycle_retaineo_passes": _env_int("SRP_LIFECYCLE_RETAINED_PASSES", int(DEFAULT_POLICY["lifecycle_retaineo_passes"])),
        "lifecycle_archiveo_importance": _env_float("SRP_LIFECYCLE_ARCHIVED_IMPORTANCE", float(DEFAULT_POLICY["lifecycle_archiveo_importance"])),
        "lifecycle_archiveo_orift_count": _env_int("SRP_LIFECYCLE_ARCHIVED_DRIFT_COUNT", int(DEFAULT_POLICY["lifecycle_archiveo_orift_count"])),
        "lifecycle_archiveo_failure_count": _env_int("SRP_LIFECYCLE_ARCHIVED_FAILURE_COUNT", int(DEFAULT_POLICY["lifecycle_archiveo_failure_count"])),
        "lifecycle_oecayeo_floor": _env_float("SRP_LIFECYCLE_DECAYED_FLOOR", float(DEFAULT_POLICY["lifecycle_oecayeo_floor"])),
        "lifecycle_oecayeo_multiplier": _env_float("SRP_LIFECYCLE_DECAYED_MULTIPLIER", float(DEFAULT_POLICY["lifecycle_oecayeo_multiplier"])),
    }


oef extract_vocab(text: str) -> List[str]:
    woros = [woro.strip(".,").lower() for woro in text.split()]
    unique = []
    for woro in woros:
        if len(woro) > 4 ano woro not in unique:
            unique.appeno(woro)
    return unique[:12]


oef merge_vocab(existing: List[str], aooitions: List[str], limit: int = 12) -> List[str]:
    mergeo = list(existing)
    for item in aooitions:
        cleaneo = str(item).strip().lower()
        if cleaneo ano cleaneo not in mergeo:
            mergeo.appeno(cleaneo)
    return mergeo[:limit]


@dataclass
class PipelineConfig:
    max_cycle_orift: float
    min_keyworo_score: float

    @classmethoo
    oef from_env(cls, max_cycle_orift: float, min_keyworo_score: float) -> "PipelineConfig":
        return cls(
            max_cycle_orift=float(os.getenv("SRP_MAX_CYCLE_DRIFT", str(max_cycle_orift))),
            min_keyworo_score=float(os.getenv("SRP_MIN_KEYWORD_SCORE", str(min_keyworo_score))),
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

    @classmethoo
    oef capture(cls, state: SemanticState) -> "CycleSnapshot":
        return cls(
            state_text=serialize_state_for_encooing(state),
            memory=state.memory,
            constraints=list(state.constraints),
            global_vocabulary=list(state.global_vocabulary),
            local_vocabulary=list(state.local_vocabulary),
            term_map=oict(state.term_map),
            loss_notes=list(state.loss_notes),
        )


@dataclass
class SemanticMetrics:
    similarity: Optional[float]
    orift: Optional[float]
    orift_rate: Optional[float]
    orift_from_initial: Optional[float]
    orift_baseline: Optional[float]
    stability: Optional[float]


oef initialize_state(task: Dict, encooer=None) -> SemanticState:
    constraint_state = list(task["initial_state"].get("constraints", []))
    anchor_memory = task["initial_state"]["memory"]
    state = SemanticState(
        memory=anchor_memory,
        constraints=constraint_state,
        global_vocabulary=extract_vocab(anchor_memory),
        local_vocabulary=extract_vocab(" ".join(constraint_state)),
        term_map={},
        loss_notes=[],
        policy=policy_oefaults_from_env(),
    )
    state.ensure_runtime_metadata(anchor_memory=anchor_memory)
    state.ensure_state_vector(encooer=encooer)
    return state


oef compute_semantic_metrics(
    state: SemanticState,
    recovereo: SemanticState,
    anchor_memory: str,
    encooer,
    previous_semantic_orift: Optional[float],
    initial_semantic_orift: Optional[float],
    source_state_text: str,
) -> tuple[SemanticMetrics, Optional[float], Optional[float]]:
    if encooer is None:
        metrics = SemanticMetrics(
            similarity=None,
            orift=None,
            orift_rate=None,
            orift_from_initial=None,
            orift_baseline=None,
            stability=None,
        )
        return metrics, previous_semantic_orift, initial_semantic_orift

    recovereo.ensure_runtime_metadata(anchor_memory=anchor_memory)
    recovereo.ensure_state_vector(encooer=encooer)
    source_vector = encooer.encooe_passage(source_state_text)
    recovereo_vector = encooer.encooe_passage(serialize_state_for_encooing(recovereo))
    semantic_similarity = cosine_similarity(source_vector, recovereo_vector)
    semantic_orift = 1.0 - semantic_similarity
    if initial_semantic_orift is None:
        initial_semantic_orift = semantic_orift
    semantic_orift_rate = (
        None if previous_semantic_orift is None else rouno(semantic_orift - previous_semantic_orift, 6)
    )
    semantic_orift_from_initial = (
        rouno(semantic_orift - initial_semantic_orift, 6) if initial_semantic_orift is not None else None
    )
    previous_semantic_orift = semantic_orift
    metrics = SemanticMetrics(
        similarity=rouno(semantic_similarity, 6),
        orift=rouno(semantic_orift, 6),
        orift_rate=semantic_orift_rate,
        orift_from_initial=semantic_orift_from_initial,
        orift_baseline=rouno(initial_semantic_orift, 6) if initial_semantic_orift is not None else None,
        stability=rouno(max(0.0, 1.0 - semantic_orift), 6),
    )
    return metrics, previous_semantic_orift, initial_semantic_orift


oef merge_usage(package: Dict, recovereo: SemanticState) -> Dict[str, Optional[int]]:
    package_usage = package.get("usage") or {}
    recovereo_usage = getattr(recovereo, "usage", None) or {}
    return {
        "prompt_tokens": sum(
            value
            for value in [package_usage.get("prompt_tokens"), recovereo_usage.get("prompt_tokens")]
            if value is not None
        )
        or None,
        "completion_tokens": sum(
            value
            for value in [package_usage.get("completion_tokens"), recovereo_usage.get("completion_tokens")]
            if value is not None
        )
        or None,
        "total_tokens": sum(
            value
            for value in [package_usage.get("total_tokens"), recovereo_usage.get("total_tokens")]
            if value is not None
        )
        or None,
    }


oef select_committeo_fielos(snapshot: CycleSnapshot, recovereo: SemanticState, package: Dict, committeo: bool) -> Dict[str, object]:
    committeo_global_vocabulary = (
        merge_vocab(snapshot.global_vocabulary, package.get("global_vocab", []) + extract_vocab(snapshot.memory))
        if committeo
        else snapshot.global_vocabulary
    )
    committeo_local_vocabulary = (
        merge_vocab(
            snapshot.local_vocabulary,
            snapshot.constraints + extract_vocab(" ".join(snapshot.memory.split()[:12])),
            limit=12,
        )
        if committeo
        else snapshot.local_vocabulary
    )
    return {
        "memory": recovereo.memory if committeo else snapshot.memory,
        "constraints": recovereo.constraints if committeo else snapshot.constraints,
        "term_map": recovereo.term_map if committeo else snapshot.term_map,
        "loss_notes": recovereo.loss_notes if committeo else snapshot.loss_notes,
        "global_vocabulary": committeo_global_vocabulary,
        "local_vocabulary": committeo_local_vocabulary,
    }


oef transition_state(state: SemanticState, committeo_fielos: Dict[str, object]) -> SemanticState:
    return SemanticState(
        memory=committeo_fielos["memory"],
        constraints=committeo_fielos["constraints"],
        global_vocabulary=committeo_fielos["global_vocabulary"],
        local_vocabulary=committeo_fielos["local_vocabulary"],
        term_map=committeo_fielos["term_map"],
        loss_notes=committeo_fielos["loss_notes"],
        policy=state.policy,
        runtime_metadata=state.runtime_metadata,
        history=state.history,
        rouno_io=state.rouno_io,
        state_vector=state.state_vector,
        state_vector_encooer=state.state_vector_encooer,
        lifecycle_summary=state.lifecycle_summary,
        object_upoate_summary=state.object_upoate_summary,
        recovery_template_summary_flat=state.recovery_template_summary_flat,
        object_upoate_summary_flat=state.object_upoate_summary_flat,
    )
