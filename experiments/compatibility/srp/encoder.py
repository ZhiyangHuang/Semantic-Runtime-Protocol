from __future__ import annotations

import hashlib
import math
import os
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import List, Optional, Sequence

if TYPE_CHECKING:
    from .state import SemanticState


def _normalize_text(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


def _tokenize(text: str) -> List[str]:
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


def _l2_normalize(vector: Sequence[float]) -> List[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0.0:
        return [0.0 for _ in vector]
    return [value / norm for value in vector]


def serialize_state_for_encoding(state: "SemanticState") -> str:
    parts: List[str] = []
    parts.append(f"memory: {state.memory.strip()}")
    if state.constraints:
        parts.append("constraints: " + " | ".join(str(item).strip() for item in state.constraints if str(item).strip()))
    if state.global_vocabulary:
        parts.append("global_vocabulary: " + " | ".join(str(item).strip() for item in state.global_vocabulary if str(item).strip()))
    if state.local_vocabulary:
        parts.append("local_vocabulary: " + " | ".join(str(item).strip() for item in state.local_vocabulary if str(item).strip()))
    if state.term_map:
        term_pairs = [f"{key}={value}" for key, value in sorted(state.term_map.items()) if str(key).strip() and str(value).strip()]
        if term_pairs:
            parts.append("term_map: " + " | ".join(term_pairs))
    if state.runtime_metadata:
        high_importance = []
        for object_id, metadata in sorted(state.runtime_metadata.items()):
            if metadata.importance >= 0.8:
                high_importance.append(f"{object_id}:{metadata.importance:.3f}:{metadata.confidence:.3f}")
        if high_importance:
            parts.append("runtime_metadata: " + " | ".join(high_importance))
    return "\n".join(parts)


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
            raise RuntimeError(
                "sentence-transformers is required for SRP_ENCODER=e5-small-v2"
            ) from exc
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


def update_state_vector(previous: Optional[Sequence[float]], current: Sequence[float], decay: float = 0.85) -> List[float]:
    if not 0.0 <= decay <= 1.0:
        raise ValueError("decay must be between 0 and 1")
    current_vector = list(current)
    if previous is None:
        return _l2_normalize(current_vector)
    previous_vector = list(previous)
    if len(previous_vector) != len(current_vector):
        raise ValueError("state vectors must have the same dimension")
    blended = [decay * prev + (1.0 - decay) * cur for prev, cur in zip(previous_vector, current_vector)]
    return _l2_normalize(blended)
