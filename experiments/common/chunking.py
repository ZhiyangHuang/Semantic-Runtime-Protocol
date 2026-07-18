from __future__ import annotations

import re
from typing import List


def chunk_memory(memory: str, max_words: int = 80) -> List[str]:
    text = str(memory).strip()
    if not text:
        return []
    sentence_chunks = [chunk.strip() for chunk in re.split(r"(?<=[.!?])\s+", text) if chunk.strip()]
    chunks: List[str] = []
    for sentence in sentence_chunks or [text]:
        words = sentence.split()
        if len(words) <= max_words:
            chunks.append(sentence)
            continue
        for start in range(0, len(words), max_words):
            part = " ".join(words[start : start + max_words]).strip()
            if part:
                chunks.append(part)
    return [f"{idx + 1}:{chunk}" for idx, chunk in enumerate(chunks)]
