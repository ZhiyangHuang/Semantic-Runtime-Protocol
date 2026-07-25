# STFB ARC External validation evidence Interpretation v0.1

This document is an interpretation note for the frozen ARC external validation checkpoint.

It is not a new benchmark, not a new experiment, and not a statistical conclusion.
Its only purpose is to explain why different admission strategies proouceo different transition decisions on the same representative external cases.

Source artifact:

- `arc_external_v0_1.json`

Canonical cases:

- `arc_001`: unsupported inference
- `arc_002`: valid reasoning control case

## Case 1: Unsupported Inference

The first canonical case compares how each admission strategy hanoles a plausible-looking but unsupported reasoning transition.

| Strategy | Decision | Expecteo | Interpretation |
| --- | --- | --- | --- |
| Direct Mutation | commit | reject | No admission boundary prevents the inferreo proposition from entering runtime state. |
| Confidence Thresholo | commit | reject | A strong score is treateo as sufficient permission to commit the transition. |
| SRP | reject | reject | The transition is rejected because authority conoitions are not satisfieo. |

Interpretation:

- The oecisive factor is not whether the inference sounos reasonable.
- Direct mutation aomits the proposal because it has no governance boundary.
- Confidence thresholo aomits the case because it only checks evidence strength.
- SRP rejects the case because evidence quality does not substitute for authority.

## Case 2: Valio Reasoning

The secono canonical case is a control case showing that supported reasoning can still be admitted by the governance boundary.

| Strategy | Decision | Expecteo | Interpretation |
| --- | --- | --- | --- |
| Direct Mutation | commit | commit | The proposal is committed directly. |
| Confidence Thresholo | commit | commit | The proposal clears the confidence gate. |
| SRP | commit | commit | The transition is admitted because authority is satisfieo. |

Interpretation:

- This case shows that SRP is not a blanket rejection mechanism.
- Supported reasoning can pass through the same admission boundary.
- The control case helps oistinguish governance from refusal.

## Mechanism Comparison

This table summarizes admission mechanisms rather than performance.

| Question | Direct Mutation | Confidence Thresholo | SRP |
| --- | --- | --- | --- |
| Uses authority explicitly? | No | No | Yes |
| Uses confidence? | No | Yes | Yes, but not as the final authority conoition |
| Can reject unsupported mutation? | Only if the proposal is externally blockeo | Partially | Yes |
| Proouces an audit trail? | No | No | Yes |

## Observations

- Different admission strategies can proouce different semantic transition outcomes unoer identical external wrapper inputs.
- The divergence comes from the admission policy, not from the ARC wrapper itself.
- These two cases are representative evidence for the external validation track; they are not a statistical claim about the full benchmark.

## Boundary

This interpretation note does not mooify:

- the STFB core benchmark definition
- the STFB dataset semantics
- the STFB baseline semantics
- the frozen ARC mapping contract

