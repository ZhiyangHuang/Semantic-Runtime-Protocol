# Cleanup Guardrail Plan

This file is a temporary cleanup guardrail for the current repository reorganization.

The goal is not to delete aggressively. The goal is to:

- reduce experiment coupling
- preserve the strongest paper-facing path
- keep diagnostics and legacy material visible but demoted
- avoid deleting evidence that may still matter for paper writing or later audit

## Cleanup Principles

1. Keep one canonical experiment path for the first paper.
2. Keep one canonical public benchmark path for formal evidence.
3. Keep one canonical paper draft path for submission shaping.
4. Demote duplicate or exploratory tools before deleting anything.
5. Preserve all paper-relevant diagnostics until the submission freeze is complete.

## Canonical Experiment Stack To Keep

- `srp_experiment/longbench_launcher.py`
- `srp_experiment/run_experiment.py`
- `srp_experiment/batch_run.py`
- `srp_experiment/collect_batch_summary.py`
- `srp_experiment/repeat_aggregate.py`
- `srp_experiment/long_horizon_report.py`
- `srp_experiment/experiment_qualification.py`
- `srp_experiment/run_qualified_experiment.py`
- `srp_experiment/check_env_alignment.py`

## Keep But Demote To Diagnostic / Infrastructure

- `srp_experiment/protocol_behavior_trace.py`
- `srp_experiment/runtime_equivalence_test.py`
- `srp_experiment/evidence_pipeline.py`
- `srp_experiment/check_local_backend.py`
- `srp_experiment/progress_popup.py`

These remain important, but they should not be presented as primary user-facing entrypoints.

## Keep But Mark As Exploratory / Not Main Paper Core

- `srp_experiment/baselines/rag_srp.py`
- `srp_experiment/baselines/rag_srp_anchor.py`

## Data Layers To Preserve

- `srp_experiment/data/longbench_v2/` as the public benchmark layer
- `srp_experiment/data/task_a.json`
- `srp_experiment/data/task_b.json`
- `srp_experiment/data/task_c.json`

The toy tasks should remain available as protocol validation, not main public evidence.

## Result Layers To Preserve

- `srp_experiment/results/batch_runs/` as active experiment namespace
- `srp_experiment/results/paper_figure_pack/` as paper-facing figure namespace
- `srp_experiment/results/paper_figure_core_local/` as current formal local evidence
- `srp_experiment/results/long_horizon_report/` as analysis namespace

## Result Layers To Flag As Accidental Or Legacy

- `srp_experiment/srp_experiment/results/` should be treated as accidental duplicate output namespace
- smoke folders under `srp_experiment/results/` should remain preserved but not treated as primary evidence

## Paper Sources To Keep

- `first_paper/draft/01_Full_Draft.md`
- `first_paper/draft/02_Submission_Version.md`
- `first_paper/latex/main_submission.tex`

## Reorganization Tasks

1. Write a semester-level experiment master plan.
2. Write a live progress report with current stage and open blockers.
3. Write a task plan with next-step execution order.
4. Write a stage-freeze document defining what is frozen and what is still allowed to change.
5. Update the main experiment README so canonical entrypoints are obvious.
6. Update the strategy README so the four management documents are first-class navigation targets.

## Do Not Delete Yet

- any submission artifact
- any runtime equivalence result
- any protocol-layer smoke evidence
- any figure or paper-ready table already referenced by the draft

Deletion or archive moves should happen only after the canonical map is stable.
