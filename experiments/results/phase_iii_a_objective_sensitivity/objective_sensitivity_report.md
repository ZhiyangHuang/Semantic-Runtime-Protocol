# SRP Phase III-A Objective Sensitivity Report

This report freezes the Phase III-A objective sensitivity package for SRP.
It is a sensitivity report, not a calibration artifact and not an optimization artifact.

## Purpose

The objective sensitivity study compares how different objective weights change the ranking of the same feasible-region candidates.

## Experimental Boundary

- feasible region coverage: `0.4000`
- candidate count: `25`
- feasible candidate count: `10`

## Scenario Summary

### O1_balanced

- top candidate: `{'activation_threshold': 0.9, 'recovery_min_evidence': 1, 'label': 'a0.9_r1'}`
- top objective value: `0.54`
- objective span: `0.13000000000000006`
- candidate count: `10`

### O2_quality_priority

- top candidate: `{'activation_threshold': 0.9, 'recovery_min_evidence': 1, 'label': 'a0.9_r1'}`
- top objective value: `0.68`
- objective span: `0.26500000000000007`
- candidate count: `10`

### O3_cost_priority

- top candidate: `{'activation_threshold': 0.1, 'recovery_min_evidence': 1, 'label': 'a0.1_r1'}`
- top objective value: `0.38`
- objective span: `0.425`
- candidate count: `10`

### O4_stability_priority

- top candidate: `{'activation_threshold': 0.1, 'recovery_min_evidence': 1, 'label': 'a0.1_r1'}`
- top objective value: `0.36`
- objective span: `0.09999999999999998`
- candidate count: `10`

## Stability Analysis

The study reports Top-1 match, Top-3 overlap, Top-5 overlap, Spearman rho, and Kendall tau between objective settings.
The main expectation is not invariant Top-1 results, but controlled sensitivity of rankings to the declared objective.
In the current feasible region, recovery success and instability penalty are constant across candidates, so the observed ranking shifts are primarily driven by semantic-quality and resource-cost tradeoffs.

## Figures

- rank correlation heatmap: `experiments\results\phase_iii_a_objective_sensitivity\figures\rank_correlation_heatmap.png`
- top objective bar chart: `experiments\results\phase_iii_a_objective_sensitivity\figures\top_objective_bar.png`

## Relation to the Paper

This study supports the paper's governed-optimization claim by showing that the feasible region is fixed while the ranking depends on the objective weights.
