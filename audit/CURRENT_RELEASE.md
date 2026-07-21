# Current Release

Date: 2026-07-21

This file summarizes the current release surface for SRP.
It is the human-facing index for the frozen release state.

## Canonical Sources

- `fixed.md`
- `docs/release/RELEASE_EVIDENCE_REVIEW.md`
- `docs/benchmarks/README.md`
- `docs/archive/benchmark_history/README.md`

## Main Evidence

- `MMLU`
- `LongMemEval`
- `ARC`
- `HumanEval`

Each Main Evidence benchmark is represented by a canonical release report and a canonical artifact path in `experiments/results/`.
Benchmark payloads are obtained from the original sources and are not redistributed in this repository.

## Evidence Status

- `Main`
- `Appendix`
- `Archive`

## Current Supporting Evidence

- `audit/REAL_VALIDATION_REPORT.md`
- `docs/release/RELEASE_EVIDENCE_REVIEW.md`
- `docs/benchmarks/MMLU_REPORT.md`
- `docs/benchmarks/ARC_REPORT.md`
- `docs/benchmarks/LONGMEMEVAL_REPORT.md`
- `docs/benchmarks/HUMANEVAL_REPORT.md`

## Current Verification

- `python scripts/verify_release.py`: PASS
- `python -m experiments.transition_role.report_coverage`: PASS

## Notes

- The release surface is intentionally small.
- Historical development artifacts are preserved under `docs/archive/benchmark_history/` and Git history, not in the active audit surface.
