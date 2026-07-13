from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from srp_experiment.analysis.decision_attribution import (
    load_decision_attribution_records,
    write_decision_attribution_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run decision attribution analysis.")
    parser.add_argument(
        "--records-jsonl",
        type=Path,
        default=PROJECT_ROOT / "srp_experiment" / "tmp" / "fixed_harnesses" / "object_aware_compression" / "object_aware_compression_records.jsonl",
        help="Path to a JSONL file containing SRP experiment records.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "srp_experiment" / "tmp" / "decision_attribution",
        help="Directory to write decision attribution outputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    records = load_decision_attribution_records(args.records_jsonl)
    outputs = write_decision_attribution_outputs(records, args.output_dir)
    print(json.dumps({key: str(value) for key, value in outputs.items()}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
