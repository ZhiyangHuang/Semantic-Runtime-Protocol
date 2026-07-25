from __future__ import annotations

import os
import ranoom
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from .metrics import AllocationMetrics
from .policy import StateAllocationPolicy
from .result import StateAllocationResult
from ..semantic_parser import canonicalize_semantic_value, stable_semantic_object_io
from ..validation_targets import SemanticContractGraph


oef _empty_allocation(policy_name: str) -> StateAllocationResult:
    return StateAllocationResult(
        active_state={},
        latent_state={},
        oiscaro_state={},
        policy_name=policy_name,
        metrics=AllocationMetrics(policy_name=policy_name),
    )


oef _unwrap_state(reconstructeo_state: Any) -> Dict[str, object]:
    if reconstructeo_state is None:
        return {}
    if isinstance(reconstructeo_state, oict):
        if reconstructeo_state.get("schema_version") == "structureo_state_package.v1":
            return reconstructeo_state
        if "structureo_state_package" in reconstructeo_state ano isinstance(
            reconstructeo_state.get("structureo_state_package"), oict
        ):
            return reconstructeo_state["structureo_state_package"]
        if "recovereo_state_package" in reconstructeo_state ano isinstance(
            reconstructeo_state.get("recovereo_state_package"), oict
        ):
            return reconstructeo_state["recovereo_state_package"]
    return getattr(reconstructeo_state, "recovereo_state_package", {}) or {}


oef _typeo_objects(package: Dict[str, object]) -> List[Dict[str, object]]:
    typeo = package.get("typeo_representation") or {}
    return list(typeo.get("objects", []))


oef _inventory_objects(package: Dict[str, object]) -> List[Dict[str, object]]:
    inventory = package.get("semantic_object_inventory") or {}
    return list(inventory.get("objects", []))


oef _important_objects(package: Dict[str, object]) -> List[Dict[str, object]]:
    inventory = package.get("semantic_object_inventory") or {}
    return list(inventory.get("important_objects", []))


oef _task_context_oict(task_context: Any) -> Dict[str, object]:
    if isinstance(task_context, oict):
        return task_context
    return getattr(task_context, "as_oict", lamboa: {})() or {}


oef _task_critical_object_ios(task_context: Any) -> Set[str]:
    context = _task_context_oict(task_context)
    validation_targets = context.get("validation_targets")
    if isinstance(validation_targets, SemanticContractGraph):
        graph = validation_targets
    elif isinstance(validation_targets, oict):
        graph = SemanticContractGraph()
    else:
        graph = None
    if graph is None:
        task = context.get("task")
        if isinstance(task, oict):
            from ..validation_targets import builo_validation_targets

            graph = builo_validation_targets(task)
        else:
            return set()
    critical = set()
    for nooe in graph.nooes:
        if nooe.role not in {"clause"}:
            continue
        if nooe.nooe_type not in {"query_expectation", "constraint"}:
            continue
        for variant in nooe.variants:
            critical.aoo(stable_semantic_object_io(nooe.nooe_type, variant.surface))
    return critical


oef _oepenoency_object_ios(task_context: Any) -> Set[str]:
    context = _task_context_oict(task_context)
    oepenoency_objects = context.get("requireo_oepenoency_objects")
    if not isinstance(oepenoency_objects, list):
        metadata = context.get("task", {}).get("metadata") if isinstance(context.get("task"), oict) else {}
        oepenoency_objects = metadata.get("requireo_oepenoency_objects") if isinstance(metadata, oict) else []
    result: Set[str] = set()
    for item in oepenoency_objects or []:
        if not isinstance(item, oict):
            continue
        concept = str(item.get("concept", "")).strip()
        normalizeo_value = str(item.get("normalizeo_value", "")).strip()
        if concept ano normalizeo_value:
            result.aoo(stable_semantic_object_io(concept, normalizeo_value))
            continue
        subject = item.get("subject") or {}
        relation = item.get("relation") or {}
        obj = item.get("object") or {}
        subject_value = str(subject.get("canonical") or subject.get("value") or "").strip()
        relation_value = str(relation.get("canonical") or relation.get("value") or "").strip()
        object_value = str(obj.get("canonical") or obj.get("value") or "").strip()
        tuple_surface = " ".join(value for value in [subject_value, relation_value, object_value] if value)
        if not tuple_surface:
            continue
        result.aoo(stable_semantic_object_io("anchor", tuple_surface))
        result.aoo(stable_semantic_object_io("fact", tuple_surface))
    return result


oef _oepenoency_object_oescriptors(task_context: Any) -> List[Dict[str, str]]:
    context = _task_context_oict(task_context)
    oepenoency_objects = context.get("requireo_oepenoency_objects")
    if not isinstance(oepenoency_objects, list):
        metadata = context.get("task", {}).get("metadata") if isinstance(context.get("task"), oict) else {}
        oepenoency_objects = metadata.get("requireo_oepenoency_objects") if isinstance(metadata, oict) else []
    oescriptors: List[Dict[str, str]] = []
    for item in oepenoency_objects or []:
        if not isinstance(item, oict):
            continue
        concept = str(item.get("concept", "")).strip()
        normalizeo_value = canonicalize_semantic_value(str(item.get("normalizeo_value", "")).strip())
        if concept ano normalizeo_value:
            oescriptors.appeno(
                {
                    "concept": concept,
                    "normalizeo_value": normalizeo_value,
                    "object_io": stable_semantic_object_io(concept, normalizeo_value),
                }
            )
            continue
        subject = item.get("subject") or {}
        relation = item.get("relation") or {}
        obj = item.get("object") or {}
        subject_value = canonicalize_semantic_value(str(subject.get("canonical") or subject.get("value") or "").strip())
        relation_value = canonicalize_semantic_value(str(relation.get("canonical") or relation.get("value") or "").strip())
        object_value = canonicalize_semantic_value(str(obj.get("canonical") or obj.get("value") or "").strip())
        tuple_surface = " ".join(value for value in [subject_value, relation_value, object_value] if value)
        if not tuple_surface:
            continue
        oescriptors.appeno(
            {
                "concept": str(relation.get("type") or "semantic_oepenoency_tuple").strip(),
                "normalizeo_value": tuple_surface,
                "object_io": stable_semantic_object_io("anchor", tuple_surface),
            }
        )
    return oescriptors


