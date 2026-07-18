# SRP Calibration Phase II Rollup Model

This document freezes the rollup model for Phase II calibration evidence.
It is a research aggregation definition, not an implementation plan.

Phase II already produces round-level calibration evidence for individual parameters.
The rollup layer defines how those round outputs are interpreted together without collapsing them into a single optimization target.

---

## 1. Purpose

The purpose of the rollup model is to create a unified view of constrained calibration evidence across parameter rounds.

It answers:

> What acceptable regions and boundary guarantees have been validated so far?

It does not answer:

> What is the best parameter configuration?

That question remains outside Phase II.

---

## 2. Rollup Object

The Phase II rollup object is:

```text
CalibrationRoundSummary
```

Suggested fields:

- `parameter`
- `tested_region`
- `accepted_region`
- `rejected_region`
- `constraint_status`
- `invariant_status`
- `evidence_type`

Suggested interpretation:

- `parameter`
  - the parameter being calibrated
- `tested_region`
  - the region or candidate set that was explored
- `accepted_region`
  - the subset that satisfied frozen SRP constraints
- `rejected_region`
  - the subset that failed or degraded under the same constraints
- `constraint_status`
  - concise summary of boundary checks
- `invariant_status`
  - replay, state transition, and authority isolation status
- `evidence_type`
  - the boundary class being characterized

---

## 3. Rollup Role

The rollup model does not merge parameter semantics.
It groups boundary evidence into a higher-level map:

```text
parameter
    |
    v
boundary evidence
    |
    v
acceptable region map
```

This keeps each parameter boundary distinct while still allowing Phase II to produce a unified calibration picture.

---

## 4. Boundary Classes

The first Phase II rollup should cover these boundary classes:

- semantic mutation boundary
  - `activation_threshold`
- evidence acceptance boundary
  - `recovery_min_evidence`
- history preservation boundary
  - `preserve_evidence`
- archive enrichment boundary
  - `archive_relations`

Each round contributes a distinct boundary evidence record to the same rollup layer.

---

## 5. Rollup Output

The Phase II rollup output should be a map of validated acceptable regions by boundary class.

Example shape:

```text
Phase II Calibration Evidence Map

Semantic Mutation Boundary
Evidence Governance Boundary
History Preservation Boundary
Archive Enrichment Boundary
```

The rollup output is a characterization map, not a chosen configuration.

---

## 6. Non-goals

The rollup model does not include:

- parameter ranking
- best-candidate selection
- utility scoring
- Bayesian optimization
- reinforcement learning
- adaptive updates

The rollup layer is an evidence synthesis layer only.

---

## 7. Phase II Role

Phase II should now be understood as:

```text
Round Evidence
    ->
Rollup Evidence
    ->
Constrained Calibration Closure
```

This structure preserves the distinction between:

- single-round evidence
- phase-level evidence synthesis
- future adaptive evolution

---

## 8. Summary

Phase II now has three distinct layers:

- round-level calibration evidence
- rollup-level evidence synthesis
- frozen constrained calibration boundary

This model prepares Phase II to complete as a coherent evidence map before any future adaptive phase is considered.

