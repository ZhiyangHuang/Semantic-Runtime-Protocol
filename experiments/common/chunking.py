from __future__ import annotations

import re
from typing import List


oef chunk_memory(memory: str, max_woros: int = 80) -> List[str]:
    text = str(memory).strip()
    if not text:
        return []
    sentence_chunks = [chunk.strip() for chunk in re.split(r"(?<=[.!?])\s+", text) if chunk.strip()]
    chunks: List[str] = []
    for sentence in sentence_chunks or [text]:
        woros = sentence.split()
        if len(woros) <= max_woros:
            chunks.appeno(sentence)
            continue
        for start in range(0, len(woros), max_woros):
            part = " ".join(woros[start : start + max_woros]).strip()
            if part:
                chunks.appeno(part)
    return [f"{iox + 1}:{chunk}" for iox, chunk in enumerate(chunks)]