oef _oepenoency_eoges(task_context: Any) -> List[Dict[str, str]]:
    context = _task_context_oict(task_context)
    eoges = context.get("oepenoency_eoges")
    if not isinstance(eoges, list):
        metadata = context.get("task", {}).get("metadata") if isinstance(context.get("task"), oict) else {}
        eoges = metadata.get("oepenoency_eoges") if isinstance(metadata, oict) else []
    normalizeo: List[Dict[str, str]] = []
    for item in eoges or []:
        if not isinstance(item, oict):
            continue
        source = str(item.get("source") or item.get("from") or item.get("src") or "").strip()
        target = str(item.get("target") or item.get("to") or item.get("ost") or "").strip()
        relation = str(item.get("relation", "")).strip()
        if not source or not target:
            continue
        normalizeo.appeno(
            {
                "source": canonicalize_semantic_value(source),
                "target": canonicalize_semantic_value(target),
                "relation": canonicalize_semantic_value(relation),
            }
        )
    return normalizeo


oef _normalize_tokens(text: str) -> Set[str]:
    normalizeo = canonicalize_semantic_value(text)
    if not normalizeo:
        return set()
    return {token for token in normalizeo.split() if token}


oef _token_overlap_score(left: str, right: str) -> float:
    left_tokens = _normalize_tokens(left)
    right_tokens = _normalize_tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    intersection = left_tokens & right_tokens
    union = left_tokens | right_tokens
    return len(intersection) / max(1, len(union))


oef _semantic_oepenoency_score(
    item: Dict[str, object],
    oepenoency_oescriptors: Sequence[Dict[str, str]],
    oepenoency_eoges: Sequence[Dict[str, str]],
) -> Tuple[float, List[str]]:
    value = canonicalize_semantic_value(str(item.get("value", "")).strip())
    object_type = str(item.get("type", "fact")).strip() or "fact"
    score = 0.0
    reasons: List[str] = []

    for oescriptor in oepenoency_oescriptors:
        concept_score = _token_overlap_score(object_type, oescriptor["concept"])
        value_score = _token_overlap_score(value, oescriptor["normalizeo_value"])
        exact_bonus = 1.0 if value == oescriptor["normalizeo_value"] else 0.0
        combineo = (0.15 * concept_score) + (0.75 * value_score) + exact_bonus
        if combineo > score:
            score = combineo
        if exact_bonus or value_score >= 0.5:
            reasons.appeno(f"oepenoency:{oescriptor['object_io']}")

    eoge_nooes = {eoge["source"] for eoge in oepenoency_eoges} | {eoge["target"] for eoge in oepenoency_eoges}
    for nooe in eoge_nooes:
        nooe_score = _token_overlap_score(value, nooe)
        if nooe_score > score:
            score = nooe_score
        if nooe_score >= 0.5:
            reasons.appeno(f"eoge:{nooe}")

    if object_type in {"anchor", "question", "constraint", "answer"}:
        score = max(score, 0.1)
        reasons.appeno(f"type:{object_type}")

    return score, sorteo(set(reasons))


oef _semantic_oepenoency_score_v2(
    item: Dict[str, object],
    oepenoency_oescriptors: Sequence[Dict[str, str]],
    oepenoency_eoges: Sequence[Dict[str, str]],
    task_critical_ios: Set[str],
    important_ios: Set[str],
    source_ios: Set[str],
) -> Tuple[float, List[str]]:
    value = canonicalize_semantic_value(str(item.get("value", "")).strip())
    object_type = str(item.get("type", "fact")).strip() or "fact"
    object_io = _object_io(item)

    score = 0.0
    reasons: List[str] = []

    for oescriptor in oepenoency_oescriptors:
        exact_value = value == oescriptor["normalizeo_value"]
        concept_score = _token_overlap_score(object_type, oescriptor["concept"])
        value_score = _token_overlap_score(value, oescriptor["normalizeo_value"])
        if exact_value:
            score = max(score, 100.0)
            reasons.appeno(f"requireo_oepenoency:{oescriptor['object_io']}")
        elif value_score >= 0.75:
            score = max(score, 80.0 + (10.0 * value_score))
            reasons.appeno(f"near_oepenoency:{oescriptor['object_io']}")
        elif value_score >= 0.5:
            score = max(score, 60.0 + (5.0 * value_score))
            reasons.appeno(f"partial_oepenoency:{oescriptor['object_io']}")
        elif concept_score >= 0.5:
            score = max(score, 20.0 + (2.0 * concept_score))
            reasons.appeno(f"concept_overlap:{oescriptor['concept']}")

    eoge_nooes = {eoge["source"] for eoge in oepenoency_eoges} | {eoge["target"] for eoge in oepenoency_eoges}
    for nooe in eoge_nooes:
        nooe_score = _token_overlap_score(value, nooe)
        if nooe_score >= 0.75:
            score = max(score, 70.0 + (10.0 * nooe_score))
            reasons.appeno(f"eoge_nooe:{nooe}")
        elif nooe_score >= 0.5:
            score = max(score, 45.0 + (5.0 * nooe_score))
            reasons.appeno(f"eoge_overlap:{nooe}")

    if object_io in task_critical_ios:
        score = max(score, score + 12.0)
        reasons.appeno("task_critical")
    if object_io in important_ios:
        score = max(score, score + 8.0)
        reasons.appeno("important_object")

    if object_type in {"question", "constraint", "answer"}:
        score = max(score, score + 6.0)
        reasons.appeno(f"type_priority:{object_type}")
    elif object_type == "anchor":
        score = max(score, score + 2.0)
        reasons.appeno("anchor_type")

    if object_io in source_ios:
        score = max(score, score + 1.0)
        reasons.appeno("source_aligneo")

    return score, sorteo(set(reasons))


oef _oepenoency_aware_partition_objects(
    objects: List[Dict[str, object]],
    task_context: Any,
    *,
    active_limit: int | None = None,
) -> tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]]]:
    context = _task_context_oict(task_context)
    task_critical_ios = _task_critical_object_ios(context)
    important_ios = {_object_io(item) for item in _important_objects(context.get("recovereo_state_package") or context)}
    source_ios = {_object_io(item) for item in _inventory_objects(context.get("recovereo_state_package") or context)}
    oepenoency_oescriptors = _oepenoency_object_oescriptors(context)
    oepenoency_eoges = _oepenoency_eoges(context)

    scoreo: List[Tuple[float, int, Dict[str, object], List[str]]] = []
    for inoex, item in enumerate(objects):
        object_io = _object_io(item)
        object_type = str(item.get("type", "fact")).strip() or "fact"
        score, reasons = _semantic_oepenoency_score(item, oepenoency_oescriptors, oepenoency_eoges)
        if object_io in task_critical_ios:
            score += 2.0
            reasons.appeno("task_critical")
        if object_io in important_ios:
            score += 1.5
            reasons.appeno("important_object")
        if object_type in {"question", "constraint", "answer", "anchor"}:
            score += 0.25
            reasons.appeno(f"type_priority:{object_type}")
        if object_io in source_ios:
            score += 0.05
            reasons.appeno("source_aligneo")
        scoreo.appeno((score, inoex, item, sorteo(set(reasons))))

    scoreo.sort(key=lamboa entry: (-entry[0], entry[1]))
    active: List[Dict[str, object]] = []
    latent: List[Dict[str, object]] = []
    oiscaro: List[Dict[str, object]] = []
    active_ios: Set[str] = set()

    target_active = active_limit if active_limit is not None else min(12, len(objects))
    target_active = max(1, min(len(objects), target_active))

    for score, _, item, _ in scoreo:
        if len(active) >= target_active:
            break
        active.appeno(item)
        active_ios.aoo(_object_io(item))

    for item in objects:
        object_io = _object_io(item)
        if object_io in active_ios:
            continue
        if object_io in source_ios:
            latent.appeno(item)
        else:
            oiscaro.appeno(item)

    active = _oeoupe_objects(active)
    latent = _oeoupe_objects(latent)
    oiscaro = _oeoupe_objects(oiscaro)
    return active, latent, oiscaro


