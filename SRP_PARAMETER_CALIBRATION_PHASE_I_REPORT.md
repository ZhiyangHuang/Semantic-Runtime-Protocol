# SRP Parameter Calibration Phase I Report

This report freezes Phase I of SRP parameter calibration.
It summarizes the validated sensitivity studies and the first pairwise interaction observation.
It is a research closure document, not an optimization plan.

---

## 1. Objective

Establish whether SRP runtime parameters have observable, isolated, and verifiable behavior boundaries before any optimization work begins.

Phase I answers:

> Can SRP expose a calibrated parameter surface without violating runtime authority separation?

---

## 2. Parameter Coverage

Phase I validates four single-parameter sensitivity axes:

- `activation_threshold`
  - semantic mutation boundary
- `recovery_min_evidence`
  - governance / recovery boundary
- `preserve_evidence`
  - history / audit boundary
- `archive_relations`
  - archive evidence boundary

Phase I also validates one pairwise interaction observation:

- `activation_threshold x recovery_min_evidence`
  - mutation and recovery boundary interaction

---

## 3. Observed Effects

### `activation_threshold`

Observed:

- changes activation admission behavior
- preserves deterministic execution
- produces visible changes in final activation

### `recovery_min_evidence`

Observed:

- changes recovery acceptance boundary
- preserves evidence-based governance checks
- yields visible differences in recovery acceptance conditions

### `preserve_evidence`

Observed:

- changes evidence retention behavior in forgetting
- affects evidence record count and audit completeness
- preserves replay equivalence in the current validation setup

### `archive_relations`

Observed:

- changes evidence enrichment through the archive boundary
- improves conflict evidence coverage in the current validation setup
- preserves runtime state transition equivalence
- preserves replay independence from archive evidence exposure

### `activation_threshold x recovery_min_evidence`

Observed:

- activation and recovery controls remain separately observable
- recovery strictness changes with `recovery_min_evidence`
- mutation boundary remains isolated from recovery boundary
- replay equivalence remains preserved

---

## 4. Boundary Guarantees

Phase I provides evidence for the following guarantees:

- runtime state mutation does not leak across parameter ownership boundaries
- evidence boundaries remain observable without replacing runtime authority
- replay invariants remain intact under validated parameter changes
- archive evidence exposure does not become a state reconstruction authority

Boundary coverage matrix:

| Boundary | Parameter | Status |
| --- | --- | --- |
| Mutation | `activation_threshold` | Observed |
| Governance | `recovery_min_evidence` | Observed |
| History | `preserve_evidence` | Observed |
| Archive Evidence | `archive_relations` | Observed |

---

## 5. Current Parameter Calibration Status

| Parameter | Calibration Status | Optimization |
| --- | --- | --- |
| `activation_threshold` | Observed | Not started |
| `recovery_min_evidence` | Observed | Not started |
| `preserve_evidence` | Observed | Not started |
| `archive_relations` | Observed | Not started |

This status is intentionally conservative.
Phase I establishes observability, not optimality.

---

## 6. Known Limitations

Phase I does not include:

- global optimization
- Bayesian tuning
- adaptive policy learning
- higher-order interaction analysis
- parameter coupling inference beyond the first pairwise study

The current evidence is sufficient to characterize single-parameter behavior and one boundary interaction case study.

---

## 7. Future Calibration Direction

Phase II should begin only after Phase I is frozen.
Phase II may include:

- interaction case studies beyond the first pair
- controlled pairwise calibration across additional boundaries
- multi-objective scoring
- grid search for experimental comparison

Phase III, if justified, may introduce optimization.

---

## 8. Phase Freeze Statement

Phase I is frozen as:

- `Sensitivity Infrastructure`: frozen
- `Validated Parameter Catalog`: frozen
- `Interaction Observation Layer`: frozen

The next phase should not be described as optimization until a separate calibration phase explicitly begins.

