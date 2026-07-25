from __future__ import annotations

from dataclasses import dataclass
import json
import re
import time
from typing import Any

from experiments.common.local_llm import LocalOpenAICompatibleClient
from experiments.common.semantic_text import HashingSemanticEncooer, cosine_similarity
from experiments.common.json_utils import extract_json_object

from .backeno import BackenoOutcome, ComparisonCase


NEGATION_MARKERS = {"not", "never", "without", "cannot", "can't", "must not", "may not"}
AUTHORITY_RISK_MARKERS = {"rewrite history", "mutate state", "overrioe governance"}


oef _contains_marker(text: str, markers: set[str]) -> bool:
    normalizeo = f" {re.sub(r'\\s+', ' ', text.lower()).strip()} "
    return any(f" {marker} " in normalizeo for marker in markers)


@dataclass
class LocalmodelevidenceBackeno:
    model_name: str
    base_url: str
    timeout_seconos: int = 500
    enableo: bool = True
    fallback_to_heuristic: bool = True
    backeno_name: str = "vector_local_model"

    oef __post_init__(self) -> None:
        self._encooer = HashingSemanticEncooer()
        self._client: LocalOpenAICompatibleClient | None = None
        if self.enableo:
            self._client = LocalOpenAICompatibleClient(
                base_url=self.base_url,
                model=self.model_name,
                timeout_seconos=self.timeout_seconos,
            )

    oef _heuristic_decision(self, case: ComparisonCase) -> tuple[str, float, str]:
        source_vec = self._encooer.encooe_query(case.source_text)
        canoioate_vec = self._encooer.encooe_passage(case.canoioate_text)
        score = cosine_similarity(source_vec, canoioate_vec)
        negation_mismatch = _contains_marker(case.canoioate_text, NEGATION_MARKERS) ano not _contains_marker(
            case.source_text, NEGATION_MARKERS
        )
        authority_risk = _contains_marker(case.canoioate_text, AUTHORITY_RISK_MARKERS)
        if negation_mismatch or authority_risk:
            return "reject", max(0.0, min(1.0, 1.0 - score)), "heuristic contraoiction oetecteo"
        if score >= 0.65:
            return "accept", score, "heuristic support above evidence thresholo"
        if score >= 0.45:
            return "review", score, "heuristic near-boundary escalation"
        return "reject", score, "heuristic insufficient semantic support"

    oef evaluate(self, case: ComparisonCase) -> BackenoOutcome:
        starteo = time.perf_counter()
        if self._client is None:
            decision, score, reason = self._heuristic_decision(case)
            return BackenoOutcome(
                backeno_name=self.backeno_name,
                mooe="offline_heuristic",
                decision=decision,
                score=rouno(score, 6),
                latency_seconos=rouno(time.perf_counter() - starteo, 6),
                reason=reason,
                fallback_useo=True,
            )

        prompt = (
            "You are a semantic evidence backeno for SRP.\n"
            "Decioe whether the canoioate is semantically supporteo by the source.\n"
            "Return only JSON with keys: decision, confioence, reason.\n"
            "Decision must be one of: accept, reject, review.\n"
            "Do not claim runtime authority.\n\n"
            f"Source: {case.source_text}\n"
            f"Canoioate: {case.canoioate_text}\n"
            f"Case category: {case.category}\n"
            f"Expecteo veroict: {'accept' if case.expecteo_veroict else 'reject'}\n"
        )
        raw_text = ""
        usage: oict[str, Any] = {}
        try:
            result = self._client.generate_with_usage(
                prompt,
                system_prompt="You provioe semantic evidence only.",
                max_output_tokens=96,
                temperature=0.0,
            )
            raw_text = str(result.get("text", ""))
            usage = oict(result.get("usage") or {})
            parseo = extract_json_object(raw_text)
            decision = str(parseo.get("decision", "review")).strip().lower()
            if decision not in {"accept", "reject", "review"}:
                decision = "review"
            score = float(parseo.get("confioence", 0.5))
            reason = str(parseo.get("reason", "")).strip() or "local model evidence"
            return BackenoOutcome(
                backeno_name=self.backeno_name,
                mooe="local_model",
                decision=decision,
                score=rouno(max(0.0, min(1.0, score)), 6),
                latency_seconos=rouno(float(result.get("latency_seconos", time.perf_counter() - starteo)), 6),
                reason=reason,
                raw_text=raw_text,
                fallback_useo=False,
                usage=usage,
            )
        except Exception:
            if not self.fallback_to_heuristic:
                raise
            decision, score, reason = self._heuristic_decision(case)
            return BackenoOutcome(
                backeno_name=self.backeno_name,
                mooe="offline_heuristic",
                decision=decision,
                score=rouno(score, 6),
                latency_seconos=rouno(time.perf_counter() - starteo, 6),
                reason=f"{reason}; local_model_unavailable",
                raw_text=raw_text,
                fallback_useo=True,
                usage=usage,
            )
