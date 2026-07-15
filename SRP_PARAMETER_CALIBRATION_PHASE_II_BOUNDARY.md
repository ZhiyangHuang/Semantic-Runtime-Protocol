# SRP Parameter Calibration Phase II: Constrained Calibration Boundary

This document defines the boundary for Phase II of SRP parameter calibration.
It is a research boundary preview, not an implementation plan.

Phase I established that SRP parameters have observable behavior boundaries.
Phase II asks a narrower question:

> How can SRP evaluate parameter configurations while preserving deterministic semantic evolution and governance boundaries?

---

## 1. Position

Phase II sits between Phase I observability and future adaptive evolution.

```text
Phase I
    Parameter Observability
        |
        v
Phase II
    Constrained Parameter Calibration
        |
        v
Future
    Adaptive Parameter Evolution
```

Phase II is not an optimization engine.
It is a constrained calibration boundary.

---

## 2. Motivation

Phase I answered whether parameter changes are observable and whether SRP boundaries remain intact.

Phase II asks whether SRP can evaluate parameter regions under constraints without converting calibration into runtime governance.

The key concern is not "what is best?"
The key concern is:

> Which parameter regions remain acceptable under SRP invariants?

---

## 3. Starting Point

Phase II begins from the frozen Phase I assets:

- `Parameter Registry`
- `Validated Sensitivity Catalog`
- `Interaction Observation Layer`
- `Phase I Calibration Closure`

The Phase II input shape is:

```text
Parameter Configuration
    |
    v
Runtime Evaluation
    |
    v
Observed Behavior
```

---

## 4. Calibration Boundary

Phase II only allows constrained parameter exploration and evaluation.

### 4.1 Parameter Space Exploration

Allowed activities:

- candidate configuration generation
- bounded search region definition
- metric comparison

### 4.2 Evaluation

Allowed evaluation families:

Execution:

- successful transitions
- activation behavior

Recovery:

- evidence usage
- recovery behavior

Governance:

- audit completeness
- evidence enrichment

Invariants:

- replay equivalent
- state transition equivalence
- authority isolation

---

## 5. Calibration Objective

Phase II does not define a global optimum.

It defines the following objective:

> Identify acceptable parameter regions under SRP constraints.

This choice is intentional.
Phase I establishes observability.
Phase II establishes constrained acceptance.
Optimization may come later, but it is not part of this boundary.

---

## 6. Frozen Non-goals

Phase II explicitly excludes:

- automatic optimization
- Bayesian optimization
- reinforcement learning
- adaptive parameter updates
- runtime self-modification

Calibration remains external to runtime governance.

---

## 7. Research Questions

### RQ1

> Which parameter regions preserve SRP invariants?

### RQ2

> Which parameter combinations improve behavior without violating authority boundaries?

### RQ3

> Can calibration remain external to runtime governance?

This third question is central to SRP design.

```text
Runtime executes.
Calibration observes.
Learning proposes.
Governance decides.
```

---

## 8. Architecture Boundary

Phase II should be modeled as an observing and evaluating layer, not a mutating authority.

```text
Parameter Registry
    |
    v
Calibration Layer
    |
    v
Candidate Configuration
    |
    v
Evaluation Runtime
    |
    v
Evidence Report

(no direct mutation)
```

Calibration does not own:

- Execution Authority
- History Authority
- Governance Authority

---

## 9. Future Transition

Phase II may later provide evidence for adaptive semantic evolution.
However, adaptive policy remains outside the current boundary.

---

## 10. Summary

Phase I answered:

> Do parameters have observable and bounded behavior?

Phase II asks:

> Which parameter regions remain acceptable while SRP invariants are preserved?

This keeps calibration separate from runtime governance and preserves the learning boundary.

