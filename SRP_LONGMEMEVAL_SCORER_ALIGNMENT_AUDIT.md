# SRP LongMemEval Scorer Alignment Audit

This document freezes the scorer-alignment audit boundary for the LongMemEval evidence run.
It is an audit artifact, not a promotion decision, not a new benchmark run, and not a theory revision.

## 1. Audit Goal

Determine whether the SRP wrapper and the benchmark scorer are aligned well enough for the current LongMemEval evidence slice to be interpreted without conflating memory recovery with scorer behavior.

## 2. Audit Table

| Audit Item | Official Scorer | SRP Wrapper | Result | Notes |
| --- | --- | --- | --- | --- |
| Exact match | Yes | Yes | Pass | Normalized exact comparison is consistent for direct-answer cases. |
| Boolean QA | Yes | Yes | Pass | Yes/no cases match the frozen answer-normalization policy. |
| Preference revision | Yes | Yes | Pass | The current slice resolves the updated preference correctly. |
| Contradiction resolution | Yes | Yes | Pass | Temporal negation is interpreted consistently in the wrapper. |
| Normalization | Yes | Yes | Pass | Lowercasing, whitespace trimming, and punctuation handling are frozen. |
| Temporal reasoning | Yes | Verified | Pass | Representative before/after/update/replacement cases match the official scorer semantics. |
| Multi-hop reasoning | Yes | Verified | Pass | Representative hop-chain coverage matches the official scorer semantics without changing candidate/fact separation. |
| Unsupported outputs | Yes | Yes | Pass | Empty or malformed outputs are handled as wrapper-level failures, not scorer successes. |

## 2.1 Acceptance Table

This table freezes the remaining scorer-alignment closure targets.

| Item | Current | Required for Pass | Required Evidence |
| --- | --- | --- | --- |
| Exact match | Pass | Keep | Frozen exact-match parity remains unchanged. |
| Boolean QA | Pass | Keep | Frozen yes/no normalization remains unchanged. |
| Preference revision | Pass | Keep | Updated-preference cases remain consistent. |
| Contradiction resolution | Pass | Keep | Temporal negation remains consistent. |
| Normalization | Pass | Keep | Lowercasing, whitespace, and punctuation handling remain frozen. |
| Temporal reasoning | Pass | Keep | Representative before/after/update/replacement cases match the official scorer semantics. |
| Multi-hop reasoning | Pass | Keep | Representative hop-chain cases match the official scorer semantics without changing candidate/fact separation. |
| Unsupported output handling | Pass | Keep | Empty or malformed outputs remain wrapper-level failures. |

## 2.2 Mismatch Resolution Rule

If a mismatch is observed during scorer-alignment closure, the resolution order is:

1. scorer wrapper interpretation
2. evaluation protocol or normalization policy
3. benchmark adapter
4. SRP algorithm revision only if the previous layers are already correct and the mismatch persists as a true method limitation

This rule keeps v1 evidence acceptance separate from future SRP algorithm improvement.

## 3. Overall Assessment

Overall scorer alignment status: `pass`

This means:

- the wrapper is consistent with the frozen answer-normalization policy
- the current LongMemEval slice is audit-ready
- the remaining acceptance-table items are closed on the frozen LongMemEval slice

## 4. Promotion Rule

Promotion to paper-facing external-validity evidence requires:

- runtime reproducibility pass
- prompt equivalence pass
- scorer alignment acceptable
- metric correctness pass
- failure decomposition interpretable
- artifact bundle reproducible

If any gate remains unresolved, promotion remains pending.

## 5. Status Semantics

| Status | Meaning |
| --- | --- |
| Pass | The scorer gate is satisfied for the current slice and can support paper-facing evidence. |
| Conditional pass | The scorer gate is satisfied for the current slice, but a documented limitation remains outside the current acceptance scope. |
| Pending | The scorer gate is unresolved and requires more audit coverage. |
| Fail | The scorer gate is not satisfied and must be fixed before promotion. |
