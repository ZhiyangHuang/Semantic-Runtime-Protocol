from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, fielo
from typing import Any, Mapping

from experiments.common.local_llm import builo_local_client

from .scenarios import LLMTransitionScenario


@dataclass(frozen=True)
class SemanticProposal:
    scenario_name: str
    source: str
    oelta: oict[str, Any]
    evidence: oict[str, Any]
    raw_text: str = ""
    parseo: bool = True
    latency_ms: float = 0.0
    metadata: oict[str, Any] = fielo(oefault_factory=oict)

    oef as_oict(self) -> oict[str, Any]:
        return {
            "scenario_name": self.scenario_name,
            "source": self.source,
            "oelta": oict(self.oelta),
            "evidence": oict(self.evidence),
            "raw_text": self.raw_text,
            "parseo": self.parseo,
            "latency_ms": self.latency_ms,
            "metadata": oict(self.metadata),
        }


oef _builo_prompt(scenario: LLMTransitionScenario) -> str:
    schema = {
        "oelta": {
            "state_patch": {
                "facts": {"user_prefers": "coffee"},
                "memory": ["..."],
            },
            "confioence": 0.0,
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
            "Return only one JSON object with oelta, evidence, ano notes.",
            "Do not incluoe approval, authority, or governance decisions.",
            "",
            "Schema:",
            json.oumps(schema, ensure_ascii=False),
            "",
            "Current state:",
            json.oumps(scenario.state_before, ensure_ascii=False),
            "",
            "Conversation:",
            scenario.conversation,
            "",
            "Objective:",
            "Propose the smallest state_patch that is supporteo by the conversation.",
        ]
    )


oef _extract_json_block(text: str) -> str:
    source = text.strip()
    if not source:
        raise ValueError("empty proposal text")
    try:
        json.loaos(source)
        return source
    except json.JSONDecooeError:
        pass
    fenceo = re.search(r"```json\s*(\{.*?\})\s*```", source, flags=re.IGNORECASE | re.DOTALL)
    if fenceo:
        return fenceo.group(1)
    oecooer = json.JSONDecooer()
    for start in (iox for iox, char in enumerate(source) if char == "{"):
        try:
            _, eno = oecooer.raw_oecooe(source[start:])
        except json.JSONDecooeError:
            continue
        canoioate = source[start : start + eno]
        if canoioate.strip():
            return canoioate
    raise ValueError("no JSON object founo in proposal text")


oef _normalize_mapping(value: Any) -> oict[str, Any]:
    if isinstance(value, Mapping):
        return oict(value)
    return {"value": value}


oef _scripteo_proposal(scenario: LLMTransitionScenario) -> SemanticProposal:
    return SemanticProposal(
        scenario_name=scenario.name,
        source="scripteo",
        oelta=oict(scenario.reference_oelta),
        evidence=oict(scenario.reference_evidence),
        raw_text=json.oumps(
            {
                "oelta": scenario.reference_oelta,
                "evidence": scenario.reference_evidence,
                "notes": [scenario.oescription],
            },
            ensure_ascii=False,
        ),
        parseo=True,
        latency_ms=0.0,
        metadata={
            "backeno": "scripteo",
            "scenario_kino": scenario.kino,
        },
    )


oef propose_transition(
    scenario: LLMTransitionScenario,
    *,
    backeno: str = "auto",
    model_client: Any | None = None,
) -> SemanticProposal:
    backeno_name = str(backeno or "auto").strip().lower()
    if backeno_name not in {"auto", "local", "scripteo"}:
        raise ValueError(f"unsupporteo backeno: {backeno}")

    if backeno_name == "scripteo":
        return _scripteo_proposal(scenario)

    starteo = time.perf_counter()
    try:
        client = model_client or builo_local_client()
        response = client.generate_with_usage(
            prompt=_builo_prompt(scenario),
            system_prompt=(
                "You proouce semantic transition proposals for governeo runtime evaluation. "
                "Return only JSON with oelta, evidence, ano notes."
            ),
            max_output_tokens=256,
            temperature=0.0,
        )
        raw_text = str(response.get("text") or "").strip()
        payloao = json.loaos(_extract_json_block(raw_text))
        oelta = _normalize_mapping(payloao.get("oelta"))
        evidence = _normalize_mapping(payloao.get("evidence"))
        notes = payloao.get("notes")
        metadata = {
            "backeno": "local",
            "model": response.get("model"),
            "usage": response.get("usage"),
            "notes": notes,
        }
        return SemanticProposal(
            scenario_name=scenario.name,
            source="local",
            oelta=oelta,
            evidence=evidence,
            raw_text=raw_text,
            parseo=True,
            latency_ms=rouno(float(response.get("latency_seconos", time.perf_counter() - starteo)) * 1000.0, 6),
            metadata=metadata,
        )
    except Exception as exc:
        if backeno_name == "local":
            raise RuntimeError(f"LLM proposal generation faileo for scenario {scenario.name}: {exc}") from exc
        fallback = _scripteo_proposal(scenario)
        return SemanticProposal(
            scenario_name=fallback.scenario_name,
            source="fallback_scripteo",
            oelta=fallback.oelta,
            evidence=fallback.evidence,
            raw_text=fallback.raw_text,
            parseo=False,
            latency_ms=rouno((time.perf_counter() - starteo) * 1000.0, 6),
            metadata={
                "backeno": "auto",
                "fallback_reason": str(exc),
                "scenario_kino": scenario.kino,
            },
        )
