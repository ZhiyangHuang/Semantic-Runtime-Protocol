# ARC Pre-Flight Audit

Date: 2026-07-21

This document records the pre-flight readiness review for full ARC execution.
It is a review only and does not execute the full benchmark.

Reviewed evidence:
- `experiments/benchmarks/arc/adapter.py`
- `experiments/benchmarks/arc/config.py`
- `experiments/benchmarks/arc/runner.py`
- `experiments/benchmarks/arc/tests/test_adapter.py`
- `experiments/benchmarks/common/safety.py`
- `experiments/results/arc_smoke/config.json`
- `experiments/results/arc_smoke/raw_predictions.jsonl`
- `experiments/results/arc_smoke/metrics.json`
- `experiments/results/arc_smoke/metadata.json`
- `BENCHMARK_PHASE_STATUS_SUMMARY.md`

---

## 1. Prompt Leakage Check

Status: PASS

Confirmed:
- the shared benchmark runner applies a blocking prompt leakage check before generation
- the ARC adapter implements `validate_prompt_leakage(...)`
- the ARC adapter does not place `expected_answer` into prompt-visible recovered context
- the ARC adapter does not place `reference_answer` into prompt-visible recovered context

Smoke artifact audit:
- `raw_predictions.jsonl` contains 100 records total
- baseline records: 50
- SRP records: 50
- prompt text occurrences of `expected_answer`: 0
- prompt text occurrences of `reference_answer`: 0

Interpretation:
- scoring-only fields are present in prediction records for auditability
- scoring-only fields do not appear in the model-visible prompt path

---

## 2. Prompt Parity Check

Status: PASS

Confirmed:
- baseline and SRP use the same benchmark case content
- both variants use the same question text
- both variants preserve the same choices
- both variants use the same system prompt
- both variants use the same model identifier and generation parameters

Allowed difference:
- SRP receives the approved recovered semantic context path

Not allowed:
- gold answer leakage
- reference answer leakage
- hidden annotations in prompt-visible context

Pairing audit:
- every sampled ARC case has both `baseline` and `srp` records
- no case is missing one of the two variants

---

## 3. Artifact Contract Check

Status: PASS

ARC smoke artifact contains:
- `config.json`
- `raw_predictions.jsonl`
- `metrics.json`
- `metadata.json`
- `report.md`

Artifact completeness:
- the bundle is present in `experiments/results/arc_smoke/`
- metadata contains provenance and artifact hashes
- metrics were derived from generated predictions

Note:
- the smoke bundle validates the artifact writer and is not the full benchmark artifact
- full ARC must use a separate versioned output directory

---

## 4. Evaluation Integrity Check

Status: PASS

Confirmed:
- ARC scoring is accuracy-based
- baseline and SRP are evaluated against the same benchmark cases
- no manual metric editing was performed
- the shared runner and shared safety guard are active

Smoke metrics:
- `sample_count`: `50`
- `prediction_count`: `100`
- `baseline_accuracy`: `0.92`
- `srp_accuracy`: `0.96`
- `accuracy_gap`: `0.04`

Interpretation boundary:
- these are smoke-scale validation results
- they confirm pipeline correctness, not paper-level superiority

---

## 5. Reproducibility Check

Status: PASS

Recorded in artifact metadata:
- model identifier
- dataset version
- prompt format
- sample count
- generation parameters
- SRP configuration
- execution parameters
- artifact hashes

Configured ARC smoke scope:
- dataset source: `hf:allenai/ai2_arc|ARC-Easy|test`
- subset: `ARC-Easy`
- sample limit: `50`
- variants: `baseline`, `srp`

---

## 6. Decision

Decision: READY_FOR_FULL_ARC

Next allowed action:
- execute full ARC under the same authorized protocol and the same leakage policy

Closure note:
- ARC pre-flight is complete
- the shared leakage policy used for MMLU is active for ARC
- no paper-facing claim is promoted by this review

