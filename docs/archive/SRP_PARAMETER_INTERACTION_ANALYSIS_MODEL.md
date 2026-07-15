# SRP Parameter Interaction Analysis Model

This document freezes the first interaction-analysis boundary for SRP runtime parameters.
It is a research contract, not an optimization plan.

The question is:

> Do validated parameters interact in ways that change SRP boundary behavior, or do they remain isolated across runtime authorities?

---

## 1. Core Scope

Interaction analysis begins after single-parameter sensitivity has been validated.

Current validated sensitivity parameters:

- `activation_threshold`
- `recovery_min_evidence`
- `preserve_evidence`
- `archive_relations`

The first interaction batch should focus on pairwise observation only.

Not allowed in the first interaction phase:

- grid search
- Bayesian optimization
- adaptive learning
- RL-based tuning

---

## 2. Parameter Pair

A parameter pair is defined as:

```text
(Parameter A, Parameter B)
```

The first pair is:

```text
activation_threshold x recovery_min_evidence
```

This pair is chosen because it spans two distinct runtime authorities:

- `activation_threshold`
  - semantic mutation admission
- `recovery_min_evidence`
  - semantic recovery admission

---

## 3. InteractionExperiment

An interaction experiment should record:

- `parameter_a`
- `parameter_b`
- `baseline`
- `observations`
- `metrics`
- `invariants`

Suggested meaning:

- `parameter_a`
  - first parameter in the pair
- `parameter_b`
  - second parameter in the pair
- `baseline`
  - default values for both parameters
- `observations`
  - cell-level behavior notes
- `metrics`
  - observable runtime measurements
- `invariants`
  - boundary checks that must remain preserved

---

## 4. First Matrix

The first interaction matrix should be a minimal 2x2 grid:

```text
A0 R0
A0 R1
A1 R0
A1 R1
```

Where:

- `A0` = low activation threshold
- `A1` = high activation threshold
- `R0` = low recovery minimum evidence
- `R1` = high recovery minimum evidence

This is a pairwise observation matrix, not a sweep for optimization.

---

## 5. Metrics

### 5.1 Mutation-side metrics

From activation behavior:

- `successful_transitions`
- `final_activation`
- `runtime_event_count`

### 5.2 Recovery-side metrics

From recovery behavior:

- `evidence_usage_count`
- `recovery_success`
- `replay_equivalent`

### 5.3 Interaction metric

The first interaction metric is:

- `boundary_consistency_score`

Meaning:

- whether the pair preserves authority separation
- whether deterministic mutation remains stable
- whether replay remains equivalent

---

## 6. Boundary Expectations

### Semantic mutation boundary

`activation_threshold` may change which semantic mutation is admitted.

### Governance boundary

`recovery_min_evidence` may change whether recovery is admitted.

### History boundary

`preserve_evidence` is not part of this first pair, but the interaction model should remain compatible with history boundary analysis.

### Archive evidence boundary

`archive_relations` is not part of this first pair, but the interaction model should remain compatible with archive boundary analysis.

---

## 7. Expected Observation Style

The report should describe interaction effects without claiming optimality.

Example:

```text
activation_threshold increases and recovery_min_evidence increases

Observed:
- fewer transitions admitted
- recovery requires stronger evidence
- replay equivalence unchanged

Interpretation:
Parameters reinforce governance strictness.

Invariant:
History authority preserved.
```

---

## 8. Explicit Non-goals

The first interaction phase does not:

- choose a best configuration
- tune parameters automatically
- infer a learned policy
- modify runtime ownership boundaries

It only observes whether validated parameters interact and whether the frozen boundaries remain intact.

---

## 9. Next Step

After this model is frozen, the next artifact should be the first pairwise interaction experiment for `activation_threshold x recovery_min_evidence`.

