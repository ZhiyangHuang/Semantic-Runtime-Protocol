# SRP Phase I Observability Report

This report freezes the Phase I parameter observability evidence package for SRP.
It is a data report, not a calibration artifact and not an optimization artifact.

## Summary

- observed parameter count: `4`
- repeat count: `5`
- transition count: `130`
- replay success rate: `1.0000`
- state consistency rate: `1.0000`
- mean parameter drift: `0.5538`
- median parameter drift: `0.3750`
- parameter drift std: `0.6672`
- parameter drift p25: `0.1000`
- parameter drift p75: `0.7000`
- max parameter drift: `3.0000`

## Metric Definitions

- `parameter drift` is the absolute difference from the frozen default profile; boolean values use `0/1` encoding.
- `replay success` is reported when the direct and replayed transition paths produce the same state signature.

## Observed Axes

### activation_threshold

- observation count: `85`
- replay success rate: `1.0000`
- state consistency rate: `1.0000`
- mean parameter drift: `0.3176`
- median parameter drift: `0.3000`
- parameter drift std: `0.2216`
- max parameter drift: `0.7000`

### recovery_min_evidence

- observation count: `25`
- replay success rate: `1.0000`
- state consistency rate: `1.0000`
- mean parameter drift: `1.4000`
- median parameter drift: `1.0000`
- parameter drift std: `1.0198`
- max parameter drift: `3.0000`

### preserve_evidence

- observation count: `10`
- replay success rate: `1.0000`
- state consistency rate: `1.0000`
- mean parameter drift: `0.5000`
- median parameter drift: `0.5000`
- parameter drift std: `0.5000`
- max parameter drift: `1.0000`

### archive_relations

- observation count: `10`
- replay success rate: `1.0000`
- state consistency rate: `1.0000`
- mean parameter drift: `0.5000`
- median parameter drift: `0.5000`
- parameter drift std: `0.5000`
- max parameter drift: `1.0000`

## Result Interpretation

SRP establishes an observable parameter space that can be measured before validation or optimization.
The export uses repeated observations over a dense parameter grid so the observability layer is machine-readable rather than a smoke test.

## Figures

- observation frequency: `experiments\results\phase_i\figures\observation_frequency.png`
- drift histogram: `experiments\results\phase_i\figures\parameter_drift_histogram.png`

## Record Count

- records exported: `130`