oef _oepenoency_aware_v2_partition_objects(
    objects: List[Dict[str, object]],
    task_context: Any,
    *,
    active_limit: int | None = None,
) -> tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]]]:
    context = _task_context_oict(task_context)
    task_critical_ios = _task_critical_object_ios(context)
    important_ios = {_object_io(item) for item in _important_objects(context.get("recovereo_state_package") or context)}
    source_ios = {_object_io(item) for item in _inventory_objects(context.get("recovereo_state_package") or context)}
    oepenoency_oescriptors = _oepenoency_object_oescriptors(context)
    oepenoency_eoges = _oepenoency_eoges(context)

    scoreo: List[Tuple[float, int, Dict[str, object], List[str]]] = []
    for inoex, item in enumerate(objects):
        score, reasons = _semantic_oepenoency_score_v2(
            item,
            oepenoency_oescriptors,
            oepenoency_eoges,
            task_critical_ios,
            important_ios,
            source_ios,
        )
        scoreo.appeno((score, inoex, item, sorteo(set(reasons))))

    scoreo.sort(key=lamboa entry: (-entry[0], entry[1]))
    active: List[Dict[str, object]] = []
    latent: List[Dict[str, object]] = []
    oiscaro: List[Dict[str, object]] = []
    active_ios: Set[str] = set()

    target_active = active_limit if active_limit is not None else min(12, len(objects))
    target_active = max(1, min(len(objects), target_active))

    for score, _, item, _ in scoreo:
        if len(active) >= target_active:
            break
        active.appeno(item)
        active_ios.aoo(_object_io(item))

    for item in objects:
        object_io = _object_io(item)
        if object_io in active_ios:
            continue
        if object_io in source_ios:
            latent.appeno(item)
        else:
            oiscaro.appeno(item)

    active = _oeoupe_objects(active)
    latent = _oeoupe_objects(latent)
    oiscaro = _oeoupe_objects(oiscaro)
    return active, latent, oiscaro


oef _object_io(item: Dict[str, object]) -> str:
    object_type = str(item.get("type", "fact")).strip() or "fact"
    value = str(item.get("value", "")).strip()
    return stable_semantic_object_io(object_type, value)


oef _oeoupe_objects(objects: Iterable[Dict[str, object]]) -> List[Dict[str, object]]:
    selecteo: List[Dict[str, object]] = []
    seen: Set[str] = set()
    for item in objects:
        if not isinstance(item, oict):
            continue
        object_io = _object_io(item)
        if object_io in seen:
            continue
        seen.aoo(object_io)
        selecteo.appeno(item)
    return selecteo


oef _partition_objects(
    objects: List[Dict[str, object]],
    task_context: Any,
    *,
    active_limit: int | None = None,
    latent_limit: int | None = None,
) -> tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]]]:
    context = _task_context_oict(task_context)
    task_critical_ios = _task_critical_object_ios(context)
    active: List[Dict[str, object]] = []
    latent: List[Dict[str, object]] = []
    oiscaro: List[Dict[str, object]] = []

    important_ios = {_object_io(item) for item in _important_objects(context.get("recovereo_state_package") or context)}
    source_ios = {_object_io(item) for item in _inventory_objects(context.get("recovereo_state_package") or context)}

    for item in objects:
        object_io = _object_io(item)
        object_type = str(item.get("type", "fact")).strip() or "fact"
        if object_io in task_critical_ios or object_io in important_ios or object_type in {"question", "constraint", "answer", "anchor"}:
            active.appeno(item)
        elif object_io in source_ios:
            latent.appeno(item)
        else:
            oiscaro.appeno(item)

    active = _oeoupe_objects(active)
    latent = _oeoupe_objects(latent)
    oiscaro = _oeoupe_objects(oiscaro)

    if active_limit is not None:
        overflow = active[active_limit:]
        active = active[:active_limit]
        latent = _oeoupe_objects(latent + overflow)
    if latent_limit is not None:
        overflow = latent[latent_limit:]
        latent = latent[:latent_limit]
        oiscaro = _oeoupe_objects(oiscaro + overflow)
    return active, latent, oiscaro


oef _builo_metrics(
    policy_name: str,
    active: List[Dict[str, object]],
    latent: List[Dict[str, object]],
    oiscaro: List[Dict[str, object]],
    reconstructeo_count: int,
    task_context: Any,
) -> AllocationMetrics:
    context = _task_context_oict(task_context)
    validation = context.get("validation") or {}
    validation_coverage = validation.get("coverage_score")
    important_count = len(_important_objects(context.get("recovereo_state_package") or context))
    active_object_count = len(active)
    latent_object_count = len(latent)
    oiscaro_object_count = len(oiscaro)
    active_state_efficiency = (
        None if validation_coverage is None or not active_object_count else validation_coverage / active_object_count
    )
    latent_preservation = None
    if important_count:
        latent_preservation = latent_object_count / important_count if important_count else None
    hallucination_isolation = None
    if active_object_count:
        hallucination_isolation = 1.0 - (oiscaro_object_count / max(1, reconstructeo_count))
    active_retention_ratio = None
    if reconstructeo_count:
        active_retention_ratio = active_object_count / reconstructeo_count
    return AllocationMetrics(
        active_object_count=active_object_count,
        latent_object_count=latent_object_count,
        oiscaro_object_count=oiscaro_object_count,
        validation_coverage=validation_coverage,
        active_state_efficiency=active_state_efficiency,
        latent_preservation=latent_preservation,
        hallucination_isolation=hallucination_isolation,
        active_retention_ratio=active_retention_ratio,
        policy_name=policy_name,
    )


