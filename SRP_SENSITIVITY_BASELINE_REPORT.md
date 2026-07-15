# SRP Sensitivity Baseline Report v2

This report summarizes the first validated SRP sensitivity experiments.
It is a research baseline, not an optimization report.
Version 2 upgrades the report from parameter-result listing to boundary-aware calibration.

---

## 1. Purpose

Establish initial empirical understanding of SRP runtime parameter effects before optimization.

The report records validated OFAT experiments for:

- `activation_threshold`
- `recovery_min_evidence`
- `preserve_evidence`
- `archive_relations`

---

## 2. Validated Parameter Coverage

| Parameter | Layer | Type | Experiment | Validation |
| --- | --- | --- | --- | --- |
| `activation_threshold` | semantic mutation | numeric OFAT | `activation_threshold_ofat_v1` | validated |
| `archive_relations` | archive evidence | boolean OFAT | `archive_relations_ofat_v1` | validated |
| `recovery_min_evidence` | governance | numeric OFAT | `recovery_min_evidence_ofat_v1` | validated |
| `preserve_evidence` | history / audit | boolean OFAT | `preserve_evidence_ofat_v1` | validated |

---

## 3. Observed Effects

### `activation_threshold`

Observed:

- changes activation behavior in the runtime kernel
- preserves deterministic execution
- produces visible changes in final activation under OFAT sweep

### `recovery_min_evidence`

Observed:

- changes the recovery acceptance boundary
- preserves evidence-based governance checks
- yields visible differences in recovery acceptance conditions

### `archive_relations`

Observed:

- changes evidence enrichment through the archive boundary
- improves conflict evidence coverage in the current validation setup
- preserves runtime state transition equivalence
- keeps replay independent from archive evidence exposure

### `preserve_evidence`

Observed:

- changes evidence retention behavior in forgetting
- affects evidence record count and audit completeness
- does not break replay equivalence in the current validation setup

---

## 4. Current Parameter Maturity

| Parameter | Status |
| --- | --- |
| `activation_threshold` | Validated sensitivity |
| `archive_relations` | Validated sensitivity |
| `recovery_min_evidence` | Validated sensitivity |
| `preserve_evidence` | Validated sensitivity |

These parameters are now part of the validated sensitivity catalog.

---

## 5. Explicit Non-goals

These experiments characterize parameter effects; they do not optimize runtime behavior.

Not included:

- optimal value selection
- automatic tuning
- Bayesian search
- RL policy learning
- multi-parameter interaction analysis

---

## 6. Baseline Interpretation

The current baseline indicates that SRP parameterization can be measured across four distinct runtime authorities:

- semantic mutation authority
- governance / recovery authority
- history / audit authority
- archive evidence authority

This baseline is sufficient for the next phase of controlled interaction analysis.

---

## 7. Parameter Boundary Coverage

| Boundary | Parameter | Validation |
| --- | --- | --- |
| Mutation | `activation_threshold` | Passed |
| Governance | `recovery_min_evidence` | Passed |
| History | `preserve_evidence` | Passed |
| Archive Evidence | `archive_relations` | Passed |

The purpose of this section is to show that SRP now exposes a validated parameter surface across all four runtime boundary types.
