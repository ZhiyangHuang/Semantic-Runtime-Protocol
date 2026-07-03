# Experiment File Canonical Map

This file records which script should be treated as the canonical implementation when several files feel similar.

## Run Entry

- keep: `srp_experiment/run_experiment.py`
- reason: this is the actual single-run engine

## Formal Qualified Entry

- keep: `srp_experiment/run_qualified_experiment.py`
- reason: this is the paper-facing gatekeeper

## Interactive Entry

- keep: `srp_experiment/longbench_launcher.py`
- reason: this is the best user-facing control surface for grouped LongBench runs

## Batch Sweep

- keep: `srp_experiment/batch_run.py`
- reason: this is the canonical multi-run execution engine

## Batch Summary Reduction

- keep: `srp_experiment/collect_batch_summary.py`
- reason: this is the canonical merger from many run folders into one analysis table

## Repeat Statistics

- keep: `srp_experiment/repeat_aggregate.py`
- reason: this is the canonical mean/std/count reducer for repeated runs

## Long-Horizon Analysis

- keep: `srp_experiment/long_horizon_report.py`
- reason: this is the canonical stage and curve report

## Qualification Gate

- keep: `srp_experiment/experiment_qualification.py`
- reason: this is the experiment readiness gate

## Environment Alignment

- keep: `srp_experiment/check_env_alignment.py`
- reason: this is the canonical preflight alignment checker

## Backend Diagnostics

- keep: `srp_experiment/check_local_backend.py`
- reason: this is the canonical backend health probe

## Trace / Equivalence Diagnostics

- keep: `srp_experiment/protocol_behavior_trace.py`
- keep: `srp_experiment/runtime_equivalence_test.py`
- reason: both are important, but only as diagnostics

## Evidence Integration

- keep: `srp_experiment/evidence_pipeline.py`
- reason: this is the canonical artifact-binding layer

## Comparison Family

Main paper family:

- keep: `raw_prompt.py`
- keep: `summarization.py`
- keep: `rag.py`
- keep: `srp/`
- keep: `rag_srp_v2.py`

Exploratory but not main-paper-primary:

- preserve: `rag_srp.py`
- preserve: `rag_srp_anchor.py`

## Paper Draft Family

- keep: `first_paper/draft/02_Submission_Version.md` as the best short submission-shape source
- preserve: `first_paper/draft/01_Full_Draft.md` as the long-form evidence-bound draft
- preserve: `first_paper/draft/00_Current_Stage_Report.md` as the quick status report

## Submission Packaging

- keep: `first_paper/submission_audit.py`
- keep: `first_paper/latex/main_submission.tex`

## Rule

If two files appear to serve the same role, the file listed here should be treated as canonical unless the paper scope is explicitly redefined.
