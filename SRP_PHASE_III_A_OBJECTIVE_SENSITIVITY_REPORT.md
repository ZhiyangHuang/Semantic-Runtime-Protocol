# SRP Phase III-A Objective Sensitivity Report

This report freezes the Phase III-A objective sensitivity package for SRP.
It is a sensitivity report, not a calibration artifact and not an optimization artifact.

## 1. Purpose

The objective sensitivity study compares how different objective weights change the ranking of the same feasible-region candidates.

It answers:

> How sensitive is Phase III-A ranking to the declared objective?

## 2. Experimental Boundary

The runtime baseline is frozen by [SRP Experiment Environment Freeze](SRP_EXPERIMENT_ENV_FREEZE.md).

The study does not change:

- runtime execution
- authority boundaries
- the feasible region
- evidence routing rules

## 3. Sensitivity Evidence

The current package compares four objective settings over the same Phase II feasible region:

- `O1_balanced`
- `O2_quality_priority`
- `O3_cost_priority`
- `O4_stability_priority`

Reference scenario:

- `O1_balanced`

Observed ranking behavior:

- `O1_balanced` top candidate: `a0.9_r1`
- `O2_quality_priority` top candidate: `a0.9_r1`
- `O3_cost_priority` top candidate: `a0.1_r1`
- `O4_stability_priority` top candidate: `a0.1_r1`

Pairwise comparison against the balanced reference:

- quality-priority: Top-1 match `True`, Top-3 overlap `0.6667`, Spearman rho `0.6364`
- cost-priority: Top-1 match `False`, Top-3 overlap `0.3333`, Spearman rho `0.2000`
- stability-priority: Top-1 match `False`, Top-3 overlap `1.0000`, Spearman rho `0.9030`

## 4. Result Interpretation

The feasible region remains fixed while the ranking changes with objective weights.
That is the expected behavior for constrained optimization: boundary validation stays stable, but recommendation is objective-dependent.

This is objective decoupling rather than boundary drift: the feasible set does not change, but the ranking order within that fixed set does.

The result does not imply instability of the method.
It implies that the optimization objective is doing real work.

In the current feasible region, recovery success and instability penalty are constant across candidates, so the observed ranking shifts are primarily driven by semantic-quality and resource-cost tradeoffs.

## 5. Relation to the Paper

This report supports the paper's governed-optimization claim by showing that Phase III-A is sensitive to the declared objective while preserving the validated feasible region.

For the raw export package, see `experiments/results/phase_iii_a_objective_sensitivity/`.
