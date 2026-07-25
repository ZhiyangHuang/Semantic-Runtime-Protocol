# Evidence-Authority Separation

## Research Question

RQ2: Does stronger evidence necessarily imply higher transition authority in semantic state transitions?

## Hypothesis

No. Evidence should improve validation, but it should not by itself expand authority or authorize a semantic transition.

## Core Claim

Evidence and authority are separable protocol variables:

- `Phi_E(E_t)` evaluates supporting evidence
- `Phi_A(A_t)` evaluates authority conditions

The key boundary is that evidence validation does not rewrite authority state.

## Formal Target

Experiment 2 is not a validation-accuracy experiment.
Its formal target is authority invariance under evidence variation:

```text
Phi_E(E_t) != Phi_A(A_t)
```

or, more concretely:

```text
A_(t+1) = A_t
```

when only `E_t` changes, unless an authority transition rule explicitly permits an authority update.

In short:

```text
evidence changes -> validation result may change
evidence changes -> authority must not change by itself
```

## Metric

The single core metric is Authority Drift Rate:

```text
ADR = authority changes caused only by evidence / all evidence variations
```

The target outcome is:

```text
ADR = 0
```

## Minimal Case Matrix

| Evidence | Authority | Expected |
| --- | --- | --- |
| low | deny | reject |
| high | deny | reject |
| low | allow | accept |
| high | allow | accept |

The decisive case is `high evidence + deny authority rule`.
That case should still be rejected if evidence is not allowed to substitute for authority.

## Expected Outcome

The experiment should show that:

- stronger evidence can improve validation confidence
- authority remains an independent gating condition
- evidence-rich but unauthorized transitions are still inadmissible

The intended paper-facing interpretation is:

> evidence strength does not imply permission

## Non-Goals

- This is not a benchmark for evidence quality.
- This is not a search for the best authority policy.
- This does not re-test the admissibility boundary itself; that is Experiment 1.

## Relation to Experiment 1

Experiment 1 answers whether an explicit admissibility boundary can reject invalid transitions.
This experiment answers a narrower follow-up question:

> even when evidence is strong, does authority remain separate?

Experiment 2 does not evaluate whether evidence improves validation accuracy.
It evaluates whether evidence can alter authority independently of governance rules.

Experiment 1 = existence of governance boundary.
Experiment 2 = separation of governance dimensions.

If this README survives review without overlapping Experiment 1, then the code for the experiment can be justified later.
