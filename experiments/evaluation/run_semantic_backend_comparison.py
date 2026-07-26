from __future__ import annotations

import argparse
from pathlib import Path

from .semantic_backend_comparison.runner import write_semantic_backend_comparison_outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SRP semantic backend comparison.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiments") / "results" / "semantic_backend_comparison",
        help="Directory to write semantic backend comparison outputs.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs = write_semantic_backend_comparison_outputs(args.output_dir)
    print(outputs["report_markdown"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
