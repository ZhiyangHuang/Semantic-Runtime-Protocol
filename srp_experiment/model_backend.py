import json
import os
import http.client
import re
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Dict, Optional


def _truncate_words(text: str, max_words: int) -> str:
    words = text.split()
    return " ".join(words[:max_words])


def _extract_mock_anchor_terms(text: str, limit: int = 6) -> list[str]:
    words = [word.strip(".,;:!?()[]{}\"'").lower() for word in text.split()]
    unique: list[str] = []
    for word in words:
        if len(word) > 4 and word not in unique:
            unique.append(word)
    return unique[:limit]


def _extract_prompt_block(prompt: str, header: str, stop_headers: list[str]) -> str:
    lowered = prompt.lower()
    marker = f"{header.lower()}:"
    if marker not in lowered:
        return ""
    start = lowered.index(marker) + len(marker)
    remaining_original = prompt[start:]
    remaining_lowered = lowered[start:]
    end = len(remaining_original)
    for stop_header in stop_headers:
        stop_marker = f"{stop_header.lower()}:"
        idx = remaining_lowered.find(stop_marker)
        if idx != -1:
            end = min(end, idx)
    return remaining_original[:end].strip()


@dataclass
class BackendConfig:
    backend: str = "mock"
    model: str = "gpt-4o-mini"
    openai_api_key: Optional[str] = None
    openai_base_url: str = "https://api.openai.com/v1"
    local_model_url: Optional[str] = None
    timeout_seconds: int = 60

    @classmethod
    def from_env(cls, backend: Optional[str] = None, model: Optional[str] = None) -> "BackendConfig":
        return cls(
            backend=backend or os.getenv("SRP_BACKEND", "mock"),
            model=model or os.getenv("SRP_MODEL", "gpt-4o-mini"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
            local_model_url=os.getenv("LOCAL_MODEL_URL"),
            timeout_seconds=int(os.getenv("SRP_TIMEOUT_SECONDS", "60")),
        )


class ModelClient:
    def __init__(self, config: BackendConfig):
        self.config = config

    def generate(self, prompt: str, system_prompt: Optional[str] = None, max_output_tokens: int = 256) -> str:
        result = self.generate_with_usage(prompt, system_prompt=system_prompt, max_output_tokens=max_output_tokens)
        return result["text"]

    def generate_with_usage(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_output_tokens: int = 256,
    ) -> Dict:
        backend = self.config.backend.lower()
        if backend == "mock":
            return {"text": self._mock_generate(prompt), "usage": None}
        if backend == "openai":
            return self._openai_generate(prompt, system_prompt, max_output_tokens)
        if backend == "local":
            return self._local_generate(prompt, system_prompt, max_output_tokens)
        raise ValueError(f"Unsupported backend: {self.config.backend}")

    def describe(self) -> Dict[str, Optional[str]]:
        description: Dict[str, Optional[str]] = {
            "backend": self.config.backend.lower(),
            "model": self.config.model,
            "timeout_seconds": self.config.timeout_seconds,
        }
        if self.config.backend.lower() == "openai":
            description["api_base"] = self.config.openai_base_url
        if self.config.backend.lower() == "local":
            description["endpoint"] = self._resolve_local_url()
        return description

    def _mock_generate(self, prompt: str) -> str:
        lowered = prompt.lower()
        is_recovery_prompt = lowered.startswith("reconstruct a concise task-grounded semantic memory")
        is_compression_prompt = lowered.startswith("compress this semantic runtime state")
        if "answer the query using only the provided memory snapshot" in lowered:
            memory_text = _extract_prompt_block(prompt, "Memory snapshot", ["Query"])
            return _truncate_words(memory_text.replace("\n", " ").strip(), 28)
        if is_recovery_prompt:
            anchor_memory = _extract_prompt_block(
                prompt,
                "Anchor memory",
                ["Compact representation", "Constraints", "Global vocabulary", "Local vocabulary", "Policy"],
            )
            compact = _extract_prompt_block(
                prompt,
                "Compact representation",
                ["Constraints", "Global vocabulary", "Local vocabulary", "Policy"],
            )
            recovery_source = compact or anchor_memory
            if compact:
                try:
                    payload = json.loads(compact)
                    recovery_source = str(payload.get("memory_summary", "")).strip() or recovery_source
                except json.JSONDecodeError:
                    pass
            recovered = _truncate_words(recovery_source.replace("\n", " ").strip(), 22)
            if recovered and recovered[-1] not in ".!?":
                recovered = f"{recovered}."
            return recovered
        if is_compression_prompt:
            memory_text = _extract_prompt_block(
                prompt,
                "Memory",
                ["Constraints", "Global vocabulary", "Local vocabulary", "Policy"],
            )
            constraints_text = _extract_prompt_block(
                prompt,
                "Constraints",
                ["Global vocabulary", "Local vocabulary", "Policy"],
            )
            constraints = [item.strip() for item in constraints_text.split(",") if item.strip()]
            summary = _truncate_words(memory_text.replace("\n", " ").strip(), 18)
            anchor_terms = _extract_mock_anchor_terms(summary)
            return json.dumps(
                {
                    "memory_summary": summary,
                    "constraints": constraints,
                    "anchor_terms": anchor_terms,
                }
            )
        if "summarize" in lowered or "summary" in lowered:
            memory_text = _extract_prompt_block(prompt, "Memory", [])
            return _truncate_words(memory_text.replace("\n", " ").strip(), 16)
        if "judge" in lowered or "equivalent" in lowered:
            return "Score: 0.75. The candidate preserves most task-relevant keywords."
        return _truncate_words(prompt.replace("\n", " "), 24)

    def _openai_generate(self, prompt: str, system_prompt: Optional[str], max_output_tokens: int) -> Dict:
        api_key = self.config.openai_api_key
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set. Cannot use backend=openai.")
        payload = self._build_chat_payload(prompt, system_prompt, max_output_tokens)
        request = urllib.request.Request(
            f"{self.config.openai_base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"OpenAI request failed: {exc.code} {details}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"OpenAI request failed: {exc}") from exc
        return self._extract_text(body, source="OpenAI")

    def _local_generate(self, prompt: str, system_prompt: Optional[str], max_output_tokens: int) -> Dict:
        url = self._resolve_local_url()
        if not url:
            raise RuntimeError("LOCAL_MODEL_URL is not set. Cannot use backend=local.")
        payload: Dict = self._build_chat_payload(prompt, system_prompt, max_output_tokens)
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except http.client.RemoteDisconnected as exc:
            raise RuntimeError(
                f"Local model request failed: {exc}.{self._build_local_empty_reply_hint()}"
            ) from exc
        except urllib.error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Local model request failed: {exc.code} {details}") from exc
        except urllib.error.URLError as exc:
            message = f"Local model request failed: {exc}"
            if self._is_localhost_endpoint() and self._looks_like_empty_reply(str(exc)):
                message = f"{message}.{self._build_local_empty_reply_hint()}"
            raise RuntimeError(message) from exc
        return self._extract_text(body, source="local model")

    def _build_chat_payload(self, prompt: str, system_prompt: Optional[str], max_output_tokens: int) -> Dict:
        prompt, system_prompt = self._prepare_chat_prompts(prompt, system_prompt)
        payload = {
            "model": self.config.model,
            "messages": [],
            "temperature": 0,
            "max_tokens": max_output_tokens,
        }
        if system_prompt:
            payload["messages"].append({"role": "system", "content": system_prompt})
        payload["messages"].append({"role": "user", "content": prompt})
        return payload

    def _prepare_chat_prompts(self, prompt: str, system_prompt: Optional[str]) -> tuple[str, Optional[str]]:
        if self.config.backend.lower() != "local":
            return prompt, system_prompt
        if "qwen" not in self.config.model.lower():
            return prompt, system_prompt
        no_think = "/no_think"
        if system_prompt:
            if no_think not in system_prompt:
                system_prompt = f"{no_think}\n{system_prompt}"
            return prompt, system_prompt
        if no_think not in prompt:
            prompt = f"{no_think}\n{prompt}"
        return prompt, system_prompt

    def _resolve_local_url(self) -> Optional[str]:
        url = self.config.local_model_url
        if not url:
            return None
        normalized = url.rstrip("/")
        if normalized.endswith("/chat/completions"):
            return normalized
        if normalized.endswith("/v1"):
            return f"{normalized}/chat/completions"
        return f"{normalized}/v1/chat/completions"

    def _is_localhost_endpoint(self) -> bool:
        url = (self.config.local_model_url or "").lower()
        return "localhost" in url or "127.0.0.1" in url

    def _looks_like_empty_reply(self, message: str) -> bool:
        lowered = message.lower()
        return "remote end closed connection without response" in lowered or "empty reply" in lowered

    def _suggest_wsl_ip(self) -> Optional[str]:
        try:
            result = subprocess.run(
                ["wsl.exe", "hostname", "-I"],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )
        except Exception:
            return None
        candidates = [part.strip() for part in result.stdout.split() if part.strip()]
        return candidates[0] if candidates else None

    def _build_local_empty_reply_hint(self) -> str:
        if not self._is_localhost_endpoint():
            return ""
        suggested_ip = self._suggest_wsl_ip()
        if suggested_ip:
            return (
                " localhost appears to be hitting a WSL forwarding issue. "
                f"Please use the active WSL IP instead, for example set LOCAL_MODEL_URL=http://{suggested_ip}:8000."
            )
        return (
            " localhost appears to be hitting a WSL forwarding issue. "
            "Please use the active WSL IP instead of localhost for LOCAL_MODEL_URL."
        )

    def _extract_text(self, body: Dict, source: str) -> Dict:
        if "choices" in body:
            try:
                message = body["choices"][0]["message"]["content"]
                if isinstance(message, list):
                    chunks = [part.get("text", "") for part in message if isinstance(part, dict)]
                    text = self._postprocess_text(" ".join(chunk for chunk in chunks if chunk))
                else:
                    text = self._postprocess_text(str(message))
                return {"text": text, "usage": self._extract_usage(body)}
            except (KeyError, IndexError, TypeError) as exc:
                raise RuntimeError(f"Unexpected {source} response: {body}") from exc
        if "text" in body:
            return {"text": self._postprocess_text(str(body["text"])), "usage": self._extract_usage(body)}
        if "output" in body:
            return {"text": self._postprocess_text(str(body["output"])), "usage": self._extract_usage(body)}
        raise RuntimeError(f"Unexpected {source} response: {body}")

    def _extract_usage(self, body: Dict) -> Optional[Dict[str, int]]:
        usage = body.get("usage")
        if not isinstance(usage, dict):
            return None
        prompt_tokens = usage.get("prompt_tokens")
        completion_tokens = usage.get("completion_tokens")
        total_tokens = usage.get("total_tokens")
        normalized = {}
        if isinstance(prompt_tokens, int):
            normalized["prompt_tokens"] = prompt_tokens
        if isinstance(completion_tokens, int):
            normalized["completion_tokens"] = completion_tokens
        if isinstance(total_tokens, int):
            normalized["total_tokens"] = total_tokens
        return normalized or None

    def _postprocess_text(self, text: str) -> str:
        cleaned = text.strip()
        cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.DOTALL | re.IGNORECASE).strip()
        return cleaned
