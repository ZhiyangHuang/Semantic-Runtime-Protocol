from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from typing import Sequence


def _normalize_text(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


def _tokenize(text: str) -> list[str]:
    return [token for token in re.split(r"[^a-z0-9]+", _normalize_text(text)) if token]


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return max(0.0, min(1.0, dot / (norm_a * norm_b)))


def _l2_normalize(vector: Sequence[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0.0:
        return [0.0 for _ in vector]
    return [value / norm for value in vector]


@dataclass
class HashingSemanticEncoder:
    name: str = "hashing"
    dimension: int = 256

    def _encode(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        for token in _tokenize(text):
            digest = hashlib.sha1(token.encode("utf-8")).hexdigest()
            bucket = int(digest[:8], 16) % self.dimension
            sign = -1.0 if int(digest[8:9], 16) % 2 else 1.0
            vector[bucket] += sign
        return _l2_normalize(vector)

    def encode_passage(self, text: str) -> list[float]:
        return self._encode(text)

    def encode_query(self, text: str) -> list[float]:
        return self._encode(text)
