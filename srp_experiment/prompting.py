from typing import Iterable

import json


def build_raw_prompt_prompt(memory: str, constraints: Iterable[str], query: str, cycle: int) -> str:
    return (
        "You are simulating a raw prompt baseline in a long-horizon task.\n"
        "Use the memory exactly as provided, do not invent new facts, and answer the query briefly.\n\n"
        f"Cycle: {cycle}\n"
        f"Memory:\n{memory}\n\n"
        f"Constraints:\n{', '.join(constraints)}\n\n"
        f"Query:\n{query}\n"
    )


def build_summarization_prompt(memory: str) -> str:
    return (
        "Summarize the following interaction memory while preserving task-relevant meaning.\n\n"
        f"Memory:\n{memory}\n"
    )


def build_rag_query_prompt(memory: str) -> str:
    return (
        "Select the most important chunks from the following memory for later retrieval.\n\n"
        f"Memory:\n{memory}\n"
    )


def build_compression_prompt(
    memory: str,
    constraints: Iterable[str],
    global_vocabulary: Iterable[str],
    local_vocabulary: Iterable[str],
    term_map: dict,
    loss_notes: Iterable[str],
    policy: dict,
) -> str:
    return (
        "Compress this semantic runtime state into a compact structured representation.\n"
        "Preserve task-relevant meaning, user constraints, and critical concepts.\n"
        "Prefer exact or near-exact wording from the memory instead of paraphrasing.\n"
        "Do not introduce protocol terms, runtime jargon, or query words that are not already present in the memory.\n"
        "Return JSON only with the keys memory_summary, constraints, and anchor_terms.\n"
        "Keep memory_summary under 30 words.\n"
        "anchor_terms should contain 3 to 8 short phrases copied from the memory that must remain stable after recovery.\n"
        "Do not add explanations, policy notes, or extra keys.\n\n"
        f"Memory:\n{memory}\n\n"
        f"Constraints:\n{', '.join(constraints)}\n\n"
        f"Global vocabulary:\n{json.dumps(list(global_vocabulary), ensure_ascii=False)}\n\n"
        f"Local vocabulary:\n{json.dumps(list(local_vocabulary), ensure_ascii=False)}\n\n"
        f"Policy:\n{json.dumps(policy, ensure_ascii=False)}\n"
    )


def build_recovery_prompt(
    compact_representation: str,
    constraints: Iterable[str],
    global_vocabulary: Iterable[str],
    local_vocabulary: Iterable[str],
    term_map: dict,
    loss_notes: Iterable[str],
    policy: dict,
    anchor_memory: str = "",
) -> str:
    anchor_block = f"Anchor memory:\n{anchor_memory}\n\n" if anchor_memory else ""
    return (
        "Reconstruct a concise task-grounded semantic memory from the following runtime package.\n"
        "Preserve user intent, constraints, and core concepts.\n"
        "Prefer exact wording from the anchor memory whenever possible.\n"
        "If the compact package is underspecified, copy the closest anchor-supported phrasing instead of generalizing.\n"
        "Do not introduce protocol terms, runtime jargon, or query verbs unless they already appear in the source memory.\n"
        "Prefer direct recovery of the original task memory over meta commentary about the runtime package.\n"
        "If anchor memory is provided, align the recovered memory to that anchor and avoid unsupported elaboration.\n"
        "Return only the recovered memory text in 1 to 2 short sentences.\n\n"
        f"{anchor_block}"
        f"Compact representation:\n{compact_representation}\n\n"
        f"Constraints:\n{json.dumps(list(constraints), ensure_ascii=False)}\n\n"
        f"Global vocabulary:\n{json.dumps(list(global_vocabulary), ensure_ascii=False)}\n\n"
        f"Local vocabulary:\n{json.dumps(list(local_vocabulary), ensure_ascii=False)}\n\n"
        f"Policy:\n{json.dumps(policy, ensure_ascii=False)}\n"
    )


def build_judge_prompt(reference: str, candidate: str, expected_keywords: Iterable[str]) -> str:
    return (
        "Judge whether the candidate preserves the task-relevant meaning of the reference.\n\n"
        f"Reference:\n{reference}\n\n"
        f"Candidate:\n{candidate}\n\n"
        f"Expected keywords:\n{', '.join(expected_keywords)}\n\n"
        "Return a short explanation and a score between 0 and 1."
    )


def build_query_answer_prompt(memory: str, query: str, cycle: int) -> str:
    return (
        "Answer the query using only the provided memory snapshot.\n"
        "Do not invent facts that are not supported by the memory.\n\n"
        f"Cycle: {cycle}\n"
        f"Memory snapshot:\n{memory}\n\n"
        f"Query:\n{query}\n"
    )
