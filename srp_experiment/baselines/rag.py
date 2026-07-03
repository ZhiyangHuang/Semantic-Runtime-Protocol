from time import perf_counter
from typing import Dict, List, Tuple, Optional

from budgeting import available_memory_budget, chunk_text, get_budget_config, pack_chunks_to_budget
from prompting import build_rag_query_prompt


def _top_k_chunks(text: str) -> List[str]:
    budget = get_budget_config()
    chunks = chunk_text(text, budget.rag_chunk_tokens)
    shortlisted = chunks[: budget.rag_top_k]
    return pack_chunks_to_budget(shortlisted, available_memory_budget())


def _retrieve_chunks(memory: str, client=None) -> Tuple[List[str], Optional[Dict]]:
    if client is None:
        return _top_k_chunks(memory), None
    budget = get_budget_config()
    memory_view = " ".join(memory.split()[: available_memory_budget()])
    prompt = build_rag_query_prompt(memory_view)
    model_result = client.generate_with_usage(
        prompt,
        system_prompt="You select concise retrievable chunks.",
        max_output_tokens=budget.output_tokens,
    )
    response = model_result["text"]
    usage = model_result.get("usage") or None
    retrieved = [chunk.strip() for chunk in response.split("||") if chunk.strip()]
    selected = retrieved or _top_k_chunks(memory)
    return pack_chunks_to_budget(selected, available_memory_budget()), usage


def run_rag(task: Dict, cycles: int, client=None) -> List[Dict]:
    memory = task["initial_state"]["memory"]
    budget = get_budget_config()
    records = []
    for cycle in range(1, cycles + 1):
        started_at = perf_counter()
        retrieved, usage = _retrieve_chunks(memory, client=client)
        representation = " || ".join(retrieved)
        records.append(
            {
                "cycle": cycle,
                "representation": representation,
                "tokens": len(representation.split()) + 10,
                "prompt_tokens": usage.get("prompt_tokens") if usage else None,
                "completion_tokens": usage.get("completion_tokens") if usage else None,
                "total_tokens": usage.get("total_tokens") if usage else None,
                "latency_seconds": round(perf_counter() - started_at, 4),
                "notes": f"retrieval-selection baseline (chunk={budget.rag_chunk_tokens}, top_k={budget.rag_top_k}, budget={budget.prompt_budget_tokens})",
            }
        )
        memory = representation
    return records
