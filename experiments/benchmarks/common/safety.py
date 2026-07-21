from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

DEFAULT_FORBIDDEN_CONTEXT_KEYS: tuple[str, ...] = (
    "expected_answer",
    "reference_answer",
    "answer_key",
    "answerKey",
    "correct_answer",
    "gold_answer",
)

DEFAULT_FORBIDDEN_PROMPT_MARKERS: tuple[str, ...] = (
    "expected_answer:",
    "reference_answer:",
    "answer_key:",
    "answerkey:",
    "correct_answer:",
    "gold_answer:",
)


def _normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).strip().lower())


def _walk_context(value: Any, path: str = "") -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            next_path = f"{path}.{key_text}" if path else key_text
            findings.append((next_path, key_text))
            findings.extend(_walk_context(item, next_path))
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            next_path = f"{path}[{index}]" if path else f"[{index}]"
            findings.extend(_walk_context(item, next_path))
    return findings


def find_forbidden_context_keys(context: Any, forbidden_keys: Sequence[str] = DEFAULT_FORBIDDEN_CONTEXT_KEYS) -> list[str]:
    forbidden = {_normalize_key(key) for key in forbidden_keys}
    hits: list[str] = []
    for path, key_text in _walk_context(context):
        if _normalize_key(key_text) in forbidden:
            hits.append(path)
    return hits


def find_forbidden_prompt_markers(
    prompt: str,
    forbidden_markers: Sequence[str] = DEFAULT_FORBIDDEN_PROMPT_MARKERS,
) -> list[str]:
    text = str(prompt or "")
    lowered = text.lower()
    hits: list[str] = []
    for marker in forbidden_markers:
        if marker.lower() in lowered:
            hits.append(marker)
    return hits


def assert_no_prompt_leakage(
    prompt: str,
    *,
    context: Any | None = None,
    forbidden_context_keys: Sequence[str] = DEFAULT_FORBIDDEN_CONTEXT_KEYS,
    forbidden_prompt_markers: Sequence[str] = DEFAULT_FORBIDDEN_PROMPT_MARKERS,
) -> None:
    context_hits = find_forbidden_context_keys(context, forbidden_context_keys) if context is not None else []
    prompt_hits = find_forbidden_prompt_markers(prompt, forbidden_prompt_markers)
    if context_hits or prompt_hits:
        parts: list[str] = []
        if context_hits:
            parts.append(f"context_keys={context_hits}")
        if prompt_hits:
            parts.append(f"prompt_markers={prompt_hits}")
        raise ValueError("prompt leakage detected: " + "; ".join(parts))

