from __future__ import annotations

import argparse
from pathlib import Path

from .phase_i_observability import write_phase_i_observability_outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SRP Phase I observability data generation.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiments") / "results" / "phase_i",
        help="Directory to write Phase I observability outputs.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs = write_phase_i_observability_outputs(args.output_dir)
    print(outputs["report"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

