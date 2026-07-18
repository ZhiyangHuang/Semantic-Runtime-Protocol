# Phase 6 Cluster C

This batch continues repository consolidation by removing a small set of live runtime dependencies on `srp_experiment/` while keeping the migration reversible and easy to audit.

## Scope

The cluster focused on the remaining `P0` runtime import layer around mechanism ablation support.

### Files Updated

- `experiments/common/state_allocation.py`
- `srp_experiment/mechanism_ablation/variants/common.py`
- `srp_experiment/mechanism_ablation/ablation_runner.py`

## What Changed

The cluster moved shared allocation types and the mechanism-ablation export helper to the live utility layer:

- `AllocationMetrics`, `StateAllocationResult`, and `StateAllocationPolicy` are now provided from `experiments/common/state_allocation.py`
- `mechanism_ablation/variants/common.py` now imports the live-side allocation types from `experiments/common/state_allocation.py`
- `mechanism_ablation/ablation_runner.py` now imports record writers from `experiments/common/export_support.py`

The migration did not touch tests and did not change the experimental protocol itself.

## Dependency Impact

This batch reduced the blocking runtime dependency count.

Before:

- `runtime_imports`: `8`
- `blocking hits`: `122`

After:

- `runtime_imports`: `4`
- `blocking hits`: `118`

Migration velocity after this batch:

- `runtime_imports`: `16 / 20` completed
- `tooling_imports`: `1 / 28` completed
- `test_imports`: `0 / 87` completed

## Verification

The following checks passed after the migration:

- `python scripts/find_dependency_refs.py`
- `python scripts/verify_release.py`
- `python -m compileall scripts experiments\common srp_experiment`

## Remaining Runtime Blockers

The remaining `P0` runtime imports are concentrated in:

- `srp_experiment/export_csv.py`
- `srp_experiment/export_markdown.py`
- `srp_experiment/mechanism_ablation/ablation_runner.py`
- `srp_experiment/mechanism_ablation/variants/common.py`

Those are the next small cluster candidates.
