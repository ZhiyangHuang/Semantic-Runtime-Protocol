# MMLU Report

## Release Artifact

- canonical artifact: `experiments/results/mmlu_full_v3/`
- status: closed
- metric authority: `accuracy`

## Summary

The v3 artifact is the authoritative MMLU release evidence.

Key properties:
- prompt leakage was removed before release closure
- the invalid v2 artifact is retained as historical evidence only
- baseline and SRP variants remain paired under the shared benchmark contract

## Related Audits

- `FULL_MMLU_ARTIFACT_AUDIT.md`
- `MMLU_PROMPT_LEAKAGE_AUDIT_V2.md`
- `FULL_MMLU_EXECUTION_CLOSURE_REVIEW_V3.md`
