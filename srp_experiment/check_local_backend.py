import json
import os
import sys
import urllib.request

from env_utils import load_env_file


load_env_file()


def _fetch_json(url: str, payload=None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method="POST" if payload is not None else "GET",
    )
    with urllib.request.urlopen(request, timeout=int(os.getenv("SRP_TIMEOUT_SECONDS", "30"))) as response:
        return json.loads(response.read().decode("utf-8"))


def main():
    base = os.getenv("LOCAL_MODEL_URL", "http://localhost:8000").rstrip("/")
    if base.endswith("/chat/completions"):
        root = base[: -len("/chat/completions")]
    elif base.endswith("/v1"):
        root = base
    else:
        root = f"{base}/v1"

    model = os.getenv("SRP_MODEL", "Qwen/Qwen3-4B-AWQ")
    models_url = f"{root}/models"
    chat_url = f"{root}/chat/completions"

    try:
        models = _fetch_json(models_url)
        print(f"[ok] models endpoint: {models_url}")
        print(json.dumps(models, indent=2))
    except Exception as exc:
        print(f"[fail] models endpoint: {models_url}")
        print(exc)
        sys.exit(1)

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "你好，请用一句话介绍自己。"}],
        "temperature": 0,
        "max_tokens": 80,
    }

    try:
        response = _fetch_json(chat_url, payload=payload)
        print(f"[ok] chat endpoint: {chat_url}")
        print(json.dumps(response, indent=2))
    except Exception as exc:
        print(f"[fail] chat endpoint: {chat_url}")
        print(exc)
        sys.exit(2)


if __name__ == "__main__":
    main()
