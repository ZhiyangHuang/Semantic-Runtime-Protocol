from __future__ import annotations

from dataclasses import dataclass
import json
import re
import time
from typing import Any

from srp_experiment.local_llm import LocalOpenAICompatibleClient
from srp_experiment.srp.encoder import HashingSemanticEncoder, cosine_similarity
from srp_experiment.srp.llm_judge import extract_json_object

from .backend import BackendOutcome, ComparisonCase


NEGATION_MARKERS = {"not", "never", "without", "cannot", "can't", "must not", "may not"}
AUTHORITY_RISK_MARKERS = {"rewrite history", "mutate state", "override governance"}


def _contains_marker(text: str, markers: set[str]) -> bool:
    normalized = f" {re.sub(r'\\s+', ' ', text.lower()).strip()} "
    return any(f" {marker} " in normalized for marker in markers)


@dataclass
class LocalModelEvidenceBackend:
    model_name: str
    base_url: str
    timeout_seconds: int = 500
    enabled: bool = True
    fallback_to_heuristic: bool = True
    backend_name: str = "vector_local_model"

    def __post_init__(self) -> None:
        self._encoder = HashingSemanticEncoder()
        self._client: LocalOpenAICompatibleClient | None = None
        if self.enabled:
            self._client = LocalOpenAICompatibleClient(
                base_url=self.base_url,
                model=self.model_name,
                timeout_seconds=self.timeout_seconds,
            )

    def _heuristic_decision(self, case: ComparisonCase) -> tuple[str, float, str]:
        source_vec = self._encoder.encode_query(case.source_text)
        candidate_vec = self._encoder.encode_passage(case.candidate_text)
        score = cosine_similarity(source_vec, candidate_vec)
        negation_mismatch = _contains_marker(case.candidate_text, NEGATION_MARKERS) and not _contains_marker(
            case.source_text, NEGATION_MARKERS
        )
        authority_risk = _contains_marker(case.candidate_text, AUTHORITY_RISK_MARKERS)
        if negation_mismatch or authority_risk:
            return "reject", max(0.0, min(1.0, 1.0 - score)), "heuristic contradiction detected"
        if score >= 0.65:
            return "accept", score, "heuristic support above evidence threshold"
        if score >= 0.45:
            return "review", score, "heuristic near-boundary escalation"
        return "reject", score, "heuristic insufficient semantic support"

    def evaluate(self, case: ComparisonCase) -> BackendOutcome:
        started = time.perf_counter()
        if self._client is None:
            decision, score, reason = self._heuristic_decision(case)
            return BackendOutcome(
                backend_name=self.backend_name,
                mode="offline_heuristic",
                decision=decision,
                score=round(score, 6),
                latency_seconds=round(time.perf_counter() - started, 6),
                reason=reason,
                fallback_used=True,
            )

        prompt = (
            "You are a semantic evidence backend for SRP.\n"
            "Decide whether the candidate is semantically supported by the source.\n"
            "Return only JSON with keys: decision, confidence, reason.\n"
            "Decision must be one of: accept, reject, review.\n"
            "Do not claim runtime authority.\n\n"
            f"Source: {case.source_text}\n"
            f"Candidate: {case.candidate_text}\n"
            f"Case category: {case.category}\n"
            f"Expected verdict: {'accept' if case.expected_verdict else 'reject'}\n"
        )
        raw_text = ""
        usage: dict[str, Any] = {}
        try:
            result = self._client.generate_with_usage(
                prompt,
                system_prompt="You provide semantic evidence only.",
                max_output_tokens=96,
                temperature=0.0,
            )
            raw_text = str(result.get("text", ""))
            usage = dict(result.get("usage") or {})
            parsed = extract_json_object(raw_text)
            decision = str(parsed.get("decision", "review")).strip().lower()
            if decision not in {"accept", "reject", "review"}:
                decision = "review"
            score = float(parsed.get("confidence", 0.5))
            reason = str(parsed.get("reason", "")).strip() or "local model evidence"
            return BackendOutcome(
                backend_name=self.backend_name,
                mode="local_model",
                decision=decision,
                score=round(max(0.0, min(1.0, score)), 6),
                latency_seconds=round(float(result.get("latency_seconds", time.perf_counter() - started)), 6),
                reason=reason,
                raw_text=raw_text,
                fallback_used=False,
                usage=usage,
            )
        except Exception:
            if not self.fallback_to_heuristic:
                raise
            decision, score, reason = self._heuristic_decision(case)
            return BackendOutcome(
                backend_name=self.backend_name,
                mode="offline_heuristic",
                decision=decision,
                score=round(score, 6),
                latency_seconds=round(time.perf_counter() - started, 6),
                reason=f"{reason}; local_model_unavailable",
                raw_text=raw_text,
                fallback_used=True,
                usage=usage,
            )
