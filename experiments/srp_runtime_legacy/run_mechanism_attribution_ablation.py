from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.mechanism_ablation.ablation_runner import (
    run_mechanism_attribution_ablation,
    write_mechanism_attribution_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SRP mechanism attribution / ablation protocol.")
    parser.add_argument(
        "--budget",
        action="append",
        type=int,
        default=[],
        help="Active budget to test. Repeatable. Defaults to the frozen mechanism-ablation sweep.",
    )
    parser.add_argument(
        "--seed",
        action="append",
        type=int,
        default=[],
        help="Random seed to test. Repeatable. Defaults to five seeds.",
    )
    parser.add_argument("--cycles", type=int, default=1, help="Cycles per task.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "srp_experiment" / "tmp" / "mechanism_attribution_ablation",
        help="Directory for ablation records and reports.",
    )
    parser.add_argument("--no-write", action="store_true", help="Run the ablation without writing output files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    budgets = args.budget or [8, 10, 12, 14, 16, 18, 20, 22, 24]
    seeds = args.seed or [0, 1, 2, 3, 4]
    records = run_mechanism_attribution_ablation(budgets=budgets, seeds=seeds, cycles=args.cycles)

    if not args.no_write:
        outputs = write_mechanism_attribution_outputs(records, args.output_dir)
        summary = {"records": len(records), "outputs": {key: str(value) for key, value in outputs.items()}}
    else:
        summary = {"records": len(records)}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

