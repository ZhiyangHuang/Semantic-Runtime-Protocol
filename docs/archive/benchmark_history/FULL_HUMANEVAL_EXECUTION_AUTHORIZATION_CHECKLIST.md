# Full HumanEval Execution Authorization Checklist

Date: 2026-07-21

This checklist freezes the release boundary for full HumanEval execution.

This is an authorization document only.

Do not:
- run HumanEval full execution
- update `paper/`
- update evidence manifests
- modify benchmark code as part of this checklist

---

## 1. Scope Gate

Verify the full run scope is fixed as follows:

- benchmark: `HumanEval`
- source: frozen dataset source
- variants: `baseline`, `srp`
- primary metric: `pass@1` only
- sampling rule: first generation only
- execution model: sandboxed subprocess execution

Prohibited behaviors:
- best-of-n evaluation
- retry sampling
- self-repair loops
- test-guided generation

Decision required:
- `PASS`
- `FAIL`

---

## 2. Prompt Boundary Gate

Baseline prompt must include only:
- problem statement
- function signature
- system instruction

SRP prompt must include:
- the same problem statement
- the same function signature
- the same system instruction
- approved recovered semantic context only

Forbidden from any prompt-visible path:
- `reference_solution`
- `canonical_solution`
- `hidden_tests`
- `private_tests`
- `expected_output`
- grader logic

Required condition:
- `leakage_count = 0`

Decision required:
- `PASS`
- `FAIL`

---

## 3. Executor Gate

Verify the full run uses:
- subprocess isolation
- timeout enforcement
- exception classification
- deterministic execution policy under fixed inputs

Required execution record fields:

```json
{
  "task_id": "...",
  "variant": "baseline|srp",
  "execution_status": "...",
  "passed": true,
  "runtime": "...",
  "failure_type": null
}
```

Decision required:
- `PASS`
- `FAIL`

---

## 4. Artifact Gate

Expected full output directory:
- `experiments/results/humaneval_full_v1/`

Required files:
- `config.json`
- `raw_predictions.jsonl`
- `execution_results.json`
- `metrics.json`
- `metadata.json`
- `report.md`

Required metadata fields:
- dataset provenance
- runtime version
- artifact hash
- execution timestamp
- seed / config

Decision required:
- `PASS`
- `FAIL`

---

## 5. Interpretation Boundary Gate

The full run must not be interpreted as:

- `SRP improves coding capability`

The full run may be interpreted as:

- `SRP context-recovery treatment evaluated under a code-generation execution benchmark`

HumanEval should be used to evaluate:
- generated program correctness
- execution robustness

It should not be used as a direct measure of SRP memory capability.

Decision required:
- `PASS`
- `FAIL`

---

## 6. Final Authorization Decision

Authorize full HumanEval execution only if all gates pass.

Authorization outcomes:

- `AUTHORIZED`
- `BLOCKED`

If `AUTHORIZED`, the next allowed action is:

1. run Full HumanEval v1
2. audit artifacts
3. audit prompt leakage
4. write closure review

If `BLOCKED`, list the exact blockers and stop before execution.

---

## 7. Evidence Boundary

Before HumanEval full closure:
- do not update evidence manifests
- do not update paper-facing benchmark tables

The release sequence remains:

1. HumanEval Full
2. Release Evidence Review
3. Evidence Manifest Update
4. Paper benchmark table freeze

