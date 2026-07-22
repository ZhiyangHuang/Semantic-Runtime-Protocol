# SRP Main Results Summary V1

This document provides a paper-facing summary of the release evidence surface for SRP.
It is a synthesis artifact, not a new experiment, not a mechanism design, and not a policy document.

## 1. Release Summary

| Benchmark | Metric | Canonical Artifact | Evidence Role |
| --- | --- | --- | --- |
| MMLU | accuracy | `experiments/results/mmlu_full_v3/` | General knowledge reasoning |
| ARC | accuracy | `experiments/results/arc_full_v1/` | Science reasoning |
| LongMemEval | official scorer + bridge alignment | `experiments/results/longmemeval_full_v5/` | Long-context memory evaluation with dual surface |
| HumanEval | pass@1 | `experiments/results/humaneval_full_v1/` | Code-generation execution benchmark |

## 2. Release Narrative

The SRP evidence chain supports the following release-facing claims:

1. Governed semantic transitions can reject unsupported mutation while preserving authority separation.
2. Benchmark evidence can be validated under a shared artifact contract without collapsing metric authority.
3. LongMemEval can be represented with a dual-evaluation surface, preserving both the official scorer and the bridge alignment layer.
4. MMLU and ARC can be evaluated under the approved SRP context-recovery treatment while preserving prompt-leakage controls and artifact integrity.
5. HumanEval can be executed under sandbox isolation with pass@1 reporting while preserving execution integrity and prompt-boundary controls.

## 3. Interpretation Boundary

The most important methodological separation is:

```text
LongMemEval Track A
  preserves original scorer authority

LongMemEval Track B
  preserves shared benchmark alignment

MMLU / ARC / HumanEval
  preserve the shared benchmark evidence contract
```

This means the release evidence should be interpreted benchmark by benchmark, not as a single blended SRP score.

## 4. Where the Evidence Lives

- MMLU release artifact: `experiments/results/mmlu_full_v3/`
- ARC release artifact: `experiments/results/arc_full_v1/`
- LongMemEval bridge artifact: `experiments/results/longmemeval_full_v5/`
- HumanEval release artifact: `experiments/results/humaneval_full_v1/`
- Release evidence review: `docs/release/RELEASE_EVIDENCE_REVIEW.md`
- Release status: `docs/release/RELEASE_STATUS.md`
- Release manifest freeze review: `docs/release/RELEASE_MANIFEST_FREEZE_REVIEW.md`

## 5. Paper Use

This summary can be used as the paper's compact evidence map for the abstract, conclusion, and results overview.

For the consolidated evidence surface and cross-environment interpretation, see `docs/release/SRP_EVIDENCE_SURFACE_V1_1.md`.
