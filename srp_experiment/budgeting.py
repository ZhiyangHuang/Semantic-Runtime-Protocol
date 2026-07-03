import os
from dataclasses import dataclass
from typing import Iterable, List


def approx_token_count(text: str) -> int:
    return len((text or "").split())


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return int(default)
    try:
        parsed = int(value)
    except ValueError:
        return int(default)
    return parsed if parsed > 0 else int(default)


@dataclass(frozen=True)
class BudgetConfig:
    total_tokens: int
    system_tokens: int
    output_tokens: int
    query_tokens: int
    safety_margin_tokens: int
    rag_chunk_tokens: int
    rag_top_k: int

    @property
    def prompt_budget_tokens(self) -> int:
        budget = self.total_tokens - self.system_tokens - self.output_tokens - self.query_tokens - self.safety_margin_tokens
        return max(64, budget)


def get_budget_config() -> BudgetConfig:
    return BudgetConfig(
        total_tokens=_env_int("SRP_TOTAL_TOKEN_BUDGET", 1024),
        system_tokens=_env_int("SRP_SYSTEM_TOKEN_BUDGET", 150),
        output_tokens=_env_int("SRP_OUTPUT_TOKEN_BUDGET", 120),
        query_tokens=_env_int("SRP_QUERY_TOKEN_BUDGET", 64),
        safety_margin_tokens=_env_int("SRP_SAFETY_MARGIN_TOKENS", 32),
        rag_chunk_tokens=_env_int("SRP_RAG_CHUNK_TOKENS", 256),
        rag_top_k=_env_int("SRP_RAG_TOP_K", 4),
    )


def available_memory_budget(query: str = "", constraints: Iterable[str] | None = None, extra_tokens: int = 0) -> int:
    budget = get_budget_config().prompt_budget_tokens
    budget -= approx_token_count(query)
    if constraints:
        budget -= approx_token_count(" ".join(str(item) for item in constraints))
    budget -= max(0, int(extra_tokens))
    return max(32, budget)


def clip_tail_to_budget(text: str, max_tokens: int) -> str:
    words = (text or "").split()
    if len(words) <= max_tokens:
        return text
    return " ".join(words[-max_tokens:])


def clip_head_to_budget(text: str, max_tokens: int) -> str:
    words = (text or "").split()
    if len(words) <= max_tokens:
        return text
    return " ".join(words[:max_tokens])


def chunk_text(text: str, chunk_tokens: int) -> List[str]:
    words = (text or "").split()
    if not words:
        return []
    return [" ".join(words[i : i + chunk_tokens]) for i in range(0, len(words), chunk_tokens)]


def pack_chunks_to_budget(chunks: Iterable[str], max_tokens: int) -> List[str]:
    packed: List[str] = []
    used = 0
    for chunk in chunks:
        chunk_tokens = approx_token_count(chunk)
        if not packed and chunk_tokens > max_tokens:
            packed.append(clip_head_to_budget(chunk, max_tokens))
            break
        if used + chunk_tokens > max_tokens:
            break
        packed.append(chunk)
        used += chunk_tokens
    return packed