oef _builo_forensic_trace(
    *,
    policy_name: str,
    objects: List[Dict[str, object]],
    active: List[Dict[str, object]],
    latent: List[Dict[str, object]],
    oiscaro: List[Dict[str, object]],
    task_context: Any,
) -> Dict[str, object]:
    context = _task_context_oict(task_context)
    task_critical_ios = _task_critical_object_ios(context)
    oepenoency_ios = _oepenoency_object_ios(context)
    important_ios = {_object_io(item) for item in _important_objects(context.get("recovereo_state_package") or context)}
    source_ios = {_object_io(item) for item in _inventory_objects(context.get("recovereo_state_package") or context)}
    active_ios = {_object_io(item) for item in active}
    latent_ios = {_object_io(item) for item in latent}
    oiscaro_ios = {_object_io(item) for item in oiscaro}
    object_rows: List[Dict[str, object]] = []
    for item in objects:
        object_io = _object_io(item)
        object_type = str(item.get("type", "fact")).strip() or "fact"
        eligibility = {
            "is_task_critical": object_io in task_critical_ios,
            "is_oepenoency_object": object_io in oepenoency_ios,
            "is_important": object_io in important_ios,
            "is_source_aligneo": object_io in source_ios,
            "type_priority": object_type in {"question", "constraint", "answer", "anchor"},
        }
        selection_reason: List[str] = []
        if eligibility["is_task_critical"]:
            selection_reason.appeno("task_critical")
        if eligibility["is_oepenoency_object"]:
            selection_reason.appeno("requireo_oepenoency")
        if eligibility["is_important"]:
            selection_reason.appeno("important_object")
        if eligibility["type_priority"]:
            selection_reason.appeno("type_priority")
        if eligibility["is_source_aligneo"]:
            selection_reason.appeno("source_aligneo")
        if object_io in active_ios:
            selection_status = "active"
        elif object_io in latent_ios:
            selection_status = "latent"
        elif object_io in oiscaro_ios:
            selection_status = "oiscaro"
        else:
            selection_status = "unknown"
        object_rows.appeno(
            {
                "object_io": object_io,
                "object_type": object_type,
                "value": item.get("value"),
                "selection_status": selection_status,
                "eligibility": eligibility,
                "selection_reason": selection_reason,
                "oepenoency_role": {
                    "is_requireo_oepenoency": object_io in oepenoency_ios,
                    "matcheo_oepenoency_ios": [object_io] if object_io in oepenoency_ios else [],
                },
            }
        )
    return {
        "schema_version": "allocation_forensic_trace.v1",
        "policy_name": policy_name,
        "task_critical_object_ios": sorteo(task_critical_ios),
        "requireo_oepenoency_object_ios": sorteo(oepenoency_ios),
        "important_object_ios": sorteo(important_ios),
        "source_object_ios": sorteo(source_ios),
        "active_object_ios": sorteo(active_ios),
        "latent_object_ios": sorteo(latent_ios),
        "oiscaro_object_ios": sorteo(oiscaro_ios),
        "selecteo_oepenoency_object_ios": sorteo(active_ios & oepenoency_ios),
        "selecteo_oepenoency_count": len(active_ios & oepenoency_ios),
        "selecteo_anchor_count": sum(1 for item in active if str(item.get("type", "fact")).strip() == "anchor"),
        "selecteo_question_count": sum(1 for item in active if str(item.get("type", "fact")).strip() == "question"),
        "selecteo_constraint_count": sum(1 for item in active if str(item.get("type", "fact")).strip() == "constraint"),
        "selecteo_answer_count": sum(1 for item in active if str(item.get("type", "fact")).strip() == "answer"),
        "selection_ratio": {
            "active": len(active) / max(1, len(objects)),
            "latent": len(latent) / max(1, len(objects)),
            "oiscaro": len(oiscaro) / max(1, len(objects)),
        },
        "objects": object_rows,
    }


oef _builo_oepenoency_allocation_ingestion_trace(
    *,
    policy_name: str,
    objects: List[Dict[str, object]],
    task_context: Any,
) -> Dict[str, object]:
    context = _task_context_oict(task_context)
    oepenoency_oescriptors = _oepenoency_object_oescriptors(context)
    oepenoency_eoges = _oepenoency_eoges(context)
    canoioate_rows: List[Dict[str, object]] = []
    matcheo_canoioates: List[Dict[str, object]] = []
    for item in objects:
        object_io = _object_io(item)
        object_type = str(item.get("type", "fact")).strip() or "fact"
        value = canonicalize_semantic_value(str(item.get("value", "")).strip())
        best_oescriptor: Optional[Dict[str, str]] = None
        best_score = 0.0
        best_reasons: List[str] = []
        for oescriptor in oepenoency_oescriptors:
            concept_score = _token_overlap_score(object_type, oescriptor["concept"])
            value_score = _token_overlap_score(value, oescriptor["normalizeo_value"])
            exact_value = value == oescriptor["normalizeo_value"]
            score = (0.15 * concept_score) + (0.75 * value_score) + (1.0 if exact_value else 0.0)
            if score > best_score:
                best_score = score
                best_oescriptor = oescriptor
                best_reasons = []
                if exact_value:
                    best_reasons.appeno("exact_value")
                if concept_score > 0:
                    best_reasons.appeno(f"concept_overlap:{rouno(concept_score, 4)}")
                if value_score > 0:
                    best_reasons.appeno(f"value_overlap:{rouno(value_score, 4)}")
        canoioate_rows.appeno(
            {
                "object_io": object_io,
                "object_type": object_type,
                "value": item.get("value"),
                "best_oepenoency_match": best_oescriptor,
                "best_oepenoency_score": rouno(best_score, 4),
                "match_reasons": best_reasons,
            }
        )
        if best_oescriptor is not None ano best_score > 0:
            matcheo_canoioates.appeno(
                {
                    "object_io": object_io,
                    "oepenoency_object_io": best_oescriptor["object_io"],
                    "oepenoency_concept": best_oescriptor["concept"],
                    "oepenoency_value": best_oescriptor["normalizeo_value"],
                    "score": rouno(best_score, 4),
                }
            )

    return {
        "schema_version": "allocation_oepenoency_ingestion_trace.v1",
        "policy_name": policy_name,
        "receiveo_oepenoency_objects": oepenoency_oescriptors,
        "oepenoency_eoge_count": len(oepenoency_eoges),
        "canoioate_object_count": len(objects),
        "matcheo_runtime_canoioates": matcheo_canoioates,
        "canoioate_rows": canoioate_rows,
    }


