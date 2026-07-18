import json
import os
import re
from typing import Dict, List, Sequence, Tuple


def llm_chunk_judge_enabled() -> bool:
    return str(os.getenv("SRP_USE_LLM_JUDGE", "false")).strip().lower() in {"1", "true", "yes", "on"}


def extract_json_object(raw_text: str):
    cleaned = str(raw_text).strip()
    if not cleaned:
        raise json.JSONDecodeError("empty response", cleaned, 0)

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    if start < 0:
        raise json.JSONDecodeError("no JSON object found", cleaned, 0)

    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(cleaned)):
        char = cleaned[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return json.loads(cleaned[start : index + 1])

    raise json.JSONDecodeError("unterminated JSON object", cleaned, start)


def apply_llm_chunk_judge(
    selected_chunks: List[Dict[str, object]],
    constraints: Sequence[str],
    expected_keywords: Sequence[str] | None = None,
    client=None,
) -> Tuple[List[Dict[str, object]], Dict[str, object]]:
    judge_calls = 0
    judge_failures = 0
    if not llm_chunk_judge_enabled() or client is None:
        return selected_chunks, {
            "enabled": False,
            "judge_calls": judge_calls,
            "judge_failures": judge_failures,
        }

    adjusted: List[Dict[str, object]] = []
    for chunk in selected_chunks:
        judge_calls += 1
        try:
            prompt = (
                "Given task constraints and a memory chunk, score whether this chunk is answer-critical from 0 to 1.\n"
                "Return only JSON: {\"score\": 0.0, \"reason\": \"...\"}\n\n"
                f"Constraints: {'; '.join(constraints)}\n"
                f"Expected keywords: {'; '.join(expected_keywords or [])}\n"
                f"Chunk: {chunk['text']}"
            )
            if hasattr(client, "generate_with_usage"):
                result = client.generate_with_usage(
                    prompt,
                    system_prompt="You score chunk saliency.",
                    max_output_tokens=64,
                )
                raw_text = result.get("text", "")
            else:
                raw_text = client.generate(prompt)
            parsed = extract_json_object(raw_text)
            bonus = float(parsed.get("score", 0.0))
            reason = str(parsed.get("reason", "")).strip()
            chunk = dict(chunk)
            chunk["llm_judge_score"] = max(0.0, min(1.0, bonus))
            chunk["llm_judge_reason"] = reason
            chunk["score"] = round(min(1.0, float(chunk["score"]) + 0.2 * chunk["llm_judge_score"]), 4)
            chunk["reason"] = f"{chunk['reason']}; llm={chunk['llm_judge_score']:.3f}"
            adjusted.append(chunk)
        except Exception:
            judge_failures += 1
            adjusted.append(chunk)
    adjusted.sort(key=lambda item: (-float(item["score"]), int(item["chunk_id"])))
    return adjusted, {
        "enabled": True,
        "judge_calls": judge_calls,
        "judge_failures": judge_failures,
    }
