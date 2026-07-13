from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from srp_experiment.policy_boundary_analysis import (  # noqa: E402
    build_policy_boundary_tasks,
    run_policy_boundary_analysis,
    write_policy_boundary_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SRP policy boundary analysis.")
    parser.add_argument(
        "--preset",
        choices=["coarse", "fine", "dependency-fine", "dependency-ultrafine"],
        default="coarse",
        help="Budget preset to run when no explicit budgets are provided.",
    )
    parser.add_argument(
        "--budget",
        action="append",
        type=int,
        default=[],
        help="Active budget to test. Repeatable. Defaults to a memory-saturation sweep.",
    )
    parser.add_argument(
        "--seed",
        action="append",
        type=int,
        default=[],
        help="Random allocation seed to test. Repeatable. Defaults to five seeds.",
    )
    parser.add_argument("--cycles", type=int, default=1, help="Cycles per task.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "srp_experiment" / "tmp" / "policy_boundary",
        help="Directory for JSONL, CSV, markdown, and summary outputs.",
    )
    parser.add_argument("--no-write", action="store_true", help="Run the analysis without writing output files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.budget:
        budgets = args.budget
    elif args.preset == "fine":
        budgets = [20, 22, 24, 26, 28, 30, 32]
    elif args.preset == "dependency-fine":
        budgets = [8, 10, 12, 14, 16, 18, 20, 22, 24]
    elif args.preset == "dependency-ultrafine":
        budgets = [8, 9, 10, 11, 12]
    else:
        budgets = [4, 8, 12, 16, 24, 32]
    seeds = args.seed or [0, 1, 2, 3, 4]
    tasks = build_policy_boundary_tasks()
    records = run_policy_boundary_analysis(budgets=budgets, seeds=seeds, tasks=tasks, cycles=args.cycles)

    if not args.no_write:
        outputs = write_policy_boundary_outputs(records, args.output_dir)
        summary = {"records": len(records), "outputs": {key: str(value) for key, value in outputs.items()}}
    else:
        summary = {"records": len(records)}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
