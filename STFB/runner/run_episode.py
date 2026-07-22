from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from STFB.runner.evaluate import evaluate_instance, load_instance
from STFB.runner.evaluate import evaluate_episodes


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one STFB episode.")
    parser.add_argument(
        "--instance",
        default=str(Path(__file__).resolve().parents[1] / "instances" / "examples"),
        help="Path to a STFB instance JSON file or a directory of JSON files.",
    )
    parser.add_argument(
        "--output",
        default=str(Path(__file__).resolve().parents[1] / "reports" / "milestone0_report.json"),
        help="Path to write the evaluation report.",
    )
    args = parser.parse_args()

    instance_path = Path(args.instance)
    if instance_path.is_dir():
        instances = [load_instance(path) for path in sorted(instance_path.glob("*.json"))]
        report = evaluate_episodes(instances)
    else:
        instance = load_instance(instance_path)
        report = {
            "instances": [
                {
                    "id": instance.get("id") or instance.get("instance_id"),
                    "failure_type": instance.get("failure_type"),
                    "results": evaluate_instance(instance),
                }
            ],
            "aggregate": evaluate_episodes([instance])["aggregate"],
        }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
