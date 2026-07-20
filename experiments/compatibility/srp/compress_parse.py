import json
import re
from typing import Dict

from .llm_judge import extract_json_object
from .state import SemanticState


def coerce_vocab(value, fallback):
    if isinstance(value, list):
        cleaned = [str(item).strip() for item in value if str(item).strip()]
        if cleaned:
            return cleaned
    return list(fallback)


def coerce_list(value, fallback):
    if isinstance(value, list):
        cleaned = [str(item).strip() for item in value if str(item).strip()]
        if cleaned:
            return cleaned
    return list(fallback)


def coerce_term_map(value, fallback):
    if isinstance(value, dict):
        cleaned = {
            str(key).strip(): str(mapped).strip()
            for key, mapped in value.items()
            if str(key).strip() and str(mapped).strip()
        }
        if cleaned:
            return cleaned
    return dict(fallback)


def extract_json_string_field(raw_text: str, field_name: str) -> str:
    pattern = rf'"{re.escape(field_name)}"\s*:\s*"((?:\\.|[^"\\])*)"'
    match = re.search(pattern, raw_text, flags=re.DOTALL)
    if not match:
        return ""
    try:
        return json.loads(f'"{match.group(1)}"')
    except json.JSONDecodeError:
        return match.group(1).strip()


def extract_json_list_field(raw_text: str, field_name: str):
    pattern = rf'"{re.escape(field_name)}"\s*:\s*(\[[^\]]*\])'
    match = re.search(pattern, raw_text, flags=re.DOTALL)
    if not match:
        return None
    try:
        value = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, list) else None


def parse_compressed_payload(raw_text: str, state: SemanticState) -> Dict:
    try:
        payload = extract_json_object(raw_text)
    except json.JSONDecodeError as exc:
        memory_summary = extract_json_string_field(raw_text, "memory_summary")
        constraints = extract_json_list_field(raw_text, "constraints")
        anchor_terms = extract_json_list_field(raw_text, "anchor_terms")
        loss_risks = extract_json_list_field(raw_text, "loss_risks")
        if memory_summary:
            return {
                "memory": memory_summary,
                "constraints": coerce_list(constraints, state.constraints),
                "global_vocab": coerce_vocab(anchor_terms, state.global_vocabulary[:10])[:10],
                "local_vocab": coerce_vocab(anchor_terms, state.local_vocabulary[:6])[:6],
                "term_map": dict(state.term_map),
                "loss_notes": coerce_list(loss_risks, state.loss_notes),
                "policy": state.policy,
                "typed_representation": state.ensure_typed_representation().as_dict(),
                "parse_status": "partial_json",
                "parse_error": str(exc),
            }
        return {
            "memory": raw_text.strip(),
            "constraints": list(state.constraints),
            "global_vocab": state.global_vocabulary[:10],
            "local_vocab": state.local_vocabulary[:6],
            "term_map": dict(state.term_map),
            "loss_notes": list(state.loss_notes),
            "policy": state.policy,
            "typed_representation": state.ensure_typed_representation().as_dict(),
            "parse_status": "fallback_raw_text",
            "parse_error": str(exc),
        }

    memory = str(payload.get("memory_summary", "")).strip() or raw_text.strip()
    constraints = coerce_list(payload.get("constraints"), state.constraints)
    anchor_terms = payload.get("anchor_terms")
    if anchor_terms is None:
        anchor_terms = payload.get("core_concepts")
    global_vocab = coerce_vocab(anchor_terms, state.global_vocabulary[:10])
    local_vocab = coerce_vocab(anchor_terms, state.local_vocabulary[:6])
    term_map = coerce_term_map(payload.get("term_map"), state.term_map)
    loss_notes = coerce_list(payload.get("loss_risks"), state.loss_notes)
    return {
        "memory": memory,
        "constraints": constraints,
        "global_vocab": global_vocab[:10],
        "local_vocab": local_vocab[:6],
        "term_map": term_map,
        "loss_notes": loss_notes,
        "policy": dict(state.policy),
        "typed_representation": state.ensure_typed_representation().as_dict(),
        "parse_status": "json",
        "parse_error": None,
    }
