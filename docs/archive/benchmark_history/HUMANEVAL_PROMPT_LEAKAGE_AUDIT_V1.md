# HumanEval Prompt Leakage Audit V1

Date: 2026-07-21

Reviewed smoke artifact:
- `experiments/results/humaneval_smoke_v1/`

Smoke scope:
- 20 synthetic/local tasks
- baseline and SRP variants

This audit covers prompt-visible leakage only.

---

## 1. Audit Method

Reviewed:
- every prompt in `raw_predictions.jsonl`
- every execution record in `execution_results.json`

Checked for prompt-visible leakage of:
- `reference_solution`
- `canonical_solution`
- `hidden_tests`
- `test_cases`
- `expected_output`
- `gold_solution`

---

## 2. Result Summary

Prompt-visible leakage counts:
- `reference_solution`: `0`
- `canonical_solution`: `0`
- `hidden_tests`: `0`
- `test_cases`: `0`
- `expected_output`: `0`
- `gold_solution`: `0`

Variant counts:
- baseline records: `20`
- srp records: `20`

---

## 3. Conclusion

Confirmed:
- baseline prompts do not expose scoring-only or hidden-evaluation fields
- SRP prompts only add approved runtime context
- no gold solution or hidden test content appears in the prompt-visible path

Decision:
- `PASS`

Meaning:
- the HumanEval smoke prompt boundary is clean
- the execution boundary can proceed to artifact audit and closure review

