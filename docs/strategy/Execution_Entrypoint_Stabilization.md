# Execution Entrypoint Stabilization

This note freezes the entrypoint hierarchy for the current semester so the experiment system does not keep expanding sideways.

## Goal

The repository should feel like one experiment framework with a few stable doors, not a pile of overlapping scripts.

## Primary Entrypoints

The current canonical entrypoints are:

1. `srp_experiment/longbench_launcher.py`
2. `srp_experiment/run_qualified_experiment.py`
3. `srp_experiment/batch_run.py`
4. `srp_experiment/collect_batch_summary.py`
5. `srp_experiment/repeat_aggregate.py`
6. `srp_experiment/long_horizon_report.py`

These files define the semester-stable execution path.

## Wrapper Layer

The following scripts are wrappers and should remain thin:

- `srp_experiment/run-longbench-batch-with-popup.ps1`
- `srp_experiment/run-longbench-smoke.ps1`
- `srp_experiment/first-paper-run.ps1`
- `srp_experiment/comparison-run.ps1`

They are useful for convenience, but they should not become the place where core experiment semantics live.

## Design Rule

When a workflow feels duplicated, prefer:

1. keeping the Python engine
2. demoting the shell wrapper to convenience status
3. documenting the relationship instead of inventing another entrypoint

## Current Stable Picture

- `longbench_launcher.py` is the human-facing launcher for LongBench staged runs
- `run_qualified_experiment.py` is the formal gated single-run entry
- `batch_run.py` is the canonical repeated-run engine
- `collect_batch_summary.py`, `repeat_aggregate.py`, and `long_horizon_report.py` are the canonical reduction/reporting layer

This is enough for the semester paper. More entrypoints should be treated as scope growth unless they remove confusion from these existing layers.
