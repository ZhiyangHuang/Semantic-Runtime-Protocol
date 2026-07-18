# SRP Constrained Parameter Optimization Round 1 Protocol

This document freezes the execution protocol for Phase III-A Round 1.
It defines the first constrained optimization experiment over validated feasible regions.
It does not define reinforcement learning, online adaptation, or runtime self-modification.

---

## 1. Purpose

Phase III-A Round 1 evaluates parameter configurations inside the validated feasible region and identifies recommendations that improve a declared objective while preserving SRP invariants.

It answers:

> Which configuration performs best under the fixed objective inside the frozen feasible region?

It does not answer:

> How should the system learn to change parameters online?

---

## 2. Round 1 Candidate Space

Round 1 uses the following candidate axes:

- `activation_threshold`
- `recovery_min_evidence`

Candidate values:

- `activation_threshold`: `0.3, 0.4, 0.5, 0.6, 0.7, 0.8`
- `recovery_min_evidence`: `1, 2, 3`

This yields a bounded 6 x 3 candidate matrix.

---

## 3. Objective Model

Round 1 uses an explicit objective.

Example:

```text
Objective =
  0.4 * semantic_quality
  + 0.3 * recovery_success
  - 0.2 * resource_cost
  - 0.1 * instability_penalty
```

The exact values are experiment inputs, not hidden runtime constants.

The objective must remain compatible with Phase II invariants:

- replay equivalence
- state transition equivalence
- authority preservation
- evidence consistency

---

## 4. Evaluation Metrics

Round 1 may evaluate:

- semantic quality
- recovery success
- resource cost
- latency
- memory overhead
- instability penalty

Metrics must be collected without changing runtime authority.

---

## 5. Ranking Rule

Candidates may be ranked by objective value after invariant checks pass.

Allowed output:

- ranked candidate list
- recommended configuration
- tradeoff analysis
- optimization report

Ranking does not grant deployment authority.

---

## 6. Approval Boundary

Round 1 output is advisory.

```text
Optimizer proposes
        ↓
Governance reviews
        ↓
Runtime executes
```

The optimizer cannot mutate runtime configuration directly.

---

## 7. Rollback Rule

If a candidate fails invariant checks or governance review, it must be rejected or rolled back to the last validated configuration.

Rollback preserves:

- event-derived history
- replay consistency
- authority separation

---

## 8. Non-goals

Round 1 does not include:

- reinforcement learning
- online adaptation
- runtime self-modification
- autonomous deployment
- policy learning

Those concerns belong to Phase III-B.

