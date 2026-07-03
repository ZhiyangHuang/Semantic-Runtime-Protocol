from time import perf_counter
from typing import Dict, List

from budgeting import available_memory_budget, clip_tail_to_budget, get_budget_config
from prompting import build_summarization_prompt


def _summarize(text: str, max_words: int = 20) -> str:
    words = text.split()
    return " ".join(words[:max_words])


def run_summarization(task: Dict, cycles: int, client=None) -> List[Dict]:
    memory = task["initial_state"]["memory"]
    budget = get_budget_config()
    records = []
    for cycle in range(1, cycles + 1):
        started_at = perf_counter()
        if client is None:
            summary = _summarize(memory, max_words=max(8, 20 - cycle))
            prompt_tokens = completion_tokens = total_tokens = None
        else:
            memory_view = clip_tail_to_budget(memory, available_memory_budget())
            prompt = build_summarization_prompt(memory_view)
            model_result = client.generate_with_usage(
                prompt,
                system_prompt="You are a concise memory summarizer.",
                max_output_tokens=budget.output_tokens,
            )
            summary = model_result["text"]
            usage = model_result.get("usage") or {}
            prompt_tokens = usage.get("prompt_tokens")
            completion_tokens = usage.get("completion_tokens")
            total_tokens = usage.get("total_tokens")
        records.append(
            {
                "cycle": cycle,
                "representation": summary,
                "tokens": len(summary.split()) + 6,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "latency_seconds": round(perf_counter() - started_at, 4),
                "notes": f"summary-compression baseline (budget-aware prompt cap {budget.prompt_budget_tokens})",
            }
        )
        memory = summary
    return records
