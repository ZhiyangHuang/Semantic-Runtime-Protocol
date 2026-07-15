# SRP Phase II Density Baseline Report

This report freezes the Phase II sampling-density baseline package for SRP.
It is a baseline report, not a calibration artifact and not an optimization artifact.

## 1. Purpose

The density baseline compares coarse, standard, and dense candidate grids for Phase II boundary validation.

It answers:

> Is the validated feasible region stable as sampling density increases?

## 2. Experimental Boundary

The runtime baseline is frozen by [SRP Experiment Environment Freeze](SRP_EXPERIMENT_ENV_FREEZE.md).

The baseline does not change:

- runtime execution
- authority boundaries
- optimization objectives
- evidence routing rules

## 3. Baseline Evidence

The current package compares three sampling densities:

- `coarse_3x3`
- `standard_5x5`
- `dense_9x9`

Observed coverage:

- coarse_3x3: `0.3333`
- standard_5x5: `0.4000`
- dense_9x9: `0.2222`

Across all three densities, the feasible-region bounds remained:

- `activation_threshold`: `0.1` to `0.9`
- `recovery_min_evidence`: `1` to `2`

The export includes:

- `density_results.csv`
- `density_results.jsonl`
- `density_summary.json`
- `metadata.json`
- `figures/density_coverage.pdf`
- `figures/density_coverage.png`

## 4. Result Interpretation

The density baseline checks whether the feasible-region result is an artifact of a single grid resolution.
It supports the boundary-validation claim by comparing coverage and feasible-region bounds under increasing sampling density.

The main observation is that the boundary extents remained stable while feasible coverage changed with grid density, which is a useful distinction for paper discussion.

The baseline is intended to complement the Phase II boundary report, not replace it.

## 5. Relation to the Paper

This report supports the paper's boundary-robustness story and provides a baseline comparison for Phase II.

For the raw export package, see `experiments/results/phase_ii_density_baseline/`.
