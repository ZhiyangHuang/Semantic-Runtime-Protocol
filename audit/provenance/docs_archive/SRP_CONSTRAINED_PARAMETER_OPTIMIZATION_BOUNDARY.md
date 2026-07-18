# SRP Constrained Parameter Optimization Boundary

This document freezes the boundary for Phase III-A of SRP research.
It defines constrained optimization over validated feasible regions.
It does not define adaptive learning or runtime self-modification.

---

## 1. Position

Phase III-A begins after Phase II validation has established frozen feasible regions.

```text
Phase I
  Parameter Observability
        ↓
Phase II
  Validated Feasible Region
  Boundary Stability
        ↓
Phase III-A
  Constrained Parameter Optimization
        ↓
Phase III-B
  Adaptive Semantic Evolution
```

Phase III-A is a constrained optimization phase, not a reinforcement learning phase.

---

## 2. Purpose

The purpose of Phase III-A is to search within already validated feasible regions and identify recommended configurations that improve a defined objective while preserving SRP invariants.

It answers:

> Which parameter combinations perform better inside the frozen feasible region?

It does not answer:

> How should the system learn to change parameters online?

---

## 3. Optimization Scope

Allowed:

- search inside Phase II feasible regions
- compare candidate configurations
- produce ranked recommendations
- generate an optimization report

Disallowed:

- runtime self-modification
- autonomous deployment
- authority bypass
- adaptive policy execution

---

## 4. Objective Model

Phase III-A introduces an explicit objective function.

Example:

```text
Objective =
  w1 * semantic_quality
  + w2 * recovery_success
  - w3 * resource_cost
  - w4 * instability_penalty
```

The exact objective may vary by experiment, but it must remain bounded by Phase II invariants.

---

## 5. Candidate Evaluation

Phase III-A evaluates candidate configurations using controlled comparison.

Candidate flow:

```text
Validated Feasible Region
        ↓
Candidate Generation
        ↓
Runtime Evaluation
        ↓
Objective Scoring
        ↓
Candidate Ranking
        ↓
Governance Review
```

Candidate evaluation must preserve:

- replay equivalence
- state transition equivalence
- authority preservation
- evidence consistency

---

## 6. Authority Flow

Phase III-A preserves the SRP authority split.

```text
Optimizer proposes
        ↓
Governance reviews
        ↓
Runtime executes
```

Optimization does not own runtime mutation authority.
Optimization does not auto-deploy runtime changes.
Governance remains the approval boundary.

---

## 7. Output Contract

Phase III-A may produce:

- `recommended_configuration`
- `optimization_report`
- `tradeoff_analysis`
- `candidate_ranking`

Phase III-A does not produce autonomous runtime updates.

---

## 8. Optimization Boundary Constraints

Phase III-A must inherit the following constraints from Phase II:

- `Calibration != Runtime Controller`
- `Learning != Mutation Authority`
- `Evidence != Historical Authority`
- `Archive != State Authority`

It must also preserve:

- deterministic mutation
- evidence-based governance
- event-derived history
- bounded learning authority

---

## 9. Non-goals

Phase III-A does not include:

- reinforcement learning
- online adaptation
- runtime self-modification
- autonomous parameter mutation
- policy learning

Those concerns belong to Phase III-B.

---

## 10. Phase III-B Boundary Preview

Phase III-B is reserved for adaptive semantic evolution.

It may later define:

- proposal authority
- evidence requirement
- approval mechanism
- rollback semantics
- learning containment
- governance override

Phase III-B is not activated by this document.

