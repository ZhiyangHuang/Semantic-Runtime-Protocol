# Phase 6 Cluster D

This batch removes the last export-wrapper runtime dependency arrows from `srp_experiment/` by narrowing the wrappers to pure record-formatting entrypoints.

## Scope

The cluster focused on the two legacy export wrappers that still imported the legacy SRP pipeline at runtime.

### Files Updated

- `srp_experiment/export_csv.py`
- `srp_experiment/export_markdown.py`

## What Changed

The wrappers are now pure exporters:

- they read SRP records from `--input-json`
- they write CSV or markdown artifacts
- they no longer execute tasks internally

The shared export helpers remain in `experiments/common/export_support.py`.

## Dependency Impact

This batch removed the final export-wrapper runtime imports.

Before:

- `runtime_imports`: `4`
- `blocking hits`: `118`

After:

- `runtime_imports`: `2`
- `blocking hits`: `116`

Migration velocity after this batch:

- `runtime_imports`: `18 / 20` completed
- `tooling_imports`: `1 / 28` completed
- `test_imports`: `0 / 87` completed

## Verification

The following checks passed after the migration:

- `python scripts/find_dependency_refs.py`
- `python scripts/verify_release.py`
- `python -m compileall scripts experiments\common srp_experiment`

## Remaining Runtime Blockers

The remaining `P0` runtime imports are now concentrated in mechanism ablation:

- `srp_experiment/mechanism_ablation/ablation_runner.py`
- `srp_experiment/mechanism_ablation/variants/common.py`

Those two files are the next cluster candidates.

