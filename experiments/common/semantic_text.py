from __future__ import annotations

import hashlib
import math
import os
import re
from dataclasses import dataclass
from typing import List, Optional, Sequence


def _normalize_text(text: str) -> str:
    lowered = str(text).strip().lower()
    lowered = re.sub(r"[\u2018\u2019]", "'", lowered)
    lowered = re.sub(r"[\u201c\u201d]", '"', lowered)
    lowered = re.sub(r"[^\w\s/.-]+", " ", lowered)
    lowered = " ".join(lowered.split())
    return lowered


def _tokenize(text: str) -> List[str]:
    return [token for token in re.split(r"[^a-z0-9]+", _normalize_text(text)) if token]


def canonicalize_semantic_value(value: str) -> str:
    normalized = _normalize_text(value)
    if not normalized:
        return ""
    _ABBREVIATIONS = {
        "nyc": "new york city",
        "prof.": "professor",
        "prof": "professor",
        "cs": "computer science",
    }
    _MONTHS = {
        "jan": "1",
        "january": "1",
        "feb": "2",
        "february": "2",
        "mar": "3",
        "march": "3",
        "apr": "4",
        "april": "4",
        "may": "5",
        "jun": "6",
        "june": "6",
        "jul": "7",
        "july": "7",
        "aug": "8",
        "august": "8",
        "sep": "9",
        "sept": "9",
        "september": "9",
        "oct": "10",
        "october": "10",
        "nov": "11",
        "november": "11",
        "dec": "12",
        "december": "12",
    }
    if normalized in _ABBREVIATIONS:
        return _ABBREVIATIONS[normalized]
    month_year = re.fullmatch(r"([a-z]+)\s+(\d{4})", normalized)
    if month_year and month_year.group(1) in _MONTHS:
        return f"{_MONTHS[month_year.group(1)]}/{month_year.group(2)}"
    normalized = re.sub(r"\b(\d{1,2})/(\d{4})\b", lambda m: f"{int(m.group(1))}/{m.group(2)}", normalized)
    normalized = re.sub(r"\b(0?\d)/(20\d{2})\b", lambda m: f"{int(m.group(1))}/{m.group(2)}", normalized)
    return normalized


def stable_semantic_object_id(object_type: str, value: str) -> str:
    canonical = canonicalize_semantic_value(value)
    digest = hashlib.sha1(f"{object_type}:{canonical}".encode("utf-8")).hexdigest()[:8]
    return f"{object_type}:{digest}"


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return max(0.0, min(1.0, dot / (norm_a * norm_b)))


def _l2_normalize(vector: Sequence[float]) -> List[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0.0:
        return [0.0 for _ in vector]
    return [value / norm for value in vector]


@dataclass
class SemanticStateEncoder:
    name: str = "base"
    dimension: Optional[int] = None

    def encode_passage(self, text: str) -> List[float]:
        raise NotImplementedError

    def encode_query(self, text: str) -> List[float]:
        raise NotImplementedError


class HashingSemanticEncoder(SemanticStateEncoder):
    def __init__(self) -> None:
        super().__init__(name="hashing", dimension=256)

    def _encode(self, text: str) -> List[float]:
        vector = [0.0] * self.dimension
        tokens = _tokenize(text)
        if not tokens:
            return vector
        for token in tokens:
            digest = hashlib.sha1(token.encode("utf-8")).hexdigest()
            bucket = int(digest[:8], 16) % self.dimension
            sign = -1.0 if int(digest[8:9], 16) % 2 else 1.0
            vector[bucket] += sign
        return _l2_normalize(vector)

    def encode_passage(self, text: str) -> List[float]:
        return self._encode(text)

    def encode_query(self, text: str) -> List[float]:
        return self._encode(text)


class E5SmallEncoder(SemanticStateEncoder):
    def __init__(self, model_name: str = "intfloat/e5-small-v2") -> None:
        super().__init__(name="e5-small-v2", dimension=384)
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("sentence-transformers is required for SRP_ENCODER=e5-small-v2") from exc
        self.model_name = model_name
        self._model = SentenceTransformer(model_name)

    def encode_passage(self, text: str) -> List[float]:
        vector = self._model.encode([f"passage: {text}"], normalize_embeddings=True)[0]
        return list(vector)

    def encode_query(self, text: str) -> List[float]:
        vector = self._model.encode([f"query: {text}"], normalize_embeddings=True)[0]
        return list(vector)


def build_encoder(kind: str | None = None) -> SemanticStateEncoder | None:
    selected = (kind or os.getenv("SRP_ENCODER", "none")).strip().lower()
    if selected in {"", "none"}:
        return None
    if selected == "hashing":
        return HashingSemanticEncoder()
    if selected in {"e5", "e5-small-v2", "intfloat/e5-small-v2"}:
        model_name = os.getenv("SRP_ENCODER_MODEL", "intfloat/e5-small-v2").strip() or "intfloat/e5-small-v2"
        return E5SmallEncoder(model_name=model_name)
    raise ValueError(f"Unknown SRP encoder kind: {selected}")
