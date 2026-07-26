from __future__ import annotations

import re


def canonicalize_semantic_value(value: str) -> str:
    text = " ".join(str(value).strip().lower().split())
    text = re.sub(r"[\u2018\u2019]", "'", text)
    text = re.sub(r"[\u201c\u201d]", '"', text)
    text = re.sub(r"[^\w\s/.-]+", " ", text)
    text = " ".join(text.split())
    return text
