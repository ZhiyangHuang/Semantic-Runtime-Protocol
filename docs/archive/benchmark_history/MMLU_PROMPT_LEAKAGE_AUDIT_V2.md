# MMLU Prompt Leakage Audit V2

Date: 2026-07-21
Review basis:
- `MMLU_SRP_TREATMENT_DESCRIPTION.md`
- `FULL_MMLU_EXECUTION_RECORD_V3.md`
- `experiments/results/mmlu_full_v3/raw_predictions.jsonl`
- `experiments/results/mmlu_full_v3/metadata.json`
- `experiments/benchmarks/mmlu/adapter.py`

This audit verifies that the corrected full MMLU v3 artifact no longer leaks the gold answer into the prompt-visible SRP context.

---

## 1. Audit Objective

Check whether the SRP treatment on MMLU preserves the intended boundary:
- baseline and SRP share the same benchmark case
- SRP may add recovered semantic context
- the recovered context must not expose the gold answer to the model-visible prompt

---

## 2. Findings

### 2.1 Expected Answer Leakage

Result:
- baseline prompts containing `expected_answer`: `0 / 14042`
- SRP prompts containing `expected_answer`: `0 / 14042`

Verdict:
- PASS

### 2.2 Reference Answer Leakage

Result:
- baseline prompts containing `reference_answer`: `0 / 14042`
- SRP prompts containing `reference_answer`: `0 / 14042`

Verdict:
- PASS

### 2.3 Gold Label / Metadata Fields

Result:
- `subject` is preserved in both baseline and SRP prompts: PASS
- `choices` are preserved in both baseline and SRP prompts: PASS
- `question` is preserved in both baseline and SRP prompts: PASS
- `metadata.json` does not expose prompt-visible answer fields: PASS

---

## 3. Root Cause Closure

The prompt leakage issue observed in the earlier MMLU v2 run was caused by `expected_answer` being serialized into the SRP recovered context.

In v3:
- the MMLU adapter removes `expected_answer` from `srp_recovered_context`
- the shared benchmark runner applies the prompt leakage guard before generation

Therefore:
- the prompt-visible SRP context no longer includes the gold answer
- the leakage boundary is now compliant with the treatment description

---

## 4. Evaluation Integrity Impact

Confirmed:
- baseline and SRP share the same benchmark cases
- `expected_answer` is not present in either prompt path
- metrics were generated automatically
- the artifact is consistent with the audited treatment boundary

---

## 5. Decision

Decision:
- PASS

Implication:
- the corrected MMLU v3 artifact is eligible for closure review and ARC inheritance of the same prompt-leakage policy

