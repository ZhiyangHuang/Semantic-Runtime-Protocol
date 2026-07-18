from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
for path in (str(ROOT), str(REPO_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

from experiments.common.local_llm import build_local_client, iter_tasks, load_env
from experiments.srp_runtime_legacy.srp.pipeline import run_srp


DEFAULT_TASKS_PATH = ROOT / "data" / "longbench_v2" / "tasks_group_1.json"
DEFAULT_OUTPUT_PATH = ROOT / "diagnostics" / "local_llm_srp_runs.jsonl"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SRP diagnostics against a local OpenAI-compatible LLM.")
    parser.add_argument("--tasks", default=str(DEFAULT_TASKS_PATH), help="Path to canonical SRP task JSON.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="JSONL output path for per-task diagnostics.")
    parser.add_argument("--limit", type=int, default=1, help="Number of tasks to run.")
    parser.add_argument("--offset", type=int, default=0, help="Task offset.")
    parser.add_argument("--cycles", type=int, default=1, help="SRP compression/recovery cycles per task.")
    parser.add_argument("--smoke", action="store_true", help="Only test the local LLM connection.")
    parser.add_argument("--no-llm", action="store_true", help="Run SRP with client=None for deterministic offline debugging.")
    parser.add_argument("--max-cycle-drift", type=float, default=0.35)
    parser.add_argument("--min-keyword-score", type=float, default=0.5)
    return parser.parse_args()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_default(value: Any):
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    raise TypeError(f"Object of type {value.__class__.__name__} is not JSON serializable")


def summarize_records(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not records:
        return {"cycles": 0}
    last = records[-1]
    return {
        "cycles": len(records),
        "last_validation_passed": last.get("validation_passed"),
        "last_state_committed": last.get("state_committed"),
        "last_validation_score": last.get("validation_score"),
        "last_validation_drift": last.get("validation_drift"),
        "last_validation_coverage": last.get("validation_coverage"),
        "last_validation_alignment": last.get("validation_alignment"),
        "last_prompt_tokens": last.get("prompt_tokens"),
        "last_completion_tokens": last.get("completion_tokens"),
        "last_total_tokens": last.get("total_tokens"),
    }


def run_smoke(client) -> Dict[str, Any]:
    result = client.generate_with_usage(
        "/no_think\nReply with exactly this token and nothing else: SRP_LOCAL_LLM_OK",
        system_prompt="You are a concise diagnostic assistant. Do not include analysis or hidden reasoning.",
        max_output_tokens=64,
    )
    return {
        "ok": "SRP_LOCAL_LLM_OK" in result["text"],
        "text": result["text"],
        "usage": result.get("usage"),
        "model": result.get("model"),
        "latency_seconds": result.get("latency_seconds"),
    }


def main() -> int:
    args = parse_args()
    loaded_env = load_env()
    client = None if args.no_llm else build_local_client()

    if args.smoke:
        if client is None:
            print(json.dumps({"ok": True, "mode": "no-llm"}, indent=2))
            return 0
        result = run_smoke(client)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["ok"] else 1

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tasks_path = Path(args.tasks)
    task_count = 0
    failure_count = 0

    with output_path.open("w", encoding="utf-8") as handle:
        for task in iter_tasks(tasks_path, limit=args.limit, offset=args.offset):
            task_count += 1
            entry: Dict[str, Any] = {
                "timestamp": now_iso(),
                "task_id": task.get("id"),
                "task_type": task.get("task_type"),
                "model": os.getenv("SRP_MODEL"),
                "backend": "offline" if client is None else "local_openai_compatible",
                "local_model_url": None if client is None else client.base_url,
                "loaded_env_keys": sorted(loaded_env.keys()),
            }
            try:
                records = run_srp(
                    task,
                    cycles=args.cycles,
                    client=client,
                    max_cycle_drift=args.max_cycle_drift,
                    min_keyword_score=args.min_keyword_score,
                )
                entry["ok"] = True
                entry["summary"] = summarize_records(records)
                entry["records"] = records
            except Exception as exc:
                failure_count += 1
                entry["ok"] = False
                entry["error"] = str(exc)
                entry["traceback"] = traceback.format_exc()
            handle.write(json.dumps(entry, ensure_ascii=False, default=_json_default) + "\n")
            handle.flush()
            status = "ok" if entry["ok"] else "failed"
            print(f"[{status}] {entry.get('task_id')} -> {output_path}")

    print(
        json.dumps(
            {
                "tasks": task_count,
                "failures": failure_count,
                "output": str(output_path),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 1 if failure_count else 0


if __name__ == "__main__":
    raise SystemExit(main())

