from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


DEFAULT_ENV_PATH = Path(__file__).resolve().parent / ".env"


def load_env(path: str | Path = DEFAULT_ENV_PATH, override: bool = True) -> Dict[str, str]:
    """Load simple KEY=VALUE lines without requiring python-dotenv."""
    env_path = Path(path)
    loaded: Dict[str, str] = {}
    if not env_path.exists():
        return loaded

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and (override or key not in os.environ):
            os.environ[key] = value
        if key:
            loaded[key] = value
    return loaded


def _join_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def strip_thinking_blocks(text: str) -> str:
    """Remove visible reasoning traces used by Qwen/DeepSeek-style models."""
    source = str(text)
    cleaned = re.sub(r"<think>.*?</think>", "", source, flags=re.IGNORECASE | re.DOTALL)
    if re.search(r"^\s*<think>", cleaned, flags=re.IGNORECASE):
        return ""
    return cleaned.strip()


class LocalOpenAICompatibleClient:
    """Minimal client for local OpenAI-compatible chat-completions servers."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        api_key: Optional[str] = None,
    ) -> None:
        load_env()
        self.base_url = base_url or os.getenv("LOCAL_MODEL_URL", "http://localhost:8000")
        self.model = model or os.getenv("SRP_MODEL", "local-model")
        self.timeout_seconds = float(timeout_seconds or os.getenv("SRP_TIMEOUT_SECONDS", "120"))
        self.api_key = api_key or os.getenv("LOCAL_MODEL_API_KEY", "EMPTY")
        self.disable_thinking = _env_bool("SRP_DISABLE_THINKING", True)
        self.strip_thinking = _env_bool("SRP_STRIP_THINKING", True)
        self.thinking_prefix = os.getenv("SRP_THINKING_PREFIX", "/no_think").strip()
        self.use_chat_template_kwargs = _env_bool("SRP_CHAT_TEMPLATE_DISABLE_THINKING", True)

    def generate_with_usage(
        self,
        prompt: str,
        system_prompt: str = "",
        max_output_tokens: int = 128,
        temperature: float = 0.0,
    ) -> Dict[str, Any]:
        messages: List[Dict[str, str]] = []
        if self.disable_thinking and self.thinking_prefix:
            prompt = f"{self.thinking_prefix}\n{prompt}"
            if system_prompt:
                system_prompt = (
                    f"{system_prompt}\nDo not include hidden reasoning, scratchpads, or <think> blocks. "
                    "Return only the requested final content."
                )
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_output_tokens,
        }
        if self.disable_thinking and self.use_chat_template_kwargs:
            payload["chat_template_kwargs"] = {"enable_thinking": False}
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            _join_url(self.base_url, "/v1/chat/completions"),
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )

        started_at = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Local LLM HTTP {exc.code}: {body[:1000]}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Local LLM connection failed: {exc}") from exc

        parsed = json.loads(raw)
        choices = parsed.get("choices") or []
        if not choices:
            raise RuntimeError(f"Local LLM returned no choices: {raw[:1000]}")
        message = choices[0].get("message") or {}
        raw_text = str(message.get("content", "")).strip()
        text = strip_thinking_blocks(raw_text) if self.strip_thinking else raw_text
        if self.strip_thinking and not text and raw_text:
            text = raw_text
        return {
            "text": text,
            "raw_text": raw_text,
            "stripped_thinking": text != raw_text,
            "usage": parsed.get("usage"),
            "model": parsed.get("model", self.model),
            "latency_seconds": round(time.perf_counter() - started_at, 4),
            "raw_id": parsed.get("id"),
        }

    def list_models(self) -> List[str]:
        request = urllib.request.Request(
            _join_url(self.base_url, "/v1/models"),
            method="GET",
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            parsed = json.loads(response.read().decode("utf-8"))
        return [str(item.get("id")) for item in parsed.get("data", []) if item.get("id")]


def build_local_client() -> LocalOpenAICompatibleClient:
    load_env()
    return LocalOpenAICompatibleClient()


def iter_tasks(path: str | Path, limit: Optional[int] = None, offset: int = 0) -> Iterable[Dict[str, Any]]:
    """Load the canonical task file and yield tasks after offset.

    The current LongBench v2 files are JSON objects with a top-level "tasks"
    array. This function keeps task loading in one place so diagnostics can be
    swapped to a streaming parser later if the dataset grows further.
    """
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    tasks = payload.get("tasks", [])
    end = None if limit is None else offset + limit
    for task in tasks[offset:end]:
        yield task
