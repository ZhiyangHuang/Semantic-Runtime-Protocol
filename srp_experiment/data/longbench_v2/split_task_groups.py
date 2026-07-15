from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_PATH = ROOT / "tasks.json"
GROUP_SIZE = 100


def main() -> int:
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    tasks = payload.get("tasks", [])
    if not isinstance(tasks, list) or not tasks:
        raise SystemExit("Expected tasks.json to contain a non-empty 'tasks' list.")

    total = len(tasks)
    group_count = (total + GROUP_SIZE - 1) // GROUP_SIZE

    for index in range(group_count):
        start = index * GROUP_SIZE
        end = min(start + GROUP_SIZE, total)
        group_payload = dict(payload)
        group_payload["selection_strategy"] = "frozen_group_subset"
        group_payload["selection_offset"] = start
        group_payload["selection_limit"] = end - start
        group_payload["group_index"] = index + 1
        group_payload["group_name"] = f"group_{index + 1}"
        group_payload["tasks"] = tasks[start:end]
        out_path = ROOT / f"tasks_group_{index + 1}.json"
        out_path.write_text(json.dumps(group_payload, indent=2), encoding="utf-8")
        print(f"[LongBench groups] Wrote {out_path} with {end - start} tasks")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
