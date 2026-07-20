import os
from typing import Dict

from ..budgeting import available_memory_budget, clip_tail_to_budget, get_budget_config
from ..prompting import build_compression_prompt
from .chunking import chunk_memory
from .compress_parse import parse_compressed_payload
from .llm_judge import apply_llm_chunk_judge
from .saliency import rank_memory_chunks
from .semantic_objects import build_semantic_object_inventory
from .state import SemanticState


def _offline_compression_package(
    state: SemanticState,
    selected_chunks,
    llm_judge_summary: Dict[str, object],
) -> Dict:
    object_inventory = build_semantic_object_inventory(state)
    compressed_memory = "\n".join(item["text"] for item in selected_chunks) or clip_tail_to_budget(state.memory, 18)
    stable_terms = state.global_vocabulary[:6] or state.local_vocabulary[:6]
    return {
        "memory": compressed_memory,
        "constraints": list(state.constraints),
        "global_vocab": stable_terms,
        "local_vocab": stable_terms[:6],
        "term_map": dict(state.term_map),
        "loss_notes": list(state.loss_notes),
        "policy": state.policy,
        "semantic_objects": object_inventory["objects"],
        "semantic_object_inventory": object_inventory,
        "typed_representation": state.ensure_typed_representation().as_dict(),
        "runtime_summary": state.runtime_summary(),
        "selected_chunk_ids": [item["chunk_id"] for item in selected_chunks],
        "chunk_selection_method": "rule",
        "chunk_selection": selected_chunks,
        "chunk_selection_scores": [item["score"] for item in selected_chunks],
        "chunk_selection_reasons": [item["reason"] for item in selected_chunks],
        "chunk_selection_factors": [item["saliency_factors"] for item in selected_chunks],
        "llm_judge_calls": llm_judge_summary["judge_calls"],
        "llm_judge_failures": llm_judge_summary["judge_failures"],
        "parse_status": "offline",
        "parse_error": None,
        "usage": None,
    }


def _online_compression_package(
    state: SemanticState,
    selected_chunks,
    llm_judge_summary: Dict[str, object],
    client,
) -> Dict:
    object_inventory = build_semantic_object_inventory(state)
    budget = get_budget_config()
    selected_memory = "\n".join(item["text"] for item in selected_chunks)
    memory_view = selected_memory or clip_tail_to_budget(
        state.memory,
        available_memory_budget(constraints=state.constraints),
    )
    prompt = build_compression_prompt(
        memory_view,
        state.constraints or state.local_vocabulary or state.global_vocabulary,
        state.global_vocabulary,
        state.local_vocabulary,
        state.term_map,
        state.loss_notes,
        state.policy,
    )
    model_result = client.generate_with_usage(
        prompt,
        system_prompt="You compress semantic state while preserving essential constraints and concepts.",
        max_output_tokens=min(160, budget.output_tokens),
    )
    parsed = parse_compressed_payload(model_result["text"], state)
    parsed["usage"] = model_result.get("usage")
    parsed["raw_model_text"] = model_result.get("raw_text", model_result["text"])
    parsed["stripped_thinking"] = model_result.get("stripped_thinking")
    parsed["runtime_summary"] = state.runtime_summary()
    parsed["semantic_objects"] = object_inventory["objects"]
    parsed["semantic_object_inventory"] = object_inventory
    parsed["selected_chunk_ids"] = [item["chunk_id"] for item in selected_chunks]
    parsed["chunk_selection_method"] = (
        "hybrid"
        if any(item["embedding_score"] is not None for item in selected_chunks) and llm_judge_summary["enabled"]
        else "embedding"
        if any(item["embedding_score"] is not None for item in selected_chunks)
        else "rule"
    )
    parsed["chunk_selection"] = selected_chunks
    parsed["chunk_selection_scores"] = [item["score"] for item in selected_chunks]
    parsed["chunk_selection_reasons"] = [item["reason"] for item in selected_chunks]
    parsed["chunk_selection_factors"] = [item["saliency_factors"] for item in selected_chunks]
    parsed["llm_judge_calls"] = llm_judge_summary["judge_calls"]
    parsed["llm_judge_failures"] = llm_judge_summary["judge_failures"]
    return parsed


def _object_support_enabled() -> bool:
    return str(os.getenv("SRP_OBJECT_SUPPORT_ENABLED", "true")).strip().lower() not in {"0", "false", "no", "off"}


def compress_state(state: SemanticState, client=None) -> Dict:
    expected_keywords = state.global_vocabulary or state.local_vocabulary
    object_inventory = build_semantic_object_inventory(state)
    selected_chunks, _ = rank_memory_chunks(
        state.memory,
        state.constraints,
        expected_keywords=expected_keywords,
        top_k=int(os.getenv("SRP_RAG_TOP_K", "4")),
        semantic_object_inventory=object_inventory if _object_support_enabled() else None,
    )
    selected_chunks, llm_judge_summary = apply_llm_chunk_judge(
        selected_chunks,
        state.constraints,
        expected_keywords=expected_keywords,
        client=client,
    )
    if client is None:
        return _offline_compression_package(state, selected_chunks, llm_judge_summary)
    return _online_compression_package(state, selected_chunks, llm_judge_summary, client)


__all__ = ["chunk_memory", "compress_state"]
