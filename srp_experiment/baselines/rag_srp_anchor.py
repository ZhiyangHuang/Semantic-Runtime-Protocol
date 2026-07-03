from time import perf_counter
from typing import Dict, List, Optional, Tuple

from prompting import build_rag_query_prompt
from srp.compress import compress_state
from srp.state import SemanticState
from srp.validate import validate_state
from srp.validation_targets import build_validation_targets


def _top_k_chunks(text: str, chunk_size: int = 8, top_k: int = 2) -> List[str]:
    words = text.split()
    chunks = [" ".join(words[i : i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks[:top_k]


def _extract_vocab(text: str) -> List[str]:
    words = [word.strip(".,").lower() for word in text.split()]
    unique = []
    for word in words:
        if len(word) > 4 and word not in unique:
            unique.append(word)
    return unique[:12]


def _retrieve_chunks(memory: str, client=None) -> Tuple[List[str], Optional[Dict]]:
    if client is None:
        return _top_k_chunks(memory, chunk_size=8, top_k=2), None
    prompt = build_rag_query_prompt(memory)
    model_result = client.generate_with_usage(
        prompt,
        system_prompt="You select concise retrievable chunks.",
        max_output_tokens=96,
    )
    response = model_result["text"]
    usage = model_result.get("usage") or None
    retrieved = [chunk.strip() for chunk in response.split("||") if chunk.strip()]
    return retrieved or _top_k_chunks(memory, chunk_size=8, top_k=2), usage


def _build_anchor_memory(task: Dict) -> str:
    memory = task["initial_state"]["memory"].strip()
    constraints = [item.strip() for item in task["initial_state"].get("constraints", []) if item.strip()]
    if constraints:
        return f"{memory}\nConstraints: {'; '.join(constraints)}"
    return memory


def _recover_with_anchor(anchor_memory: str, compact_memory: str, constraints: List[str], client=None) -> Tuple[str, Optional[Dict]]:
    if client is None:
        memory = compact_memory if compact_memory.endswith(".") else f"{compact_memory}."
        return memory, None
    prompt = (
        "Reconstruct a concise task-grounded memory from the working memory.\n"
        "Use the anchor memory as the stable semantic reference.\n"
        "Preserve the anchor facts and constraints.\n"
        "Do not add explanatory details that are not supported by the anchor.\n"
        "Return only the recovered task memory in 1 to 3 sentences.\n\n"
        f"Anchor memory:\n{anchor_memory}\n\n"
        f"Working memory:\n{compact_memory}\n\n"
        f"Constraints:\n{'; '.join(constraints)}\n"
    )
    model_result = client.generate_with_usage(
        prompt,
        system_prompt="You recover task memory by aligning a compact working state to a stable semantic anchor.",
        max_output_tokens=96,
    )
    return model_result["text"], model_result.get("usage") or None


def run_rag_srp_anchor(task: Dict, cycles: int, client=None) -> List[Dict]:
    anchor_memory = _build_anchor_memory(task)
    working_memory = task["initial_state"]["memory"]
    constraints = list(task["initial_state"].get("constraints", []))
    records = []

    for cycle in range(1, cycles + 1):
        started_at = perf_counter()
        retrieved, retrieval_usage = _retrieve_chunks(working_memory, client=client)
        retrieved_memory = " || ".join(retrieved)
        state = SemanticState(
            memory=retrieved_memory,
            constraints=constraints,
            global_vocabulary=_extract_vocab(anchor_memory),
            local_vocabulary=_extract_vocab(" ".join(constraints)),
            term_map={},
            loss_notes=[],
            policy={
                "compression_goal": "preserve retrieved task evidence under bounded drift",
                "anti_leakage": "do not introduce query verbs or protocol terms unless they are already in memory",
                "recovery_goal": "recover the retrieved task evidence by aligning to a stable anchor memory",
            },
        )
        package = compress_state(state, client=client)
        recovered_memory, recovery_usage = _recover_with_anchor(anchor_memory, package["memory"], constraints, client=client)
        validation_targets = build_validation_targets(task)
        validation = validate_state(anchor_memory, recovered_memory, validation_targets)
        package_usage = package.get("usage") or {}
        records.append(
            {
                "cycle": cycle,
                "representation": package["memory"],
                "recovered_text": recovered_memory,
                "tokens": len(package["memory"].split()) + len(package.get("global_vocab", [])) + 10,
                "prompt_tokens": sum(
                    value
                    for value in [retrieval_usage and retrieval_usage.get("prompt_tokens"), package_usage.get("prompt_tokens"), recovery_usage and recovery_usage.get("prompt_tokens")]
                    if value is not None
                )
                or None,
                "completion_tokens": sum(
                    value
                    for value in [
                        retrieval_usage and retrieval_usage.get("completion_tokens"),
                        package_usage.get("completion_tokens"),
                        recovery_usage and recovery_usage.get("completion_tokens"),
                    ]
                    if value is not None
                )
                or None,
                "total_tokens": sum(
                    value
                    for value in [retrieval_usage and retrieval_usage.get("total_tokens"), package_usage.get("total_tokens"), recovery_usage and recovery_usage.get("total_tokens")]
                    if value is not None
                )
                or None,
                "latency_seconds": round(perf_counter() - started_at, 4),
                "validation_score": validation["score"],
                "validation_contract_satisfaction": validation["contract_satisfaction"],
                "validation_passed": validation["passed"],
                "notes": "exploratory retrieval-guided srp hybrid with stable anchor",
            }
        )
        working_memory = recovered_memory
    return records
