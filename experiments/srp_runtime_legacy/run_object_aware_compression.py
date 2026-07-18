from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from .object_aware_compression_harness import (
    available_suite_names,
    run_object_aware_compression,
    summarize_object_aware_compression,
    write_object_aware_compression_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the fixed SRP object-aware compression ablation.")
    parser.add_argument(
        "--suite",
        action="append",
        choices=["all", *available_suite_names()],
        default=[],
        help="Object-aware compression suite to run. Repeatable. Defaults to all suites.",
    )
    parser.add_argument("--cycles", type=int, default=1, help="Cycles per task.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "srp_experiment" / "tmp" / "object_aware_compression",
        help="Directory for JSONL, CSV, markdown, and summary outputs.",
    )
    parser.add_argument("--no-write", action="store_true", help="Run the ablation without writing output files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    suites = args.suite or ["all"]
    records = run_object_aware_compression(suites, cycles=args.cycles)
    summary = summarize_object_aware_compression(records)

    if not args.no_write:
        outputs = write_object_aware_compression_outputs(records, args.output_dir)
        summary["outputs"] = {key: str(value) for key, value in outputs.items()}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

