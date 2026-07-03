# Experiment Master Plan

This document is the global experiment charter for the first SRP paper.

## Goal

Deliver one semester-bounded, reproducible, public-benchmark-backed paper that supports a narrow and defensible claim:

> SRP improves bounded long-horizon semantic stability under a shared token budget, relative to controlled baseline memory operators.

## Canonical Experiment Path

The main experiment path is:

1. benchmark/task selection
2. qualified run
3. batch summary
4. repeat aggregation
5. long-horizon reporting
6. paper tables and figures
7. submission audit

## Canonical Entry Points

- single interactive entry: `srp_experiment/longbench_launcher.py`
- single-run debug entry: `srp_experiment/run_experiment.py`
- formal qualified entry: `srp_experiment/run_qualified_experiment.py`
- batch sweep entry: `srp_experiment/batch_run.py`
- repeat statistics entry: `srp_experiment/repeat_aggregate.py`
- long-horizon report entry: `srp_experiment/long_horizon_report.py`

## Canonical Public Evidence Layer

- benchmark: `LongBench v2`
- local frozen import: `srp_experiment/data/longbench_v2/tasks.json`
- frozen sample count: `300`
- grouped execution slices:
  - `tasks_group_1.json`
  - `tasks_group_2.json`
  - `tasks_group_3.json`

## Canonical Comparison Family

Main five methods:

- `raw_prompt`
- `summarization`
- `rag`
- `srp`
- `rag_srp_v2`

Main claim should be written against this family only.

## Demoted But Preserved Tools

The following remain important but are not primary experiment entrypoints:

- `protocol_behavior_trace.py`
- `runtime_equivalence_test.py`
- `evidence_pipeline.py`
- `check_local_backend.py`

These support debugging, evidence inspection, and reviewer-facing auditability.

## Semester Constraint

The experiment system should optimize for:

- reproducibility
- reviewability
- narrow scope
- stable evidence

It should not optimize for:

- maximal benchmark coverage
- maximal model coverage
- speculative future-work extensions

## Clean Structure Rule

If a new tool duplicates an existing tool, the repository should keep only one canonical user-facing entrypoint and demote the rest to diagnostic support.
