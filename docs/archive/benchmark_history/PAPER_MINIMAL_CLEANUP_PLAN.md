# Paper Minimal Cleanup Plan

This is a planning-only cleanup plan based on `PAPER_WORKTREE_CHANGE_AUDIT.md` and `FULL_BENCHMARK_EXECUTION_AUTHORIZATION_CHECKLIST.md`.

Goal:
restore a clean paper boundary before re-running the Phase 5.5 authorization review, without deleting safe manuscript work.

---

## 1. Classification Summary

| File | Category | Contains benchmark claims? | Recommended action |
|---|---|---|---|
| `paper/SRP_ARXIV_DRAFT_V1.md` | Evidence-facing content | Yes | STASH TEMPORARILY |
| `paper/SRP_MAIN_RESULTS_SUMMARY_V1.md` | Evidence-facing content | Yes | WAIT UNTIL AFTER FULL BENCHMARK |
| `paper/SRP_PAPER_FINAL_V1.md` | Evidence-facing content | Yes | STASH TEMPORARILY |
| `paper/latex/body_content.md` | Evidence-facing content | Yes | STASH TEMPORARILY |
| `paper/SRP_MAIN_RESULTS_SUMMARY_V1.json` | Generated artifact | Yes | WAIT UNTIL AFTER FULL BENCHMARK |
| `paper/SRP_MAIN_RESULTS_SUMMARY_V1.metadata.json` | Generated artifact | Yes | WAIT UNTIL AFTER FULL BENCHMARK |
| `paper/main_evidence_manifest.json` | Evidence-facing content | Yes | WAIT UNTIL AFTER FULL BENCHMARK |

---

## 2. File-by-File Rationale

### `paper/SRP_ARXIV_DRAFT_V1.md`

- Category: evidence-facing content
- Why it blocks authorization: it now states the release-facing main evidence set and the registry-based policy, which depends on benchmark-facing evidence state that is not yet fully authorized
- Recommended action: `STASH TEMPORARILY`
- Integrity reason: stashing preserves the manuscript changes without letting them participate in the current benchmark authorization boundary

### `paper/SRP_MAIN_RESULTS_SUMMARY_V1.md`

- Category: evidence-facing content
- Why it blocks authorization: it is the paper-facing source of truth for benchmark counts and status tiers
- Recommended action: `WAIT UNTIL AFTER FULL BENCHMARK`
- Integrity reason: this document should only be finalized when the full benchmark evidence exists and has been audited

### `paper/SRP_PAPER_FINAL_V1.md`

- Category: evidence-facing content
- Why it blocks authorization: it mirrors the same release-facing evidence claims as the draft
- Recommended action: `STASH TEMPORARILY`
- Integrity reason: stashing keeps the current paper boundary clean while preserving the intended final wording for later restoration

### `paper/latex/body_content.md`

- Category: evidence-facing content
- Why it blocks authorization: it propagates the same benchmark-count and release-policy narrative into the LaTeX source
- Recommended action: `STASH TEMPORARILY`
- Integrity reason: this keeps the rendered paper aligned with the manuscript state only after the evidence gate is reopened

### `paper/SRP_MAIN_RESULTS_SUMMARY_V1.json`

- Category: generated artifact
- Why it blocks authorization: it is a generated paper-facing summary artifact that encodes benchmark counts before full benchmark authorization
- Recommended action: `WAIT UNTIL AFTER FULL BENCHMARK`
- Integrity reason: generated summary data should not sit in the worktree as active paper-facing evidence until the full evidence chain is authorized

### `paper/SRP_MAIN_RESULTS_SUMMARY_V1.metadata.json`

- Category: generated artifact
- Why it blocks authorization: it is metadata for the generated summary artifact and inherits the same evidence boundary risk
- Recommended action: `WAIT UNTIL AFTER FULL BENCHMARK`
- Integrity reason: metadata for paper-facing generated evidence should be finalized together with the audited benchmark results

### `paper/main_evidence_manifest.json`

- Category: evidence-facing content
- Why it blocks authorization: it is the release-facing claim registry for benchmark counts and evidence tiers
- Recommended action: `WAIT UNTIL AFTER FULL BENCHMARK`
- Integrity reason: the manifest should only be finalized after the benchmark artifacts it references have been audited and approved

---

## 3. Minimal Safe Action Set

To make Phase 5.5 eligible for re-review with minimal disruption:

1. Temporarily stash the manuscript updates in:
   - `paper/SRP_ARXIV_DRAFT_V1.md`
   - `paper/SRP_PAPER_FINAL_V1.md`
   - `paper/latex/body_content.md`

2. Keep the generated evidence files out of the active working tree until the full benchmark audit completes:
   - `paper/SRP_MAIN_RESULTS_SUMMARY_V1.md`
   - `paper/SRP_MAIN_RESULTS_SUMMARY_V1.json`
   - `paper/SRP_MAIN_RESULTS_SUMMARY_V1.metadata.json`
   - `paper/main_evidence_manifest.json`

3. Re-run `git status -- paper/` and confirm the paper boundary is clean enough that no unverified benchmark-facing evidence remains active.

---

## 4. Why This Preserves Research Integrity

- Manuscript wording can be preserved without promoting unverified benchmark claims.
- Generated summary and manifest files remain deferred until the benchmark evidence exists and is audited.
- The paper boundary becomes clean enough for authorization without losing the work already done on the narrative.
- This avoids the two failure modes we are trying to prevent:
  - paper claims getting ahead of evidence
  - benchmark evidence being retrofitted into the paper before audit

---

## 5. Minimal Steps Required To Make Phase 5.5 Eligible For Re-Review

- Stash the three manuscript/body files listed above.
- Defer the generated summary and manifest files until after full benchmark execution and audit.
- Re-check `git status -- paper/`.
- If the paper boundary is clean, re-run the authorization review.
- If the paper boundary is still dirty, classify any remaining files before touching them.

