from typing import Dict, Iterable

from prompting import build_query_answer_prompt
from .scoring import compute_contract_satisfaction


def _fallback_answer(memory: str, max_words: int = 40) -> str:
    words = memory.split()
    return " ".join(words[:max_words])


def run_shared_query_evaluation(
    memory_snapshot: str,
    query: str,
    semantic_contract: Iterable,
    cycle: int,
    client=None,
) -> Dict:
    if client is None:
        answer = _fallback_answer(memory_snapshot)
        usage = None
    else:
        if len(memory_snapshot) + len(query) > 20000:
            answer = _fallback_answer(memory_snapshot)
            usage = None
            return {
                "query": query,
                "answer": answer,
                "query_success": compute_contract_satisfaction(answer, semantic_contract),
                "usage": usage,
            }
        prompt = build_query_answer_prompt(memory_snapshot, query, cycle)
        try:
            model_result = client.generate_with_usage(
                prompt,
                system_prompt="You are answering a controlled evaluation query for an SRP experiment.",
                max_output_tokens=120,
            )
        except RuntimeError as exc:
            message = str(exc).lower()
            if "maximum context length" in message or "upper bound" in message or "input_text" in message:
                answer = _fallback_answer(memory_snapshot)
                usage = None
                return {
                    "query": query,
                    "answer": answer,
                    "query_success": compute_contract_satisfaction(answer, semantic_contract),
                    "usage": usage,
                }
            raise
        answer = model_result["text"]
        usage = model_result.get("usage")
    return {
        "query": query,
        "answer": answer,
        "query_success": compute_contract_satisfaction(answer, semantic_contract),
        "usage": usage,
    }
