import json
from typing import Dict

from budgeting import available_memory_budget, clip_tail_to_budget, get_budget_config
from .state import SemanticState
from prompting import build_compression_prompt


def _coerce_vocab(value, fallback):
    if isinstance(value, list):
        cleaned = [str(item).strip() for item in value if str(item).strip()]
        if cleaned:
            return cleaned
    return list(fallback)


def _coerce_list(value, fallback):
    if isinstance(value, list):
        cleaned = [str(item).strip() for item in value if str(item).strip()]
        if cleaned:
            return cleaned
    return list(fallback)


def _coerce_term_map(value, fallback):
    if isinstance(value, dict):
        cleaned = {
            str(key).strip(): str(mapped).strip()
            for key, mapped in value.items()
            if str(key).strip() and str(mapped).strip()
        }
        if cleaned:
            return cleaned
    return dict(fallback)


def _parse_compressed_payload(raw_text: str, state: SemanticState) -> Dict:
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError:
        return {
            "memory": raw_text.strip(),
            "constraints": list(state.constraints),
            "global_vocab": state.global_vocabulary[:10],
            "local_vocab": state.local_vocabulary[:6],
            "term_map": dict(state.term_map),
            "loss_notes": list(state.loss_notes),
            "policy": state.policy,
            "typed_representation": state.ensure_typed_representation().as_dict(),
        }

    memory = str(payload.get("memory_summary", "")).strip() or raw_text.strip()
    constraints = _coerce_list(payload.get("constraints"), state.constraints)
    anchor_terms = payload.get("anchor_terms")
    if anchor_terms is None:
        anchor_terms = payload.get("core_concepts")
    global_vocab = _coerce_vocab(anchor_terms, state.global_vocabulary[:10])
    local_vocab = _coerce_vocab(anchor_terms, state.local_vocabulary[:6])
    term_map = _coerce_term_map(payload.get("term_map"), state.term_map)
    loss_notes = _coerce_list(payload.get("loss_risks"), state.loss_notes)
    policy = dict(state.policy)
    return {
        "memory": memory,
        "constraints": constraints,
        "global_vocab": global_vocab[:10],
        "local_vocab": local_vocab[:6],
        "term_map": term_map,
        "loss_notes": loss_notes,
        "policy": policy,
        "typed_representation": state.ensure_typed_representation().as_dict(),
    }


def compress_state(state: SemanticState, client=None) -> Dict:
    if client is None:
        words = state.memory.split()
        compressed_memory = " ".join(words[: min(18, len(words))])
        stable_terms = state.global_vocabulary[:6] or state.local_vocabulary[:6]
        return {
            "memory": compressed_memory,
            "constraints": list(state.constraints),
            "global_vocab": stable_terms,
            "local_vocab": stable_terms[:6],
            "term_map": dict(state.term_map),
            "loss_notes": list(state.loss_notes),
            "policy": state.policy,
            "typed_representation": state.ensure_typed_representation().as_dict(),
            "usage": None,
        }
    else:
        budget = get_budget_config()
        memory_view = clip_tail_to_budget(state.memory, available_memory_budget(constraints=state.constraints))
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
        compressed_memory = model_result["text"]
        parsed = _parse_compressed_payload(compressed_memory, state)
        parsed["usage"] = model_result.get("usage")
        return parsed
    return _parse_compressed_payload(compressed_memory, state)
