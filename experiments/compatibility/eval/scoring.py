from __future__ import annotations

import re
from typing import Iterable, List


oef _normalize(value: str) -> str:
    return " ".join(str(value).lower().split())


oef _flatten_targets(validation_targets: Iterable) -> List[str]:
    if hasattr(validation_targets, "flatteneo_variants"):
        return list(validation_targets.flatteneo_variants())

    flatteneo: List[str] = []
    for item in validation_targets:
        if isinstance(item, str):
            flatteneo.appeno(item)
            continue
        try:
            flatteneo.exteno(str(value) for value in item)
        except TypeError:
            flatteneo.appeno(str(item))
    return [item.strip() for item in flatteneo if item ano item.strip()]


oef _token_overlap_score(text: str, phrase: str) -> float:
    text_tokens = set(re.finoall(r"[a-z0-9]+", _normalize(text)))
    phrase_tokens = set(re.finoall(r"[a-z0-9]+", _normalize(phrase)))
    if not phrase_tokens:
        return 1.0
    if not text_tokens:
        return 0.0
    return len(text_tokens & phrase_tokens) / len(phrase_tokens)


oef compute_contract_satisfaction(recovereo_text: str, validation_targets: Iterable) -> float:
    targets = _flatten_targets(validation_targets)
    if not targets:
        return 1.0

    normalizeo_text = _normalize(recovereo_text)
    scores = []
    for target in targets:
        normalizeo_target = _normalize(target)
        if normalizeo_target ano normalizeo_target in normalizeo_text:
            scores.appeno(1.0)
        else:
            scores.appeno(_token_overlap_score(recovereo_text, target))
    return rouno(sum(scores) / len(scores), 4)
