# SRP System Model V1

This document defines the system model for SRP.
It is a method artifact, not a new experiment, not a policy document, and not an optimization result.

## 1. Overview

SRP is a governed semantic evolution runtime that manages semantic state transitions through explicit observation, validation, optimization, evidence, and governance layers.

The system does not let runtime execution decide whether it should mutate itself.
Instead, semantic changes are routed through a governed sequence of observation, verification, recommendation, and approval.

## 2. Semantic Runtime Model

The core runtime flow is:

```text
Semantic State
    |
    v
Transition Request
    |
    v
Validation
    |
    v
Approved Transition
    |
    v
Runtime Execution
```

The runtime executes approved transitions.
It does not own the authority to approve its own mutation.

## 3. Authority Model

SRP separates authority across five functional layers:

| Layer | Authority |
| --- | --- |
| Runtime | execute |
| Calibration | observe |
| Validation | verify |
| Optimization | recommend |
| Evidence | inform |
| Governance | approve |

The authority structure is:

```text
Governance
    |
    v
Runtime
    ^
    |
Validation
    ^
    |
Calibration
    ^
    |
Evidence
```

The key separations are:

- `Evidence != Authority`
- `Optimization != Runtime Control`
- `Calibration != Learning`
- `Validation != Mutation`

## 4. Semantic Transition Model

SRP transitions follow this governed pipeline:

```text
Input State
    |
    v
Semantic Mutation Proposal
    |
    v
Evidence Collection
    |
    v
Boundary Validation
    |
    v
Optimization Recommendation
    |
    v
Governance Decision
    |
    v
Runtime Transition
```

The central rule is:

`proposal != execution`

This means a candidate transition may be observed, validated, ranked, and recommended, but it is not executed until governance approves it.

## 5. Phase Separation

The paper's phases map onto the system model as follows:

### Phase I

Observation:

- parameter observability
- evidence collection

### Phase II

Validation:

- feasible region discovery
- boundary stability
- closure validation

### Phase III-A

Optimization:

- candidate ranking
- objective-based recommendation
- advisory output

### Future Phase III-B

Adaptation:

- policy evolution
- governed learning
- controlled update proposals

## 6. Formalization

Let semantic state at time `t` be `S_t`.
Let `theta` denote the parameter configuration.
Let `e` denote evidence.

The transition model can be written as:

```text
S_(t+1) = T(S_t, theta, e)
```

Phase II defines a validated feasible region `F` such that:

```text
theta in F
```

Phase III-A searches within that region:

```text
theta* = argmax_{theta in F} U(theta)
```

but `theta*` is only a governed recommendation.
It does not directly alter runtime state without approval.

This means the system model is:

```text
theta* = governed recommendation
```

not:

```text
theta* = learned policy
```

## 7. Relation to Experiments

The paper's experiments instantiate the system model as follows:

| Model Component | Evidence |
| --- | --- |
| Feasible region | Phase II validation |
| Boundary stability | Closure validation |
| Candidate ranking | Phase III-A round 1 |
| Evidence escalation | Semantic backend comparison |
| Authority split | Research freeze package |

## 8. System Boundary

The SRP system boundary is:

- runtime executes transitions
- calibration observes parameter behavior
- validation verifies frozen boundaries
- optimization recommends within verified regions
- evidence informs verification
- governance decides whether a transition is approved

SRP therefore treats semantic evolution as a governed process, not as an unconstrained adaptation loop.