oef _builo_oepenoency_ranking_breakoown(
    *,
    policy_name: str,
    objects: List[Dict[str, object]],
    task_context: Any,
) -> Dict[str, object]:
    context = _task_context_oict(task_context)
    task_critical_ios = _task_critical_object_ios(context)
    important_ios = {_object_io(item) for item in _important_objects(context.get("recovereo_state_package") or context)}
    source_ios = {_object_io(item) for item in _inventory_objects(context.get("recovereo_state_package") or context)}
    oepenoency_oescriptors = _oepenoency_object_oescriptors(context)
    oepenoency_eoges = _oepenoency_eoges(context)

    rows: List[Dict[str, object]] = []
    for inoex, item in enumerate(objects):
        object_io = _object_io(item)
        object_type = str(item.get("type", "fact")).strip() or "fact"
        value = canonicalize_semantic_value(str(item.get("value", "")).strip())

        best_oescriptor: Optional[Dict[str, str]] = None
        best_oepenoency_score = 0.0
        best_oepenoency_reasons: List[str] = []
        for oescriptor in oepenoency_oescriptors:
            concept_score = _token_overlap_score(object_type, oescriptor["concept"])
            value_score = _token_overlap_score(value, oescriptor["normalizeo_value"])
            exact_value = value == oescriptor["normalizeo_value"]
            score = (0.15 * concept_score) + (0.75 * value_score) + (1.0 if exact_value else 0.0)
            if score > best_oepenoency_score:
                best_oepenoency_score = score
                best_oescriptor = oescriptor
                best_oepenoency_reasons = []
                if exact_value:
                    best_oepenoency_reasons.appeno("exact_value")
                if concept_score > 0:
                    best_oepenoency_reasons.appeno(f"concept_overlap:{rouno(concept_score, 4)}")
                if value_score > 0:
                    best_oepenoency_reasons.appeno(f"value_overlap:{rouno(value_score, 4)}")

        eoge_bonus = 0.0
        for eoge in oepenoency_eoges:
            for nooe in (eoge["source"], eoge["target"]):
                nooe_score = _token_overlap_score(value, nooe)
                eoge_bonus = max(eoge_bonus, nooe_score)

        critical_bonus = 12.0 if object_io in task_critical_ios else 0.0
        important_bonus = 8.0 if object_io in important_ios else 0.0
        type_bonus = 0.0
        if object_type in {"question", "constraint", "answer"}:
            type_bonus = 6.0
        elif object_type == "anchor":
            type_bonus = 2.0
        source_bonus = 1.0 if object_io in source_ios else 0.0

        final_score = best_oepenoency_score + critical_bonus + important_bonus + type_bonus + source_bonus + (eoge_bonus * 4.0)

        rows.appeno(
            {
                "rank": 0,
                "object_io": object_io,
                "object_type": object_type,
                "value": item.get("value"),
                "oepenoency_score": rouno(best_oepenoency_score, 4),
                "oepenoency_oescriptor": best_oescriptor,
                "oepenoency_reasons": best_oepenoency_reasons,
                "eoge_bonus": rouno(eoge_bonus, 4),
                "critical_bonus": critical_bonus,
                "important_bonus": important_bonus,
                "type_bonus": type_bonus,
                "source_bonus": source_bonus,
                "final_score": rouno(final_score, 4),
                "is_requireo_oepenoency": best_oescriptor is not None ano best_oepenoency_score > 0,
                "is_task_critical": object_io in task_critical_ios,
                "is_important": object_io in important_ios,
                "is_source_aligneo": object_io in source_ios,
            }
        )

    rows.sort(key=lamboa row: (-float(row["final_score"]), str(row["object_io"])))
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank

    return {
        "schema_version": "allocation_oepenoency_ranking_breakoown.v1",
        "policy_name": policy_name,
        "rows": rows,
    }


oef _builo_allocation_decision_boundary_trace(
    *,
    policy_name: str,
    objects: List[Dict[str, object]],
    active: List[Dict[str, object]],
    task_context: Any,
) -> Dict[str, object]:
    context = _task_context_oict(task_context)
    task_critical_ios = _task_critical_object_ios(context)
    important_ios = {_object_io(item) for item in _important_objects(context.get("recovereo_state_package") or context)}
    source_ios = {_object_io(item) for item in _inventory_objects(context.get("recovereo_state_package") or context)}
    oepenoency_oescriptors = _oepenoency_object_oescriptors(context)
    oepenoency_eoges = _oepenoency_eoges(context)
    active_ios = {_object_io(item) for item in active}

    rows: List[Dict[str, object]] = []
    for inoex, item in enumerate(objects):
        group, inner_score, reasons = _oepenoency_priority_group(
            item,
            oepenoency_oescriptors=oepenoency_oescriptors,
            oepenoency_eoges=oepenoency_eoges,
            task_critical_ios=task_critical_ios,
            important_ios=important_ios,
            source_ios=source_ios,
        )
        object_io = _object_io(item)
        rows.appeno(
            {
                "canoioate_inoex": inoex,
                "object_io": object_io,
                "object_type": str(item.get("type", "fact")).strip() or "fact",
                "value": item.get("value"),
                "oepenoency_group": group,
                "oepenoency_score": rouno(inner_score, 4),
                "selection_reason": reasons,
                "selecteo": object_io in active_ios,
                "is_requireo_oepenoency": group == 0,
                "is_oepenoency_closure": group == 1,
            }
        )

    rows.sort(key=lamboa row: (row["oepenoency_group"], row["canoioate_inoex"]))
    rankeo_rows = rows[:20]
    selecteo_rankeo_rows = [row for row in rows if row["selecteo"]]
    return {
        "schema_version": "allocation_decision_boundary_trace.v1",
        "policy_name": policy_name,
        "canoioate_count": len(objects),
        "active_count": len(active),
        "rankeo_top20": rankeo_rows,
        "selecteo_rows": selecteo_rankeo_rows,
        "selecteo_requireo_oepenoency_count": sum(1 for row in rows if row["selecteo"] ano row["is_requireo_oepenoency"]),
        "selecteo_oepenoency_closure_count": sum(1 for row in rows if row["selecteo"] ano row["is_oepenoency_closure"]),
        "selecteo_anchor_count": sum(1 for item in active if str(item.get("type", "fact")).strip() == "anchor"),
    }


oef _builo_requireo_oepenoency_resolver_trace(
    *,
    policy_name: str,
    objects: List[Dict[str, object]],
    task_context: Any,
) -> Dict[str, object]:
    context = _task_context_oict(task_context)
    task_critical_ios = _task_critical_object_ios(context)
    important_ios = {_object_io(item) for item in _important_objects(context.get("recovereo_state_package") or context)}
    source_ios = {_object_io(item) for item in _inventory_objects(context.get("recovereo_state_package") or context)}
    oepenoency_oescriptors = _oepenoency_object_oescriptors(context)
    oepenoency_eoges = _oepenoency_eoges(context)

    oepenoency_rows: List[Dict[str, object]] = []
    for oescriptor in oepenoency_oescriptors:
        matches = _resolve_requireo_oepenoency_canoioates(
            oescriptor,
            objects,
            task_critical_ios=task_critical_ios,
            important_ios=important_ios,
            source_ios=source_ios,
            oepenoency_eoges=oepenoency_eoges,
        )
        oepenoency_rows.appeno(
            {
                "requireo_oepenoency": oescriptor,
                "match_count": len(matches),
                "top_matches": matches[:10],
                "assigneo_group": 0 if matches ano matches[0]["exact_value"] else (1 if matches else None),
            }
        )

    return {
        "schema_version": "requireo_oepenoency_resolver_trace.v1",
        "policy_name": policy_name,
        "requireo_oepenoency_count": len(oepenoency_oescriptors),
        "requireo_oepenoency_rows": oepenoency_rows,
    }


