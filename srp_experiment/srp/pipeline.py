from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Sequence

from .encoder import HashingSemanticEncoder, cosine_similarity
from .semantic_parser import canonicalize_semantic_value


def _split_sentences(text: str) -> list[str]:
    normalized = " ".join(str(text).strip().split())
    if not normalized:
        return []
    sentences: list[str] = []
    for chunk in normalized.replace("?", ".").replace("!", ".").split("."):
        cleaned = chunk.strip(" ,;")
        if cleaned:
            sentences.append(cleaned)
    return sentences


def _first_query(task: dict[str, Any]) -> str:
    if "queries" in task and isinstance(task["queries"], list) and task["queries"]:
        return str(task["queries"][0])
    if "query" in task:
        return str(task["query"])
    expectations = task.get("query_expectations", [])
    if isinstance(expectations, list) and expectations:
        first = expectations[0]
        if isinstance(first, list):
            flat: list[str] = []
            stack: list[Any] = [first]
            while stack:
                item = stack.pop(0)
                if isinstance(item, list):
                    stack = list(item) + stack
                elif isinstance(item, str):
                    flat.append(item)
            if flat:
                return flat[0]
    return ""


def _expected_answer(task: dict[str, Any]) -> str:
    expectations = task.get("query_expectations", [])
    stack: list[Any] = [expectations]
    while stack:
        item = stack.pop(0)
        if isinstance(item, str) and item.strip():
            return item.strip()
        if isinstance(item, list):
            stack = list(item) + stack
    expected_output = task.get("expected_output")
    if isinstance(expected_output, str):
        return expected_output.strip()
    return ""


def _heuristic_answer(memory: str, query: str) -> str:
    query_tokens = {token for token in canonicalize_semantic_value(query).split() if token}
    for sentence in _split_sentences(memory):
        sentence_tokens = {token for token in canonicalize_semantic_value(sentence).split() if token}
        if query_tokens & sentence_tokens:
            return sentence
    sentences = _split_sentences(memory)
    return sentences[0] if sentences else ""


def _score_answer(predicted: str, expected: str, query: str, memory: str) -> tuple[float, float, float, float]:
    encoder = HashingSemanticEncoder()
    query_vec = encoder.encode_query(query)
    memory_vec = encoder.encode_passage(memory)
    coverage = cosine_similarity(query_vec, memory_vec)
    expected_norm = canonicalize_semantic_value(expected)
    predicted_norm = canonicalize_semantic_value(predicted)
    alignment = 1.0 if expected_norm and expected_norm in predicted_norm else 0.5 if predicted_norm else 0.0
    drift = round(max(0.0, min(1.0, 1.0 - ((coverage + alignment) / 2.0))), 6)
    score = round((coverage + alignment) / 2.0, 6)
    return round(coverage, 6), round(alignment, 6), drift, score


def run_srp(
    task: dict[str, Any],
    cycles: int,
    client=None,
    max_cycle_drift: float = 0.35,
    min_keyword_score: float = 0.5,
) -> list[dict[str, Any]]:
    memory = str(task.get("initial_state", {}).get("memory", ""))
    query = _first_query(task)
    expected_answer = _expected_answer(task)
    records: list[dict[str, Any]] = []

    for cycle in range(1, max(1, int(cycles)) + 1):
        predicted_answer = _heuristic_answer(memory, query)
        usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        generation_mode = "offline_heuristic"

        if client is not None and hasattr(client, "generate_with_usage"):
            try:
                prompt = (
                    "Answer the question using only the provided memory.\n"
                    f"Question: {query}\n"
                    f"Memory: {memory}\n"
                    "Return only the answer."
                )
                response = client.generate_with_usage(
                    prompt,
                    system_prompt="You answer using only the provided semantic memory.",
                    max_output_tokens=64,
                    temperature=0.0,
                )
                raw_text = str(response.get("text", "")).strip()
                if raw_text:
                    predicted_answer = raw_text.splitlines()[0].strip()
                usage = dict(response.get("usage") or {})
                generation_mode = str(response.get("model", "local_model"))
            except Exception:
                generation_mode = "offline_heuristic"

        coverage, alignment, drift, score = _score_answer(predicted_answer, expected_answer, query, memory)
        keyword_score = coverage
        validation_passed = drift <= max_cycle_drift and keyword_score >= min_keyword_score

        records.append(
            {
                "cycle": cycle,
                "task_io": str(task.get("io", task.get("id", "task"))),
                "task_type": str(task.get("task_type", "unknown")),
                "task_source": str(task.get("source", "")),
                "query": query,
                "expected_answer": expected_answer,
                "predicted_answer": predicted_answer,
                "state_committed": validation_passed,
                "validation_passed": validation_passed,
                "validation_score": score,
                "validation_drift": drift,
                "validation_coverage": coverage,
                "validation_alignment": alignment,
                "prompt_tokens": int(usage.get("prompt_tokens", 0) or 0),
                "completion_tokens": int(usage.get("completion_tokens", 0) or 0),
                "total_tokens": int(usage.get("total_tokens", 0) or 0),
                "generation_mode": generation_mode,
                "experiment_result": {
                    "metrics": {
                        "validation_passed": validation_passed,
                        "validation_score": score,
                        "validation_drift": drift,
                        "validation_coverage": coverage,
                        "validation_alignment": alignment,
                    }
                },
                "source_package": {
                    "memory": memory,
                    "expected_answer": expected_answer,
                    "query": query,
                },
                "notes": [
                    f"max_cycle_drift={max_cycle_drift}",
                    f"min_keyword_score={min_keyword_score}",
                    f"generation_mode={generation_mode}",
                ],
            }
        )

        memory = f"{memory}\n{predicted_answer}".strip()

    return records
