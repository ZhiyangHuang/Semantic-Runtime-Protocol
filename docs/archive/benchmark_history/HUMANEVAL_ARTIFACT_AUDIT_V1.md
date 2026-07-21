# HumanEval Artifact Audit V1

Date: 2026-07-21

Reviewed artifact bundle:
- `experiments/results/humaneval_smoke_v1/`

Smoke scope:
- 20 synthetic/local tasks
- 40 evaluated predictions total
- baseline and SRP variants

This audit covers the smoke artifact only.

---

## 1. Official Artifact Identification

Confirmed:
- `experiments/results/humaneval_smoke_v1/` is the official HumanEval smoke artifact bundle
- the smoke run is a boundary-validation artifact, not the full benchmark release artifact

Interpretation:
- the smoke artifact exists to validate the execution path
- it is not paper-facing release evidence

---

## 2. Artifact Integrity

Confirmed counts:
- `sample_count`: `20`
- `prediction_count`: `40`
- `execution_results_count`: `40`
- baseline predictions: `20`
- SRP predictions: `20`

Presence checks:
- `config.json` exists
- `raw_predictions.jsonl` exists
- `execution_results.json` exists
- `metrics.json` exists
- `metadata.json` exists
- `report.md` exists

Consistency checks:
- raw predictions align with the reported prediction count
- execution results are present and populated
- metadata includes artifact hashes
- the shared artifact contract is satisfied

---

## 3. Execution Integrity

Confirmed:
- `pass@1` is present in `metrics.json`
- baseline and SRP pass@1 values are reported separately
- execution results capture passed/failed state, stdout, stderr, timing, and failure category
- no timeout, runtime, syntax, or sandbox failures occurred in the smoke run

Metrics summary:
- `pass@1`: `1.0`
- `baseline_pass@1`: `1.0`
- `srp_pass@1`: `1.0`
- `pass@1_gap`: `0.0`

Note:
- the smoke dataset was intentionally simple so the main goal was boundary validation, not benchmark difficulty

---

## 4. Provenance and Safety

Confirmed:
- prompt leakage guard is enabled
- executor isolation is enabled via subprocess execution
- timeout policy is recorded in metadata
- payloads remain isolated from the shared artifact surface
- `paper/` was not modified
- evidence manifests were not modified

Metadata confirms:
- `generated_by`: `humaneval_runner_v1`
- `runner_version`: `humaneval_runner_v1`
- `executor_version`: `humaneval_executor_v1`
- `execution_sandbox_policy`: `subprocess_isolation_v1`
- `allow_network`: `False`

---

## 5. Decision

Status:
- `PASS`

Meaning:
- the HumanEval smoke artifact is complete and auditable
- the smoke bundle is suitable for closure review

Next allowed action:
- write the HumanEval smoke closure review

