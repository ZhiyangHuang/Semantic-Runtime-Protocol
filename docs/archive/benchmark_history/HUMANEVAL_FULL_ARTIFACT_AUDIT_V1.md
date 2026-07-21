# HumanEval Full Artifact Audit V1

Date: 2026-07-21

Reviewed artifact bundle:
- `experiments/results/humaneval_full_v1/`

Smoke-to-full transition note:
- smoke artifact validated the boundary and artifact contract before this full run

This audit covers the full HumanEval artifact only.

---

## 1. Official Artifact Identification

Confirmed:
- `experiments/results/humaneval_full_v1/` is the authoritative HumanEval full artifact bundle
- the full run is a release-grade benchmark execution artifact

Interpretation:
- the full artifact is the benchmark-family evidence to be used for later release review
- it is distinct from the smoke artifact and supersedes smoke for release-evidence purposes

---

## 2. Artifact Integrity

Confirmed counts:
- `sample_count`: `164`
- `prediction_count`: `328`
- `execution_results_count`: `328`
- baseline predictions: `164`
- SRP predictions: `164`

Presence checks:
- `config.json` exists
- `raw_predictions.jsonl` exists
- `execution_results.json` exists
- `metrics.json` exists
- `metadata.json` exists
- `report.md` exists

Consistency checks:
- every task produced one baseline prediction and one SRP prediction
- every prediction has a corresponding execution record
- artifact hashes are recorded in metadata
- the shared artifact contract is satisfied

---

## 3. Execution Integrity

Confirmed:
- `pass@1` is present in `metrics.json`
- baseline and SRP pass@1 are reported separately
- execution results capture passed/failed state, stdout, stderr, timing, and failure category
- execution failures are retained in the artifact rather than dropped

Metrics summary:
- `pass@1`: `0.987805`
- `baseline_pass@1`: `0.987805`
- `srp_pass@1`: `1.0`
- `pass@1_gap`: `0.012195`

Failure summary:
- `syntax_error`: `2`
- `runtime_error`: `0`
- `timeout`: `0`
- `sandbox_error`: `0`

Execution integrity note:
- the denominator remains the full evaluated task count
- the artifact does not collapse failures into silence

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
- `execution_timeout_seconds`: `5.0`

---

## 5. Decision

Status:
- `PASS`

Meaning:
- the HumanEval full artifact is complete and auditable
- the full bundle is suitable for prompt leakage audit and closure review

Next allowed action:
- write the full HumanEval prompt leakage audit

