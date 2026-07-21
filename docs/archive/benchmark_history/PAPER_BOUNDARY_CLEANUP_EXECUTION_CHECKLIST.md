# Paper Boundary Cleanup Execution Checklist

This checklist prepares a safe cleanup procedure for the paper boundary.

Goal:
make `paper/` clean enough for benchmark authorization without losing any work.

This is execution preparation only:
- do not modify files
- do not run git commands
- do not commit changes
- do not revert changes
- do not run benchmarks

---

## 1. Objective

The goal is to make the paper boundary clean for benchmark authorization while preserving the current manuscript and evidence-related work for later restoration.

---

## 2. Files Requiring Temporary Preservation

### STASH TEMPORARILY

| File | Current Status | Reason | Preservation Action |
|---|---|---|---|
| `paper/SRP_ARXIV_DRAFT_V1.md` | modified | contains benchmark-facing narrative updates that should not remain active before authorization | stash temporarily |
| `paper/SRP_PAPER_FINAL_V1.md` | modified | mirrors the same benchmark-facing narrative updates | stash temporarily |
| `paper/latex/body_content.md` | modified | LaTeX body mirrors the benchmark-facing narrative updates | stash temporarily |

### WAIT UNTIL AFTER FULL BENCHMARK

| File | Current Status | Reason | Preservation Action |
|---|---|---|---|
| `paper/SRP_MAIN_RESULTS_SUMMARY_V1.md` | modified | paper-facing summary of benchmark counts and evidence tiers | keep isolated until full benchmark audit completes |
| `paper/SRP_MAIN_RESULTS_SUMMARY_V1.json` | untracked | generated summary artifact that encodes benchmark counts | keep isolated until full benchmark audit completes |
| `paper/SRP_MAIN_RESULTS_SUMMARY_V1.metadata.json` | untracked | metadata for the generated summary artifact | keep isolated until full benchmark audit completes |
| `paper/main_evidence_manifest.json` | untracked | release-facing evidence manifest and claim registry | keep isolated until full benchmark audit completes |

---

## 3. Safe Operation Sequence

### Step 1: Record current provenance

Before any cleanup action, preserve:
- current paper file list
- current diff summary
- current rationale for preserving each file

### Step 2: Create a backup or stash point

Use a reversible preservation method so the current manuscript edits can be restored later without re-deriving them.

### Step 3: Temporarily remove blocked paper changes from the working tree

Remove only the changes that block authorization:
- manuscript files with benchmark-facing edits
- generated summary and manifest files that should not be active before full benchmark authorization

### Step 4: Verify the paper boundary

Confirm the paper tree is clean enough that no unverified benchmark-facing evidence remains active.

### Step 5: Prepare authorization re-review

Once the boundary is clean, re-check the authorization gate before any benchmark execution.

---

## 4. Verification Commands

Use the following checks during cleanup review:

- `git status -- paper/`
- confirm there are no uncommitted changes under `paper/`
- confirm no evidence manifest changes remain active

Verification target:
- the paper boundary should be clean enough that the authorization checklist can be re-reviewed

---

## 5. Recovery Procedure

After benchmark audit and authorization:

1. Restore the temporarily preserved manuscript files.
2. Restore the generated summary and manifest only if the audited full benchmark evidence is ready to be promoted.
3. Re-validate the paper-facing outputs against the audited artifacts before committing anything new.

Important:
- preservation is temporary
- nothing should be lost
- the original manuscript work should be recoverable exactly

---

## 6. Authorization Recheck Condition

Phase 5.5 can be reviewed again only when all of the following are true:

- the paper boundary is clean
- no unverified benchmark claims remain active
- evidence manifests are untouched until the benchmark audit is complete

At that point, the authorization checklist can be rerun to determine whether Phase 6 is eligible to proceed.

---

## 7. Minimal Executable Order

Use this exact order when performing the cleanup:

### Step 0: Save current status snapshot

Record:
- `git status`
- `git diff --stat`
- `git diff -- paper/`

Purpose:
- preserve cleanup provenance before any cleanup action

### Step 1: Temporarily preserve manuscript files

Target files:
- `paper/SRP_ARXIV_DRAFT_V1.md`
- `paper/SRP_PAPER_FINAL_V1.md`
- `paper/latex/body_content.md`

Action:
- stash or otherwise temporarily preserve these files without deleting them

Purpose:
- remove manuscript-level benchmark-facing edits from the active working tree

### Step 2: Isolate evidence-facing generated files

Target files:
- `paper/SRP_MAIN_RESULTS_SUMMARY_V1.md`
- `paper/SRP_MAIN_RESULTS_SUMMARY_V1.json`
- `paper/SRP_MAIN_RESULTS_SUMMARY_V1.metadata.json`
- `paper/main_evidence_manifest.json`

Action:
- keep them out of the active paper state until after the full benchmark audit

Purpose:
- prevent unverified benchmark-facing evidence from remaining active before authorization

### Step 3: Verify the paper boundary

Checks:
- `git status -- paper/`
- `git diff -- paper/`

Target:
- no remaining uncommitted `paper/` changes

### Step 4: Re-run authorization review

Action:
- re-check `FULL_BENCHMARK_EXECUTION_AUTHORIZATION_CHECKLIST.md`

Expected outcome:
- `Phase 5.5` moves from `BLOCKED` to `AUTHORIZED` only if the paper boundary is clean

### Step 5: Proceed only after authorization

Allowed next action:
- `Phase 6.1` full MMLU execution

Not allowed:
- benchmark runs before authorization
- paper updates before audited results
- manifest updates before audited full benchmark evidence

