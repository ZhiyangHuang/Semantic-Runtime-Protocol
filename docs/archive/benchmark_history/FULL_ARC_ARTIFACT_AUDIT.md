# Full ARC Artifact Audit

Date: 2026-07-21

Reviewed artifact:
- `experiments/results/arc_full_v1/`

Execution record:
- `FULL_ARC_EXECUTION_RECORD_V1.md`

This document audits the full ARC artifact bundle and confirms whether it is suitable for release-branch evidence tracking.

---

## 1. Artifact Identification

Confirmed:
- `experiments/results/arc_full_v1/` is the authoritative full ARC artifact bundle for the current release branch
- the run is scoped to `ARC-Easy` full test coverage
- the smoke artifact remains separate at `experiments/results/arc_smoke/`

Not in scope for this run:
- ARC-Challenge

---

## 2. Artifact Completeness

Confirmed files:
- `config.json`
- `raw_predictions.jsonl`
- `metrics.json`
- `metadata.json`
- `report.md`

Artifact completeness status: PASS

---

## 3. Record Counts

From `metrics.json`:
- `sample_count`: `2376`
- `prediction_count`: `4752`
- `baseline` records: `2376`
- `srp` records: `2376`

Pairing audit:
- every benchmark case has both a baseline and SRP prediction
- no case is missing a variant

---

## 4. Metric Integrity

Confirmed:
- metrics are derived from generated predictions
- no manual metric editing was performed
- shared runner metrics and adapter metrics are aligned

Key metrics:
- `accuracy`: `0.904461`
- `baseline_accuracy`: `0.904461`
- `srp_accuracy`: `0.883838`
- `accuracy_gap`: `-0.020623`
- `failed_prediction_count`: `0`

Interpretation boundary:
- this is a full benchmark result for ARC-Easy only
- it is not a paper claim by itself

---

## 5. Provenance

Confirmed from `metadata.json`:
- benchmark name
- dataset version
- adapter name
- generation timestamp
- runner version
- sample count
- variant count
- model identifier
- prompt format
- seed
- SRP configuration
- execution parameters
- full config copy
- artifact hashes

Provenance status: PASS

---

## 6. Decision

Decision: PASS

The ARC full artifact is complete and suitable for closure review and prompt leakage audit.

