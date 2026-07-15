# SRP Phase II Validation Appendix

This appendix freezes the audit evidence for the Phase II validation layer.
It complements the main report and does not repeat its narrative framing.

## 1. Purpose

The purpose of this appendix is to provide a compact, auditable record of the validation coverage used to verify frozen Phase II boundaries.

It records what was tested, under which conditions, and which invariants were checked.

It does not rank parameters, optimize values, or introduce new boundaries.

---

## 2. Validation Execution Matrix

The Phase II validation stack is organized around four validation groups.

| Validation Group | Target | Variation | Observation |
| --- | --- | --- | --- |
| Boundary Stability | `activation_threshold` | threshold range | semantic mutation boundary |
| Boundary Stability | `recovery_min_evidence` | evidence threshold range | evidence acceptance boundary |
| Cross-condition | `preserve_evidence` | history mode | history preservation boundary |
| Cross-condition | `archive_relations` | archive mode | archive enrichment boundary |

The closure validation suite evaluates these groups under controlled runtime conditions without modifying runtime authority.

---

## 3. Boundary Observation Records

### 3.1 `activation_threshold`

Boundary class: semantic mutation boundary

Round 1 boundary-stability scan:

| Scenario | Candidate Region | Observed Behavior | Constraint Status |
| --- | --- | --- | --- |
| baseline | frozen region around `0.5` | stable semantic transition | accepted |
| high_transition | frozen region around `0.5` | stable semantic transition | accepted |
| high_conflict | frozen region around `0.5` | stable semantic transition | accepted |
| high_evidence | frozen region around `0.5` | stable semantic transition | accepted |

### 3.2 `recovery_min_evidence`

Boundary class: evidence acceptance boundary

Round 1 boundary-stability scan:

| Scenario | Candidate Region | Observed Behavior | Constraint Status |
| --- | --- | --- | --- |
| baseline | frozen region around `2` | acceptable recovery boundary | accepted |
| high_transition | frozen region around `2` | acceptable recovery boundary | accepted |
| high_conflict | frozen region around `2` | acceptable recovery boundary | accepted |
| high_evidence | frozen region around `2` | acceptable recovery boundary | accepted |

### 3.3 `preserve_evidence`

Boundary class: history preservation boundary

Round 1 boundary-stability scan:

| Scenario | Candidate Region | Observed Behavior | Constraint Status |
| --- | --- | --- | --- |
| baseline | `False / True` | history preservation remained bounded | accepted |
| high_transition | `False / True` | history preservation remained bounded | accepted |
| high_conflict | `False / True` | history preservation remained bounded | accepted |
| high_evidence | `False / True` | history preservation remained bounded | accepted |

### 3.4 `archive_relations`

Boundary class: archive enrichment boundary

Round 1 boundary-stability scan:

| Scenario | Candidate Region | Observed Behavior | Constraint Status |
| --- | --- | --- | --- |
| baseline | `False / True` | archive enrichment remained isolated | accepted |
| high_transition | `False / True` | archive enrichment remained isolated | accepted |
| high_conflict | `False / True` | archive enrichment remained isolated | accepted |
| high_evidence | `False / True` | archive enrichment remained isolated | accepted |

---

## 4. Closure Validation Records

The full closure validation suite covers 32 observations across four scenarios.

| Condition | Parameter | Result | Invariant |
| --- | --- | --- | --- |
| workload variation | `activation_threshold` | stable | preserved |
| workload variation | `recovery_min_evidence` | stable | preserved |
| workload variation | `preserve_evidence` | stable | preserved |
| workload variation | `archive_relations` | stable | preserved |
| conflict density variation | `activation_threshold` | stable | preserved |
| conflict density variation | `recovery_min_evidence` | stable | preserved |
| conflict density variation | `preserve_evidence` | stable | preserved |
| conflict density variation | `archive_relations` | stable | preserved |
| evidence variation | `activation_threshold` | stable | preserved |
| evidence variation | `recovery_min_evidence` | stable | preserved |
| evidence variation | `preserve_evidence` | stable | preserved |
| evidence variation | `archive_relations` | stable | preserved |

The remaining closure observations repeat the same four-dimensional verification pattern across the controlled runtime scenarios used by the validation suite.

---

## 5. Invariant Verification Matrix

| Invariant | Validation Method | Result |
| --- | --- | --- |
| replay equivalence | replay execution comparison | pass |
| state transition equivalence | transition trace comparison | pass |
| authority preservation | ownership check | pass |
| evidence consistency | evidence audit | pass |

These checks ensure that validation observes frozen boundaries without gaining runtime authority.

---

## 6. Reproducibility Details

Minimal reproducibility metadata:

| Field | Value |
| --- | --- |
| Runtime version | Phase II frozen runtime baseline |
| Experiment version | Phase II closure validation round 1 |
| Seed policy | deterministic scenario construction |
| Execution environment | local repository runtime |

The validation suite is intended to be deterministic under the frozen conditions described in the main report.

---

## 7. Limitations

This appendix does not address:

- parameter optimization
- adaptive updates
- online learning
- runtime self-modification

It only documents the evidence used to validate frozen Phase II boundaries.
