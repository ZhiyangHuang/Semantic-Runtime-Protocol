# Semester Experiment Governance

This file is the single-entry governance view for the current semester experiment system.

Use this page first when you need the global picture.

## Mission

The current experiment system exists to support one semester of focused work toward a top-conference-oriented first SRP paper.

Its job is not to maximize feature growth.
Its job is to keep the experiment stack:

- runnable
- reproducible
- reviewable
- narrow enough to finish

## Canonical Global Structure

The current experiment system is governed through five stabilized layers plus one management layer:

1. entrypoint layer
2. config layer
3. data layer
4. baseline layer
5. evaluation layer
6. semester management layer

## What To Use First

### If you want to run experiments

Read in this order:

1. `srp_experiment/README.md`
2. `srp_experiment/ENTRYPOINT_EXECUTION_MAP.md`
3. `srp_experiment/configs/CANONICAL_CONFIG_MAP.md`

### If you want to understand the semester plan

Read in this order:

1. `Experiment_Master_Plan.md`
2. `Experiment_Progress_Report.md`
3. `Experiment_Task_Plan.md`
4. `Experiment_Stage_Freeze.md`

### If you want to decide whether a change is safe

Read in this order:

1. `Experiment_Stage_Freeze.md`
2. `Config_Layer_Management.md`
3. `Data_Layer_Management.md`
4. `Baseline_Layer_Management.md`
5. `Evaluation_Layer_Management.md`

## Frozen Canonical Pieces

### Entrypoints

Canonical entrypoints:

- `srp_experiment/longbench_launcher.py`
- `srp_experiment/run_qualified_experiment.py`
- `srp_experiment/batch_run.py`
- `srp_experiment/collect_batch_summary.py`
- `srp_experiment/repeat_aggregate.py`
- `srp_experiment/long_horizon_report.py`

### Configs

Canonical configs:

- `srp_experiment/configs/longbench_v2_multimodel_100_1000_smoke.json`
- `srp_experiment/configs/longbench_v2_multimodel_100_1000.json`
- `srp_experiment/configs/first_paper_formal_local.json`

### Data

Canonical data split:

- toy tasks = protocol validation layer
- `longbench_v2/tasks.json` = public benchmark evidence layer
- `tasks_group_1/2/3.json` = execution partitions

### Baselines

Canonical five-method comparison:

- `raw_prompt`
- `summarization`
- `rag`
- `srp`
- `rag_srp_v2`

Preserved diagnostics only:

- `rag_srp`
- `rag_srp_anchor`

### Metrics

Primary paper metrics:

- `drift`
- `validation_contract_satisfaction`
- `state_committed`

## What Is Preserved But Not Primary

These classes of artifacts remain important, but they are not the main semester-facing path:

- smoke outputs
- debug outputs
- latency-only outputs
- duplicate namespace snapshots
- exploratory configs
- exploratory hybrid baselines
- runtime diagnostics
- wrapper scripts

These should be preserved, indexed, and demoted rather than confused with formal evidence.

## Where To Look For Formal Evidence

Use:

- `srp_experiment/results/FORMAL_EVIDENCE_INDEX.md`
- `srp_experiment/results/README.md`

Do not treat archived namespaces as if they were current paper-facing evidence unless a note explicitly re-promotes them.

## Where To Look For Current Status

Use:

- `Experiment_Progress_Report.md`

That file should answer:

- what is done
- what is blocked
- what is currently frozen
- what the next highest-value action is

## Governance Rule

When the repository feels confusing, do not add another top-level workflow by default.

Instead:

1. identify the relevant layer
2. update the canonical layer-management note
3. preserve older artifacts through archive or demotion
4. keep the semester-facing path narrow

## Canonical Navigation Map

- master scope: `Experiment_Master_Plan.md`
- current state: `Experiment_Progress_Report.md`
- next actions: `Experiment_Task_Plan.md`
- freeze boundary: `Experiment_Stage_Freeze.md`
- file deduplication: `Experiment_File_Canonical_Map.md`
- results policy: `Results_Namespace_Management.md`
- config policy: `Config_Layer_Management.md`
- entrypoint policy: `Execution_Entrypoint_Stabilization.md`
- data policy: `Data_Layer_Management.md`
- baseline policy: `Baseline_Layer_Management.md`
- evaluation policy: `Evaluation_Layer_Management.md`

This is the governance spine for the semester experiment system.
