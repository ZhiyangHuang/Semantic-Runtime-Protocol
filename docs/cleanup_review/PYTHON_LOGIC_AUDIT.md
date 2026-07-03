# Python Logic Audit

This note exists to stop accidental “cleanup” from turning into duplicate reimplementation later.

## Principle

Do not delete Python source just because there are many files.

The correct question is:

> Does this file still hold unique execution logic, reproducibility logic, audit logic, or reviewer-visible inspection value?

If yes, keep it and classify it.

## Current Python Role Split

### Canonical Execution Core

- `srp_experiment/run_experiment.py`
- `srp_experiment/batch_run.py`
- `srp_experiment/run_qualified_experiment.py`
- `srp_experiment/longbench_launcher.py`
- `srp_experiment/collect_batch_summary.py`
- `srp_experiment/repeat_aggregate.py`
- `srp_experiment/long_horizon_report.py`

### Canonical Support / Guardrails

- `srp_experiment/check_env_alignment.py`
- `srp_experiment/check_local_backend.py`
- `srp_experiment/progress_popup.py`
- `srp_experiment/experiment_qualification.py`
- `srp_experiment/evidence_pipeline.py`

### Canonical Data / Import Logic

- `srp_experiment/data/longbench_v2/import_longbench_v2.py`
- `srp_experiment/data/longbench_v2/split_task_groups.py`

### Preserve As Diagnostics

- `srp_experiment/runtime_equivalence_test.py`
- `srp_experiment/protocol_behavior_trace.py`

### Preserve As Secondary Wrapper Logic

- `srp_experiment/run_qualified_batch.py`

## Audit Rule

If two Python files seem similar:

1. keep the file with the canonical execution role
2. keep the other if it still contains unique wrapper, audit, or diagnostic logic
3. only delete when the secondary file has become pure duplication

## Current Recommendation

At the current paper stage:

- do not delete Python source files by default
- prefer documentation and demotion over source deletion
- use the governance maps to prevent future duplicate wheel-building
