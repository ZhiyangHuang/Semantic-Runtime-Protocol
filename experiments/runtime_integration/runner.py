from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from .replay import run_runtime_integration_replay, write_runtime_integration_replay_outputs
from .controlled import run_runtime_integration_controlled, write_runtime_integration_controlled_outputs
from .shadow import run_runtime_integration_shadow, write_runtime_integration_shadow_outputs


def run_runtime_integration(*, mode: str = "replay", fixture_path: str | Path | None = None) -> dict[str, object]:
    if mode == "shadow":
        return run_runtime_integration_shadow(fixture_path=fixture_path)
    if mode == "controlled":
        return run_runtime_integration_controlled(fixture_path=fixture_path)
    return run_runtime_integration_replay(mode=mode, fixture_path=fixture_path)


def write_runtime_integration_outputs(report: dict[str, object], output_dir: str | Path) -> dict[str, Path]:
    mode = str(report.get("mode") or "replay")
    if mode == "shadow":
        return write_runtime_integration_shadow_outputs(report, output_dir)
    if mode == "controlled":
        return write_runtime_integration_controlled_outputs(report, output_dir)
    return write_runtime_integration_replay_outputs(report, output_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SRP runtime integration scaffold.")
    parser.add_argument(
        "--mode",
        choices=["replay", "shadow", "controlled"],
        default="replay",
        help="Runtime integration mode.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "experiments" / "results" / "runtime_integration",
        help="Directory to write runtime integration outputs.",
    )
    parser.add_argument(
        "--fixture",
        type=Path,
        default=None,
        help="Optional frozen replay fixture path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_runtime_integration(mode=args.mode, fixture_path=args.fixture)
    outputs = write_runtime_integration_outputs(report, args.output_dir)
    print(json.dumps({key: str(value) for key, value in outputs.items()}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
