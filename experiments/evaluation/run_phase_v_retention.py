from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.config import load_phase_v_retention_config
from experiments.evaluation.phase_v_retention.runner import write_phase_v_retention_outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SRP Phase V retention and drift evaluation.")
    parser.add_argument(
        "--config",
        type=Path,
        default=PROJECT_ROOT / "configs" / "phase_v_retention.env",
        help="Optional env file for the Phase V retention evaluation.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "experiments" / "results" / "phase_v_retention",
        help="Directory for Phase V outputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_phase_v_retention_config(args.config)
    outputs = write_phase_v_retention_outputs(args.output_dir, config=config)
    print(json.dumps({key: str(value) for key, value in outputs.items()}, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
