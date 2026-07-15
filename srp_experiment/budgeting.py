from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class BudgetConfig:
    model_context_tokens: int = 1024
    total_tokens: int = 1024
    system_tokens: int = 150
    output_tokens: int = 120
    query_tokens: int = 64
    safety_margin_tokens: int = 32
    prompt_overhead_tokens: int = 480


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def get_budget_config() -> BudgetConfig:
    return BudgetConfig(
        model_context_tokens=_env_int("SRP_MODEL_CONTEXT_BUDGET", 1024),
        total_tokens=_env_int("SRP_TOTAL_TOKEN_BUDGET", 1024),
        system_tokens=_env_int("SRP_SYSTEM_TOKEN_BUDGET", 150),
        output_tokens=_env_int("SRP_OUTPUT_TOKEN_BUDGET", 120),
        query_tokens=_env_int("SRP_QUERY_TOKEN_BUDGET", 64),
        safety_margin_tokens=_env_int("SRP_SAFETY_MARGIN_TOKENS", 32),
        prompt_overhead_tokens=_env_int("SRP_PROMPT_OVERHEAD_TOKENS", 480),
    )


def estimate_tokens(text: str) -> int:
    return max(1, len(str(text).split()))


def available_memory_budget(constraints: Iterable[str] | None = None) -> int:
    budget = get_budget_config()
    constraint_tokens = estimate_tokens(" ".join(constraints or []))
    return max(
        32,
        budget.total_tokens
        - budget.system_tokens
        - budget.output_tokens
        - budget.query_tokens
        - budget.safety_margin_tokens
        - budget.prompt_overhead_tokens
        - constraint_tokens,
    )


def clip_tail_to_budget(text: str, token_budget: int) -> str:
    words = str(text).split()
    if len(words) <= token_budget:
        return str(text)
    return " ".join(words[-token_budget:])
