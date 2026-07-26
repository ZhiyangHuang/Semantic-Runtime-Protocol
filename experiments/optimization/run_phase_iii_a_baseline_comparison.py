from __future__ import annotations

import argparse
from pathlib import Path

from experiments.optimization.phase_iii_a_round1.baseline import write_phase_iii_a_baseline_comparison_report
from experiments.validation.phase_ii_boundary import load_feasible_region


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SRP Phase III-A baseline comparison.")
    parser.add_argument(
        "--feasible-region",
        type=Path,
        default=Path("experiments") / "results" / "phase_ii_boundary" / "feasible_region.json",
        help="Phase II feasible region file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiments") / "results" / "phase_iii_a_baseline_comparison",
        help="Directory to write baseline comparison outputs.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    region = load_feasible_region(args.feasible_region)
    outputs = write_phase_iii_a_baseline_comparison_report(
        feasible_region=region,
        output_dir=args.output_dir,
    )
    print(outputs["report_markdown"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
