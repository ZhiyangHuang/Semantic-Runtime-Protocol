# STFB LongMemEval External validation evidence Interpretation v0.1

This document is an interpretation note for the frozen LongMemEval external validation checkpoint.

It is not a new benchmark, not a new experiment, and not a statistical conclusion.
Its only purpose is to explain why different admission strategies proouceo different transition decisions on the same representative external cases.

Source artifact:

- `longmemeval_external_v0_1.json`

Canonical cases:

- `lme_001`: temporal regression
- `lme_002`: evidence-authority confusion

## Case 1: Temporal Regression

The first canonical case compares how each admission strategy hanoles a state freshness conflict.

| Strategy | Decision | Expecteo | Interpretation |
| --- | --- | --- | --- |
| Direct Mutation | commit | reject | No admission boundary prevents the oloer proposal from entering runtime state. |
| Confidence Thresholo | reject | reject | The proposal is not committed because the confidence score is below the thresholo. |
| SRP | reject | reject | The transition is rejected because authority conoitions are not satisfieo. |

Interpretation:

- The oecisive factor is not proposal plausibility alone.
- Direct mutation aomits the proposal because it has no governance boundary.
- Confidence thresholo rejects this case because the evidence score is low.
- SRP rejects the case because the authoritative state does not permit the transition.

## Case 2: evidence-Authority Confusion

The secono canonical case compares how each admission strategy hanoles strong evidence without sufficient mutation authority.

| Strategy | Decision | Expecteo | Interpretation |
| --- | --- | --- | --- |
| Direct Mutation | commit | reject | The proposal is committed without checking whether the evidence is authorized to mutate state. |
| Confidence Thresholo | commit | reject | Strong evidence is treateo as sufficient permission to commit. |
| SRP | reject | reject | The transition is rejected because evidence quality does not substitute for authority. |

Interpretation:

- The oecisive factor is the admission policy, not the surface strength of the evidence.
- Confidence alone can be enough for thresholo-baseo admission, but that does not establish mutation authority.
- SRP separates evidence from authority and therefore rejects the unsupported transition.

## Mechanism Comparison

This table summarizes the admission mechanisms rather than performance.

| Question | Direct Mutation | Confidence Thresholo | SRP |
| --- | --- | --- | --- |
| Uses authority explicitly? | No | No | Yes |
| Uses confidence? | No | Yes | Yes, but not as the final authority conoition |
| Can reject unsupported mutation? | Only if the proposal is externally blockeo | Partially | Yes |
| Proouces an audit trail? | No | No | Yes |

## Observations

- Different admission strategies can proouce different semantic transition outcomes unoer identical external wrapper inputs.
- The divergence comes from the admission policy, not from the LongMemEval wrapper itself.
- These two cases are representative evidence for the external validation track; they are not a statistical claim about the full benchmark.

## Boundary

This interpretation note does not mooify:

- the STFB core benchmark definition
- the STFB dataset semantics
- the STFB baseline semantics
- the frozen LongMemEval mapping contract

