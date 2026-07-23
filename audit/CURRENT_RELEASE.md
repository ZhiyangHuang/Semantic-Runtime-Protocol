# Current Release

Date: 2026-07-22

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
- `audit/RUNTIME_INTEGRATION_EVIDENCE_INDEX.md`
- `audit/RUNTIME_INTEGRATION_EVIDENCE_INDEX.json`
- `audit/RUNTIME_INTEGRATION_EVIDENCE_SUMMARY.md`
- `docs/release/RELEASE_EVIDENCE_REVIEW.md`
- `docs/benchmarks/MMLU_REPORT.md`
- `docs/benchmarks/ARC_REPORT.md`
- `docs/benchmarks/LONGMEMEVAL_REPORT.md`
- `docs/benchmarks/HUMANEVAL_REPORT.md`
- `experiments/results/runtime_governance/governance_summary.json`
- `experiments/results/runtime_governance/runtime_latency_summary.json`
- `experiments/results/runtime_governance/llm_transition/llm_transition_report.json`
- `experiments/results/runtime_integration/runtime_integration_manifest.json`
- `experiments/results/runtime_integration/runtime_integration_report.json`
- `experiments/results/runtime_integration/runtime_backend_consistency_manifest.json`
- `experiments/results/runtime_integration/runtime_backend_consistency_report.json`
- `experiments/results/runtime_integration/runtime_shadow_manifest.json`
- `experiments/results/runtime_integration/runtime_shadow_report.json`
- `experiments/results/runtime_integration/runtime_admission_manifest.json`
- `experiments/results/runtime_integration/runtime_admission_report.json`
- `experiments/results/phase_viii_representation_invariance/metadata.json`
- `experiments/results/phase_viii_representation_invariance/representation_invariance_report.json`
- `experiments/results/phase_viii_representation_invariance/representation_invariance_summary.json`
- `experiments/results/phase_viii_representation_invariance/representation_invariance_report.md`
- `experiments/results/phase_viii_implementation_independence/metadata.json`
- `experiments/results/phase_viii_implementation_independence/implementation_independence_report.json`
- `experiments/results/phase_viii_implementation_independence/implementation_independence_summary.json`
- `experiments/results/phase_viii_implementation_independence/implementation_independence_report.md`

## Current Verification

- `python scripts/verify_release.py`: PASS
- `python -m experiments.transition_role.report_coverage`: PASS

## Notes

- The release surface is intentionally small.
- Historical development artifacts are preserved under `docs/archive/benchmark_history/` and Git history, not in the active audit surface.
