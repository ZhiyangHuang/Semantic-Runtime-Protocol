# SRP Parameter Calibration Round 1 Boundary

This document freezes the boundary for Phase II calibration round 1.
It is a research boundary definition, not an implementation plan.

Round 1 upgrades Phase I sensitivity evidence into constrained calibration evidence.

---

## 1. Objective

Round 1 asks:

> Which parameter regions satisfy frozen SRP invariants under constrained evaluation?

The goal is not to find a global optimum.
The goal is to identify acceptable parameter regions.

---

## 2. Scope

Round 1 uses the four validated parameter axes from Phase I:

| Parameter | Calibration Type |
| --- | --- |
| `activation_threshold` | numeric region |
| `recovery_min_evidence` | numeric region |
| `preserve_evidence` | boolean boundary |
| `archive_relations` | boolean boundary |

Round 1 is organized as:

- Round 1A
  - `activation_threshold`
- Round 1B
  - `recovery_min_evidence`
- Round 1C
  - `preserve_evidence`
- Round 1D
  - `archive_relations`

The first two rounds are region-oriented numeric calibration.
The last two rounds are boundary-oriented boolean calibration.

---

## 3. Candidate Region

Calibration operates on candidate regions, not on a single best value.

Example for `activation_threshold`:

```text
candidate space: [0.1, 1.0]
tested region: [0.4, 0.8]
acceptable region: [0.5, 0.7]
rejected region: [0.8, 1.0]
```

Candidate regions may be expressed as:

- numeric bounds
- discrete probe sets
- boolean comparisons

---

## 4. Calibration Experiment Shape

The first calibration shape is:

```text
CalibrationCandidate
    |
    v
RuntimeConfig
    |
    v
RuntimeKernel
    |
    v
Evaluation
    |
    v
Constraint Check
    |
    v
CalibrationResult
```

The output is a calibration result record, not an optimization result.

Suggested calibration result fields:

- `parameter`
- `tested_region`
- `acceptable_region`
- `rejected_region`
- `constraints_passed`
- `notes`

---

## 5. Calibration Registry

Round 1 requires a calibration registry distinct from the experiment index.

ExperimentIndex answers:

> What did we measure?

CalibrationIndex answers:

> Which parameter regions were accepted under frozen SRP invariants?

The registry boundary is:

```text
Parameter
    |
    +-- sensitivity records
    |
    +-- calibration records
```

This document freezes the calibration side of that split.

---

## 6. Frozen Boundaries

### Runtime boundary

Calibration may inject configuration values.
Calibration may not rewrite runtime state directly.

### Governance boundary

Calibration may provide evidence.
Calibration may not automatically approve parameters.

### Learning boundary

Calibration may search regions.
Calibration may not perform adaptive updates.

---

## 7. Acceptance Criteria

A region is acceptable if it preserves the frozen SRP invariants under the chosen scenario.

Core invariant checks:

- replay equivalent
- state transition equivalent
- authority isolation

Round-specific evaluation may also use:

- successful transitions
- activation behavior
- evidence usage
- recovery behavior
- audit completeness
- evidence enrichment

---

## 8. Non-goals

Round 1 does not include:

- optimization
- Bayesian optimization
- reinforcement learning
- adaptive parameter updates
- runtime self-modification
- automatic parameter approval

Round 1 is constrained calibration evidence, not a learned policy system.

---

## 9. Next Step

After this boundary is frozen, the next artifact should be the `experiments/calibration/` layer for Round 1 implementation.

