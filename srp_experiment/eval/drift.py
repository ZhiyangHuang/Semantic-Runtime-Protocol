from typing import List


def _token_set(text: str) -> set:
    return {token.strip(".,").lower() for token in text.split() if token.strip(".,")}


def compute_drift(reference: str, candidate: str) -> float:
    ref = _token_set(reference)
    cand = _token_set(candidate)
    if not ref and not cand:
        return 0.0
    overlap = len(ref & cand)
    union = len(ref | cand)
    similarity = overlap / max(union, 1)
    return round(1.0 - similarity, 4)
