#!/usr/bin/env python3
"""Lightweight release hygiene check for the SRP arXiv artifact branch."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_SIZE = 100 * 1024 * 1024

REQUIRED_PATHS = [
    "README.md",
    "ARTIFACT_README.md",
    "SRP_PAPER_FINAL_V1.md",
    "SRP_MAIN_RESULTS_SUMMARY_V1.md",
    "SRP_EVIDENCE_AUDIT_SPECIFICATION_V1.md",
    "SRP_LONGMEMEVAL_EVIDENCE_PROMOTION_DECISION.md",
    "SRP_LONGMEMEVAL_EVIDENCE_AUDIT_NOTE.md",
    "SRP_LONGMEMEVAL_SCORER_ALIGNMENT_AUDIT.md",
    "experiments/evaluation/run_longmemeval_evidence.py",
    "experiments/evaluation/run_longmemeval_scorer_alignment_audit.py",
    "experiments/evaluation/run_longmemeval_adapter_validation.py",
    "experiments/evaluation/run_locomo_manual_sanity.py",
    "experiments/external_validation/runtime_contract.py",
    "experiments/results/external_validation_longmemeval_evidence_strong_baselines/MANIFEST.md",
    "experiments/results/external_validation_longmemeval_evidence_strong_baselines/longmemeval_evidence_report.md",
    "experiments/results/external_validation_longmemeval_evidence_strong_baselines/runtime_manifest.json",
    "configs/external_validation_longmemeval_evidence.env",
    "configs/external_validation_longmemeval_evidence_strong_baselines.env",
    "configs/external_validation_longmemeval_adapter_validation.env",
    "configs/external_validation_locomo_manual_sanity.env",
    "configs/external_validation_locomo_mvp.env",
    "configs/external_validation_locomo_mvp_calibration_aware.env",
    "srp_experiment/local_llm.py",
    "srp_experiment/run_local_diagnostics.py",
    "srp_experiment/data/longbench_v2/import_longbench_v2.py",
    "srp_experiment/data/longbench_v2/split_task_groups.py",
    "srp_experiment/data/longbench_v2/manifest.json",
]


def main() -> int:
    missing = [rel for rel in REQUIRED_PATHS if not (ROOT / rel).exists()]

    oversized: list[tuple[str, int]] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts:
            continue
        if path.is_symlink():
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > MAX_FILE_SIZE:
            oversized.append((str(path.relative_to(ROOT)).replace("\\", "/"), size))

    oversized.sort(key=lambda item: item[1], reverse=True)

    if missing:
        print("Missing required release files:")
        for rel in missing:
            print(f"  - {rel}")

    if oversized:
        print(f"Oversized files above {MAX_FILE_SIZE // (1024 * 1024)} MB:")
        for rel, size in oversized[:25]:
            print(f"  - {rel} ({size / (1024 * 1024):.1f} MB)")
        if len(oversized) > 25:
            print(f"  ... and {len(oversized) - 25} more")

    if missing or oversized:
        return 1

    print("Release verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
