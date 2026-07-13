from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from srp_experiment.object_aware_threshold_sampling import (
    run_object_aware_threshold_sampling,
    write_object_aware_threshold_sampling_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SRP object-aware threshold sampling experiment.")
    parser.add_argument(
        "--seed",
        action="append",
        type=int,
        default=[],
        help="Seed to sample. Repeatable. Defaults to seeds 1..5.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "srp_experiment" / "tmp" / "object_aware_threshold_sampling",
        help="Directory for JSON and markdown outputs.",
    )
    parser.add_argument("--no-write", action="store_true", help="Run the sampling experiment without writing output files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results = run_object_aware_threshold_sampling(args.seed or None)

    if not args.no_write:
        outputs = write_object_aware_threshold_sampling_outputs(results, args.output_dir)
        results["outputs"] = {key: str(value) for key, value in outputs.items()}
    print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
