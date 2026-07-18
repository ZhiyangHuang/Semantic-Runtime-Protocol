# Phase 6 Cluster B

This note records the second live-code consolidation batch for repository governance.
It is a migration record, not a claim, and not an experiment result.

## Scope

The cluster focused on pure boundary-calculation helpers that could be extracted without moving any runtime execution logic.

Files moved to live helper utilities:

- `experiments/common/boundary_utils.py`

Files retargeted to live helpers:

- `srp_experiment/mechanism_ablation/ablation_metrics.py`

## Why This Cluster

The batch was chosen because the moved code was helper-only and did not depend on the SRP execution pipeline directly.
That made it a low-risk way to continue reducing deletion blockers while keeping the experimental semantics unchanged.

## Result

Dependency audit before the batch:

- `runtime_imports`: `11`
- `tooling_imports`: `27`
- `test_imports`: `87`

Dependency audit after the batch:

- `runtime_imports`: `10`
- `tooling_imports`: `27`
- `test_imports`: `87`

Overall impact:

- `P0` runtime imports decreased by `1`
- `P1` tooling imports unchanged
- `P2` test imports unchanged
- total blocking hits decreased from `125` to `124`

## Verification

Passed checks:

- `python scripts/find_dependency_refs.py`
- `python scripts/verify_release.py`
- `python -m compileall scripts experiments\common srp_experiment`

## Notes

This cluster confirmed a second migration pattern:

1. extract pure analysis helper logic into `experiments/common/`
2. retarget the legacy caller
3. rerun dependency audit and release verification
4. keep the scientific behavior unchanged

The next cluster should continue with the remaining `P0` files, now starting from a runtime-import baseline of `10`.
