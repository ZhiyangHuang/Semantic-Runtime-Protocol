from time import perf_counter
from typing import Dict, List

from budgeting import available_memory_budget, get_budget_config
from prompting import build_raw_prompt_prompt


def _clip_memory_tail(memory: str, query: str, constraints: List[str]) -> str:
    max_words = available_memory_budget(query=query, constraints=constraints)
    words = memory.split()
    if len(words) <= max_words:
        return memory
    return " ".join(words[-max_words:])


def run_raw_prompt(task: Dict, cycles: int, client=None) -> List[Dict]:
    memory = task["initial_state"]["memory"]
    constraints = list(task["initial_state"].get("constraints", []))
    queries = list(task.get("queries", [])) or ["Restate the task-relevant memory."]
    budget = get_budget_config()
    records = []
    for cycle in range(1, cycles + 1):
        started_at = perf_counter()
        if client is None:
            response = f"{memory} Constraints: {', '.join(constraints)}"
            note = "direct carryover baseline"
        else:
            query = queries[(cycle - 1) % len(queries)]
            clipped_memory = _clip_memory_tail(memory, query, constraints)
            prompt = build_raw_prompt_prompt(clipped_memory, constraints, query, cycle)
            model_result = client.generate_with_usage(
                prompt,
                system_prompt="You are evaluating how well a raw accumulated prompt preserves task-relevant memory.",
                max_output_tokens=budget.output_tokens,
            )
            model_response = model_result["text"]
            response = f"{clipped_memory}\nModel response: {model_response}"
            note = (
                f"direct carryover baseline (budget-clipped to ~{available_memory_budget(query=query, constraints=constraints)} tokens)"
                if clipped_memory != memory
                else "direct carryover baseline"
            )
        records.append(
            {
                "cycle": cycle,
                "representation": response,
                "tokens": len(response.split()) + cycle * 4,
                "prompt_tokens": model_result["usage"]["prompt_tokens"] if client is not None and model_result.get("usage") else None,
                "completion_tokens": model_result["usage"]["completion_tokens"] if client is not None and model_result.get("usage") else None,
                "total_tokens": model_result["usage"]["total_tokens"] if client is not None and model_result.get("usage") else None,
                "latency_seconds": round(perf_counter() - started_at, 4),
                "notes": note,
            }
        )
        memory = f"{memory} {response}"
    return records
