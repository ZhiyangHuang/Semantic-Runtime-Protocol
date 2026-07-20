from __future__ import annotations

import argparse
from pathlib import Path

from .admissibility_boundary_validation import write_admissibility_boundary_outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SRP admissibility boundary validation export.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiments") / "results" / "governance_validation" / "admissibility_boundary_validation",
        help="Directory to write admissibility boundary validation outputs.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs = write_admissibility_boundary_outputs(args.output_dir)
    print(outputs["report"]["summary"]["boundary_violation_rate"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
