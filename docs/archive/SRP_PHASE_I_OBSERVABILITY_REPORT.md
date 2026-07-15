# SRP Phase I Observability Report

This report freezes the Phase I parameter observability evidence package for SRP.
It is a data report, not a calibration artifact and not an optimization artifact.

## 1. Purpose

Phase I observability verifies that semantic evolution variables can be measured before validation or optimization.

It answers:

> Which semantic change variables can be observed as runtime evidence?

## 2. Experimental Boundary

The runtime baseline is frozen by [SRP Experiment Environment Freeze](SRP_EXPERIMENT_ENV_FREEZE.md).

Phase I does not change:

- runtime execution
- authority boundaries
- validation logic
- optimization logic

## 3. Observability Evidence

The Phase I observability package records:

- `130` transition observations
- `5` repeated observation passes
- `4` observed parameter axes
- replay consistency for all recorded observations
- state consistency for all recorded observations
- `metadata.json` for provenance and reproducibility
- `figures/observation_frequency.pdf` and `figures/observation_frequency.png` for parameter coverage
- `figures/parameter_drift_histogram.pdf` and `figures/parameter_drift_histogram.png` for drift distribution

Summary statistics:

- mean parameter drift: `0.5538`
- median parameter drift: `0.3750`
- parameter drift std: `0.6672`
- parameter drift p25: `0.1000`
- parameter drift p75: `0.7000`
- max parameter drift: `3.0000`

Metric definitions:

- `parameter drift` is the absolute difference from the frozen default profile; boolean values use `0/1` encoding.
- `replay success` is reported when the direct and replayed transition paths produce the same state signature.

Observed axes:

- `activation_threshold`
- `recovery_min_evidence`
- `preserve_evidence`
- `archive_relations`

## 4. Result Interpretation

Phase I establishes an observable parameter space that can be measured before boundary validation or constrained optimization.
The current package uses repeated observations over a dense parameter grid so the layer is machine-readable rather than a smoke test.

This is not an optimization result.
It is the measurement layer that makes later phases interpretable.

## 5. Relation to the Paper

This report supports the paper's observability claim and provides the machine-readable data layer for Phase I.

For the raw export package, see `experiments/results/phase_i/`.
For paper figures, see `experiments/results/phase_i/figures/`.
