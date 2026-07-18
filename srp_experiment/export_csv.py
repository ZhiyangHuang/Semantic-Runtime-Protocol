import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.common.export_support import (
    load_records,
    apply_task_identity,
    write_records_csv,
)


def _apply_task_identity(record: dict, task: dict, task_path: Path, task_id_prefix: str = "") -> None:
    apply_task_identity(record, task, task_path, task_id_prefix)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export SRP run records to CSV.")
    parser.add_argument("--input-json", type=Path, required=True, help="Path to a JSON file containing SRP records.")
    parser.add_argument("--output-csv", type=Path, default=Path("srp_experiment") / "tmp" / "srp_records.csv")
    args = parser.parse_args()

    records = load_records(args.input_json)

    output_path = write_records_csv(records, args.output_csv)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

