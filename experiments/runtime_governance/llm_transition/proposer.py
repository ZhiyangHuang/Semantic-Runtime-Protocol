from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from typing import Any, Mapping

from experiments.common.local_llm import build_local_client

from .scenarios import LLMTransitionScenario


@dataclass(frozen=True)
class SemanticProposal:
    scenario_name: str
    source: str
    delta: dict[str, Any]
    evidence: dict[str, Any]
    raw_text: str = ""
    parsed: bool = True
    latency_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "scenario_name": self.scenario_name,
            "source": self.source,
            "delta": dict(self.delta),
            "evidence": dict(self.evidence),
            "raw_text": self.raw_text,
            "parsed": self.parsed,
            "latency_ms": self.latency_ms,
            "metadata": dict(self.metadata),
        }


def _build_prompt(scenario: LLMTransitionScenario) -> str:
    schema = {
        "delta": {
            "state_patch": {
                "facts": {"user_prefers": "coffee"},
                "memory": ["..."],
            },
            "confidence": 0.0,
        },
        "evidence": {
            "verification_score": 0.0,
            "sources": [{"source": "conversation_turn", "content": "..." }],
        },
        "notes": ["short reasoning summary"],
    }
    return "\n".join(
        [
            "You are proposing a semantic transition, not approving it.",
            "Return only one JSON object with delta, evidence, and notes.",
            "Do not include approval, authority, or governance decisions.",
            "",
            "Schema:",
            json.dumps(schema, ensure_ascii=False),
            "",
            "Current state:",
            json.dumps(scenario.state_before, ensure_ascii=False),
            "",
            "Conversation:",
            scenario.conversation,
            "",
            "Objective:",
            "Propose the smallest state_patch that is supported by the conversation.",
        ]
    )


def _extract_json_block(text: str) -> str:
    source = text.strip()
    if not source:
        raise ValueError("empty proposal text")
    if source.startswith("{") and source.endswith("}"):
        return source
    fenced = re.search(r"```json\s*(\{.*?\})\s*```", source, flags=re.IGNORECASE | re.DOTALL)
    if fenced:
        return fenced.group(1)
    bracketed = re.search(r"(\{.*\})", source, flags=re.DOTALL)
    if bracketed:
        return bracketed.group(1)
    raise ValueError("no JSON object found in proposal text")


def _normalize_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    return {"value": value}


def _scripted_proposal(scenario: LLMTransitionScenario) -> SemanticProposal:
    return SemanticProposal(
        scenario_name=scenario.name,
        source="scripted",
        delta=dict(scenario.reference_delta),
        evidence=dict(scenario.reference_evidence),
        raw_text=json.dumps(
            {
                "delta": scenario.reference_delta,
                "evidence": scenario.reference_evidence,
                "notes": [scenario.description],
            },
            ensure_ascii=False,
        ),
        parsed=True,
        latency_ms=0.0,
        metadata={
            "backend": "scripted",
            "scenario_kind": scenario.kind,
        },
    )


def propose_transition(
    scenario: LLMTransitionScenario,
    *,
    backend: str = "auto",
    model_client: Any | None = None,
) -> SemanticProposal:
    backend_name = str(backend or "auto").strip().lower()
    if backend_name not in {"auto", "local", "scripted"}:
        raise ValueError(f"unsupported backend: {backend}")

    if backend_name == "scripted":
        return _scripted_proposal(scenario)

    started = time.perf_counter()
    try:
        client = model_client or build_local_client()
        response = client.generate_with_usage(
            prompt=_build_prompt(scenario),
            system_prompt=(
                "You produce semantic transition proposals for governed runtime evaluation. "
                "Return only JSON with delta, evidence, and notes."
            ),
            max_output_tokens=256,
            temperature=0.0,
        )
        raw_text = str(response.get("text") or "").strip()
        payload = json.loads(_extract_json_block(raw_text))
        delta = _normalize_mapping(payload.get("delta"))
        evidence = _normalize_mapping(payload.get("evidence"))
        notes = payload.get("notes")
        metadata = {
            "backend": "local",
            "model": response.get("model"),
            "usage": response.get("usage"),
            "notes": notes,
        }
        return SemanticProposal(
            scenario_name=scenario.name,
            source="local",
            delta=delta,
            evidence=evidence,
            raw_text=raw_text,
            parsed=True,
            latency_ms=round(float(response.get("latency_seconds", time.perf_counter() - started)) * 1000.0, 6),
            metadata=metadata,
        )
    except Exception as exc:
        if backend_name == "local":
            raise RuntimeError(f"LLM proposal generation failed for scenario {scenario.name}: {exc}") from exc
        fallback = _scripted_proposal(scenario)
        return SemanticProposal(
            scenario_name=fallback.scenario_name,
            source="fallback_scripted",
            delta=fallback.delta,
            evidence=fallback.evidence,
            raw_text=fallback.raw_text,
            parsed=False,
            latency_ms=round((time.perf_counter() - started) * 1000.0, 6),
            metadata={
                "backend": "auto",
                "fallback_reason": str(exc),
                "scenario_kind": scenario.kind,
            },
        )
