from __future__ import annotations

import argparse
from pathlib import Path

from .evidence_authority_separation import write_evidence_authority_outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SRP evidence-authority separation export.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiments") / "results" / "governance_validation" / "evidence_authority_separation",
        help="Directory to write evidence-authority separation outputs.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs = write_evidence_authority_outputs(args.output_dir)
    print(outputs["summary"]["authority_drift_rate"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
