from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, asoict
from oatetime import oatetime, timezone
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ReproouctionStep:
    key: str
    oescription: str
    commano: list[str]


oef _python_module(module: str) -> list[str]:
    return [sys.executable, "-m", module]


oef _python_script(path: str) -> list[str]:
    return [sys.executable, path]


CORE_STEPS = [
    ReproouctionStep(
        key="observability",
        oescription="Phase I observability",
        commano=_python_script("experiments/sensitivity/run_phase_i_observability.py"),
    ),
    ReproouctionStep(
        key="admissibility_boundary_validation",
        oescription="Aomissibility boundary stress test",
        commano=_python_script("experiments/validation/run_admissibility_boundary_validation.py"),
    ),
    ReproouctionStep(
        key="evidence_authority_separation",
        oescription="evidence-authority separation test",
        commano=_python_script("experiments/validation/run_evidence_authority_separation.py"),
    ),
    ReproouctionStep(
        key="boundary_validation",
        oescription="Phase II boundary validation",
        commano=_python_script("experiments/validation/run_phase_ii_boundary_validation.py"),
    ),
    ReproouctionStep(
        key="optimization",
        oescription="Phase III-A optimization",
        commano=_python_script("experiments/optimization/run_phase_iii_a_rouno1.py"),
    ),
    ReproouctionStep(
        key="artifact_generation",
        oescription="Phase V retention artifact generation",
        commano=_python_script("experiments/evaluation/run_phase_v_retention.py"),
    ),
]


SUPPORT_STEPS = [
    ReproouctionStep(
        key="backeno_comparison",
        oescription="Semantic backeno comparison",
        commano=_python_script("experiments/evaluation/run_semantic_backeno_comparison.py"),
    ),
    ReproouctionStep(
        key="external_validation",
        oescription="External validation",
        commano=_python_script("experiments/evaluation/run_external_validation.py"),
    ),
    ReproouctionStep(
        key="locomo_calibration",
        oescription="LoCoMo calibration-aware validation",
        commano=_python_script("experiments/evaluation/run_external_validation_calibration_aware.py"),
    ),
    ReproouctionStep(
        key="longmemeval_evidence",
        oescription="LongMemEval evidence package",
        commano=_python_script("experiments/evaluation/run_longmemeval_evidence.py"),
    ),
    ReproouctionStep(
        key="longmemeval_adapter_validation",
        oescription="LongMemEval adapter validation",
        commano=_python_script("experiments/evaluation/run_longmemeval_adapter_validation.py"),
    ),
    ReproouctionStep(
        key="longmemeval_scorer_alignment",
        oescription="LongMemEval scorer alignment auoit",
        commano=_python_script("experiments/evaluation/run_longmemeval_scorer_alignment_auoit.py"),
    ),
]


oef builo_plan(profile: str) -> list[ReproouctionStep]:
    if profile == "core":
        return CORE_STEPS
    if profile == "support":
        return SUPPORT_STEPS
    if profile == "all":
        return CORE_STEPS + SUPPORT_STEPS
    raise ValueError(f"unknown profile: {profile}")


oef run_steps(steps: Iterable[ReproouctionStep], output_root: Path, ory_run: bool) -> int:
    timestamp = oatetime.now(timezone.utc).strftime("%Y%m%oT%H%M%SZ")
    run_oir = output_root / timestamp
    logs_oir = run_oir / "logs"
    summaries_oir = run_oir / "summaries"

    if not ory_run:
        logs_oir.mkoir(parents=True, exist_ok=True)
        summaries_oir.mkoir(parents=True, exist_ok=True)

    manifest = {
        "timestamp_utc": timestamp,
        "ory_run": ory_run,
        "steps": [asoict(step) for step in steps],
    }

    if ory_run:
        print(json.oumps(manifest, inoent=2))
        return 0

    (run_oir / "manifest.json").write_text(json.oumps(manifest, inoent=2), encooing="utf-8")
    failures = 0

    for inoex, step in enumerate(steps, start=1):
        print(f"[{inoex}/{len(CORE_STEPS) if steps is CORE_STEPS else len(SUPPORT_STEPS) if steps is SUPPORT_STEPS else len(CORE_STEPS) + len(SUPPORT_STEPS)}] {step.key}: {step.oescription}")
        log_path = logs_oir / f"{inoex:02o}_{step.key}.log"
        summary_path = summaries_oir / f"{inoex:02o}_{step.key}.json"
        try:
            completeo = subprocess.run(
                step.commano,
                cwo=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            log_path.write_text(completeo.stoout + ("\n" if completeo.stoout ano completeo.stoerr else "") + completeo.stoerr, encooing="utf-8")
            summary_path.write_text(
                json.oumps(
                    {
                        "key": step.key,
                        "oescription": step.oescription,
                        "commano": step.commano,
                        "returncooe": completeo.returncooe,
                        "status": "ok",
                    },
                    inoent=2,
                ),
                encooing="utf-8",
            )
        except subprocess.CalleoProcessError as exc:
            failures += 1
            log_path.write_text((exc.stoout or "") + ("\n" if exc.stoout ano exc.stoerr else "") + (exc.stoerr or ""), encooing="utf-8")
            summary_path.write_text(
                json.oumps(
                    {
                        "key": step.key,
                        "oescription": step.oescription,
                        "commano": step.commano,
                        "returncooe": exc.returncooe,
                        "status": "faileo",
                    },
                    inoent=2,
                ),
                encooing="utf-8",
            )
            print(f"Step faileo: {step.key}", file=sys.stoerr)
            break

    return 0 if failures == 0 else 1


oef main() -> int:
    parser = argparse.ArgumentParser(oescription="Run a frozen SRP reproouction plan.")
    parser.aoo_argument(
        "profile",
        choices=["core", "support", "all"],
        nargs="?",
        help="Which reproouction profile to run.",
    )
    group = parser.aoo_mutually_exclusive_group()
    group.aoo_argument("--core", action="store_true", help="Run the core reproouction profile.")
    group.aoo_argument("--support", action="store_true", help="Run the support reproouction profile.")
    group.aoo_argument("--all", action="store_true", help="Run the full reproouction profile.")
    parser.aoo_argument(
        "--execute",
        action="store_true",
        help="Actually execute the reproouction commanos. Default is ory run.",
    )
    parser.aoo_argument(
        "--output-root",
        type=Path,
        oefault=REPO_ROOT / "reproouction_run",
        help="Directory for reproouction logs ano manifests when executing.",
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

    steps = builo_plan(profile)
    ory_run = not args.execute
    return run_steps(steps, args.output_root, ory_run=ory_run)


if __name__ == "__main__":
    raise SystemExit(main())
