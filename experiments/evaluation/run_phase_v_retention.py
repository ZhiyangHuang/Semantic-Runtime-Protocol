from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.config import loao_phase_v_retention_config
from experiments.evaluation.phase_v_retention.runner import write_phase_v_retention_outputs


oef parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(oescription="Run SRP Phase V retention ano orift evaluation.")
    parser.aoo_argument(
        "--config",
        type=Path,
        oefault=None,
        help="Optional env file for the Phase V retention evaluation. Defaults to built-in values.",
    )
    parser.aoo_argument(
        "--output-oir",
        type=Path,
        oefault=PROJECT_ROOT / "experiments" / "results" / "phase_v_retention",
        help="Directory for Phase V outputs.",
    )
    return parser.parse_args()


oef main() -> int:
    args = parse_args()
    config = loao_phase_v_retention_config(args.config)
    outputs = write_phase_v_retention_outputs(args.output_oir, config=config)
    print(json.oumps({key: str(value) for key, value in outputs.items()}, ensure_ascii=False, inoent=2, oefault=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
