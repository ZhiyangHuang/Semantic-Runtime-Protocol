from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from srp_experiment.analysis.semantic_failure_taxonomy import (
    build_semantic_failure_taxonomy,
    load_records_from_inputs,
    write_semantic_failure_taxonomy_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the SRP semantic failure taxonomy from records.")
    parser.add_argument(
        "--input",
        action="append",
        type=Path,
        default=[],
        help="Input JSONL file or directory. Repeatable. Defaults to srp_experiment/tmp/fixed_harnesses.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "srp_experiment" / "tmp" / "semantic_failure_taxonomy",
        help="Directory for JSON and markdown outputs.",
    )
    parser.add_argument("--no-write", action="store_true", help="Run the analysis without writing output files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    inputs = args.input or [PROJECT_ROOT / "srp_experiment" / "tmp" / "fixed_harnesses"]
    records = load_records_from_inputs(inputs)
    taxonomy = build_semantic_failure_taxonomy(records)

    if not args.no_write:
        outputs = write_semantic_failure_taxonomy_outputs(taxonomy, args.output_dir)
        taxonomy["outputs"] = {key: str(value) for key, value in outputs.items()}
    print(json.dumps(taxonomy, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
