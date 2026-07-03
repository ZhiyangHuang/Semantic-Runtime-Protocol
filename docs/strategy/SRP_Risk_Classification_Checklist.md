# SRP Risk Classification Checklist

## Purpose

This checklist records which SRP-family experiment lines are currently safe to treat as formal evidence, which lines should be treated as legacy archive evidence, and which lines should only be promoted after a refactor rerun.

The goal is not to delete evidence.
The goal is to keep formal evidence, legacy archive outputs, and future refactor reruns separated so later comparisons do not silently mix different protocol generations.

## Scope

This checklist is limited to:

- inference-time SRP behavior
- retrieval-guided hybrid behavior
- runtime-state shaping
- validation-side shaping

It does not claim to classify training-time contamination, model pretraining leakage, or optimizer-level memorization.

Those broader risks are acknowledged in the risk report, but they are not the primary focus of this checklist.

## Classification Rule

### Definite Risk

A line belongs here if the current code already shows a concrete protocol mismatch or a direct benchmark-shaping path that should not be treated as clean comparison evidence.

### Possible Risk

A line belongs here if the current code still has a plausible leakage or benchmark-shaping path, but we cannot yet say the experimental data is invalid without refactoring and rerunning.

### Clean After Refactor

A line belongs here only after:

- `expected_keywords` is removed from runtime-state shaping
- validation no longer depends on evaluation-shaped keyword pools
- compression/recovery use admissible evidence-oriented state only
- the line is rerun under the refactored protocol

## Current Classification

### `rag_srp`

Status: **definite risk**

Reason:

- legacy hybrid logic
- no main-line commit/rollback semantics
- runtime state still shaped by `expected_keywords`
- not generation-matched to the current main SRP path

Interpretation:

- useful as exploratory history
- not clean enough for final same-generation comparison

### `rag_srp_anchor`

Status: **definite risk**

Reason:

- legacy anchor hybrid logic
- custom recovery path rather than the shared main-line recovery path
- no main-line commit/rollback semantics
- runtime state still shaped by `expected_keywords`

Interpretation:

- useful as exploratory evidence
- not clean enough to compare directly with the current main SRP line

### `rag_srp_v2`

Status: **possible risk**

Reason:

- it is structurally closer to the current SRP line
- it has commit/rollback semantics
- but it still seeds runtime state and validation from `expected_keywords`

Interpretation:

- likely better than the older hybrids
- still not clean enough to be treated as fully refactor-safe evidence

### Main `srp`

Status: **possible risk**

Reason:

- current main SRP still uses `expected_keywords` in runtime-state shaping and validation
- the protocol is better than the legacy hybrids, but not yet fully refactor-clean

Interpretation:

- the current results are meaningful
- but they are not the final clean version until the runtime-state source cleanup is done

## Clean-After-Refactor Target

None of the current lines should be treated as fully clean after refactor yet.

The target clean state is:

- no `expected_keywords` in runtime-state construction
- no evaluation-side keyword pool in commit decisions
- only admissible evidence, constraints, and anchor-compatible state in SRP packaging

After that refactor, a rerun would be required before any line is promoted to clean comparison evidence.

## Data Handling Guidance

Current rule:

- keep formal comparison outputs in the main results path
- move legacy or suspect hybrid outputs out of the clean comparison path

Recommended treatment:

- `rag_srp` and `rag_srp_anchor`: archive as legacy exploratory outputs
- `rag_srp_v2`: keep as a candidate protocol line, but do not promote its old results to clean evidence yet
- main `srp`: keep in the main line, but classify its current results as possible-risk until refactored

## Formal Results Status

The `first_paper_formal_local` outputs are **not** legacy contamination.

They should be treated as:

- `retain as formal evidence`
- `re-run after refactor before final claim`

This means:

- keep them in the main results path
- use them as the current formal baseline for the paper draft
- do not present them as the final clean post-refactor evidence

Reason:

- they come from the validated formal workflow
- they support the paper's current comparison story
- but the current SRP runtime still has an acknowledged `expected_keywords` shaping risk, so a refactored rerun is still required before making the strongest final claim

### Recommended Naming And Segregation

To avoid future confusion, keep the current outputs in a clearly labeled **formal evidence** namespace, and place the post-refactor rerun in a separate namespace.

Recommended split:

- current evidence: `first_paper_formal_local`
- future refactor rerun: `first_paper_formal_local_refactored`

If a broader organization is preferred, use:

- `formal_current/first_paper_formal_local`
- `formal_refactored/first_paper_formal_local`

The important rule is:

- do not overwrite the current formal evidence with the refactored rerun
- do not mix the two generations in the same directory

This keeps the current evidence intact while still making room for a clean post-refactor comparison later.

## New Risk Evidence: `risk_test_srp_vs_hybrids_5_7`

The temporary risk-test comparison confirmed the current classification boundary.

Observed results:

- `srp`
  - `5 cycles`: `mean_drift = 0.054`, `mean_task_success = 0.9167`, `mean_query_success = 0.8444`
  - `7 cycles`: `mean_drift = 0.054`, `mean_task_success = 0.9167`, `mean_query_success = 0.8254`
- `rag_srp_anchor`
  - `5 cycles`: `mean_drift = 0.4049`, `mean_task_success = 0.92`, `mean_query_success = 0.8222`
  - `7 cycles`: `mean_drift = 0.4257`, `mean_task_success = 0.8667`, `mean_query_success = 0.8254`
- `rag_srp_v2`
  - `5 cycles`: `mean_drift = 0.0511`, `mean_task_success = 0.9167`, `mean_query_success = 1.0`
  - `7 cycles`: `mean_drift = 0.0492`, `mean_task_success = 0.9167`, `mean_query_success = 0.9524`

Interpretation:

- `rag_srp_anchor` remains clearly legacy-risk-bearing and does not appear to be a clean candidate for final evidence.
- `rag_srp_v2` is the closest legacy-adjacent line to the current main SRP behavior, but it still remains risk-bearing because the runtime state shaping has not yet been fully refactored away from evaluation-side inputs.
- main `srp` remains the formal evidence line for the current paper package, but it still needs the refactor rerun before it can be promoted to the strongest final claim.

Practical classification after this risk test:

- `rag_srp` -> definite risk
- `rag_srp_anchor` -> definite risk
- `rag_srp_v2` -> possible risk
- main `srp` -> possible risk / formal evidence pending refactor rerun
