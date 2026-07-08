import re
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .chunking import chunk_memory
from .encoder import build_encoder, cosine_similarity


def _normalize_text(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


def keyword_overlap_score(chunk: str, keywords: Iterable[str]) -> float:
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


def saliency_boost(chunk: str) -> float:
    score = 0.0
    lowered = chunk.lower()
    if re.search(r"\b\d{1,2}/\d{4}\b", lowered) or re.search(
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}\b", lowered
    ):
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


def rule_chunk_saliency(
    chunk: str,
    constraints: Sequence[str],
    expected_keywords: Sequence[str] | None = None,
) -> float:
    score = 0.1
    score += 0.45 * keyword_overlap_score(chunk, constraints)
    score += 0.25 * keyword_overlap_score(chunk, expected_keywords or [])
    score += saliency_boost(chunk)
    return max(0.0, min(1.0, score))


def saliency_factors(
    chunk: str,
    constraints: Sequence[str],
    expected_keywords: Sequence[str] | None = None,
    embedding_score: Optional[float] = None,
    object_support_score: Optional[float] = None,
    object_support_count: Optional[int] = None,
) -> Dict[str, object]:
    constraint_overlap = round(keyword_overlap_score(chunk, constraints), 4)
    keyword_overlap = round(keyword_overlap_score(chunk, expected_keywords or []), 4)
    boost = round(saliency_boost(chunk), 4)
    support_bonus = round(min(0.25, max(0.0, object_support_score or 0.0)), 4)
    score = 0.1 + 0.45 * constraint_overlap + 0.25 * keyword_overlap + boost + support_bonus
    return {
        "schema_version": "saliency_factors.v1",
        "scores": {
            "constraint_overlap": constraint_overlap,
            "expected_keyword_overlap": keyword_overlap,
            "rule_boost": boost,
            "object_support_score": support_bonus if object_support_score is not None else None,
            "object_support_count": object_support_count,
            "embedding_score": round(embedding_score, 4) if embedding_score is not None else None,
            "rule_score": round(max(0.0, min(1.0, score)), 4),
        },
        "signals": {
            "constraint_count": len([item for item in constraints if str(item).strip()]),
            "expected_keyword_count": len([item for item in (expected_keywords or []) if str(item).strip()]),
        },
        "flags": {
            "has_date_or_month": bool(
                re.search(r"\b\d{1,2}/\d{4}\b", chunk.lower())
                or re.search(
                    r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}\b", chunk.lower()
                )
            ),
            "has_acronym": bool(re.search(r"\b[A-Z]{2,}\b", chunk)),
            "has_digit": bool(re.search(r"\b\d+\b", chunk)),
            "has_constraint_language": any(
                marker in chunk.lower()
                for marker in ("constraint", "must", "preserve", "require", "important", "critical")
            ),
            "capitalized_start": chunk[:1].isupper(),
        },
    }


def rank_memory_chunks(
    memory: str,
    constraints: Sequence[str],
    expected_keywords: Sequence[str] | None = None,
    encoder=None,
    top_k: int = 4,
    semantic_object_inventory: Optional[Dict[str, object]] = None,
) -> Tuple[List[Dict[str, object]], str]:
    chunks = chunk_memory(memory)
    ranked: List[Dict[str, object]] = []
    encoder = encoder or build_encoder()
    query_text = " ".join(list(constraints) + list(expected_keywords or []))
    query_vector = encoder.encode_query(query_text) if encoder is not None and query_text.strip() else None
    important_objects = []
    if semantic_object_inventory:
        important_objects = list(semantic_object_inventory.get("important_objects", []))
    for chunk_id, chunk in enumerate(chunks, start=1):
        rule_score = rule_chunk_saliency(chunk, constraints, expected_keywords)
        embedding_score = None
        if encoder is not None and query_vector is not None:
            passage_vector = encoder.encode_passage(chunk)
            embedding_score = cosine_similarity(query_vector, passage_vector)
        object_support_count = 0
        object_support_score = 0.0
        lowered_chunk = chunk.lower()
        if important_objects:
            for obj in important_objects:
                value = str(obj.get("value", "")).strip().lower()
                object_type = str(obj.get("type", "")).strip().lower()
                confidence = float(obj.get("confidence", 0.0) or 0.0)
                if not value:
                    continue
                value_tokens = [token for token in re.split(r"[^a-z0-9]+", value) if token]
                matched = False
                if value in lowered_chunk:
                    matched = True
                elif value_tokens and sum(1 for token in value_tokens if token in lowered_chunk) >= max(1, len(value_tokens) // 2):
                    matched = True
                elif object_type in {"question", "constraint", "anchor"} and any(token in lowered_chunk for token in value_tokens[:3]):
                    matched = True
                if matched:
                    object_support_count += 1
                    object_support_score += min(0.15, 0.05 + confidence * 0.1)
        score = rule_score
        method = "rule"
        if embedding_score is not None:
            score = max(rule_score, embedding_score * 0.9)
            method = "hybrid" if embedding_score >= 0.2 else "embedding"
        if object_support_count > 0:
            score = min(1.0, score + min(0.25, object_support_score))
        reason_parts = [f"rule={rule_score:.3f}"]
        if embedding_score is not None:
            reason_parts.append(f"embedding={embedding_score:.3f}")
        if object_support_count > 0:
            reason_parts.append(f"objects={object_support_count}")
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
                "saliency_factors": saliency_factors(
                    chunk,
                    constraints,
                    expected_keywords,
                    embedding_score,
                    object_support_score=object_support_score if object_support_count > 0 else None,
                    object_support_count=object_support_count if object_support_count > 0 else 0,
                ),
            }
        )
    ranked.sort(key=lambda item: (-float(item["score"]), int(item["chunk_id"])))
    selected = ranked[: max(1, min(top_k, len(ranked)))]
    return selected, "\n".join(item["text"] for item in selected)
