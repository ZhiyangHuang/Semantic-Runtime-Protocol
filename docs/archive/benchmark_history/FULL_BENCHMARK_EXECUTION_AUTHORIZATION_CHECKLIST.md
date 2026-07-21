# Full Benchmark Execution Authorization Checklist

This checklist is the final gate before full benchmark execution.

It is a checklist only:
- do not execute benchmarks
- do not generate full benchmark artifacts
- do not modify `paper/`
- do not update evidence manifests

---

## 1. Repository State Check

- PASS: Working tree status recorded - `git status --short` captured for the authorization review.
- PASS: Current commit hash recorded - `be79305811f69c839c947e7018aa3559e7553d25`.
- PASS: No uncommitted paper changes - `git status --short -- paper/` is empty after cleanup.
- PASS: Benchmark infrastructure version fixed - the shared benchmark layer validated by smoke tests is unchanged for this review.

Required evidence:
- store the commit hash used for the run
- store the working tree status snapshot
- confirm the shared benchmark layer is the one validated by smoke tests

---

## 2. Environment Check

- PASS: Python environment verified - the benchmark code executes in the current Python environment.
- PASS: Dependencies verified - benchmark packages and dataset tooling are available.
- PASS: Model endpoint verified - the local OpenAI-compatible endpoint is reachable.
- PASS: Hardware availability verified - the current host has sufficient compute availability for the planned runs.
- PASS: Storage availability verified - there is enough disk space for full artifacts and raw predictions.

Required evidence:
- confirm the local OpenAI-compatible endpoint is reachable
- confirm the environment can import benchmark packages
- confirm there is enough disk space for full artifacts and raw predictions

---

## 3. Dataset Check

### MMLU

- PASS: Dataset source fixed - `cais/mmlu`.
- PASS: Dataset reference recorded - the frozen dataset reference is recorded in the execution plan and smoke configs.
- PASS: Subjects fixed - the benchmark scope is fixed before execution.
- PASS: Split fixed - the validation split is fixed for the controlled full run.

### ARC

- PASS: Dataset source fixed - `allenai/ai2_arc`.
- PASS: ARC-Easy / ARC-Challenge decision fixed - ARC-Easy is in scope for the current full run; ARC-Challenge remains optional and separate.
- PASS: Split fixed - the selected split is fixed before execution.

Required evidence:
- dataset reference must be the same one used in the execution plan
- any subject or split policy must be fixed before execution

---

## 4. Model Configuration Check

- PASS: Model identifier fixed - `Qwen/Qwen3-4B-AWQ`.
- PASS: Temperature fixed - `0.0` for deterministic smoke-style behavior and kept fixed for full-run comparability.
- PASS: Max tokens fixed - bounded for choice-based benchmarks.
- PASS: Generation settings identical between variants where required - baseline and SRP share the same generation settings.

Required evidence:
- baseline and SRP runs must share the same generation settings
- only intended context / SRP differences are allowed between variants

---

## 5. Baseline vs SRP Integrity Check

### Baseline

- PASS: Exact context configuration defined - baseline keeps the original task prompt and original dataset context only.

### SRP

- PASS: Exact SRP state input defined - SRP state input and recovered semantic context are specified in the execution plan.
- PASS: Recovery mechanism defined - the shared benchmark runner injects the recovered context path only.
- PASS: Prompt integration defined - the prompt family is aligned with baseline except for the approved SRP context path.

### Verify

- PASS: Only intended variable changes - baseline and SRP differ only in memory/context handling.
- PASS: No hidden prompt differences - the comparison protocol keeps the prompt family aligned.
- PASS: No evaluation leakage - scoring does not peek at the answer key.

Required evidence:
- baseline and SRP prompts must be comparable except for the approved SRP context path
- evaluation logic must not peek at the answer key

---

## 6. Artifact Safety Check

### Before execution

- PASS: Output directory prepared - the full-run targets are distinct from smoke directories (`experiments/results/mmlu/`, `experiments/results/arc/`).
- PASS: Previous artifacts archived - smoke artifacts remain isolated; full-run output paths are separate.
- PASS: No overwrite risk - reruns must use versioned or clearly separated run directories.

### After execution

- N/A: Raw predictions exist - this is a pre-execution authorization review.
- N/A: Metrics generated automatically - this will be checked after execution.
- N/A: Metadata generated - this will be checked after execution.
- N/A: Reports generated - this will be checked after execution.

Required evidence:
- the run directory must be empty or versioned before the run starts
- reruns must not overwrite audited artifacts without a documented reason

---

## 7. Failure Policy

### If dataset failure occurs

- PASS: stop the run
- PASS: do not synthesize results
- PASS: record the failure reason

### If endpoint failure occurs

- PASS: stop before claiming benchmark completion
- PASS: preserve any partial outputs only for diagnosis

### If partial execution occurs

- PASS: mark the run as incomplete
- PASS: do not backfill missing metrics manually

### If metric failure occurs

- PASS: preserve raw predictions
- PASS: fix the metric path before rerunning

Required evidence:
- all failure states must be explicit in the run log or metadata

---

## 8. Paper Boundary

Before benchmark completion:
- PASS: no paper changes - the active working tree no longer contains uncommitted `paper/` files.

After benchmark completion:
- PASS: only audited artifacts may update result summaries, evidence manifests, and tables

Required evidence:
- paper-facing files remain untouched until the full benchmark artifacts are audited

---

## 9. Final Authorization

### Authorization outcome

- PASS: All gates passed
- PASS: Full benchmark run authorized

### Blocked outcome

- N/A: Blocked

### Decision rule

Authorize the full benchmark run only if:
- repository state is recorded and clean enough
- environment is verified
- dataset and split policies are frozen
- model configuration is fixed
- baseline vs SRP integrity is confirmed
- artifact safety is confirmed
- failure handling is understood
- paper boundary remains untouched

## Final Decision

AUTHORIZED

No blockers remain for the paper boundary gate.

---

## 10. Execution Notes

- Execute MMLU full before ARC full unless a review changes the order.
- Do not alter the benchmark protocol after this checklist is approved.
- Do not use full benchmark execution to retroactively change the paper claim.
