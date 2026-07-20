from __future__ import annotations

import re
from typing import Iterable, List


def _normalize(value: str) -> str:
    return " ".join(str(value).lower().split())


def _flatten_targets(validation_targets: Iterable) -> List[str]:
    if hasattr(validation_targets, "flattened_variants"):
        return list(validation_targets.flattened_variants())

    flattened: List[str] = []
    for item in validation_targets:
        if isinstance(item, str):
            flattened.append(item)
            continue
        try:
            flattened.extend(str(value) for value in item)
        except TypeError:
            flattened.append(str(item))
    return [item.strip() for item in flattened if item and item.strip()]


def _token_overlap_score(text: str, phrase: str) -> float:
    text_tokens = set(re.findall(r"[a-z0-9]+", _normalize(text)))
    phrase_tokens = set(re.findall(r"[a-z0-9]+", _normalize(phrase)))
    if not phrase_tokens:
        return 1.0
    if not text_tokens:
        return 0.0
    return len(text_tokens & phrase_tokens) / len(phrase_tokens)


def compute_contract_satisfaction(recovered_text: str, validation_targets: Iterable) -> float:
    targets = _flatten_targets(validation_targets)
    if not targets:
        return 1.0

    normalized_text = _normalize(recovered_text)
    scores = []
    for target in targets:
        normalized_target = _normalize(target)
        if normalized_target and normalized_target in normalized_text:
            scores.append(1.0)
        else:
            scores.append(_token_overlap_score(recovered_text, target))
    return round(sum(scores) / len(scores), 4)
