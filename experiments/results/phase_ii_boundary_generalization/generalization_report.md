# SRP Phase II Boundary Generalization Report

This report freezes the Phase II boundary generalization package for SRP.
It is a generalization report, not a calibration artifact and not an optimization artifact.

## Summary

- scenario count: `3`
- total candidate count: `115`
- total feasible candidate count: `31`
- reference scenario: `standard_5x5`

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

## Overlap Analysis

Pairwise IoU and overlap are computed over feasible candidate sets.
The reference scenario is the standard 5x5 grid.

## Figures

- IoU heatmap: `experiments\results\phase_ii_boundary_generalization\figures\boundary_iou_heatmap.png`

## Result Interpretation

The boundary extents remained stable across grids, and the pairwise overlap quantifies how much of the feasible region is shared across sampling densities.
This is intended to support the paper's boundary-generalization claim, not to define a new optimization objective.
