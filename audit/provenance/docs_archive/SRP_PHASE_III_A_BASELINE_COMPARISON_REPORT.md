# SRP Phase III-A Baseline Comparison Report

This report freezes the Phase III-A baseline comparison package for SRP.
It is a baseline report, not a calibration artifact and not an optimization artifact.

## 1. Purpose

The baseline comparison contrasts SRP constrained optimization with a naive full-grid sweep baseline.

It answers:

> Does SRP preserve the top-ranked candidate while reducing the search space?

## 2. Experimental Boundary

The runtime baseline is frozen by [SRP Experiment Environment Freeze](SRP_EXPERIMENT_ENV_FREEZE.md).

The comparison does not change:

- runtime execution
- authority boundaries
- optimization objectives
- evidence routing rules

## 3. Baseline Evidence

The current package compares:

- naive full-grid sweep over 25 Phase II candidates
- SRP constrained optimization over 10 feasible candidates

Observed comparison:

- baseline candidate count: `25`
- SRP candidate count: `10`
- search reduction: `0.6000`
- top match: `True`
- baseline top objective value: `0.54`
- SRP top objective value: `0.54`
- feasible region coverage: `0.4000`

## 4. Result Interpretation

The comparison indicates that the constrained optimization path preserves the top-ranked candidate from the full grid while evaluating fewer candidates.

This supports the claim that SRP reduces search work without changing the recommended configuration in the evaluated benchmark.

## 5. Relation to the Paper

This report supports the paper's governed-optimization claim and provides the paper-facing baseline comparison for Phase III-A.

For the raw export package, see `experiments/results/phase_iii_a_baseline_comparison/`.
