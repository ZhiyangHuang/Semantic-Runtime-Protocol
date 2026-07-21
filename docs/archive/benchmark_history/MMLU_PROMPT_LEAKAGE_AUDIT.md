# MMLU Prompt Leakage Audit

Date: 2026-07-21
Review basis:
- `MMLU_SRP_TREATMENT_DESCRIPTION.md`
- `FULL_MMLU_EXECUTION_RECORD_V1.md`
- `FULL_MMLU_EXECUTION_RECORD_V2.md`
- `FULL_MMLU_ARTIFACT_AUDIT.md`
- `experiments/results/mmlu_full_v2/raw_predictions.jsonl`
- `experiments/results/mmlu_full_v2/metadata.json`
- `experiments/benchmarks/mmlu/adapter.py`

This audit reviews whether the prompt-visible SRP context leaks benchmark answer information.

---

## 1. Audit Objective

Check whether the SRP treatment on MMLU preserves the intended boundary:
- baseline and SRP should share the same benchmark case
- SRP may add recovered semantic context
- the recovered context must not expose the gold answer to the model-visible prompt

---

## 2. Findings

### 2.1 Expected Answer Leakage

Result:
- baseline prompts containing `expected_answer`: `0 / 14042`
- SRP prompts containing `expected_answer`: `14042 / 14042`

Verdict:
- FAIL

Interpretation:
- the SRP prompt-visible recovered context includes the gold answer for every case
- this violates the treatment boundary defined in `MMLU_SRP_TREATMENT_DESCRIPTION.md`

Evidence:
- sample SRP prompt includes:
  - `expected_answer: B`
  - question
  - choices
  - subject

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

Important distinction:
- the answer leak is not coming from `metadata.json`
- the leak is coming from the SRP prompt-visible recovered context block

---

## 3. Root Cause

The leak is introduced in `experiments/benchmarks/mmlu/adapter.py`:

- `create_cases()` constructs `recovered_context`
- that context includes `expected_answer: answer`
- `build_prompt()` passes `case.srp_recovered_context` into the SRP prompt path

Therefore:
- the prompt-visible SRP context contains the answer key
- the baseline path does not
- the MMLU comparison is therefore not treatment-parity safe under the current definition

---

## 4. Evaluation Integrity Impact

Confirmed:
- baseline and SRP share the same benchmark cases
- scoring metrics were generated automatically

Not confirmed:
- the SRP prompt path is free of gold-answer leakage

Impact:
- the current MMLU full artifact is still a valid benchmark artifact
- but it is not a valid closure point for moving to ARC under the stricter treatment definition
- the prompt treatment must be corrected before ARC is executed if ARC is meant to inherit the same policy

---

## 5. Decision

Decision:
- FAIL

Remaining blocker:
- remove `expected_answer` from the prompt-visible SRP recovered context and rerun MMLU before proceeding to ARC

Recommended next action:
1. patch the MMLU adapter so the recovered context contains only non-answer runtime state
2. rerun MMLU full into a new versioned artifact
3. rerun the MMLU closure review
4. only then proceed to ARC

