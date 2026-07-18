# Phase 6 Cluster H1

## Summary

This batch migrated a first wave of live-behavior tests from `srp_experiment` imports to live namespaces.

## Moved Tests

- `test_decision_attribution.py`
- `test_coverage_attribution.py`
- `test_importance_attribution.py`
- `test_policy_attribution.py`
- `test_policy_pareto.py`
- `test_graph_information_gap_analysis.py`
- `test_semantic_extraction_audit.py`
- `test_semantic_failure_taxonomy.py`
- `test_mechanism_attribution_ablation.py`
- `test_controlled_harness.py`
- `test_fixed_harness_bundle.py`
- `test_graph_representation_ablation_harness.py`
- `test_graph_recovery_harness.py`
- `test_object_aware_compression_harness.py`
- `test_object_aware_threshold_harness.py`
- `test_object_aware_threshold_sampling.py`
- `test_policy_boundary_analysis.py`
- `test_policy_boundary_drift.py`
- `test_policy_boundary_robustness.py`
- `test_policy_intervention_harness.py`
- `test_policy_sensitivity.py`
- `test_reconstruction_policy_harness.py`
- `test_recovery_ablation_harness.py`

## Effect on Dependency Audit

- `test_imports`: `87 -> 58`
- `runtime_imports`: `0` unchanged
- `tooling_imports`: `0` unchanged
- `blocking_hits`: `87 -> 58`

## Validation

- `python scripts/find_dependency_refs.py` passed
- `python scripts/verify_release.py` passed

## Interpretation

The remaining test blockers are now concentrated in the legacy compatibility and runtime regression suites.
