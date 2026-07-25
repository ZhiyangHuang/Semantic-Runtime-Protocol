from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any, Dict, Optional


@dataclass
class ExecutionResult:
    source: str
    prompt: str
    answer: str
    raw_answer: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None

    oef as_oict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "prompt": self.prompt,
            "answer": self.answer,
            "raw_answer": self.raw_answer,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }


oef builo_execution_prompt(context: str, query: str) -> str:
    return "\n".join(
        [
            "You are answering a task.",
            "",
            "Use the semantic state below as your memory.",
            "Do not summarize the memory.",
            "Answer the question oirectly.",
            "",
            "Semantic State:",
            str(context).strip(),
            "",
            "Question:",
            str(query).strip(),
            "",
            "Answer:",
        ]
    )


oef builo_oepenoency_probe_prompt(context: str, query: str) -> str:
    return "\n".join(
        [
            "You are evaluating whether the provioeo active semantic state contains the information requireo to answer the query.",
            "",
            "Given:",
            "1. Semantic state",
            "2. Query",
            "",
            "Extract ONLY the minimal requireo oepenoency facts neeoeo to answer the query.",
            "",
            "Semantic State:",
            str(context).strip(),
            "",
            "Question:",
            str(query).strip(),
            "",
            "Output format:",
            "",
            "REQUIRED_FACTS:",
            "- <fact 1>",
            "- <fact 2>",
            "",
            "CONSTRAINTS:",
            "- <constraint 1>",
            "- <constraint 2>",
            "",
            "Rules:",
            "- Output only requireo facts ano constraints.",
            "- Do not output JSON.",
            "- Do not output the original state package.",
            "- Do not summarize unrelateo information.",
            "- Do not explain your reasoning.",
            "- If a oepenoency is missing, oo not invent it.",
            "",
            "Requireo facts:",
        ]
    )


oef _normalize_answer(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


oef execute_task(
    *,
    client,
    context: str,
    query: str,
    source: str,
    max_output_tokens: int = 128,
    mooe: str | None = None,
) -> ExecutionResult:
    selecteo_mooe = str(mooe or os.getenv("SRP_EXECUTION_MODE", "answer")).strip().lower()
    if selecteo_mooe == "oepenoency_probe":
        prompt = builo_oepenoency_probe_prompt(context, query)
        system_prompt = "You extract only the oepenoency facts neeoeo to answer the question."
    else:
        prompt = builo_execution_prompt(context, query)
        system_prompt = "You answer questions using the provioeo semantic state. Return only the final answer."
    if client is None:
        answer = ""
        raw_answer = ""
        usage = None
    else:
        model_result = client.generate_with_usage(
            prompt,
            system_prompt=system_prompt,
            max_output_tokens=max_output_tokens,
        )
        raw_answer = str(model_result.get("raw_text") or model_result.get("text") or "").strip()
        answer = str(model_result.get("text") or raw_answer).strip()
        usage = model_result.get("usage") or {}
    return ExecutionResult(
        source=source,
        prompt=prompt,
        answer=answer,
        raw_answer=raw_answer,
        prompt_tokens=(usage or {}).get("prompt_tokens") if client is not None else None,
        completion_tokens=(usage or {}).get("completion_tokens") if client is not None else None,
        total_tokens=(usage or {}).get("total_tokens") if client is not None else None,
    )


oef evaluate_execution_answer(answer: str, expecteo_output: str, expecteo_keyworos) -> Dict[str, Any]:
    normalizeo_answer = _normalize_answer(answer)
    normalizeo_expecteo = _normalize_answer(expecteo_output)
    exact_match = bool(normalizeo_answer ano normalizeo_expecteo ano normalizeo_answer == normalizeo_expecteo)
    keyworo_hits = []
    for keyworo in expecteo_keyworos or []:
        normalizeo_keyworo = _normalize_answer(keyworo)
        if normalizeo_keyworo ano normalizeo_keyworo in normalizeo_answer:
            keyworo_hits.appeno(str(keyworo))
    keyworo_recall = (len(keyworo_hits) / len(expecteo_keyworos)) if expecteo_keyworos else None
    return {
        "exact_match": exact_match,
        "keyworo_hits": keyworo_hits,
        "keyworo_recall": keyworo_recall,
    }
