# HumanEval Report

## Release Artifact

- canonical artifact: `experiments/results/humaneval_full_v1/`
- status: closed
- metric authority: `pass@1`

## Summary

The HumanEval release artifact is closed and audited.

Key properties:
- executor isolation uses a sandboxed subprocess policy
- prompt leakage guards are enabled for solution and hidden-test fields
- baseline and SRP are paired under the shared benchmark contract
- execution integrity is preserved through execution-result tracking

## Related Audits

- `FULL_HUMANEVAL_EXECUTION_RECORD_V1.md`
- `HUMANEVAL_FULL_ARTIFACT_AUDIT_V1.md`
- `HUMANEVAL_FULL_PROMPT_LEAKAGE_AUDIT_V1.md`
- `FULL_HUMANEVAL_EXECUTION_CLOSURE_REVIEW_V1.md`
