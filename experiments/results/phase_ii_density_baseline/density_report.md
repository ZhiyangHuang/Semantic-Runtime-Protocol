# SRP Phase II Sampling Density Baseline

This report freezes the Phase II sampling-density baseline package for SRP.
It is a baseline report, not a calibration artifact and not an optimization artifact.

## Summary

- scenario count: `3`
- total candidate count: `115`
- total feasible candidate count: `31`

### coarse_3x3

- candidate count: `9`
- feasible candidate count: `3`
- coverage: `0.3333`
- activation_threshold range: `0.1` to `0.9`
- recovery_min_evidence range: `1` to `1`
- mean boundary consistency score: `1.0000`

### standard_5x5

- candidate count: `25`
- feasible candidate count: `10`
- coverage: `0.4000`
- activation_threshold range: `0.1` to `0.9`
- recovery_min_evidence range: `1` to `2`
- mean boundary consistency score: `1.0000`

### dense_9x9

- candidate count: `81`
- feasible candidate count: `18`
- coverage: `0.2222`
- activation_threshold range: `0.1` to `0.9`
- recovery_min_evidence range: `1` to `2`
- mean boundary consistency score: `1.0000`

## Interpretation

The sampling-density baseline compares coarse, standard, and dense candidate grids.
It is intended to show whether the validated feasible region remains stable as sampling density increases.

## Figures

- coverage comparison: `experiments\results\phase_ii_density_baseline\figures\density_coverage.png`

## Relation to the Paper

This baseline supports the paper's boundary-validation claim by checking that the feasible region is not an artifact of a single grid resolution.
