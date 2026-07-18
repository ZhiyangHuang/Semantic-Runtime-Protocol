from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.analysis.coverage_attribution import (
    load_coverage_attribution_records,
    summarize_coverage_attribution,
    write_coverage_attribution_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SRP coverage attribution analysis.")
    parser.add_argument(
        "--records-jsonl",
        type=Path,
        default=PROJECT_ROOT / "srp_experiment" / "tmp" / "graph_representation_ablation" / "graph_representation_ablation_records.jsonl",
        help="Input records JSONL to analyze.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "srp_experiment" / "tmp" / "coverage_attribution",
        help="Directory for coverage attribution outputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    records = load_coverage_attribution_records(args.records_jsonl)
    summary = summarize_coverage_attribution(records)
    outputs = write_coverage_attribution_outputs(records, args.output_dir)
    summary["outputs"] = {key: str(value) for key, value in outputs.items()}
    print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

