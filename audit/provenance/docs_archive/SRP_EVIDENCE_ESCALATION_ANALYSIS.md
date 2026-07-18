# SRP Evidence Escalation Analysis

This document analyzes when SRP should escalate from vector evidence to stronger semantic evidence during verification.
It is an analysis artifact, not a calibration artifact, not an optimization artifact, and not an adaptive policy artifact.

## 1. Analysis Position

The semantic backend comparison report shows that vector-only verification and vector-plus-semantic-evidence verification can differ in boundary handling.

The key question is not:

> Is a local semantic backend universally better?

The key question is:

> When is vector evidence sufficient, when should SRP escalate, and when should disagreement be routed to governance?

## 2. Why Escalation Matters

SRP is not trying to maximize model strength.
It is trying to preserve governed semantic evolution.

That means evidence should be escalated only when the additional semantic signal materially improves verification without transferring authority.

The escalation question is important because SRP needs to distinguish:

- high-confidence vector regions
- boundary regions
- evidence-conflict regions

Those are different governance situations and should not all trigger the same verification path.

## 3. Observed Comparison Signal

The current comparison report shows:

- vector accuracy: `0.5`
- variant accuracy: `0.6667`
- agreement rate: `0.8333`
- repeat stability: `1.0`

This means the augmented evidence path improved correctness in the tested case set, but it also introduced one disagreement case that required escalation handling.

The important interpretation is not that the variant is always stronger.
It is that additional evidence can improve verification behavior in some cases, especially where the vector signal is not decisive.

## 4. Escalation Regions

### 4.1 High-confidence vector region

When vector similarity is clearly above or below the threshold, vector evidence is often sufficient.

Typical action:

- accept or reject directly
- no escalation required

This region matters because it shows SRP does not need a heavy semantic backend for every case.

### 4.2 Boundary region

When vector confidence is near the threshold, the vector signal is less decisive.

Typical action:

- consult stronger semantic evidence
- keep governance in the loop for ambiguous outcomes

This is the most valuable region for escalation because it is exactly where additional semantic evidence can improve boundary handling.

### 4.3 Evidence-conflict region

When vector evidence and semantic evidence disagree, SRP should not let either source silently override the other.

Typical action:

- route to governance review
- preserve the disagreement as evidence
- avoid hidden authority transfer

This preserves the SRP boundary principle:

- evidence may inform
- evidence may not decide by itself

## 5. Escalation Matrix

| Region | Vector Confidence | Stronger Evidence Need | Action |
| --- | --- | --- | --- |
| High-confidence vector region | High | Unnecessary | Vector-only decision |
| Boundary region | Medium | Helpful | Escalate to semantic evidence |
| Evidence-conflict region | Conflicting | Required | Governance review |

This matrix is the core of the escalation policy.
It keeps the system from overusing expensive evidence sources while still allowing stronger semantic evidence where it matters.

## 6. Authority Interpretation

The local semantic evidence backend is not a controller.
It is a stronger evidence source.

That means:

- it may provide semantic support
- it may flag uncertainty
- it may surface disagreement

It may not:

- mutate runtime state
- approve deployment
- rewrite history
- bypass governance

This is consistent with the SRP authority split:

- `Runtime` executes
- `Evidence` informs verification
- `Governance` decides

## 7. What the Current Comparison Does and Does Not Show

The current comparison does show:

- additional semantic evidence can improve verification in the tested setting
- disagreement cases should be treated as escalation events, not failures
- the comparison can remain stable under repeated runs

The current comparison does not show:

- universal superiority of local semantic evidence
- that every case should escalate
- that stronger evidence should replace vector evidence everywhere
- that the local model should acquire authority

## 8. Research Meaning

This analysis turns the backend comparison into a policy question:

> Under what conditions should SRP move from vector evidence to stronger semantic evidence?

That is a more SRP-native question than simple backend ranking.
It preserves the research hierarchy:

- Phase II identifies safe regions
- Phase III-A ranks configurations inside safe regions
- Semantic backend comparison evaluates evidence sources
- Escalation analysis determines when additional evidence should be consulted

## 9. Limitations

This analysis is based on a small fixed case set.
It does not yet include a full escalation policy across all runtime conditions.
It also does not yet distinguish between heuristic fallback and live local-model inference in a separate evidence package.

## 10. Next Step

The next useful step is to formalize an escalation policy for three categories:

- vector-only decision
- vector-plus-semantic-evidence decision
- governance review on disagreement

That policy can later be tested against the semantic backend comparison stack without changing runtime authority.

For the auditable records, see [SRP Evidence Escalation Appendix](SRP_EVIDENCE_ESCALATION_APPENDIX.md).
