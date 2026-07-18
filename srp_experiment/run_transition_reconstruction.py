from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from srp_experiment.transition_reconstruction import (  # noqa: E402
    available_suite_names,
    run_transition_reconstruction_comparison,
    summarize_transition_reconstruction_comparison,
    write_transition_reconstruction_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SRP transition reconstruction comparison.")
    parser.add_argument(
        "--suite",
        action="append",
        choices=["all", *available_suite_names()],
        default=[],
        help="Transition reconstruction suite to run. Repeatable. Defaults to all suites.",
    )
    parser.add_argument("--cycles", type=int, default=1, help="Cycles per task.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "srp_experiment" / "tmp" / "transition_reconstruction",
        help="Directory for JSONL, CSV, markdown, and summary outputs.",
    )
    parser.add_argument("--no-write", action="store_true", help="Run the comparison without writing output files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    suites = args.suite or ["all"]
    records = run_transition_reconstruction_comparison(suites, cycles=args.cycles)
    summary = summarize_transition_reconstruction_comparison(records)

    if not args.no_write:
        outputs = write_transition_reconstruction_outputs(records, args.output_dir)
        summary["outputs"] = {key: str(value) for key, value in outputs.items()}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
