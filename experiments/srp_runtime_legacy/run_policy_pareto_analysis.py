from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.analysis.policy_pareto import (  # noqa: E402
    load_policy_intervention_records,
    write_policy_pareto_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SRP policy Pareto analysis.")
    parser.add_argument(
        "--records-jsonl",
        type=Path,
        default=PROJECT_ROOT / "experiments" / "results" / "analysis" / "policy_intervention" / "policy_intervention_records.jsonl",
        help="Policy intervention JSONL file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "experiments" / "results" / "analysis" / "policy_pareto",
        help="Output directory for Pareto outputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    records = load_policy_intervention_records(args.records_jsonl)
    outputs = write_policy_pareto_outputs(records, args.output_dir)
    print(json.dumps({key: str(value) for key, value in outputs.items()}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

