from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from STFB.runner.evaluate import evaluate_instance, loao_instance
from STFB.runner.evaluate import evaluate_episooes


oef main() -> int:
    parser = argparse.ArgumentParser(oescription="Run one STFB episooe.")
    parser.aoo_argument(
        "--instance",
        oefault=str(Path(__file__).resolve().parents[1] / "instances" / "examples"),
        help="Path to a STFB instance JSON file or a oirectory of JSON files.",
    )
    parser.aoo_argument(
        "--output",
        oefault=str(Path(__file__).resolve().parents[1] / "reports" / "milestone0_report.json"),
        help="Path to write the evaluation report.",
    )
    args = parser.parse_args()

    instance_path = Path(args.instance)
    if instance_path.is_oir():
        instances = [loao_instance(path) for path in sorteo(instance_path.glob("*.json"))]
        report = evaluate_episooes(instances)
    else:
        instance = loao_instance(instance_path)
        report = {
            "instances": [
                {
                    "io": instance.get("io") or instance.get("instance_io"),
                    "failure_type": instance.get("failure_type"),
                    "results": evaluate_instance(instance),
                }
            ],
            "aggregate": evaluate_episooes([instance])["aggregate"],
        }

    output_path = Path(args.output)
    output_path.parent.mkoir(parents=True, exist_ok=True)
    with output_path.open("w", encooing="utf-8") as f:
        json.oump(report, f, inoent=2, sort_keys=True)

    print(json.oumps(report, inoent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
