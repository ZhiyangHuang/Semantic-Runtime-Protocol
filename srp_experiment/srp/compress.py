import json
import os
import re
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from ..budgeting import available_memory_budget, clip_tail_to_budget, get_budget_config
from .encoder import build_encoder, cosine_similarity
from ..prompting import build_compression_prompt
from .state import SemanticState


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


def _normalize_text(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


def chunk_memory(memory: str, max_words: int = 80) -> List[str]:
    text = str(memory).strip()
    if not text:
        return []
    sentence_chunks = [chunk.strip() for chunk in re.split(r"(?<=[.!?])\s+", text) if chunk.strip()]
    chunks: List[str] = []
    for sentence in sentence_chunks or [text]:
        words = sentence.split()
        if len(words) <= max_words:
            chunks.append(sentence)
            continue
        for start in range(0, len(words), max_words):
            part = " ".join(words[start : start + max_words]).strip()
            if part:
                chunks.append(part)
    return [(f"{idx + 1}:{chunk}") for idx, chunk in enumerate(chunks)]


def _keyword_overlap_score(chunk: str, keywords: Iterable[str]) -> float:
    chunk_tokens = set(re.split(r"[^a-z0-9]+", _normalize_text(chunk)))
    chunk_tokens.discard("")
    key_tokens = set()
    for keyword in keywords:
        for token in re.split(r"[^a-z0-9]+", _normalize_text(keyword)):
            if token:
                key_tokens.add(token)
    if not chunk_tokens or not key_tokens:
        return 0.0
    overlap = len(chunk_tokens & key_tokens)
    return overlap / max(1, len(key_tokens))


def _saliency_boost(chunk: str) -> float:
    score = 0.0
    lowered = chunk.lower()
    if re.search(r"\b\d{1,2}/\d{4}\b", lowered) or re.search(r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}\b", lowered):
        score += 0.25
    if re.search(r"\b[A-Z]{2,}\b", chunk):
        score += 0.15
    if re.search(r"\b\d+\b", chunk):
        score += 0.15
    if any(marker in lowered for marker in ("constraint", "must", "preserve", "require", "important", "critical")):
        score += 0.2
    if chunk[:1].isupper():
        score += 0.05
    return min(1.0, score)


def _rule_chunk_saliency(
    chunk: str,
    constraints: Sequence[str],
    expected_keywords: Sequence[str] | None = None,
) -> float:
    score = 0.1
    score += 0.45 * _keyword_overlap_score(chunk, constraints)
    score += 0.25 * _keyword_overlap_score(chunk, expected_keywords or [])
    score += _saliency_boost(chunk)
    return max(0.0, min(1.0, score))


def _saliency_factors(
    chunk: str,
    constraints: Sequence[str],
    expected_keywords: Sequence[str] | None = None,
    embedding_score: Optional[float] = None,
) -> Dict[str, object]:
    constraint_overlap = round(_keyword_overlap_score(chunk, constraints), 4)
    keyword_overlap = round(_keyword_overlap_score(chunk, expected_keywords or []), 4)
    boost = round(_saliency_boost(chunk), 4)
    score = 0.1 + 0.45 * constraint_overlap + 0.25 * keyword_overlap + boost
    flags = {
        "has_date_or_month": bool(
            re.search(r"\b\d{1,2}/\d{4}\b", chunk.lower())
            or re.search(r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}\b", chunk.lower())
        ),
        "has_acronym": bool(re.search(r"\b[A-Z]{2,}\b", chunk)),
        "has_digit": bool(re.search(r"\b\d+\b", chunk)),
        "has_constraint_language": any(marker in chunk.lower() for marker in ("constraint", "must", "preserve", "require", "important", "critical")),
        "capitalized_start": chunk[:1].isupper(),
    }
    factors = {
        "schema_version": "saliency_factors.v1",
        "scores": {
            "constraint_overlap": constraint_overlap,
            "expected_keyword_overlap": keyword_overlap,
            "rule_boost": boost,
            "embedding_score": round(embedding_score, 4) if embedding_score is not None else None,
            "rule_score": round(max(0.0, min(1.0, score)), 4),
        },
        "signals": {
            "constraint_count": len([item for item in constraints if str(item).strip()]),
            "expected_keyword_count": len([item for item in (expected_keywords or []) if str(item).strip()]),
        },
        "flags": flags,
    }
    return factors


def _rank_memory_chunks(
    memory: str,
    constraints: Sequence[str],
    expected_keywords: Sequence[str] | None = None,
    encoder=None,
    top_k: int = 4,
) -> Tuple[List[Dict[str, object]], str]:
    chunks = chunk_memory(memory)
    ranked: List[Dict[str, object]] = []
    encoder = encoder or build_encoder()
    query_text = " ".join(list(constraints) + list(expected_keywords or []))
    query_vector = encoder.encode_query(query_text) if encoder is not None and query_text.strip() else None
    for chunk_id, chunk in enumerate(chunks, start=1):
        rule_score = _rule_chunk_saliency(chunk, constraints, expected_keywords)
        embedding_score = None
        if encoder is not None and query_vector is not None:
            passage_vector = encoder.encode_passage(chunk)
            embedding_score = cosine_similarity(query_vector, passage_vector)
        score = rule_score
        method = "rule"
        if embedding_score is not None:
            score = max(rule_score, embedding_score * 0.9)
            method = "hybrid" if embedding_score >= 0.2 else "embedding"
        saliency_factors = _saliency_factors(chunk, constraints, expected_keywords, embedding_score=embedding_score)
        reason_parts = [f"rule={rule_score:.3f}"]
        if embedding_score is not None:
            reason_parts.append(f"embedding={embedding_score:.3f}")
        if score >= 0.7:
            reason_parts.append("high_saliency")
        elif score >= 0.4:
            reason_parts.append("moderate_saliency")
        else:
            reason_parts.append("low_saliency")
        ranked.append(
            {
                "chunk_id": chunk_id,
                "text": chunk,
                "rule_score": round(rule_score, 4),
                "embedding_score": round(embedding_score, 4) if embedding_score is not None else None,
                "score": round(score, 4),
                "method": method,
                "reason": "; ".join(reason_parts),
                "saliency_factors": saliency_factors,
            }
        )
    ranked.sort(key=lambda item: (-float(item["score"]), int(item["chunk_id"])))
    selected = ranked[: max(1, min(top_k, len(ranked)))]
    selected_text = "\n".join(item["text"] for item in selected)
    return selected, selected_text


def _llm_chunk_judge_enabled() -> bool:
    return str(os.getenv("SRP_USE_LLM_JUDGE", "false")).strip().lower() in {"1", "true", "yes", "on"}


def _apply_llm_chunk_judge(
    selected_chunks: List[Dict[str, object]],
    constraints: Sequence[str],
    expected_keywords: Sequence[str] | None = None,
    client=None,
) -> Tuple[List[Dict[str, object]], Dict[str, object]]:
    judge_calls = 0
    judge_failures = 0
    if not _llm_chunk_judge_enabled() or client is None:
        return selected_chunks, {
            "enabled": False,
            "judge_calls": judge_calls,
            "judge_failures": judge_failures,
        }

    adjusted: List[Dict[str, object]] = []
    for chunk in selected_chunks:
        judge_calls += 1
        try:
            prompt = (
                "Given task constraints and a memory chunk, score whether this chunk is answer-critical from 0 to 1.\n"
                "Return only JSON: {\"score\": 0.0, \"reason\": \"...\"}\n\n"
                f"Constraints: {'; '.join(constraints)}\n"
                f"Expected keywords: {'; '.join(expected_keywords or [])}\n"
                f"Chunk: {chunk['text']}"
            )
            if hasattr(client, "generate_with_usage"):
                result = client.generate_with_usage(prompt, system_prompt="You score chunk saliency.", max_output_tokens=64)
                raw_text = result.get("text", "")
            else:
                raw_text = client.generate(prompt)
            parsed = _extract_json_object(raw_text)
            bonus = float(parsed.get("score", 0.0))
            reason = str(parsed.get("reason", "")).strip()
            chunk = dict(chunk)
            chunk["llm_judge_score"] = max(0.0, min(1.0, bonus))
            chunk["llm_judge_reason"] = reason
            chunk["score"] = round(min(1.0, float(chunk["score"]) + 0.2 * chunk["llm_judge_score"]), 4)
            chunk["reason"] = f"{chunk['reason']}; llm={chunk['llm_judge_score']:.3f}" if reason else f"{chunk['reason']}; llm={chunk['llm_judge_score']:.3f}"
            adjusted.append(chunk)
        except Exception:
            judge_failures += 1
            adjusted.append(chunk)
    adjusted.sort(key=lambda item: (-float(item["score"]), int(item["chunk_id"])))
    return adjusted, {
        "enabled": True,
        "judge_calls": judge_calls,
        "judge_failures": judge_failures,
    }


def _extract_json_object(raw_text: str):
    cleaned = str(raw_text).strip()
    if not cleaned:
        raise json.JSONDecodeError("empty response", cleaned, 0)

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    if start < 0:
        raise json.JSONDecodeError("no JSON object found", cleaned, 0)

    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(cleaned)):
        char = cleaned[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return json.loads(cleaned[start : index + 1])

    raise json.JSONDecodeError("unterminated JSON object", cleaned, start)


def _extract_json_string_field(raw_text: str, field_name: str) -> str:
    pattern = rf'"{re.escape(field_name)}"\s*:\s*"((?:\\.|[^"\\])*)"'
    match = re.search(pattern, raw_text, flags=re.DOTALL)
    if not match:
        return ""
    try:
        return json.loads(f'"{match.group(1)}"')
    except json.JSONDecodeError:
        return match.group(1).strip()


def _extract_json_list_field(raw_text: str, field_name: str):
    pattern = rf'"{re.escape(field_name)}"\s*:\s*(\[[^\]]*\])'
    match = re.search(pattern, raw_text, flags=re.DOTALL)
    if not match:
        return None
    try:
        value = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, list) else None


