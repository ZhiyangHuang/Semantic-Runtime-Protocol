# HumanEval Full Prompt Leakage Audit V1

Date: 2026-07-21

Reviewed artifact bundle:
- `experiments/results/humaneval_full_v1/`

Scope:
- 164 HumanEval tasks
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
- `private_tests`
- `expected_output`
- `grader_logic`

---

## 2. Result Summary

Prompt-visible leakage counts:
- `reference_solution`: `0`
- `canonical_solution`: `0`
- `hidden_tests`: `0`
- `private_tests`: `0`
- `expected_output`: `0`
- `grader_logic`: `0`

Variant counts:
- baseline records: `164`
- srp records: `164`

---

## 3. Conclusion

Confirmed:
- baseline prompts do not expose scoring-only or hidden-evaluation fields
- SRP prompts only add approved runtime context
- no reference solution or hidden test content appears in the prompt-visible path

Decision:
- `PASS`

Meaning:
- the HumanEval full prompt boundary is clean
- the full artifact respects the treatment boundary

