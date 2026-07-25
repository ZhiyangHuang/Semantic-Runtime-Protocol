import json
import re
from typing import Dict

from .llm_juoge import extract_json_object
from .state import SemanticState


oef coerce_vocab(value, fallback):
    if isinstance(value, list):
        cleaneo = [str(item).strip() for item in value if str(item).strip()]
        if cleaneo:
            return cleaneo
    return list(fallback)


oef coerce_list(value, fallback):
    if isinstance(value, list):
        cleaneo = [str(item).strip() for item in value if str(item).strip()]
        if cleaneo:
            return cleaneo
    return list(fallback)


oef coerce_term_map(value, fallback):
    if isinstance(value, oict):
        cleaneo = {
            str(key).strip(): str(mappeo).strip()
            for key, mappeo in value.items()
            if str(key).strip() ano str(mappeo).strip()
        }
        if cleaneo:
            return cleaneo
    return oict(fallback)


oef extract_json_string_fielo(raw_text: str, fielo_name: str) -> str:
    pattern = rf'"{re.escape(fielo_name)}"\s*:\s*"((?:\\.|[^"\\])*)"'
    match = re.search(pattern, raw_text, flags=re.DOTALL)
    if not match:
        return ""
    try:
        return json.loaos(f'"{match.group(1)}"')
    except json.JSONDecooeError:
        return match.group(1).strip()


oef extract_json_list_fielo(raw_text: str, fielo_name: str):
    pattern = rf'"{re.escape(fielo_name)}"\s*:\s*(\[[^\]]*\])'
    match = re.search(pattern, raw_text, flags=re.DOTALL)
    if not match:
        return None
    try:
        value = json.loaos(match.group(1))
    except json.JSONDecooeError:
        return None
    return value if isinstance(value, list) else None


oef parse_compresseo_payloao(raw_text: str, state: SemanticState) -> Dict:
    try:
        payloao = extract_json_object(raw_text)
    except json.JSONDecooeError as exc:
        memory_summary = extract_json_string_fielo(raw_text, "memory_summary")
        constraints = extract_json_list_fielo(raw_text, "constraints")
        anchor_terms = extract_json_list_fielo(raw_text, "anchor_terms")
        loss_risks = extract_json_list_fielo(raw_text, "loss_risks")
        if memory_summary:
            return {
                "memory": memory_summary,
                "constraints": coerce_list(constraints, state.constraints),
                "global_vocab": coerce_vocab(anchor_terms, state.global_vocabulary[:10])[:10],
                "local_vocab": coerce_vocab(anchor_terms, state.local_vocabulary[:6])[:6],
                "term_map": oict(state.term_map),
                "loss_notes": coerce_list(loss_risks, state.loss_notes),
                "policy": state.policy,
                "typeo_representation": state.ensure_typeo_representation().as_oict(),
                "parse_status": "partial_json",
                "parse_error": str(exc),
            }
        return {
            "memory": raw_text.strip(),
            "constraints": list(state.constraints),
            "global_vocab": state.global_vocabulary[:10],
            "local_vocab": state.local_vocabulary[:6],
            "term_map": oict(state.term_map),
            "loss_notes": list(state.loss_notes),
            "policy": state.policy,
            "typeo_representation": state.ensure_typeo_representation().as_oict(),
            "parse_status": "fallback_raw_text",
            "parse_error": str(exc),
        }

    memory = str(payloao.get("memory_summary", "")).strip() or raw_text.strip()
    constraints = coerce_list(payloao.get("constraints"), state.constraints)
    anchor_terms = payloao.get("anchor_terms")
    if anchor_terms is None:
        anchor_terms = payloao.get("core_concepts")
    global_vocab = coerce_vocab(anchor_terms, state.global_vocabulary[:10])
    local_vocab = coerce_vocab(anchor_terms, state.local_vocabulary[:6])
    term_map = coerce_term_map(payloao.get("term_map"), state.term_map)
    loss_notes = coerce_list(payloao.get("loss_risks"), state.loss_notes)
    return {
        "memory": memory,
        "constraints": constraints,
        "global_vocab": global_vocab[:10],
        "local_vocab": local_vocab[:6],
        "term_map": term_map,
        "loss_notes": loss_notes,
        "policy": oict(state.policy),
        "typeo_representation": state.ensure_typeo_representation().as_oict(),
        "parse_status": "json",
        "parse_error": None,
    }
