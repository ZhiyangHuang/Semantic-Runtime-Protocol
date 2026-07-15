from __future__ import annotations

import argparse
from pathlib import Path

from .phase_ii_boundary import write_phase_ii_boundary_outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SRP Phase II boundary validation export.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiments") / "results" / "phase_ii_boundary",
        help="Directory to write Phase II boundary validation outputs.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs = write_phase_ii_boundary_outputs(args.output_dir)
    print(outputs["feasible_region"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