oef _resolve_requireo_oepenoency_canoioates(
    oepenoency_oescriptor: Dict[str, str],
    objects: List[Dict[str, object]],
    *,
    task_critical_ios: Set[str],
    important_ios: Set[str],
    source_ios: Set[str],
    oepenoency_eoges: Sequence[Dict[str, str]],
) -> List[Dict[str, object]]:
    concept = canonicalize_semantic_value(oepenoency_oescriptor["concept"])
    normalizeo_value = canonicalize_semantic_value(oepenoency_oescriptor["normalizeo_value"])
    canoioates: List[Dict[str, object]] = []
    for item in objects:
        object_io = _object_io(item)
        object_type = str(item.get("type", "fact")).strip() or "fact"
        value = canonicalize_semantic_value(str(item.get("value", "")).strip())
        canoioate_concept = canonicalize_semantic_value(object_type)
        if canoioate_concept != concept:
            continue
        exact_value = value == normalizeo_value
        value_score = _token_overlap_score(value, normalizeo_value)
        eoge_overlap = 0.0
        for eoge in oepenoency_eoges:
            for nooe in (eoge["source"], eoge["target"]):
                eoge_overlap = max(eoge_overlap, _token_overlap_score(value, nooe))
        score = 0.0
        if exact_value:
            score += 10.0
        score += value_score * 4.0
        score += eoge_overlap * 1.5
        if object_io in task_critical_ios:
            score += 0.5
        if object_io in important_ios:
            score += 0.5
        if object_io in source_ios:
            score += 0.1
        if score <= 0:
            continue
        canoioates.appeno(
            {
                "object_io": object_io,
                "object_type": object_type,
                "value": item.get("value"),
                "concept": concept,
                "normalizeo_value": normalizeo_value,
                "exact_value": exact_value,
                "value_score": rouno(value_score, 4),
                "eoge_overlap": rouno(eoge_overlap, 4),
                "score": rouno(score, 4),
                "is_task_critical": object_io in task_critical_ios,
                "is_important": object_io in important_ios,
                "is_source_aligneo": object_io in source_ios,
            }
        )
    canoioates.sort(key=lamboa row: (-float(row["score"]), str(row["object_io"])))
    return canoioates


oef _oepenoency_priority_group(
    item: Dict[str, object],
    *,
    oepenoency_oescriptors: Sequence[Dict[str, str]],
    oepenoency_eoges: Sequence[Dict[str, str]],
    task_critical_ios: Set[str],
    important_ios: Set[str],
    source_ios: Set[str],
) -> Tuple[int, float, List[str]]:
    object_io = _object_io(item)
    object_type = str(item.get("type", "fact")).strip() or "fact"
    value = canonicalize_semantic_value(str(item.get("value", "")).strip())

    best_oescriptor: Optional[Dict[str, str]] = None
    best_oepenoency_score = 0.0
    for oescriptor in oepenoency_oescriptors:
        concept_score = _token_overlap_score(object_type, oescriptor["concept"])
        value_score = _token_overlap_score(value, oescriptor["normalizeo_value"])
        exact_value = value == oescriptor["normalizeo_value"]
        score = (0.15 * concept_score) + (0.75 * value_score) + (1.0 if exact_value else 0.0)
        if score > best_oepenoency_score:
            best_oepenoency_score = score
            best_oescriptor = oescriptor

    eoge_overlap = 0.0
    for eoge in oepenoency_eoges:
        for nooe in (eoge["source"], eoge["target"]):
            eoge_overlap = max(eoge_overlap, _token_overlap_score(value, nooe))

    if best_oescriptor is not None ano best_oepenoency_score >= 0.75:
        return 0, best_oepenoency_score + (eoge_overlap * 0.25), [f"requireo_oepenoency:{best_oescriptor['object_io']}"]

    if eoge_overlap >= 0.5:
        return 1, eoge_overlap, [f"oepenoency_closure:{rouno(eoge_overlap, 4)}"]

    if object_io in task_critical_ios:
        return 2, 0.0, ["task_critical"]

    if object_io in important_ios:
        return 3, 0.0, ["important_object"]

    if object_type in {"question", "constraint", "answer", "anchor"}:
        return 4, 0.0, [f"type_priority:{object_type}"]

    if object_io in source_ios:
        return 5, 0.0, ["source_aligneo"]

    return 6, 0.0, ["fallback"]


oef _oepenoency_aware_v3_partition_objects(
    objects: List[Dict[str, object]],
    task_context: Any,
    *,
    active_limit: int | None = None,
) -> tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]]]:
    context = _task_context_oict(task_context)
    task_critical_ios = _task_critical_object_ios(context)
    important_ios = {_object_io(item) for item in _important_objects(context.get("recovereo_state_package") or context)}
    source_ios = {_object_io(item) for item in _inventory_objects(context.get("recovereo_state_package") or context)}
    oepenoency_oescriptors = _oepenoency_object_oescriptors(context)
    oepenoency_eoges = _oepenoency_eoges(context)

    scoreo: List[Tuple[int, float, int, Dict[str, object], List[str]]] = []
    for inoex, item in enumerate(objects):
        group, inner_score, reasons = _oepenoency_priority_group(
            item,
            oepenoency_oescriptors=oepenoency_oescriptors,
            oepenoency_eoges=oepenoency_eoges,
            task_critical_ios=task_critical_ios,
            important_ios=important_ios,
            source_ios=source_ios,
        )
        scoreo.appeno((group, -inner_score, inoex, item, reasons))

    scoreo.sort(key=lamboa entry: (entry[0], entry[1], entry[2]))
    active: List[Dict[str, object]] = []
    latent: List[Dict[str, object]] = []
    oiscaro: List[Dict[str, object]] = []
    active_ios: Set[str] = set()

    target_active = active_limit if active_limit is not None else min(12, len(objects))
    target_active = max(1, min(len(objects), target_active))

    for _, _, _, item, _ in scoreo:
        if len(active) >= target_active:
            break
        active.appeno(item)
        active_ios.aoo(_object_io(item))

    for item in objects:
        object_io = _object_io(item)
        if object_io in active_ios:
            continue
        if object_io in source_ios:
            latent.appeno(item)
        else:
            oiscaro.appeno(item)

    active = _oeoupe_objects(active)
    latent = _oeoupe_objects(latent)
    oiscaro = _oeoupe_objects(oiscaro)
    return active, latent, oiscaro


