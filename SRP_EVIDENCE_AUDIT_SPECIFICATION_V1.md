# SRP Evidence Audit Specification V1

This document freezes the audit contract for SRP external-validation evidence.
It is an audit specification, not an experiment result, not a runtime policy, and not a theory revision.

Frozen audit version: `v1.0`

## 1. Purpose

The evidence audit exists to decide when a calibration-aware or evidence-run artifact is trustworthy enough to be promoted into paper-facing external validity.

The audit separates five questions:

- Was the runtime contract shared and frozen?
- Was the benchmark adapter correct?
- Were the diagnostic metrics computed according to frozen definitions?
- Were the reported costs and scorer outputs interpretable?
- Are the statistics and artifact bundle reproducible?

## 2. Runtime Reproducibility Gate

The following fields must be frozen and recorded in `runtime_manifest.json` for evidence runs:

- provider
- backend
- endpoint
- model
- tokenizer
- prompt template id
- temperature
- max_output_tokens
- same_endpoint_across_baselines
- baseline_generation_backend
- srp_generation_backend
- benchmark name
- baseline set
- seed set
- sample limit

The manifest is part of the evidence bundle and is required for promotion.

## 3. Scorer Correctness Gate

The official benchmark scorer must be checked against the wrapper used by SRP.

The audit should confirm:

- the wrapper does not change the benchmark's official definition
- the wrapper does not silently substitute a different tokenization or normalization policy
- the wrapper does not silently substitute a different prompt family
- prompt equivalence is preserved across baselines and SRP
- manual sanity cases and official scoring outputs do not contradict each other in systematic ways

If a scorer mismatch is observed during evidence auditing, the resolution order is:

1. scorer wrapper interpretation
2. evaluation protocol or normalization policy
3. benchmark adapter
4. SRP algorithm revision only if the previous layers are already correct and the mismatch remains a genuine method limitation

## 4. Metric Correctness Gate

### 4.1 Semantic coverage

Coverage measures how much of the target semantic state is recovered.

### 4.2 Relation accuracy

Relation accuracy measures the fraction of target relations that are recovered.

### 4.3 Hallucinated relation rate

Hallucinated relation rate measures the fraction of recovered relations that are not present in the target state.

Relation accuracy and hallucinated relation rate are not redundant:

- relation accuracy is recall-like
- hallucinated relation rate is precision-like

They can co-exist without contradiction.

The audit interprets extra recovered relations as semantic candidates rather than verified facts.

In provenance-aware SRP variants, recovered relations may also carry source and verification metadata, such as:

- observed vs. inferred relation type
- confidence score
- supporting evidence identifiers
- user-verification status
- promotion_state (`candidate`, `verified`, `rejected`)

That design allows the protocol to retain recall-oriented candidates while deferring aggressive pruning until verification is available.

The audit treats these states as follows:

- `candidate`: available for retrieval and explanation, but not for unconditional downstream fact commitment
- `verified`: allowed for persistent semantic state and downstream reasoning
- `rejected`: excluded from future recovery and should not be committed

### 4.4 Evidence cost

Evidence cost is an internal recovery-cost unit.
It is not raw token count and it is not a benchmark leaderboard metric.

Canonical interpretation:

```text
C = alpha * N_units + beta * N_relations + gamma * N_operations
```

The exact coefficients may differ across baseline families, but the unit remains an internal recovery-cost unit.

### 4.5 Statistical reporting

Statistical reporting is required for every evidence slice.

The audit must distinguish:

- descriptive statistics, which summarize the fixed evaluation slice
- inferential statistics, which attempt to generalize beyond the fixed evaluation slice

For a predefined validation slice such as the current LongMemEval evidence run:

- mean, standard deviation, and 95% CI may be reported descriptively
- the reported CI must be described as slice-level, not benchmark-wide, inference
- the sample-size limitation must be stated explicitly

### 4.6 Statistical inference

Inferential statistics are optional and should only be used when:

- the benchmark protocol is fully aligned with the official protocol
- the scorer alignment gate is acceptable
- the sample size is large enough to justify generalization
- the comparison set is fixed before the test is run

Examples of inferential statistics include:

- bootstrap confidence intervals over a larger official benchmark slice
- paired significance tests, where paired observations are available
- effect-size reporting, where the slice size supports interpretation

The audit should verify for descriptive reporting:

- mean values are computed over the stated run collection
- standard deviation or confidence intervals are computed from the same run collection
- sample size limitations are explicitly stated

## 5. Promotion Gates

An evidence candidate may be promoted only when the following are true:

- runtime reproducibility is pass
- prompt equivalence is pass
- scorer correctness is acceptable or conditional-pass with documented limitations
- metric correctness is pass
- failure decomposition is interpretable
- artifact bundle is reproducible
- the evidence slice is clearly scoped as a predefined validation slice or benchmark subset

Promotion remains pending when any gate is unresolved.

### 5.1 Status semantics

| Status | Meaning |
| --- | --- |
| Pass | The gate is satisfied and can support paper-facing evidence. |
| Conditional pass | The gate is satisfied for the current slice, but a documented limitation remains. |
| Pending | The gate is unresolved and cannot support promotion yet. |
| Fail | The gate is not satisfied and must be fixed before promotion. |

## 6. Relation to LongMemEval

LongMemEval is the first evidence-run candidate subject to this audit specification.
Its current state is audit-ready but not yet promotion-ready until scorer alignment and the evidence gate are closed.
