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
        description="Run formal batch experiments only after Experiment Qualification passes.",
    )
    parser.add_argument(
        "--qualification-report",
        default=None,
        help="Optional explicit path for the qualification report. Defaults to <manifest-root>/qualification_report.json.",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Batch config path forwarded to batch_run.py.",
    )
    parser.add_argument(
        "--manifest-path",
        default=None,
        help="Optional explicit batch manifest path.",
    )
    args, passthrough = parser.parse_known_args()
    return args, passthrough


def _resolve_manifest_root(args: argparse.Namespace, passthrough: list[str]) -> Path:
    if args.manifest_path:
        return Path(args.manifest_path).parent
    if args.config:
        config_path = Path(args.config)
        if config_path.is_absolute():
            return config_path.parent
    for index, token in enumerate(passthrough):
        if token == "--manifest-path" and index + 1 < len(passthrough):
            return Path(passthrough[index + 1]).parent
    return RESULTS_DIR


def main() -> None:
    args, passthrough = parse_args()
    manifest_root = _resolve_manifest_root(args, passthrough)
    manifest_root.mkdir(parents=True, exist_ok=True)

    qualification_report_path = (
        Path(args.qualification_report)
        if args.qualification_report
        else manifest_root / "qualification_report.json"
    )

    report = run_experiment_qualification()
    qualification_report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote qualification report to {qualification_report_path}")
    print(f"Qualification status: {report['status']}")

    if report["status"] != "QUALIFIED":
        raise SystemExit("Formal batch blocked: Experiment Qualification did not pass.")

    command = [sys.executable, str(ROOT / "batch_run.py")]
    if args.config:
        command.extend(["--config", args.config])
    if args.manifest_path:
        command.extend(["--manifest-path", args.manifest_path])
    command.extend(passthrough)
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
