import argparse
import os
import subprocess
import sys
from pathlib import Path

from check_env_alignment import enforce_alignment

ROOT = Path(__file__).resolve().parent


def parse_args():
    parser = argparse.ArgumentParser(description="Unified SRP CLI entrypoint.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="Run a qualified first-paper experiment pipeline.")
    run.add_argument("--config", default="srp_experiment/configs/first_paper_formal_local.json")
    run.add_argument("--skip-health-check", action="store_true")
    run.add_argument("--fail-fast", action="store_true")
    run.add_argument("--task-id", default=None, help="Optional task id for evidence trace filtering.")
    run.add_argument("--output-dir", default=None, help="Optional override for the evidence pipeline output directory.")
    return parser.parse_args()


def run_command(command: list[str]) -> None:
    result = subprocess.run(command, cwd=ROOT.parent)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def run_pipeline(args) -> None:
    enforce_alignment()

    script = ROOT / "first-paper-run.ps1"
    ps_command = [
        "powershell",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script),
        "-Config",
        args.config,
    ]
    if args.skip_health_check:
        ps_command.append("-SkipHealthCheck")
    if args.fail_fast:
        ps_command.append("-FailFast")
    run_command(ps_command)

    evidence_command = [sys.executable, str(ROOT / "evidence_pipeline.py")]
    if args.task_id:
        evidence_command.extend(["--task-id", args.task_id])
    if args.output_dir:
        evidence_command.extend(["--output-dir", args.output_dir])
    run_command(evidence_command)


def main():
    args = parse_args()
    if args.command == "run":
        run_pipeline(args)


if __name__ == "__main__":
    main()
