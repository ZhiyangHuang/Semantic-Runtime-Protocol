from __future__ import annotations

import hashlib
import math
import re
from functools import lru_cache
from typing import Iterable

import numpy as np

from .parsers import RELATION_TOKENS, STOPWORDS, tokenize


MODEL_NAMES = {
    "e5-small-v2": "intfloat/e5-small-v2",
    "bge-small-en-v1.5": "BAAI/bge-small-en-v1.5",
    "bge-base-en-v1.5": "BAAI/bge-base-en-v1.5",
    "all-MiniLM-L6-v2": "sentence-transformers/all-MiniLM-L6-v2",
}


def _normalize_text(text: str) -> str:
    return " ".join((text or "").split())


def _prefix_text(encoder_name: str, text: str, kind: str) -> str:
    if encoder_name == "e5-small-v2":
        if kind == "query":
            return f"query: {text}"
        return f"passage: {text}"
    return text


def _hash_vector(tokens: Iterable[str], dimension: int, salt: str) -> np.ndarray:
    vector = np.zeros(dimension, dtype=np.float32)
    for token in tokens:
        digest = hashlib.sha256(f"{salt}|{token}".encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "little") % dimension
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        weight = 1.0 + (digest[5] % 5) * 0.1
        vector[index] += sign * weight
    norm = float(np.linalg.norm(vector))
    if norm > 0:
        vector = vector / norm
    return vector


def _ngram_tokens(tokens: list[str], n: int) -> list[str]:
    if n <= 1:
        return tokens
    return ["_".join(tokens[index : index + n]) for index in range(max(0, len(tokens) - n + 1))]


def _char_ngrams(text: str, n: int) -> list[str]:
    compact = re.sub(r"\s+", "", text)
    if len(compact) < n:
        return [compact] if compact else []
    return [compact[index : index + n] for index in range(len(compact) - n + 1)]


def _fallback_profile(encoder_name: str) -> tuple[int, tuple[int, ...], bool, bool]:
    if encoder_name == "e5-small-v2":
        return 64, (1,), False, False
    if encoder_name == "bge-small-en-v1.5":
        return 72, (1, 2), False, False
    if encoder_name == "bge-base-en-v1.5":
        return 96, (1, 2), True, False
    if encoder_name == "all-MiniLM-L6-v2":
        return 48, (1,), False, True
    return 64, (1,), False, False


def _fallback_encode_text(encoder_name: str, text: str, kind: str) -> tuple[float, ...]:
    dimension, ngram_sizes, use_char_ngrams, remove_stopwords = _fallback_profile(encoder_name)
    normalized = _prefix_text(encoder_name, _normalize_text(text), kind)
    tokens = tokenize(normalized)
    if remove_stopwords:
        tokens = [token for token in tokens if token not in STOPWORDS]
    features: list[str] = list(tokens)
    for n in ngram_sizes:
        features.extend(_ngram_tokens(tokens, n))
    if use_char_ngrams:
        features.extend(_char_ngrams(normalized, 3))
    if encoder_name == "all-MiniLM-L6-v2":
        features.extend(token for token in tokens if token in RELATION_TOKENS)
    vector = _hash_vector(features, dimension, salt=f"{encoder_name}:{kind}")
    return tuple(float(value) for value in vector.tolist())


@lru_cache(maxsize=16)
def _load_sentence_transformer(model_name: str):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def _real_encode_text(encoder_name: str, text: str, kind: str) -> tuple[float, ...]:
    model_name = MODEL_NAMES[encoder_name]
    model = _load_sentence_transformer(model_name)
    encoded = model.encode(
        [_prefix_text(encoder_name, _normalize_text(text), kind)],
        normalize_embeddings=True,
        show_progress_bar=False,
    )[0]
    return tuple(float(value) for value in encoded.tolist())


def encode_text(encoder_name: str, text: str, kind: str = "passage") -> tuple[float, ...]:
    if encoder_name in MODEL_NAMES:
        try:
            return _real_encode_text(encoder_name, text, kind)
        except Exception:
            return _fallback_encode_text(encoder_name, text, kind)
    return _fallback_encode_text(encoder_name, text, kind)


def cosine_similarity(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if not left or not right:
        return 0.0
    left_vec = np.array(left, dtype=np.float32)
    right_vec = np.array(right, dtype=np.float32)
    left_norm = float(np.linalg.norm(left_vec))
    right_norm = float(np.linalg.norm(right_vec))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return float(np.dot(left_vec, right_vec) / (left_norm * right_norm))
