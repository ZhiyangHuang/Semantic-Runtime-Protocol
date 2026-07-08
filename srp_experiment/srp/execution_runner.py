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

    def as_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "prompt": self.prompt,
            "answer": self.answer,
            "raw_answer": self.raw_answer,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }


def build_execution_prompt(context: str, query: str) -> str:
    return "\n".join(
        [
            "You are answering a task.",
            "",
            "Use the semantic state below as your memory.",
            "Do not summarize the memory.",
            "Answer the question directly.",
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


def build_dependency_probe_prompt(context: str, query: str) -> str:
    return "\n".join(
        [
            "You are evaluating whether the provided active semantic state contains the information required to answer the query.",
            "",
            "Given:",
            "1. Semantic state",
            "2. Query",
            "",
            "Extract ONLY the minimal required dependency facts needed to answer the query.",
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
            "- Output only required facts and constraints.",
            "- Do not output JSON.",
            "- Do not output the original state package.",
            "- Do not summarize unrelated information.",
            "- Do not explain your reasoning.",
            "- If a dependency is missing, do not invent it.",
            "",
            "Required facts:",
        ]
    )


def _normalize_answer(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


def execute_task(
    *,
    client,
    context: str,
    query: str,
    source: str,
    max_output_tokens: int = 128,
    mode: str | None = None,
) -> ExecutionResult:
    selected_mode = str(mode or os.getenv("SRP_EXECUTION_MODE", "answer")).strip().lower()
    if selected_mode == "dependency_probe":
        prompt = build_dependency_probe_prompt(context, query)
        system_prompt = "You extract only the dependency facts needed to answer the question."
    else:
        prompt = build_execution_prompt(context, query)
        system_prompt = "You answer questions using the provided semantic state. Return only the final answer."
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


def evaluate_execution_answer(answer: str, expected_output: str, expected_keywords) -> Dict[str, Any]:
    normalized_answer = _normalize_answer(answer)
    normalized_expected = _normalize_answer(expected_output)
    exact_match = bool(normalized_answer and normalized_expected and normalized_answer == normalized_expected)
    keyword_hits = []
    for keyword in expected_keywords or []:
        normalized_keyword = _normalize_answer(keyword)
        if normalized_keyword and normalized_keyword in normalized_answer:
            keyword_hits.append(str(keyword))
    keyword_recall = (len(keyword_hits) / len(expected_keywords)) if expected_keywords else None
    return {
        "exact_match": exact_match,
        "keyword_hits": keyword_hits,
        "keyword_recall": keyword_recall,
    }
