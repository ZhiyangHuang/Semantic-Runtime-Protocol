# ARC Prompt Leakage Audit V1

Date: 2026-07-21

Reviewed artifact:
- `experiments/results/arc_full_v1/raw_predictions.jsonl`

This document audits prompt-visible leakage only.

---

## 1. Audit Method

The full ARC raw prediction stream was decoded and inspected for:
- prompt-visible `expected_answer`
- prompt-visible `reference_answer`
- gold-label fields in recovered context
- variant parity between baseline and SRP

---

## 2. Leakage Results

Status: PASS

Counts from the full ARC artifact:
- total records: `4752`
- baseline records: `2376`
- SRP records: `2376`
- prompt occurrences of `expected_answer`: `0`
- prompt occurrences of `reference_answer`: `0`
- cases missing a baseline/SRP pair: `0`

Interpretation:
- scoring-only fields are present in artifact records for auditability
- scoring-only fields do not appear in prompt-visible text
- the shared leakage guard is functioning in the full ARC run

---

## 3. Treatment Boundary

Confirmed:
- baseline and SRP use the same ARC case content
- baseline and SRP use the same system prompt and generation parameters
- the only allowed difference is the approved SRP recovered context path

Not permitted:
- gold-answer leakage
- reference-answer leakage
- hidden annotations in prompt-visible SRP context

---

## 4. Decision

Decision: PASS

The full ARC artifact does not exhibit prompt leakage in the inspected raw predictions.

