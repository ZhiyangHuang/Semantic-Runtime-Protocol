from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ReproductionStep:
    key: str
    description: str
    command: list[str]


def _python_module(module: str) -> list[str]:
    return [sys.executable, "-m", module]


def _python_script(path: str) -> list[str]:
    return [sys.executable, path]


CORE_STEPS = [
    ReproductionStep(
        key="observability",
        description="Phase I observability",
        command=_python_script("experiments/sensitivity/run_phase_i_observability.py"),
    ),
    ReproductionStep(
        key="boundary_validation",
        description="Phase II boundary validation",
        command=_python_script("experiments/validation/run_phase_ii_boundary_validation.py"),
    ),
    ReproductionStep(
        key="optimization",
        description="Phase III-A optimization",
        command=_python_script("experiments/optimization/run_phase_iii_a_round1.py"),
    ),
    ReproductionStep(
        key="artifact_generation",
        description="Phase V retention artifact generation",
        command=_python_script("experiments/evaluation/run_phase_v_retention.py"),
    ),
]


SUPPORT_STEPS = [
    ReproductionStep(
        key="backend_comparison",
        description="Semantic backend comparison",
        command=_python_script("experiments/evaluation/run_semantic_backend_comparison.py"),
    ),
    ReproductionStep(
        key="external_validation",
        description="External validation",
        command=_python_script("experiments/evaluation/run_external_validation.py"),
    ),
    ReproductionStep(
        key="locomo_calibration",
        description="LoCoMo calibration-aware validation",
        command=_python_script("experiments/evaluation/run_external_validation_calibration_aware.py"),
    ),
    ReproductionStep(
        key="longmemeval_evidence",
        description="LongMemEval evidence package",
        command=_python_script("experiments/evaluation/run_longmemeval_evidence.py"),
    ),
    ReproductionStep(
        key="longmemeval_adapter_validation",
        description="LongMemEval adapter validation",
        command=_python_script("experiments/evaluation/run_longmemeval_adapter_validation.py"),
    ),
    ReproductionStep(
        key="longmemeval_scorer_alignment",
        description="LongMemEval scorer alignment audit",
        command=_python_script("experiments/evaluation/run_longmemeval_scorer_alignment_audit.py"),
    ),
]


def build_plan(profile: str) -> list[ReproductionStep]:
    if profile == "core":
        return CORE_STEPS
    if profile == "support":
        return SUPPORT_STEPS
    if profile == "all":
        return CORE_STEPS + SUPPORT_STEPS
    raise ValueError(f"unknown profile: {profile}")


def run_steps(steps: Iterable[ReproductionStep], output_root: Path, dry_run: bool) -> int:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = output_root / timestamp
    logs_dir = run_dir / "logs"
    summaries_dir = run_dir / "summaries"

    if not dry_run:
        logs_dir.mkdir(parents=True, exist_ok=True)
        summaries_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "timestamp_utc": timestamp,
        "dry_run": dry_run,
        "steps": [asdict(step) for step in steps],
    }

    if dry_run:
        print(json.dumps(manifest, indent=2))
        return 0

    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    failures = 0

    for index, step in enumerate(steps, start=1):
        print(f"[{index}/{len(CORE_STEPS) if steps is CORE_STEPS else len(SUPPORT_STEPS) if steps is SUPPORT_STEPS else len(CORE_STEPS) + len(SUPPORT_STEPS)}] {step.key}: {step.description}")
        log_path = logs_dir / f"{index:02d}_{step.key}.log"
        summary_path = summaries_dir / f"{index:02d}_{step.key}.json"
        try:
            completed = subprocess.run(
                step.command,
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            log_path.write_text(completed.stdout + ("\n" if completed.stdout and completed.stderr else "") + completed.stderr, encoding="utf-8")
            summary_path.write_text(
                json.dumps(
                    {
                        "key": step.key,
                        "description": step.description,
                        "command": step.command,
                        "returncode": completed.returncode,
                        "status": "ok",
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        except subprocess.CalledProcessError as exc:
            failures += 1
            log_path.write_text((exc.stdout or "") + ("\n" if exc.stdout and exc.stderr else "") + (exc.stderr or ""), encoding="utf-8")
            summary_path.write_text(
                json.dumps(
                    {
                        "key": step.key,
                        "description": step.description,
                        "command": step.command,
                        "returncode": exc.returncode,
                        "status": "failed",
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            print(f"Step failed: {step.key}", file=sys.stderr)
            break

    return 0 if failures == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a frozen SRP reproduction plan.")
    parser.add_argument(
        "profile",
        choices=["core", "support", "all"],
        nargs="?",
        help="Which reproduction profile to run.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--core", action="store_true", help="Run the core reproduction profile.")
    group.add_argument("--support", action="store_true", help="Run the support reproduction profile.")
    group.add_argument("--all", action="store_true", help="Run the full reproduction profile.")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute the reproduction commands. Default is dry run.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=REPO_ROOT / "reproduction_run",
        help="Directory for reproduction logs and manifests when executing.",
    )
    args = parser.parse_args()

    profile = "core"
    if args.profile:
        profile = args.profile
    if args.support:
        profile = "support"
    if args.all:
        profile = "all"
    if args.core:
        profile = "core"

    steps = build_plan(profile)
    dry_run = not args.execute
    return run_steps(steps, args.output_root, dry_run=dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
