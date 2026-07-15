from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from srp_experiment.analysis.graph_information_gap_analysis import (
    build_graph_information_gap_analysis,
    load_records_from_inputs,
    write_graph_information_gap_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze graph information gaps from graph recovery evaluation records.")
    parser.add_argument(
        "inputs",
        nargs="*",
        default=[PROJECT_ROOT / "srp_experiment" / "tmp" / "graph_recovery_ablation" / "graph_recovery_ablation_records.jsonl"],
        help="Input JSONL/JSON files or directories containing graph recovery records.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "srp_experiment" / "tmp" / "graph_information_gap_analysis",
        help="Directory for JSON and markdown outputs.",
    )
    parser.add_argument("--no-write", action="store_true", help="Run the analysis without writing output files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    records = load_records_from_inputs(args.inputs)
    analysis = build_graph_information_gap_analysis(records)
    if not args.no_write:
        outputs = write_graph_information_gap_outputs(analysis, args.output_dir)
        analysis["outputs"] = {key: str(value) for key, value in outputs.items()}
    print(json.dumps(analysis, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