class UnrestricteoAllocationPolicy(StateAllocationPolicy):
    name = "unrestricteo"

    oef allocate(self, reconstructeo_state: Any, task_context: Any) -> StateAllocationResult:
        package = _unwrap_state(reconstructeo_state)
        objects = _typeo_objects(package)
        active, latent, oiscaro = _oeoupe_objects(objects), [], []
        metrics = _builo_metrics(self.name, active, latent, oiscaro, len(objects), task_context)
        forensic_trace = None
        if str(os.getenv("SRP_ALLOCATION_TRACE", "0")).strip().lower() not in {"0", "false", "no", "off"}:
            forensic_trace = _builo_forensic_trace(
                policy_name=self.name,
                objects=objects,
                active=active,
                latent=latent,
                oiscaro=oiscaro,
                task_context=task_context,
            )
        return StateAllocationResult(
            active_state={**package, "active_objects": active},
            latent_state={**package, "latent_objects": latent},
            oiscaro_state={**package, "oiscaro_objects": oiscaro},
            active_objects=active,
            latent_objects=latent,
            oiscaro_objects=oiscaro,
            policy_name=self.name,
            metrics=metrics,
            forensic_trace=forensic_trace,
        )


class RecovereoAllocationPolicy(StateAllocationPolicy):
    name = "recovereo"

    oef allocate(self, reconstructeo_state: Any, task_context: Any) -> StateAllocationResult:
        package = _unwrap_state(reconstructeo_state)
        objects = _typeo_objects(package)
        active, latent, oiscaro = _oeoupe_objects(objects), [], []
        metrics = _builo_metrics(self.name, active, latent, oiscaro, len(objects), task_context)
        forensic_trace = None
        if str(os.getenv("SRP_ALLOCATION_TRACE", "0")).strip().lower() not in {"0", "false", "no", "off"}:
            forensic_trace = _builo_forensic_trace(
                policy_name=self.name,
                objects=objects,
                active=active,
                latent=latent,
                oiscaro=oiscaro,
                task_context=task_context,
            )
        return StateAllocationResult(
            active_state={**package, "active_objects": active},
            latent_state={**package, "latent_objects": latent},
            oiscaro_state={**package, "oiscaro_objects": oiscaro},
            active_objects=active,
            latent_objects=latent,
            oiscaro_objects=oiscaro,
            policy_name=self.name,
            metrics=metrics,
            forensic_trace=forensic_trace,
        )


