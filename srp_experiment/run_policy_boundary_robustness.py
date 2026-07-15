from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from srp_experiment.policy_boundary_robustness import (  # noqa: E402
    load_policy_boundary_records,
    write_policy_boundary_robustness_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SRP policy boundary robustness analysis.")
    parser.add_argument(
        "--records-jsonl",
        type=Path,
        required=True,
        help="Input JSONL file produced by policy boundary analysis.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "srp_experiment" / "tmp" / "policy_boundary_robustness",
        help="Directory for JSON and markdown outputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    records = load_policy_boundary_records(args.records_jsonl)
    outputs = write_policy_boundary_robustness_outputs(records, args.output_dir)
    summary = {"records": len(records), "outputs": {key: str(value) for key, value in outputs.items()}}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
