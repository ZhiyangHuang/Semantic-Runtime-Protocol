from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from srp_experiment.policy_intervention_harness import (  # noqa: E402
    run_policy_intervention_harness,
    write_policy_intervention_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SRP policy intervention sweep.")
    parser.add_argument(
        "--policy-suites",
        nargs="*",
        default=None,
        help="Policy suite names to run (default: all).",
    )
    parser.add_argument(
        "--task-suites",
        nargs="*",
        default=None,
        help="Controlled task suite names to run (default: structured_recovery object_retention repair_loop).",
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=1,
        help="Cycles per task suite.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "srp_experiment" / "tmp" / "policy_intervention",
        help="Directory to write policy intervention outputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    records = run_policy_intervention_harness(
        args.policy_suites,
        task_suites=args.task_suites,
        cycles=args.cycles,
    )
    outputs = write_policy_intervention_outputs(records, args.output_dir)
    print(json.dumps({key: str(value) for key, value in outputs.items()}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
