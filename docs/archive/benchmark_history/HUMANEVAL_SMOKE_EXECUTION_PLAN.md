# HumanEval Smoke Execution Plan

Date: 2026-07-21

This plan defines the smallest HumanEval execution needed to validate the evaluation boundary before any full release run.

This phase is planning only.

Do not:
- run HumanEval full execution
- update `paper/`
- update evidence manifests
- claim benchmark performance

---

## 1. Validation Objective

The smoke run must prove that the HumanEval implementation can:

- load tasks
- construct prompts without leakage
- generate code
- extract executable code
- execute code in isolation
- compute `pass@1`
- write the shared artifact contract

The smoke run does not exist to measure code-generation superiority.

---

## 2. Prompt Leakage Boundary

The HumanEval prompt path must not expose scoring-only or hidden-evaluation fields.

Forbidden in prompt-visible content:
- `reference_solution`
- `canonical_solution`
- `test_cases`
- `hidden_tests`
- `unit_tests`
- `expected_output`

Allowed in prompt-visible content:
- `problem_statement`
- `function_signature`
- `docstring`
- `input_format`
- `output_format`
- approved SRP runtime context

Baseline and SRP prompts must differ only by approved SRP runtime context.

---

## 3. Executor Boundary

The smoke run must verify that generated code is executed through the HumanEval executor boundary.

Required execution properties:
- code extraction occurs before execution
- execution happens in an isolated subprocess
- timeout enforcement is active
- exceptions are captured and categorized
- stdout and stderr are preserved separately
- no host filesystem writes escape the sandbox boundary

The smoke run should include at least one failure-injection case if possible:
- syntax error
- runtime error
- timeout

---

## 4. Metric Boundary

Primary metric:
- `pass@1`

The smoke run must confirm:
- `pass@1` is computed from first-sample task success
- it is not accidentally treated as any-sample-pass
- it is not silently converted into best-of-n

Required secondary counts:
- passed tasks
- failed tasks
- syntax error count
- runtime error count
- timeout count
- sandbox error count

---

## 5. Artifact Contract

Expected output directory:
- `experiments/results/humaneval_smoke_v1/`

Expected files:
- `config.json`
- `raw_predictions.jsonl`
- `execution_results.json`
- `metrics.json`
- `metadata.json`
- `report.md`

The smoke artifact must keep `execution_results.json` as a first-class artifact because HumanEval is execution-based.

---

## 6. Sample Policy

Recommended sample size:
- 20 to 50 tasks

Reason:
- enough to validate runner / executor / leakage guard / artifact writer
- small enough to keep the first smoke pass auditable and quick

Do not run the full dataset in the smoke phase.

---

## 7. Execution Variants

Required variants:
- baseline
- srp

Comparison rule:
- baseline and SRP must see the same task payload
- SRP may differ only by approved runtime context recovery
- no reference solution or hidden test may be introduced into either prompt path

---

## 8. Smoke Deliverables

After the smoke run, produce:

- `HUMANEVAL_PROMPT_LEAKAGE_AUDIT_V1.md`
- `HUMANEVAL_ARTIFACT_AUDIT_V1.md`
- `HUMANEVAL_SMOKE_CLOSURE_REVIEW_V1.md`

### Leakage audit must confirm
- reference solution leakage: `0`
- canonical solution leakage: `0`
- hidden test leakage: `0`
- unit test leakage: `0`
- expected output leakage: `0`

### Artifact audit must confirm
- the five shared artifact files exist
- `execution_results.json` exists and is populated
- metadata contains provenance and hashes
- official execution authority is preserved

### Closure review must confirm
- executor works
- pass@1 calculation is correct
- artifact contract is complete
- leakage guard is enabled
- provenance is recorded

---

## 9. Failure Handling

If any of the following occurs:
- prompt leakage is detected
- execution isolation fails
- timeout handling fails
- pass@1 calculation is ambiguous
- artifact generation is incomplete

then:
- stop the smoke run
- fix the implementation boundary
- rerun the smoke phase before any full execution

---

## 10. Next Step

If this smoke plan is approved:
1. run HumanEval smoke
2. audit prompt leakage
3. audit artifacts
4. write the smoke closure review
5. only then consider full HumanEval execution

