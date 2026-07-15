from __future__ import annotations

import argparse
from pathlib import Path

from experiments.validation.phase_ii_boundary import load_feasible_region

from .phase_iii_a_round1.objective_sensitivity import write_phase_iii_a_objective_sensitivity_outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SRP Phase III-A objective sensitivity analysis.")
    parser.add_argument(
        "--feasible-region",
        type=Path,
        default=Path("experiments") / "results" / "phase_ii_boundary" / "feasible_region.json",
        help="Phase II feasible region file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiments") / "results" / "phase_iii_a_objective_sensitivity",
        help="Directory to write objective sensitivity outputs.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    region = load_feasible_region(args.feasible_region)
    outputs = write_phase_iii_a_objective_sensitivity_outputs(feasible_region=region, output_dir=args.output_dir)
    print(outputs["report"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
