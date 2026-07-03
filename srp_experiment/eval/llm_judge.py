from typing import Dict, Iterable

from prompting import build_judge_prompt
from .scoring import compute_contract_satisfaction


def _flatten_expectations(expected_keywords: Iterable) -> list[str]:
    flattened = []
    for item in expected_keywords:
        if isinstance(item, str):
            flattened.append(item)
        else:
            try:
                group = [str(value).strip() for value in item if str(value).strip()]
            except TypeError:
                flattened.append(str(item).strip())
                continue
            if group:
                flattened.append(" / ".join(group))
    return flattened


def score_semantic_equivalence(reference: str, candidate: str, expected_keywords: Iterable, client=None) -> Dict:
    keywords = list(expected_keywords)
    if client is None:
        proxy_score = compute_contract_satisfaction(candidate, keywords)
        return {
            "judge_name": "contract_proxy_judge",
            "score": proxy_score,
            "explanation": "Proxy score based on semantic contract satisfaction.",
            "usage": None,
        }

    proxy_score = compute_contract_satisfaction(candidate, keywords)
    if len(reference) + len(candidate) > 20000:
        return {
            "judge_name": "contract_proxy_judge_fallback",
            "score": proxy_score,
            "explanation": "Fallback to contract proxy judge because the semantic judge prompt would exceed the local model context budget.",
            "usage": None,
        }

    prompt = build_judge_prompt(reference, candidate, _flatten_expectations(keywords))
    try:
        model_result = client.generate_with_usage(
            prompt,
            system_prompt="You are a careful semantic equivalence judge for long-horizon LLM experiments.",
            max_output_tokens=120,
        )
    except RuntimeError as exc:
        message = str(exc).lower()
        if "maximum context length" in message or "upper bound" in message or "input_text" in message:
            return {
                "judge_name": "contract_proxy_judge_fallback",
                "score": proxy_score,
                "explanation": "Fallback to contract proxy judge after local judge request exceeded the backend context budget.",
                "usage": None,
            }
        raise
    output = model_result["text"]
    lowered = output.lower()
    score = 0.5
    for token in output.replace(",", " ").split():
        try:
            numeric = float(token)
            if 0.0 <= numeric <= 1.0:
                score = numeric
                break
        except ValueError:
            continue
    return {
        "judge_name": "llm_judge",
        "score": score,
        "explanation": lowered[:200],
        "usage": model_result.get("usage"),
    }
