from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parent
DATASET_ID = "zai-org/LongBench-v2"
ROWS_API = "https://datasets-server.huggingface.co/rows"
DEFAULT_TASKS_PATH = ROOT / "tasks.json"
DEFAULT_MANIFEST_PATH = ROOT / "manifest.json"
DEFAULT_LIMIT = 300
DEFAULT_OFFSET = 0
DEFAULT_PAGE_SIZE = 8
DEFAULT_MAX_RETRIES = 5

STOPWORDS = {
    "the",
    "and",
    "that",
    "with",
    "from",
    "this",
    "into",
    "your",
    "what",
    "which",
    "their",
    "there",
    "have",
    "will",
    "would",
    "should",
    "about",
    "following",
    "given",
    "using",
    "correct",
    "option",
    "answer",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import a frozen LongBench v2 subset into the SRP canonical task format.")
    parser.add_argument("--dataset", default=DATASET_ID)
    parser.add_argument("--split", default="train")
    parser.add_argument("--offset", type=int, default=DEFAULT_OFFSET)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE)
    parser.add_argument("--tasks-path", default=str(DEFAULT_TASKS_PATH))
    parser.add_argument("--manifest-path", default=str(DEFAULT_MANIFEST_PATH))
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT.parents[2] / path


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fetch_rows(dataset: str, split: str, offset: int, limit: int, page_size: int, max_retries: int = DEFAULT_MAX_RETRIES) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    next_offset = offset
    remaining = limit
    session = requests.Session()
    while remaining > 0:
        chunk = min(page_size, remaining)
        response = None
        for attempt in range(1, max_retries + 1):
            response = session.get(
                ROWS_API,
                params={
                    "dataset": dataset,
                    "config": "default",
                    "split": split,
                    "offset": next_offset,
                    "length": chunk,
                },
                timeout=60,
            )
            if response.ok:
                break
            if attempt == max_retries:
                response.raise_for_status()
            time.sleep(min(2 * attempt, 10))
        assert response is not None
        payload = response.json()
        batch = payload.get("rows", [])
        if not batch:
            break
        rows.extend(item["row"] for item in batch if "row" in item)
        consumed = len(batch)
        next_offset += consumed
        remaining -= consumed
        if consumed < chunk:
            break
    return rows


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def tokenize_keywords(*values: str, limit: int = 6) -> list[str]:
    tokens: list[str] = []
    seen = set()
    for value in values:
        for token in re.findall(r"[A-Za-z0-9]+", value.lower()):
            if len(token) < 4 or token in STOPWORDS:
                continue
            if token in seen:
                continue
            seen.add(token)
            tokens.append(token)
            if len(tokens) >= limit:
                return tokens
    return tokens


def build_query(question: str, choices: dict[str, str]) -> str:
    parts = [
        question.strip(),
        "",
        "Options:",
        f"A. {choices['A']}",
        f"B. {choices['B']}",
        f"C. {choices['C']}",
        f"D. {choices['D']}",
        "",
        "Answer with the correct option letter or the matching option text.",
    ]
    return "\n".join(parts)


def transform_row(row: dict[str, Any]) -> dict[str, Any]:
    choices = {
        "A": normalize_text(row.get("choice_A", "")),
        "B": normalize_text(row.get("choice_B", "")),
        "C": normalize_text(row.get("choice_C", "")),
        "D": normalize_text(row.get("choice_D", "")),
    }
    answer_letter = normalize_text(row.get("answer", "")).upper()
    correct_choice = choices.get(answer_letter, "")
    question = normalize_text(row.get("question", ""))
    context = normalize_text(row.get("context", ""))

    return {
        "id": f"longbench_v2::{row.get('_id', '')}",
        "task_type": "long_context_mcq",
        "source": "LongBench v2",
        "initial_state": {
            "memory": context,
            "constraints": [
                "preserve benchmark context",
                "preserve answer-critical evidence",
                "preserve option distinctions",
            ],
        },
        "queries": [
            build_query(question, choices),
        ],
        "query_expectations": [
            [
                [answer_letter, correct_choice],
            ]
        ],
        "expected_output": {
            "answer_letter": answer_letter,
            "answer_text": correct_choice,
        },
        "expected_keywords": tokenize_keywords(question, correct_choice),
        "metadata": {
            "benchmark": "LongBench v2",
            "family": "long_context",
            "split": "frozen_public_eval",
            "source": "zai-org/LongBench-v2",
            "source_id": row.get("_id"),
            "domain": row.get("domain"),
            "sub_domain": row.get("sub_domain"),
            "difficulty": row.get("difficulty"),
            "length": row.get("length"),
            "benchmark_type": "real_world",
            "context_chars": len(context),
        },
    }


def load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> int:
    args = parse_args()
    tasks_path = resolve_path(args.tasks_path)
    manifest_path = resolve_path(args.manifest_path)

    rows = fetch_rows(
        dataset=args.dataset,
        split=args.split,
        offset=args.offset,
        limit=args.limit,
        page_size=args.page_size,
    )
    tasks = [transform_row(row) for row in rows]

    payload = {
        "benchmark": "LongBench v2",
        "family": "long_context",
        "split": "frozen_public_eval",
        "selection_strategy": "first_n_frozen_subset",
        "selection_offset": args.offset,
        "selection_limit": args.limit,
        "source": args.dataset,
        "tasks": tasks,
    }
    tasks_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    manifest = load_manifest(manifest_path)
    manifest["source"] = args.dataset
    manifest["adapter_status"] = "implemented_frozen_subset"
    manifest["selection_strategy"] = "first_n_frozen_subset"
    manifest["selection_offset"] = args.offset
    manifest["selection_limit"] = args.limit
    manifest["imported_count"] = len(tasks)
    manifest["imported_at"] = now_iso()
    manifest["task_file"] = "srp_experiment/data/longbench_v2/tasks.json"
    manifest["notes"] = [
        "The current file stores a frozen public-evaluation subset rather than the full benchmark payload.",
        "Only benchmark content should vary; prompt family, query schedule, metric definitions, and cycle counts stay fixed.",
    ]
    write_manifest(manifest_path, manifest)

    print(f"[LongBench v2] Imported rows: {len(tasks)}")
    print(f"[LongBench v2] Tasks file: {tasks_path}")
    print(f"[LongBench v2] Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
