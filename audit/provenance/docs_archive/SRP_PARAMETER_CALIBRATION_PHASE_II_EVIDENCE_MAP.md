# SRP Parameter Calibration Phase II Evidence Map

This document consolidates Phase II calibration evidence into a single map.
It is a research evidence summary, not an optimization report.

Phase II does not search for the best parameter values.
It establishes:

```text
parameter
    |
    v
boundary evidence
    |
    v
acceptable region
```

---

## 1. Purpose

The purpose of this evidence map is to summarize acceptable parameter regions while preserving frozen SRP authority boundaries.

It answers:

> Which parameter regions remain acceptable under SRP constraints, and which authority boundaries remain intact?

It does not answer:

> Which parameter is globally best?

That question remains outside Phase II.

---

## 2. Boundary Evidence Map

Phase II currently validates four boundary classes.

| Boundary Class | Parameter | Type | Tested Region | Accepted Region | Evidence |
| --- | --- | --- | --- | --- | --- |
| Semantic Mutation Boundary | `activation_threshold` | continuous | `[0.3, 0.8]` | `[0.3, 0.8]` | state transition constraints |
| Evidence Acceptance Boundary | `recovery_min_evidence` | continuous | `[1, 5]` | `[1, 3]` | evidence threshold constraints |
| History Preservation Boundary | `preserve_evidence` | boolean | `False / True` | `False / True` | audit and replay constraints |
| Archive Enrichment Boundary | `archive_relations` | boolean | `False / True` | `False / True` | evidence enrichment constraints |

These regions are evidence maps, not optimization outputs.

---

## 3. Authority Preservation Matrix

Phase II validates that parameter changes do not gain authority over runtime ownership boundaries.

| Parameter | Execution Authority | History Authority | Governance Authority |
| --- | --- | --- | --- |
| `activation_threshold` | preserved | preserved | preserved |
| `recovery_min_evidence` | preserved | preserved | preserved |
| `preserve_evidence` | preserved | preserved | preserved |
| `archive_relations` | preserved | preserved | preserved |

This matrix is the core SRP calibration claim:

> parameter variation may change boundary behavior, but it does not transfer authority.

---

## 4. Frozen Non-goals

Phase II evidence mapping does not include:

- best parameter selection
- ranking
- utility scoring
- optimization
- Bayesian search
- reinforcement learning
- adaptive updates

The map is evidence-only.

---

## 5. Current Phase II State

```text
Phase II Calibration

Status:
Evidence Map Established

Completed:
- 4 boundary classes
- 4 calibrated axes
- acceptable region evidence

Not started:
- optimization
- adaptive calibration
- learning policy
```

---

## 6. Consolidated Interpretation

Phase II now shows that SRP exposes a calibrated parameter surface with preserved authority boundaries.

The evidence map distinguishes four classes of boundary evidence:

- semantic mutation
- evidence acceptance
- history preservation
- archive enrichment

The map is sufficient for future adaptive research, but it does not itself introduce adaptive behavior.

---

## 7. Phase Boundary Summary

```text
Parameter Space Model
    |
    v
Parameter Registry
    |
    v
Sensitivity Phase I
    |
    v
Calibration Protocol
    |
    v
Round 1A-1D Evidence
    |
    v
Phase II Evidence Map
    |
    v
Future Adaptive Evolution
```

---

## 8. Summary

Phase II is now frozen as an evidence map, not an optimizer.

It establishes:

- boundary evidence
- acceptable regions
- authority preservation

It does not establish:

- global best parameters
- adaptive policies
- runtime self-modification

