from time import perf_counter
from typing import Dict, List, Optional, Tuple

from budgeting import available_memory_budget, chunk_text, get_budget_config, pack_chunks_to_budget
from prompting import build_rag_query_prompt
from srp.compress import compress_state
from srp.recover import recover_state
from srp.state import SemanticState
from srp.validate import validate_state
from srp.validation_targets import SemanticContractGraph
from srp.validation_targets import build_validation_targets


def _top_k_chunks(text: str) -> List[str]:
    budget = get_budget_config()
    chunks = chunk_text(text, budget.rag_chunk_tokens)
    shortlisted = chunks[: budget.rag_top_k]
    return pack_chunks_to_budget(shortlisted, available_memory_budget())


def _extract_vocab(text: str) -> List[str]:
    words = [word.strip(".,").lower() for word in text.split()]
    unique = []
    for word in words:
        if len(word) > 4 and word not in unique:
            unique.append(word)
    return unique[:12]


def _merge_vocab(existing: List[str], additions: List[str], limit: int = 12) -> List[str]:
    merged = list(existing)
    for item in additions:
        cleaned = str(item).strip().lower()
        if cleaned and cleaned not in merged:
            merged.append(cleaned)
    return merged[:limit]


def _flatten_validation_targets(validation_targets: List | SemanticContractGraph) -> str:
    if isinstance(validation_targets, SemanticContractGraph):
        return " ".join(validation_targets.flattened_variants())
    flattened: List[str] = []
    for item in validation_targets:
        if isinstance(item, str):
            flattened.append(item)
        else:
            try:
                flattened.extend(str(value).strip() for value in item if str(value).strip())
            except TypeError:
                flattened.append(str(item).strip())
    return " ".join(flattened)


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


def _build_anchor_memory(task: Dict) -> str:
    memory = task["initial_state"]["memory"].strip()
    constraints = [item.strip() for item in task["initial_state"].get("constraints", []) if item.strip()]
    if constraints:
        return f"{memory}\nConstraints: {'; '.join(constraints)}"
    return memory


def run_rag_srp_v2(task: Dict, cycles: int, client=None) -> List[Dict]:
    constraints = list(task["initial_state"].get("constraints", []))
    anchor_memory = _build_anchor_memory(task)
    working_memory = task["initial_state"]["memory"]
    global_vocabulary = _extract_vocab(anchor_memory)
    local_vocabulary = _extract_vocab(" ".join(constraints))
    records = []

    for cycle in range(1, cycles + 1):
        started_at = perf_counter()
        pre_cycle_memory = working_memory
        pre_cycle_global_vocabulary = list(global_vocabulary)
        pre_cycle_local_vocabulary = list(local_vocabulary)

        retrieved, retrieval_usage = _retrieve_chunks(working_memory, client=client)
        retrieved_memory = " || ".join(retrieved)

        state = SemanticState(
            memory=retrieved_memory,
            constraints=constraints,
            global_vocabulary=pre_cycle_global_vocabulary,
            local_vocabulary=pre_cycle_local_vocabulary,
            term_map={},
            loss_notes=[],
            policy={
                "compression_goal": "preserve retrieved task evidence under bounded drift",
                "anti_leakage": "do not introduce query verbs or protocol terms unless they are already in memory",
                "recovery_goal": "recover the retrieved task evidence as directly as possible by aligning to a stable semantic anchor",
            },
        )
        package = compress_state(state, client=client)
        recovered = recover_state(package, client=client, anchor_memory=anchor_memory)
        validation_targets = build_validation_targets(task)
        validation = validate_state(pre_cycle_memory, recovered.memory, validation_targets)
        committed = validation["passed"]
        committed_memory = recovered.memory if committed else pre_cycle_memory
        package_usage = package.get("usage") or {}
        recovered_usage = getattr(recovered, "usage", None) or {}
        usage = {
            "prompt_tokens": sum(value for value in [retrieval_usage and retrieval_usage.get("prompt_tokens"), package_usage.get("prompt_tokens"), recovered_usage.get("prompt_tokens")] if value is not None) or None,
            "completion_tokens": sum(value for value in [retrieval_usage and retrieval_usage.get("completion_tokens"), package_usage.get("completion_tokens"), recovered_usage.get("completion_tokens")] if value is not None) or None,
            "total_tokens": sum(value for value in [retrieval_usage and retrieval_usage.get("total_tokens"), package_usage.get("total_tokens"), recovered_usage.get("total_tokens")] if value is not None) or None,
        }

        global_vocabulary = (
            _merge_vocab(pre_cycle_global_vocabulary, package.get("global_vocab", []) + _extract_vocab(pre_cycle_memory))
            if committed
            else pre_cycle_global_vocabulary
        )
        local_vocabulary = (
            _merge_vocab(pre_cycle_local_vocabulary, constraints + _extract_vocab(_flatten_validation_targets(validation_targets)), limit=12)
            if committed
            else pre_cycle_local_vocabulary
        )

        records.append(
            {
                "cycle": cycle,
                "representation": package["memory"],
                "recovered_text": recovered.memory,
                "committed_memory": committed_memory,
                "tokens": len(package["memory"].split()) + len(package.get("global_vocab", [])) + 8,
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens"),
                "latency_seconds": round(perf_counter() - started_at, 4),
                "validation_score": validation["score"],
                "validation_contract_satisfaction": validation["contract_satisfaction"],
                "validation_drift": validation["drift"],
                "validation_drift_risk": validation["drift_risk"],
                "validation_drift_blocks_commit": validation["drift_blocks_commit"],
                "validation_coverage": validation["coverage_score"],
                "validation_alignment": validation["alignment_score"],
                "validation_leakage_detected": validation["leakage_detected"],
                "max_cycle_drift": validation["max_drift"],
                "blocking_drift": validation["blocking_drift"],
                "min_keyword_score": validation["min_keyword_score"],
                "min_coverage_score": validation["min_coverage_score"],
                "validation_passed": validation["passed"],
                "state_committed": committed,
                "notes": "retrieval-guided srp v2" if committed else "retrieval-guided srp v2 (rollback to pre-retrieval memory)",
            }
        )

        working_memory = committed_memory

    return records
