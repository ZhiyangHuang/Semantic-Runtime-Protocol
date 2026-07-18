# Phase 6 Cluster G2

## Summary

This batch completed the tooling-side consolidation needed to eliminate the remaining `P1` blockers.

## What Changed

- Added a live compatibility namespace at `experiments/srp_runtime_legacy/` by copying the legacy harness and pipeline surface into a live package.
- Redirected the top-level `srp_experiment/*.py` tooling entrypoints to the live compatibility namespace instead of the legacy package.
- Patched the copied state-allocation factory to use the live `experiments.mechanism_ablation` variants.

## Effect on Dependency Audit

- `tooling_imports`: `18 -> 0`
- `runtime_imports`: `0` unchanged
- `test_imports`: `87` unchanged
- `blocking_hits`: `105 -> 87`

## Validation

- `python -m compileall experiments\\srp_runtime_legacy srp_experiment` passed
- `python scripts\\verify_release.py` passed
- `python scripts\\find_dependency_refs.py` passed

## Interpretation

Phase 6.2 is now complete at the tooling layer.
The remaining deletion blocker class is `P2` test imports.
