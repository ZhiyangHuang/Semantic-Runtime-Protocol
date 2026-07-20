import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.common.export_support import (
    load_records,
    write_records_markdown,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export SRP run records to markdown audit output.")
    parser.add_argument("--input-json", type=Path, required=True, help="Path to a JSON file containing SRP records.")
    parser.add_argument("--output-markdown", type=Path, default=Path("experiments") / "results" / "compatibility" / "srp_audit.md")
    args = parser.parse_args()

    records = load_records(args.input_json)

    output_path = write_records_markdown(records, args.output_markdown)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



