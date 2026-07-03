import argparse
import json
import subprocess
import sys
from pathlib import Path

from experiment_qualification import run_experiment_qualification


ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description="Run formal experiments only after Experiment Qualification passes.",
    )
    parser.add_argument(
        "--qualification-report",
        default=None,
        help="Optional explicit path for the qualification report. Defaults to <output-dir>/qualification_report.json.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Forwarded formal experiment output directory. Also used to place the qualification report.",
    )
    args, passthrough = parser.parse_known_args()
    return args, passthrough


def _resolve_output_dir(args: argparse.Namespace, passthrough: list[str]) -> Path:
    if args.output_dir:
        return Path(args.output_dir)
    for index, token in enumerate(passthrough):
        if token == "--output-dir" and index + 1 < len(passthrough):
            return Path(passthrough[index + 1])
    return RESULTS_DIR


def main() -> None:
    args, passthrough = parse_args()
    output_dir = _resolve_output_dir(args, passthrough)
    output_dir.mkdir(parents=True, exist_ok=True)

    qualification_report_path = (
        Path(args.qualification_report)
        if args.qualification_report
        else output_dir / "qualification_report.json"
    )

    report = run_experiment_qualification()
    qualification_report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote qualification report to {qualification_report_path}")
    print(f"Qualification status: {report['status']}")

    if report["status"] != "QUALIFIED":
        raise SystemExit("Formal experiment blocked: Experiment Qualification did not pass.")

    command = [sys.executable, str(ROOT / "run_experiment.py"), "--output-dir", str(output_dir), *passthrough]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
