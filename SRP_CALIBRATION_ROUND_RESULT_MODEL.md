# SRP Calibration Round Result Model

This document freezes the result model for Phase II calibration rounds.
It is a research definition, not an optimization artifact.

The purpose of this model is to unify how calibration evidence is recorded across parameter rounds such as:

- `activation_threshold`
- `recovery_min_evidence`
- `preserve_evidence`
- `archive_relations`

---

## 1. Core Question

Calibration round results answer:

> Which parameter regions satisfy frozen SRP constraints under a specific runtime evaluation scenario?

They do not answer:

> Which parameter is globally best?

That question belongs to a later optimization boundary, not this model.

---

## 2. Result Shape

A calibration round result should contain:

- `parameter`
- `tested_region`
- `accepted_region`
- `rejected_region`
- `constraint_summary`
- `invariant_status`
- `runtime_version`
- `notes`

Suggested interpretation:

- `tested_region`
  - the region or candidate set that was evaluated
- `accepted_region`
  - the subset judged acceptable under SRP constraints
- `rejected_region`
  - the subset judged unacceptable or degraded
- `constraint_summary`
  - concise pass / warning / fail summary for each checked boundary
- `invariant_status`
  - replay, state transition, and authority isolation status
- `runtime_version`
  - the runtime version or boundary snapshot used during evaluation
- `notes`
  - short observations for later report synthesis

---

## 3. Result Semantics

Calibration round results are evidence records, not rankings.

They must preserve the separation between:

- sensitivity evidence
  - "what changed when the parameter changed?"
- calibration evidence
  - "which parameter region remains acceptable?"

They must not introduce:

- `best_candidate`
- `rank`
- `score`
- `objective_value`

Those fields would drift toward optimization authority.

---

## 4. Minimum Invariants

Each calibration round result should record the status of the following invariants:

- `replay_equivalent`
- `state_transition_equivalent`
- `authority_isolation`

If additional scenario-specific constraints are used, they may be included in `constraint_summary`, but the minimum invariant set should remain visible.

---

## 5. Candidate-to-Result Mapping

The basic mapping is:

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
CalibrationRoundResult
```

This mapping keeps calibration external to governance and keeps runtime authority unchanged.

---

## 6. Phase II Usage

Phase II round artifacts should be recorded by parameter and by round:

- Round 1A
  - `activation_threshold`
- Round 1B
  - `recovery_min_evidence`
- Round 1C
  - `preserve_evidence`
- Round 1D
  - `archive_relations`

All of these should serialize to the same round result model.

---

## 7. Explicit Non-goals

This result model does not support:

- optimization rankings
- Bayesian search outputs
- reinforcement learning policy traces
- adaptive update proposals
- runtime self-modification records

It is a calibration evidence model only.

---

## 8. Summary

Phase I established parameter observability.
Phase II establishes constrained calibration evidence.

This model freezes the result layer so calibration rounds can be recorded uniformly without introducing optimization bias.

