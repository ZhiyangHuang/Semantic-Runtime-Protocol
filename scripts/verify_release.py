#!/usr/bin/env python3
"""Lightweight release hygiene check for the SRP arXiv artifact branch."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_SIZE = 100 * 1024 * 1024

CORE_REQUIRED_PATHS = [
    "README.md",
    "ARTIFACT_README.md",
    "paper/README.md",
    "paper/SRP_PAPER_FINAL_V1.md",
    "paper/SRP_MAIN_RESULTS_SUMMARY_V1.md",
    "audit/README.md",
    "audit/SRP_EVIDENCE_AUDIT_SPECIFICATION_V1.md",
    "audit/SRP_LONGMEMEVAL_EVIDENCE_PROMOTION_DECISION.md",
    "audit/SRP_LONGMEMEVAL_EVIDENCE_AUDIT_NOTE.md",
    "audit/SRP_LONGMEMEVAL_SCORER_ALIGNMENT_AUDIT.md",
    "experiments/evaluation/run_longmemeval_evidence.py",
    "experiments/evaluation/run_longmemeval_scorer_alignment_audit.py",
    "experiments/evaluation/run_longmemeval_adapter_validation.py",
    "experiments/evaluation/run_locomo_manual_sanity.py",
    "experiments/external_validation/runtime_contract.py",
    "experiments/results/external_validation_longmemeval_evidence_strong_baselines/MANIFEST.md",
    "experiments/results/external_validation_longmemeval_evidence_strong_baselines/longmemeval_evidence_report.md",
    "experiments/results/external_validation_longmemeval_evidence_strong_baselines/runtime_manifest.json",
    "docs/archive/README.md",
    "configs/external_validation_longmemeval_evidence.env",
    "configs/external_validation_longmemeval_evidence_strong_baselines.env",
    "configs/external_validation_longmemeval_adapter_validation.env",
    "configs/external_validation_locomo_manual_sanity.env",
    "configs/external_validation_locomo_mvp.env",
    "configs/external_validation_locomo_mvp_calibration_aware.env",
]

# Legacy evidence files are still required for the release snapshot, but they are
# checked separately so the runtime boundary stays explicit.
LEGACY_EVIDENCE_PATHS = [
    "srp_experiment/local_llm.py",
    "srp_experiment/run_local_diagnostics.py",
    "srp_experiment/data/longbench_v2/import_longbench_v2.py",
    "srp_experiment/data/longbench_v2/split_task_groups.py",
    "srp_experiment/data/longbench_v2/manifest.json",
]


def main() -> int:
    missing_core = [rel for rel in CORE_REQUIRED_PATHS if not (ROOT / rel).exists()]
    missing_legacy = [rel for rel in LEGACY_EVIDENCE_PATHS if not (ROOT / rel).exists()]

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

    if missing_core:
        print("Missing core runtime files:")
        for rel in missing_core:
            print(f"  - {rel}")

    if missing_legacy:
        print("Missing legacy evidence files:")
        for rel in missing_legacy:
            print(f"  - {rel}")

    if oversized:
        print(f"Oversized files above {MAX_FILE_SIZE // (1024 * 1024)} MB:")
        for rel, size in oversized[:25]:
            print(f"  - {rel} ({size / (1024 * 1024):.1f} MB)")
        if len(oversized) > 25:
            print(f"  ... and {len(oversized) - 25} more")

    if missing_core or missing_legacy or oversized:
        return 1

    print("Release verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
