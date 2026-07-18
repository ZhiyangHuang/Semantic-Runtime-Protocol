# Phase 6 Cluster A

This note records the first live-code consolidation batch for repository governance.
It is a migration record, not a claim, and not an experiment result.

## Scope

The cluster focused on the lowest-risk shared helper paths that still pointed at `srp_experiment/` from live entrypoints.

Files moved to or retargeted through `experiments/common/`:

- `experiments/common/export_support.py`

Files retargeted to live helpers:

- `srp_experiment/export_csv.py`
- `srp_experiment/export_markdown.py`
- `srp_experiment/verify_e5_encoder.py`
- `srp_experiment/run_local_diagnostics.py`

## Why This Cluster

The batch was chosen because it was helper-heavy and did not require changing the meaning of the core SRP protocol.
It reduced deletion blockers without touching paper-facing claims.

## Result

Dependency audit before the batch:

- `runtime_imports`: `20`
- `tooling_imports`: `28`
- `test_imports`: `87`

Dependency audit after the batch:

- `runtime_imports`: `11`
- `tooling_imports`: `27`
- `test_imports`: `87`

Overall impact:

- `P0` runtime imports decreased by `9`
- `P1` tooling imports decreased by `1`
- `P2` test imports unchanged
- total blocking hits decreased from `135` to `125`

## Verification

Passed checks:

- `python scripts/find_dependency_refs.py`
- `python scripts/verify_release.py`
- `python -m compileall scripts experiments\common srp_experiment`

## Notes

This cluster established the first reversible pattern for Phase 6:

1. extract or retarget a small helper batch
2. rerun dependency audit
3. rerun release verification
4. record the deltas before continuing

The next clusters should continue from the updated `P0` and `P1` baselines rather than from the original audit snapshot.
