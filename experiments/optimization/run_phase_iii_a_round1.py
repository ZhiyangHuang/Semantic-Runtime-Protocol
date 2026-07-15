from __future__ import annotations

import argparse
import json
from pathlib import Path

from experiments.config import load_phase_iii_a_config
from experiments.validation.phase_ii_boundary import load_feasible_region

from .phase_iii_a_round1.runner import run_phase_iii_a_round1_optimization


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SRP Phase III-A Round 1 optimization.")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs") / "phase_iii_a.env",
        help="Phase III-A config file.",
    )
    parser.add_argument(
        "--feasible-region",
        type=Path,
        default=Path("experiments") / "results" / "phase_ii_boundary" / "feasible_region.json",
        help="Phase II feasible region file.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("experiments") / "results" / "phase_iii_a_round1" / "optimization_report.json",
        help="Path to write the optimization report JSON.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = load_phase_iii_a_config(args.config)
    region = load_feasible_region(args.feasible_region)
    result = run_phase_iii_a_round1_optimization(config=config, feasible_region=region)

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(args.output_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

