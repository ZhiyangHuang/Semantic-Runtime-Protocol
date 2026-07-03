# Entrypoint Execution Map

This file freezes the practical execution map for the current semester experiment system.

## Only Use These Primary Entrypoints

1. `longbench_launcher.py`
2. `run_qualified_experiment.py`
3. `batch_run.py`
4. `collect_batch_summary.py`
5. `repeat_aggregate.py`
6. `long_horizon_report.py`

These are the only files that should define the main user-facing execution path.

## Execution Roles

### 1. Interactive LongBench Entry

- `longbench_launcher.py`

Use this when:

- selecting one method at a time
- selecting one 100-task group at a time
- selecting smoke vs formal run profiles
- editing `.env` values such as timeout and context budget

The launcher generates a session config and then delegates execution to:

- `run-longbench-batch-with-popup.ps1`
- `batch_run.py`

### 2. Formal Qualified Single-Run Entry

- `run_qualified_experiment.py`

Use this when:

- you want a qualification-gated formal run
- you are not using the LongBench launcher workflow

This path delegates to:

- `experiment_qualification.py`
- `run_experiment.py`

### 3. Canonical Batch Engine

- `batch_run.py`

This is the canonical batch execution engine.
It should remain the lowest common execution layer for repeated experiment schedules.

### 4. Canonical Reducers

- `collect_batch_summary.py`
- `repeat_aggregate.py`
- `long_horizon_report.py`

These convert raw run folders into:

- summary tables
- repeat-level mean/std/count views
- long-horizon drift/contract/stage curves

## Wrapper Scripts

These scripts are preserved for convenience, but they are wrappers rather than canonical experiment engines:

- `run-longbench-batch-with-popup.ps1`
- `run-longbench-smoke.ps1`
- `first-paper-run.ps1`
- `comparison-run.ps1`

Use them when they save time, but do not treat them as the core logic of the experiment framework.

## Practical Rule

If two files appear to "run experiments," prefer them in this order:

1. primary Python entrypoint
2. thin wrapper script
3. diagnostic utility

The main logic should stay in the Python entrypoints, not in the wrappers.