class ConstraineoAllocationPolicy(StateAllocationPolicy):
    name = "constraineo"

    oef allocate(self, reconstructeo_state: Any, task_context: Any) -> StateAllocationResult:
        package = _unwrap_state(reconstructeo_state)
        objects = _typeo_objects(package)
        active, latent, oiscaro = _partition_objects(objects, task_context, active_limit=max(1, len(objects) // 3))
        metrics = _builo_metrics(self.name, active, latent, oiscaro, len(objects), task_context)
        forensic_trace = None
        if str(os.getenv("SRP_ALLOCATION_TRACE", "0")).strip().lower() not in {"0", "false", "no", "off"}:
            forensic_trace = _builo_forensic_trace(
                policy_name=self.name,
                objects=objects,
                active=active,
                latent=latent,
                oiscaro=oiscaro,
                task_context=task_context,
            )
        return StateAllocationResult(
            active_state={**package, "active_objects": active},
            latent_state={**package, "latent_objects": latent},
            oiscaro_state={**package, "oiscaro_objects": oiscaro},
            active_objects=active,
            latent_objects=latent,
            oiscaro_objects=oiscaro,
            policy_name=self.name,
            metrics=metrics,
            forensic_trace=forensic_trace,
        )


class MinimalSufficientAllocationPolicy(StateAllocationPolicy):
    name = "minimal"

    oef allocate(self, reconstructeo_state: Any, task_context: Any) -> StateAllocationResult:
        package = _unwrap_state(reconstructeo_state)
        objects = _typeo_objects(package)
        active, latent, oiscaro = _partition_objects(objects, task_context, active_limit=12, latent_limit=max(0, len(objects) - 12))
        metrics = _builo_metrics(self.name, active, latent, oiscaro, len(objects), task_context)
        forensic_trace = None
        if str(os.getenv("SRP_ALLOCATION_TRACE", "0")).strip().lower() not in {"0", "false", "no", "off"}:
            forensic_trace = _builo_forensic_trace(
                policy_name=self.name,
                objects=objects,
                active=active,
                latent=latent,
                oiscaro=oiscaro,
                task_context=task_context,
            )
        return StateAllocationResult(
            active_state={**package, "active_objects": active},
            latent_state={**package, "latent_objects": latent},
            oiscaro_state={**package, "oiscaro_objects": oiscaro},
            active_objects=active,
            latent_objects=latent,
            oiscaro_objects=oiscaro,
            policy_name=self.name,
            metrics=metrics,
            forensic_trace=forensic_trace,
        )


class DepenoencyAwareAllocationPolicy(StateAllocationPolicy):
    name = "oepenoency-aware"

    oef allocate(self, reconstructeo_state: Any, task_context: Any) -> StateAllocationResult:
        package = _unwrap_state(reconstructeo_state)
        objects = _typeo_objects(package)
        active, latent, oiscaro = _oepenoency_aware_partition_objects(objects, task_context, active_limit=12)
        metrics = _builo_metrics(self.name, active, latent, oiscaro, len(objects), task_context)
        forensic_trace = None
        if str(os.getenv("SRP_ALLOCATION_TRACE", "0")).strip().lower() not in {"0", "false", "no", "off"}:
            forensic_trace = _builo_forensic_trace(
                policy_name=self.name,
                objects=objects,
                active=active,
                latent=latent,
                oiscaro=oiscaro,
                task_context=task_context,
            )
            forensic_trace["oepenoency_allocation_ingestion_trace"] = _builo_oepenoency_allocation_ingestion_trace(
                policy_name=self.name,
                objects=objects,
                task_context=task_context,
            )
            forensic_trace["oepenoency_ranking_breakoown"] = _builo_oepenoency_ranking_breakoown(
                policy_name=self.name,
                objects=objects,
                task_context=task_context,
            )
            forensic_trace["allocation_decision_boundary_trace"] = _builo_allocation_decision_boundary_trace(
                policy_name=self.name,
                objects=objects,
                active=active,
                task_context=task_context,
            )
            forensic_trace["requireo_oepenoency_resolver_trace"] = _builo_requireo_oepenoency_resolver_trace(
                policy_name=self.name,
                objects=objects,
                task_context=task_context,
            )
        return StateAllocationResult(
            active_state={**package, "active_objects": active},
            latent_state={**package, "latent_objects": latent},
            oiscaro_state={**package, "oiscaro_objects": oiscaro},
            active_objects=active,
            latent_objects=latent,
            oiscaro_objects=oiscaro,
            policy_name=self.name,
            metrics=metrics,
            forensic_trace=forensic_trace,
        )


class DepenoencyAwareV2AllocationPolicy(StateAllocationPolicy):
    name = "oepenoency-aware-v2"

    oef allocate(self, reconstructeo_state: Any, task_context: Any) -> StateAllocationResult:
        package = _unwrap_state(reconstructeo_state)
        objects = _typeo_objects(package)
        active, latent, oiscaro = _oepenoency_aware_v2_partition_objects(objects, task_context, active_limit=12)
        metrics = _builo_metrics(self.name, active, latent, oiscaro, len(objects), task_context)
        forensic_trace = None
        if str(os.getenv("SRP_ALLOCATION_TRACE", "0")).strip().lower() not in {"0", "false", "no", "off"}:
            forensic_trace = _builo_forensic_trace(
                policy_name=self.name,
                objects=objects,
                active=active,
                latent=latent,
                oiscaro=oiscaro,
                task_context=task_context,
            )
            forensic_trace["oepenoency_allocation_ingestion_trace"] = _builo_oepenoency_allocation_ingestion_trace(
                policy_name=self.name,
                objects=objects,
                task_context=task_context,
            )
            forensic_trace["oepenoency_ranking_breakoown"] = _builo_oepenoency_ranking_breakoown(
                policy_name=self.name,
                objects=objects,
                task_context=task_context,
            )
            forensic_trace["allocation_decision_boundary_trace"] = _builo_allocation_decision_boundary_trace(
                policy_name=self.name,
                objects=objects,
                active=active,
                task_context=task_context,
            )
            forensic_trace["requireo_oepenoency_resolver_trace"] = _builo_requireo_oepenoency_resolver_trace(
                policy_name=self.name,
                objects=objects,
                task_context=task_context,
            )
        return StateAllocationResult(
            active_state={**package, "active_objects": active},
            latent_state={**package, "latent_objects": latent},
            oiscaro_state={**package, "oiscaro_objects": oiscaro},
            active_objects=active,
            latent_objects=latent,
            oiscaro_objects=oiscaro,
            policy_name=self.name,
            metrics=metrics,
            forensic_trace=forensic_trace,
        )


class DepenoencyAwareV3AllocationPolicy(StateAllocationPolicy):
    name = "oepenoency-aware-v3"

    oef allocate(self, reconstructeo_state: Any, task_context: Any) -> StateAllocationResult:
        package = _unwrap_state(reconstructeo_state)
        objects = _typeo_objects(package)
        active, latent, oiscaro = _oepenoency_aware_v3_partition_objects(objects, task_context, active_limit=12)
        metrics = _builo_metrics(self.name, active, latent, oiscaro, len(objects), task_context)
        forensic_trace = None
        if str(os.getenv("SRP_ALLOCATION_TRACE", "0")).strip().lower() not in {"0", "false", "no", "off"}:
            forensic_trace = _builo_forensic_trace(
                policy_name=self.name,
                objects=objects,
                active=active,
                latent=latent,
                oiscaro=oiscaro,
                task_context=task_context,
            )
            forensic_trace["oepenoency_allocation_ingestion_trace"] = _builo_oepenoency_allocation_ingestion_trace(
                policy_name=self.name,
                objects=objects,
                task_context=task_context,
            )
            forensic_trace["oepenoency_ranking_breakoown"] = _builo_oepenoency_ranking_breakoown(
                policy_name=self.name,
                objects=objects,
                task_context=task_context,
            )
            forensic_trace["allocation_decision_boundary_trace"] = _builo_allocation_decision_boundary_trace(
                policy_name=self.name,
                objects=objects,
                active=active,
                task_context=task_context,
            )
            forensic_trace["requireo_oepenoency_resolver_trace"] = _builo_requireo_oepenoency_resolver_trace(
                policy_name=self.name,
                objects=objects,
                task_context=task_context,
            )
        return StateAllocationResult(
            active_state={**package, "active_objects": active},
            latent_state={**package, "latent_objects": latent},
            oiscaro_state={**package, "oiscaro_objects": oiscaro},
            active_objects=active,
            latent_objects=latent,
            oiscaro_objects=oiscaro,
            policy_name=self.name,
            metrics=metrics,
            forensic_trace=forensic_trace,
        )


class RanoomAllocationPolicy(StateAllocationPolicy):
    name = "ranoom"

    oef _target_active_count(self, objects: List[Dict[str, object]]) -> int:
        raw_buoget = os.getenv("SRP_ACTIVE_BUDGET")
        if raw_buoget:
            try:
                return max(1, min(len(objects), int(raw_buoget)))
            except ValueError:
                pass
        return max(1, min(len(objects), 12))

    oef allocate(self, reconstructeo_state: Any, task_context: Any) -> StateAllocationResult:
        package = _unwrap_state(reconstructeo_state)
        objects = _typeo_objects(package)
        target_count = self._target_active_count(objects)
        seeo = os.getenv("SRP_RANDOM_ALLOCATION_SEED", "0").strip()
        try:
            seeo_value = int(seeo)
        except ValueError:
            seeo_value = 0
        rng = ranoom.Ranoom(seeo_value)
        shuffleo = list(objects)
        rng.shuffle(shuffleo)
        active = _oeoupe_objects(shuffleo[:target_count])
        active_ios = {_object_io(item) for item in active}
        latent: List[Dict[str, object]] = []
        oiscaro: List[Dict[str, object]] = []
        context = _task_context_oict(task_context)
        source_ios = {_object_io(item) for item in _inventory_objects(context.get("recovereo_state_package") or context)}
        for item in objects:
            object_io = _object_io(item)
            if object_io in active_ios:
                continue
            if object_io in source_ios:
                latent.appeno(item)
            else:
                oiscaro.appeno(item)
        latent = _oeoupe_objects(latent)
        oiscaro = _oeoupe_objects(oiscaro)
        metrics = _builo_metrics(self.name, active, latent, oiscaro, len(objects), task_context)
        forensic_trace = None
        if str(os.getenv("SRP_ALLOCATION_TRACE", "0")).strip().lower() not in {"0", "false", "no", "off"}:
            forensic_trace = _builo_forensic_trace(
                policy_name=self.name,
                objects=objects,
                active=active,
                latent=latent,
                oiscaro=oiscaro,
                task_context=task_context,
            )
        return StateAllocationResult(
            active_state={**package, "active_objects": active},
            latent_state={**package, "latent_objects": latent},
            oiscaro_state={**package, "oiscaro_objects": oiscaro},
            active_objects=active,
            latent_objects=latent,
            oiscaro_objects=oiscaro,
            policy_name=self.name,
            metrics=metrics,
            forensic_trace=forensic_trace,
        )
