from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from .runner import run_runtime_integration_backend_consistency, write_runtime_integration_backend_consistency_outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SRP runtime backend consistency check.")
    parser.add_argument(
        "--fixture",
        type=Path,
        default=PROJECT_ROOT / "experiments" / "runtime_integration" / "fixtures" / "semantic_transition_replay_v1.json",
        help="Frozen replay fixture path.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "experiments" / "results" / "runtime_integration",
        help="Directory to write backend comparison outputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_runtime_integration_backend_consistency(fixture_path=args.fixture)
    outputs = write_runtime_integration_backend_consistency_outputs(report, args.output_dir)
    print(json.dumps({key: str(value) for key, value in outputs.items()}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
