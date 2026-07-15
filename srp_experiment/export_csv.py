import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from srp_experiment.srp.export import write_records_csv
from srp_experiment.srp.pipeline import run_srp


def _load_records(path: Path):
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def _load_tasks(path: Path):
    with path.open("r", encoding="utf-8-sig") as handle:
        payload = json.load(handle)
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        if "tasks" in payload and isinstance(payload["tasks"], list):
            return payload["tasks"]
        return [payload]
    raise ValueError(f"Unsupported task payload in {path}")


def _load_tasks_jsonl(path: Path):
    tasks = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                tasks.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_number}") from exc
    return tasks


def _expand_task_inputs(values):
    expanded = []
    for value in values or []:
        path = Path(value)
        if path.is_dir():
            expanded.extend(sorted(path.glob("*.json")))
        else:
            expanded.append(path)
    return expanded


def _apply_task_identity(record: dict, task: dict, task_path: Path, task_id_prefix: str = "") -> None:
    task_id = task.get("id") if isinstance(task, dict) else None
    if task_id_prefix and task_id:
        task_id = f"{task_id_prefix}{task_id}"
    record["task_id"] = task_id
    record["task_source"] = str(task_path)


def _default_task() -> dict:
    return {
        "id": "export-csv-demo",
        "initial_state": {
            "constraints": ["Preserve the key fact."],
            "memory": "Preserve the key fact while keeping the summary compact.",
        },
        "query_expectations": [[["Preserve the key fact."]]],
        "expected_keywords": ["fact", "summary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export SRP run records to CSV.")
    parser.add_argument("--input-json", type=Path, help="Path to a JSON file containing SRP records.")
    parser.add_argument(
        "--task-json",
        action="append",
        default=[],
        help="Path to a task JSON file, a JSON object/list of tasks, or a directory of task JSON files. Repeatable.",
    )
    parser.add_argument(
        "--input-jsonl",
        action="append",
        default=[],
        help="Path to a JSONL file containing one task per line. Repeatable.",
    )
    parser.add_argument(
        "--task-id-prefix",
        default="",
        help="Prefix applied to task_id during batch exports, useful for grouping experiments.",
    )
    parser.add_argument("--output-csv", type=Path, default=Path("srp_experiment") / "tmp" / "srp_records.csv")
    parser.add_argument("--cycles", type=int, default=1, help="Number of SRP cycles to run when no input JSON is provided.")
    args = parser.parse_args()

    if args.input_json is not None:
        records = _load_records(args.input_json)
    elif args.task_json or args.input_jsonl:
        records = []
        for task_path in _expand_task_inputs(args.task_json):
            tasks = _load_tasks(task_path)
            for task in tasks:
                task_records = run_srp(task, cycles=args.cycles, client=None)
                for record in task_records:
                    _apply_task_identity(record, task, task_path, args.task_id_prefix)
                records.extend(task_records)
        for task_path in args.input_jsonl:
            path = Path(task_path)
            tasks = _load_tasks_jsonl(path)
            for task in tasks:
                task_records = run_srp(task, cycles=args.cycles, client=None)
                for record in task_records:
                    _apply_task_identity(record, task, path, args.task_id_prefix)
                records.extend(task_records)
    else:
        records = run_srp(_default_task(), cycles=args.cycles, client=None)

    output_path = write_records_csv(records, args.output_csv)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
