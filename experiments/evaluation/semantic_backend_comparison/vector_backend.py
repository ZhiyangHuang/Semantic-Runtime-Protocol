from __future__ import annotations

from dataclasses import dataclass
import time

from experiments.common.semantic_text import HashingSemanticEncoder, cosine_similarity

from .backend import BackendOutcome, ComparisonCase


@dataclass
class VectorOnlyEvaluationBackend:
    threshold: float = 0.5
    backend_name: str = "vector"

    def __post_init__(self) -> None:
        self._encoder = HashingSemanticEncoder()

    def evaluate(self, case: ComparisonCase) -> BackendOutcome:
        started = time.perf_counter()
        source_vec = self._encoder.encode_query(case.source_text)
        candidate_vec = self._encoder.encode_passage(case.candidate_text)
        score = cosine_similarity(source_vec, candidate_vec)
        decision = "accept" if score >= self.threshold else "reject"
        return BackendOutcome(
            backend_name=self.backend_name,
            mode="vector_only",
            decision=decision,
            score=round(score, 6),
            latency_seconds=round(time.perf_counter() - started, 6),
            reason=f"similarity={score:.3f} threshold={self.threshold:.3f}",
        )
