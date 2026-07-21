# Cross-Benchmark Consistency Review

Date: 2026-07-21

This review compares the current release-branch evidence for:
- LongMemEval external validation
- MMLU full v3
- ARC full v1

It is a review only. It does not modify `paper/` or the evidence manifest.

---

## 1. Benchmark Inventory

| Benchmark | Status | Evidence | Release Role |
| --- | --- | --- | --- |
| LongMemEval | Closed external-validation evidence | `audit/REAL_VALIDATION_REPORT.md`, `experiments/results/external_validation_longmemeval_reality_check_smoke_v2/longmemeval_reality_check_report.md` | External semantic-state validation support |
| MMLU v3 | Closed official artifact | `FULL_MMLU_EXECUTION_CLOSURE_REVIEW_V3.md`, `MMLU_PROMPT_LEAKAGE_AUDIT_V2.md`, `experiments/results/mmlu_full_v3/` | Main evidence benchmark under SRP context-recovery treatment |
| ARC-Easy v1 | Closed official artifact | `FULL_ARC_EXECUTION_CLOSURE_REVIEW_V1.md`, `ARC_PROMPT_LEAKAGE_AUDIT_V1.md`, `experiments/results/arc_full_v1/` | Main evidence benchmark under the same SRP treatment family |
| MMLU v2 | Invalidated historical artifact | `MMLU_PROMPT_LEAKAGE_AUDIT.md`, `FULL_MMLU_EXECUTION_CLOSURE_REVIEW.md`, `experiments/results/mmlu_full_v2/` | Provenance only; not release evidence |
| Smoke artifacts | Validation only | `experiments/results/mmlu_smoke/`, `experiments/results/arc_smoke/` | Pipeline validation only |
| HumanEval | Not included | `HUMANEVAL_EXECUTION_DESIGN.md` | Design only; excluded from current main evidence |

---

## 2. Methodology Consistency

| Item | LongMemEval | MMLU v3 | ARC v1 | Consistency Note |
| --- | --- | --- | --- | --- |
| Shared generation backend | PASS | PASS | PASS | All release-facing runs use the same local generation backend family. |
| Frozen runtime contract | PASS | PASS | PASS | All release-facing runs record a frozen execution contract. |
| Artifact provenance / hashes | PASS | PASS | PASS | Every closed artifact bundle records metadata and hashes. |
| Official scorer preserved | PASS | N/A | N/A | LongMemEval keeps the official scorer; MMLU/ARC are accuracy-based benchmark adapters. |
| Shared benchmark runner | N/A | PASS | PASS | MMLU and ARC use the shared benchmark runner; LongMemEval uses its own reality-check pipeline. |
| Prompt leakage guard | N/A | PASS | PASS | Explicit leakage blocking is enforced in the shared benchmark runner for MMLU and ARC. |
| Closure review completed | PASS | PASS | PASS | Each closed artifact has an explicit closure review. |

Interpretation:
- the three evidence families are not byte-identical
- they are consistent at the release boundary: shared generation family, frozen provenance, separated scoring, and explicit closure

---

## 3. Treatment Consistency

Confirmed across MMLU v3 and ARC v1:
- baseline and SRP share the same benchmark cases
- baseline and SRP share the same model and generation settings
- the only intended difference is the approved SRP runtime context path
- scoring-only fields are not present in prompt-visible text

Confirmed for LongMemEval:
- the official scorer remains separate from SRP diagnostics
- the runtime contract is frozen
- the report co-reports official score and SRP diagnostics rather than replacing the scorer

Treatment boundary note:
- LongMemEval is a memory-state validation workload
- MMLU and ARC are general benchmark workloads under an SRP context-recovery treatment
- the three should be compared as related release evidence, not as identical task definitions

---

## 4. Result Interpretation Boundary

Recommended interpretation:
- LongMemEval supports SRP runtime compatibility on an external semantic-state workload
- MMLU v3 shows the effect of the SRP treatment under a leakage-free multiple-choice benchmark
- ARC v1 shows the same treatment under a second leakage-free multiple-choice benchmark

Do not infer:
- universal SRP superiority across all LLM tasks
- equivalence between LongMemEval diagnostics and benchmark accuracy
- that smoke artifacts are release evidence

Observed release-branch pattern:
- LongMemEval: strong external-validation support
- MMLU v3: baseline and SRP are both closed and leakage-free, with SRP lower than baseline in the corrected run
- ARC v1: baseline and SRP are both closed and leakage-free, with SRP slightly lower than baseline in the full ARC-Easy run

---

## 5. Invalidated and Non-Release Evidence

| Artifact | Status | Reason |
| --- | --- | --- |
| `experiments/results/mmlu_full_v2/` | Invalidated | Prompt leakage: `expected_answer` appeared in prompt-visible SRP recovered context |
| `experiments/results/mmlu_smoke/` | Validation only | Smoke-scale pipeline verification, not release evidence |
| `experiments/results/arc_smoke/` | Validation only | Smoke-scale pipeline verification, not release evidence |

---

## 6. Release Recommendation

Decision:
`READY_FOR_EVIDENCE_MANIFEST_UPDATE`

Rationale:
- the release-branch evidence set now has one external-validation bundle and two closed, leakage-free full benchmark artifacts
- the invalid MMLU v2 artifact is isolated as provenance only
- the remaining HumanEval work is explicitly design-only and does not block evidence-manifest integration for the current evidence set

Next allowed action:
- update the evidence manifest and then reintegrate the validated manuscript-facing summary chain

