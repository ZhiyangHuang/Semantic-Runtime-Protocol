# SRP Constrained Parameter Optimization Protocol

This document freezes the protocol for Phase III-A constrained parameter optimization.
It defines how optimization may occur inside validated feasible regions.
It does not define reinforcement learning, adaptive policy execution, or runtime self-modification.

---

## 1. Position

Phase III-A follows Phase II validation and operates only inside frozen feasible regions.

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

---

## 2. Objective Function

Phase III-A requires an explicit objective.

The objective must be bounded by Phase II invariants.

Example:

```text
Objective =
  w1 * semantic_quality
  + w2 * recovery_success
  - w3 * resource_cost
  - w4 * instability_penalty
```

The exact weights and metric composition are experiment-specific, but the objective must remain compatible with:

- replay equivalence
- state transition equivalence
- authority preservation
- evidence consistency

---

## 3. Candidate Representation

Candidates are explicit parameter configurations, not learned policies.

Example:

```text
{
  activation_threshold: 0.5,
  recovery_min_evidence: 2
}
```

Candidate generation is bounded by the Phase II feasible region.

---

## 4. Evaluation Metrics

Phase III-A may evaluate candidates using metrics such as:

- semantic quality
- recovery success
- evidence cost
- latency
- memory overhead

Metrics must be measurable without changing runtime authority.

---

## 5. Ranking Rule

Candidates may be ranked by objective value after invariant checks pass.

Ranking does not grant deployment authority.

Allowed output:

- ranked candidate list
- recommended configuration
- tradeoff analysis
- optimization report

---

## 6. Approval Boundary

Optimizer output is advisory.

```text
Optimizer proposes
        ↓
Governance reviews
        ↓
Runtime executes
```

The optimizer cannot directly mutate runtime configuration or bypass governance review.

---

## 7. Rollback Rule

If a candidate violates invariants or fails governance review, it must be rejected or rolled back to the last validated configuration.

Rollback must preserve:

- event-derived history
- replay consistency
- authority separation

---

## 8. Non-goals

This protocol does not include:

- reinforcement learning
- online adaptation
- runtime self-modification
- autonomous deployment
- policy learning

Those concerns belong to Phase III-B.

---

## 9. Relation to Boundary Document

This protocol depends on:

- [SRP Constrained Parameter Optimization Boundary](SRP_CONSTRAINED_PARAMETER_OPTIMIZATION_BOUNDARY.md)

The boundary document defines the scope and permissions.
This protocol defines the experimental rules inside that scope.

