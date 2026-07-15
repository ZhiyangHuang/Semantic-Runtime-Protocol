# SRP Method Overview V1

This document defines the method-level overview for the SRP paper.
It is a method artifact, not a new experiment, not a policy document, and not an optimization result.

## 1. Method Overview

SRP follows a governed pipeline for semantic evolution:

```text
Semantic Observation
    |
    v
Boundary Validation
    |
    v
Constrained Optimization
    |
    v
Evidence Verification
    |
    v
Governance Approval
    |
    v
Runtime Execution
```

The governing principle is:

```text
observe -> verify -> recommend -> approve -> execute
```

not:

```text
observe -> learn -> mutate
```

## 2. Phase I: Parameter Observability

Phase I answers:

> Which semantic change variables can be measured?

Phase I contributes:

- observable parameters
- transition metrics
- evidence collection
- state tracking

Phase I outputs:

```text
Observed Parameter Space
```

## 3. Phase II: Boundary Validation

Phase II answers:

> Which change ranges are allowed?

Phase II contributes:

- candidate region exploration
- invariant checking
- closure validation

Phase II can be formalized as:

```text
F = { theta | invariant(theta) = true }
```

Phase II outputs:

```text
Validated Feasible Region
```

## 4. Phase III-A: Constrained Optimization

Phase III-A answers:

> Inside the safe region, which configuration best satisfies the declared objective?

Phase III-A can be formalized as:

```text
theta* = argmax_{theta in F} U(theta)
```

However:

```text
theta* != runtime mutation
```

Instead, the output is a:

```text
Recommended Configuration
```

## 5. Evidence-Controlled Verification

Evidence escalation answers:

> When existing evidence is insufficient, how should verification be strengthened?

The routing logic is:

```text
Vector Evidence
    |
    v
Confidence Check
    |
    +---- sufficient -> decision
    |
    v
Semantic Evidence
    |
    v
Governance Review
```

The key rule is:

`more evidence does not mean more authority`

## 6. End-to-End Example

An SRP transition request follows this path:

```text
Semantic Transition Proposal
    |
    v
Phase II feasibility check
    |
    v
Phase III-A ranking
    |
    v
Evidence escalation if disagreement appears
    |
    v
Governance approve / reject
    |
    v
Runtime execute
```

This sequence keeps recommendation separate from execution.

## 7. Method Boundary

Current SRP does not include:

- online learning
- policy update
- autonomous mutation
- self-governing runtime

Those concerns remain future work and belong to the reserved adaptive boundary.

## 8. Relation to Experiments

The paper's experiments instantiate the method as follows:

| Method Component | Evidence |
| --- | --- |
| Observed parameter space | Phase I calibration |
| Validated feasible region | Phase II validation and closure validation |
| Recommended configuration | Phase III-A constrained optimization |
| Evidence escalation | Semantic backend comparison and escalation analysis |
| Approval boundary | Research freeze package |

## 9. Method Summary

SRP's method is to observe, validate, optimize within verified regions, strengthen evidence when needed, and require governance approval before execution.

That is the core difference from systems that directly couple observation to mutation.

