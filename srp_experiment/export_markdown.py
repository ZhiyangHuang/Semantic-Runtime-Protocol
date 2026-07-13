import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from srp_experiment.export_csv import _apply_task_identity
from srp_experiment.export_csv import _default_task
from srp_experiment.export_csv import _expand_task_inputs
from srp_experiment.export_csv import _load_records
from srp_experiment.export_csv import _load_tasks
from srp_experiment.export_csv import _load_tasks_jsonl
from srp_experiment.srp.export import write_records_markdown
from srp_experiment.srp.pipeline import run_srp


def main() -> int:
    parser = argparse.ArgumentParser(description="Export SRP run records to markdown audit output.")
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
    parser.add_argument("--output-markdown", type=Path, default=Path("srp_experiment") / "tmp" / "srp_audit.md")
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

    output_path = write_records_markdown(records, args.output_markdown)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
