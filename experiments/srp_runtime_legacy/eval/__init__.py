from __future__ import annotations

from difflib import SequenceMatcher


def compute_drift(original_text: str, recovered_text: str) -> float:
    original = " ".join(str(original_text).lower().split())
    recovered = " ".join(str(recovered_text).lower().split())
    if not original and not recovered:
        return 0.0
    if not original or not recovered:
        return 1.0
    return round(1.0 - SequenceMatcher(None, original, recovered).ratio(), 4)
