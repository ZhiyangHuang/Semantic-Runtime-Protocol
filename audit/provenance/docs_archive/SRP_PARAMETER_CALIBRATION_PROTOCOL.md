# SRP Parameter Calibration Protocol

This document defines the constrained calibration procedure for SRP Phase II.
It is a protocol for evaluating parameter regions, not an optimization algorithm.

Phase I established observable parameter behavior.
Phase II may now calibrate parameters under explicit SRP constraints.

---

## 1. Purpose

The purpose of calibration is to identify acceptable parameter regions while preserving SRP invariants.

Calibration asks:

> Which parameter values or parameter regions preserve deterministic semantic evolution, evidence-based governance, replay safety, and authority separation?

This protocol does not search for a global optimum.

---

## 2. Scope

Phase II calibration applies to validated parameters that already exist in the registry and catalog.

Current calibrated parameter families:

- numeric runtime parameters
  - `activation_threshold`
  - `recovery_min_evidence`
- boolean policy parameters
  - `preserve_evidence`
  - `archive_relations`

Calibration is performed externally to runtime governance.

---

## 3. Allowed Activities

Calibration may:

- generate candidate parameter values or bounded parameter regions
- apply candidate values through `RuntimeConfig`
- execute runtime scenarios
- collect metrics
- compare observed behavior against frozen invariants
- record acceptable regions and warnings

Calibration may not:

- modify runtime authority
- rewrite runtime state directly
- introduce hidden policy ownership
- learn or deploy adaptive parameter policies

---

## 4. Calibration Inputs

The minimal calibration input is:

```text
Parameter Configuration
    |
    v
Runtime Evaluation Scenario
    |
    v
Observed Metrics
```

Calibration inputs should include:

- `parameter`
- `candidate_values`
- `baseline_configuration`
- `scenario`
- `metrics`
- `invariants`

---

## 5. Candidate Generation

Candidate generation is bounded and explicit.

Examples:

- numeric sweep
  - `0.1`, `0.2`, `0.3`, ...
- bounded region probe
  - `[0.3, 0.7]`
- boolean comparison
  - `False`, `True`

Candidate generation does not imply optimization.

---

## 6. Evaluation Procedure

Each candidate is evaluated against a fixed runtime scenario.

### 6.1 Execution

Measure:

- successful transitions
- activation behavior

### 6.2 Recovery

Measure:

- evidence usage
- recovery behavior

### 6.3 Governance

Measure:

- audit completeness
- evidence enrichment

### 6.4 Invariants

Preserve:

- replay equivalence
- state transition equivalence
- authority isolation

---

## 7. Acceptance Criteria

A candidate value or bounded region is acceptable if it preserves SRP invariants under the chosen scenario.

Acceptance is based on boundary preservation, not optimization.

Example acceptance language:

- `pass`
- `warning`
- `fail`

Example region language:

- `acceptable region`
- `degraded region`
- `rejected region`

---

## 8. Calibration Output

Calibration should produce a record containing:

- `parameter`
- `candidate_values`
- `observed_metrics`
- `invariant_status`
- `acceptable_region`
- `notes`

The output is a calibration report, not a model policy.

---

## 9. Frozen Non-goals

This protocol explicitly excludes:

- optimization
- Bayesian optimization
- reinforcement learning
- adaptive parameter updates
- runtime self-modification
- automatic policy deployment

---

## 10. Authority Separation

Calibration remains external to runtime governance.

```text
Runtime executes.
Calibration observes.
Learning proposes.
Governance decides.
```

Calibration does not own:

- Execution Authority
- History Authority
- Governance Authority

---

## 11. Initial Phase II Use

The first Phase II use case may be called:

- `Constrained Parameter Calibration Round 1`

The expected output is a parameter region map, not an optimal parameter set.

---

## 12. Summary

Phase I answered:

> Do parameters have observable and bounded behavior?

Phase II now asks:

> Which parameter regions remain acceptable while SRP invariants are preserved?

This protocol keeps calibration bounded, observable, and external to runtime governance.

