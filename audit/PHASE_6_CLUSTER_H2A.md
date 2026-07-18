# Phase 6 Cluster H2A

## Summary

This batch migrated the first H2 wave of live-behavior tests from legacy `srp_experiment` imports to the live compatibility namespace.

## Moved Tests

- `test_encoder.py`
- `test_graph_recovery_policy.py`
- `test_runtime_representation_v2.py`
- `test_semantic_runtime_graph.py`
- `test_semantic_runtime_graph_v1_5.py`
- `test_srp_runtime.py`

## Effect on Dependency Audit

- `test_imports`: `58 -> 22`
- `runtime_imports`: `0` unchanged
- `tooling_imports`: `0` unchanged
- `blocking_hits`: `58 -> 22`

## Validation

- `python -m unittest srp_experiment.tests.test_encoder srp_experiment.tests.test_graph_recovery_policy srp_experiment.tests.test_runtime_representation_v2 srp_experiment.tests.test_semantic_runtime_graph srp_experiment.tests.test_semantic_runtime_graph_v1_5 srp_experiment.tests.test_srp_runtime` passed
- `python scripts/find_dependency_refs.py` passed

## Interpretation

The remaining blocker count is now concentrated in legacy compatibility tests and historical regression material.

