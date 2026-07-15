from __future__ import annotations

import argparse
from pathlib import Path

from .phase_ii_density_baseline import write_phase_ii_density_baseline_outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SRP Phase II sampling density baseline.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiments") / "results" / "phase_ii_density_baseline",
        help="Directory to write density baseline outputs.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs = write_phase_ii_density_baseline_outputs(args.output_dir)
    print(outputs["report"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
