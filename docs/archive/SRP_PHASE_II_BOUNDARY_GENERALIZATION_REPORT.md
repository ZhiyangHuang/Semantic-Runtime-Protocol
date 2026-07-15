# SRP Phase II Boundary Generalization Report

This report freezes the Phase II boundary generalization package for SRP.
It is a generalization report, not a calibration artifact and not an optimization artifact.

## 1. Purpose

The boundary generalization study compares feasible-region overlap across multiple Phase II sampling grids.

It answers:

> Do the validated feasible boundaries remain stable across different sampling densities?

## 2. Experimental Boundary

The runtime baseline is frozen by [SRP Experiment Environment Freeze](SRP_EXPERIMENT_ENV_FREEZE.md).

The study does not change:

- runtime execution
- authority boundaries
- optimization objectives
- evidence routing rules

## 3. Generalization Evidence

The current package compares:

- `coarse_3x3`
- `standard_5x5`
- `dense_9x9`

Reference scenario:

- `standard_5x5`

Observed reference comparison:

- `coarse_3x3` IoU vs reference: `0.3000`
- `standard_5x5` IoU vs reference: `1.0000`
- `dense_9x9` IoU vs reference: `0.5556`

Across all three grids, the feasible-region bounds remained:

- `activation_threshold`: `0.1` to `0.9`
- `recovery_min_evidence`: `1` to `2`

## 4. Result Interpretation

The generalization result suggests that the boundary extents are stable, while the observed overlap varies with sampling density.
This is useful because it distinguishes boundary stability from sampling coverage.

## 5. Relation to the Paper

This report supports the paper's boundary-generalization claim and provides a paper-facing overlap analysis for Phase II.

For the raw export package, see `experiments/results/phase_ii_boundary_generalization/`.
