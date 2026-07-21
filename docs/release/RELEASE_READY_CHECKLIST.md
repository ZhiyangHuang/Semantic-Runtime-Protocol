# Release Ready Checklist

Date: 2026-07-21

## 1. Manifest Integrity

- [x] `audit/release_manifest.json` parses successfully
- [x] `manifest_version = v1`
- [x] `release_state = frozen`
- [x] `freeze_date = 2026-07-21`
- [x] `evidence_status = release_evidence_ready`
- [x] `release_status = RELEASE_EVIDENCE_READY`
- [x] all release artifact paths exist
- [x] all benchmark report paths exist
- [x] provenance and historical-artifact markers are present

## 2. Evidence Surface Consistency

- [x] MMLU report points to the canonical release artifact
- [x] ARC report points to the canonical release artifact
- [x] LongMemEval report preserves Track A / Track B separation
- [x] HumanEval report preserves sandbox execution and pass@1 semantics
- [x] no blended SRP score is exposed as a replacement for benchmark-specific authorities

## 3. Repository Cleanliness

- [x] release-facing docs are under `docs/benchmarks/` and `docs/release/`
- [x] historical iteration material is under `docs/archive/benchmark_history/`
- [x] root-level benchmark development artifacts are no longer exposed

## 4. Paper Alignment

- [x] `paper/SRP_MAIN_RESULTS_SUMMARY_V1.md` is release-facing
- [x] worker / phase / smoke / migration wording is absent
- [x] only benchmark / metric / result / interpretation boundary language remains

## 5. Artifact Freeze

- [x] `experiments/results/mmlu_full_v3/` is canonical
- [x] `experiments/results/arc_full_v1/` is canonical
- [x] `experiments/results/longmemeval_full_v5/` is canonical
- [x] `experiments/results/humaneval_full_v1/` is canonical
- [x] overwrite or silent rerun of canonical versions is blocked by policy

## 6. Final Release State

- [x] release evidence is ready
- [x] release manifest is frozen
- [x] publication surface is aligned