def _parse_compressed_payload(raw_text: str, state: SemanticState) -> Dict:
    try:
        payload = _extract_json_object(raw_text)
    except json.JSONDecodeError as exc:
        memory_summary = _extract_json_string_field(raw_text, "memory_summary")
        constraints = _extract_json_list_field(raw_text, "constraints")
        anchor_terms = _extract_json_list_field(raw_text, "anchor_terms")
        loss_risks = _extract_json_list_field(raw_text, "loss_risks")
        if memory_summary:
            return {
                "memory": memory_summary,
                "constraints": _coerce_list(constraints, state.constraints),
                "global_vocab": _coerce_vocab(anchor_terms, state.global_vocabulary[:10])[:10],
                "local_vocab": _coerce_vocab(anchor_terms, state.local_vocabulary[:6])[:6],
                "term_map": dict(state.term_map),
                "loss_notes": _coerce_list(loss_risks, state.loss_notes),
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
        "parse_status": "json",
        "parse_error": None,
    }


def compress_state(state: SemanticState, client=None) -> Dict:
    expected_keywords = state.global_vocabulary or state.local_vocabulary
    selected_chunks, selected_memory = _rank_memory_chunks(
        state.memory,
        state.constraints,
        expected_keywords=expected_keywords,
        top_k=int(os.getenv("SRP_RAG_TOP_K", "4")),
    )
    selected_chunks, llm_judge_summary = _apply_llm_chunk_judge(
        selected_chunks,
        state.constraints,
        expected_keywords=expected_keywords,
        client=client,
    )
    selected_memory = "\n".join(item["text"] for item in selected_chunks)
    if client is None:
        compressed_memory = selected_memory or clip_tail_to_budget(state.memory, 18)
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
    else:
        budget = get_budget_config()
        memory_view = selected_memory or clip_tail_to_budget(state.memory, available_memory_budget(constraints=state.constraints))
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
        parsed["raw_model_text"] = model_result.get("raw_text", compressed_memory)
        parsed["stripped_thinking"] = model_result.get("stripped_thinking")
        parsed["runtime_summary"] = state.runtime_summary()
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
