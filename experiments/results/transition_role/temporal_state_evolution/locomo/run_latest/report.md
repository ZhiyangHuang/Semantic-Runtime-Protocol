# SRP Transition Role Role-Coverage Report

This report instantiates the `temporal_state_evolution` transition role with the LoCoMo workload.
It is a role-coverage artifact, not a leaderboard claim.

## 1. Frozen Contract

- Transition role: `temporal_state_evolution`
- Workload: `LoCoMo`
- Runtime contract: `srp-real-validation-v1`

## 2. Official Workload Summary

- case_count: `3`
- answer_accuracy: `1.0`
- official_metric_score: `1.0`

## 3. SRP Diagnostics

- semantic_coverage: `1.0`
- semantic_drift: `0.0`
- fact_accuracy: `1.0`
- relation_accuracy: `1.0`
- recovery_accuracy: `1.0`
- closure_accuracy: `1.0`
- recommendation_execution_separated: `True`
- replay_consistency: `1.0`

## 4. Governance Comparison

- accepted_delta: `1`
- rejected_delta: `-1`
- invalid_accept_rate_delta: `1.0`
- recommendation_execution_gap: `-1`

## 5. Interpretation

- LoCoMo is used as a semantic workload implementing the `temporal_state_evolution` role.
- The official workload summary remains dataset-owned.
- SRP diagnostics characterize governance behavior separately from workload scoring.
- This slice establishes role coverage for one workload under the frozen v1.2 protocol boundary.
