# SRP Experiment Index

This document is a directory of experiment records.

Use the experiment ID naming rule from `SRP_NEXT_PHASE_TASKS.md`.

---

## Index

### Measurement Infrastructure

| experiment_id | task_id | ablation | status | log file | notes |
|---|---|---|---|---|---|
| srp_meas_longbench_structrec_r01 | longbench_v2::671b1335bb02136c067d4e88 | structured recovery baseline | completed | srp_experiment/diagnostics/longbench_structured_recovery_r01.md | Baseline measurement artifact |
| srp_meas_longbench_objectret_v2_r01 | longbench_v2::671b1335bb02136c067d4e88 | object retention breakdown v2 | completed | srp_experiment/diagnostics/longbench_object_retention_breakdown_v2_r01.md | important/all/task-critical views |
| srp_meas_longbench_object_lifecycle_r01 | longbench_v2::671b1335bb02136c067d4e88 | object lifecycle baseline | completed | srp_experiment/diagnostics/longbench_object_lifecycle_r01.md | source/compressed/recovered/repaired lifecycle trace |

### Recovery Source Analysis

| experiment_id | task_id | ablation | status | log file | notes |
|---|---|---|---|---|---|
| srp_meas_longbench_recovery_reconstruction_r01 | longbench_v2::671b1335bb02136c067d4e88 | recovery reconstruction summary | completed | srp_experiment/diagnostics/longbench_recovery_reconstruction_summary.md | Compare text_only, structured_only, and hybrid reconstruction |

### Recovery Policy Evaluation

| experiment_id | task_id | ablation | status | log file | notes |
|---|---|---|---|---|---|
| srp_meas_longbench_reconstruction_policy_unrestricted_r01 | longbench_v2::671b1335bb02136c067d4e88 | reconstruction policy unrestricted | planned |  | Baseline policy for compact executable state reconstruction |
| srp_meas_longbench_reconstruction_policy_constrained_r01 | longbench_v2::671b1335bb02136c067d4e88 | reconstruction policy constrained | planned |  | Reduce inflation while preserving fidelity |
| srp_meas_longbench_reconstruction_policy_minimal_r01 | longbench_v2::671b1335bb02136c067d4e88 | reconstruction policy minimal | planned |  | Recover smallest sufficient executable state |
| srp_meas_longbench_state_allocation_unrestricted_r01 | longbench_v2::66fcffd9bb02136c067c94c5 | semantic runtime state allocation unrestricted | completed | srp_experiment/diagnostics/state_allocation_unrestricted_r01.jsonl | Upper-retention allocation baseline |
| srp_meas_longbench_state_allocation_constrained_r01 | longbench_v2::66fcffd9bb02136c067c94c5 | semantic runtime state allocation constrained | completed | srp_experiment/diagnostics/state_allocation_constrained_r01.jsonl | Constrained active/latent partition |
| srp_meas_longbench_state_allocation_minimal_r01 | longbench_v2::66fcffd9bb02136c067c94c5 | semantic runtime state allocation minimal | completed | srp_experiment/diagnostics/state_allocation_minimal_r01.md | First rule-based active/latent/discard partition |
| srp_meas_longbench_state_allocation_policy_r01 | longbench_v2::66fcffd9bb02136c067c94c5 | semantic runtime state allocation comparison | completed | srp_experiment/diagnostics/state_allocation_policy_comparison_r01.md | Three-policy comparison table |

### Repair Diagnostics

| experiment_id | task_id | ablation | status | log file | notes |
|---|---|---|---|---|---|
| srp_meas_longbench_filter_repair_r01 | longbench_v2::671b1335bb02136c067d4e88 | task-critical filter + repair off | completed | srp_experiment/diagnostics/longbench_filter_repair_r01.md | Isolated filter behavior without repair |
| srp_meas_longbench_nofilter_norepair_r01 | longbench_v2::671b1335bb02136c067d4e88 | no filter + no repair | completed | srp_experiment/diagnostics/longbench_nofilter_norepair_r01.md | Closed the 2x2 matrix |
| srp_meas_longbench_repair_constraint_r01 | longbench_v2::671b1335bb02136c067d4e88 | repair constraint summary | completed | srp_experiment/diagnostics/longbench_repair_constraint_summary.md | offline artifact; compare constraint modes |
| srp_meas_longbench_repair_constraint_conclusion_r01 | longbench_v2::671b1335bb02136c067d4e88 | repair constraint conclusion card | completed | srp_experiment/diagnostics/longbench_repair_constraint_conclusion_card.md | reconstruction policy is the bottleneck |
| srp_meas_longbench_repair_constraint_strict_r01 | longbench_v2::671b1335bb02136c067d4e88 | repair constraint strict | completed | srp_experiment/diagnostics/longbench_repair_constraint_strict_r01.md | strict repair |
| srp_meas_longbench_repair_constraint_constrained_r01 | longbench_v2::671b1335bb02136c067d4e88 | repair constraint constrained | completed | srp_experiment/diagnostics/longbench_repair_constraint_constrained_r01.md | constrained repair |
| srp_meas_longbench_repair_constraint_baseline_r01 | longbench_v2::671b1335bb02136c067d4e88 | repair constraint baseline | completed | srp_experiment/diagnostics/longbench_repair_constraint_baseline_r01.md | unrestricted repair |
| srp_meas_longbench_repair_objective_r01 | longbench_v2::671b1335bb02136c067d4e88 | repair objective summary | completed | srp_experiment/diagnostics/longbench_repair_objective_summary.md | objective switch only |
| srp_meas_longbench_repair_objective_minimal_patch_r01 | longbench_v2::671b1335bb02136c067d4e88 | repair objective minimal_patch | completed | srp_experiment/diagnostics/longbench_repair_objective_minimal_patch_r01.md | minimal patch objective |
| srp_meas_longbench_repair_objective_patch_r01 | longbench_v2::671b1335bb02136c067d4e88 | repair objective patch | completed | srp_experiment/diagnostics/longbench_repair_objective_patch_r01.md | object patch objective |
| srp_meas_longbench_repair_objective_generation_r01 | longbench_v2::671b1335bb02136c067d4e88 | repair objective generation | completed | srp_experiment/diagnostics/longbench_repair_objective_generation_r01.md | baseline generation objective |

---

## Suggested Status Values

- planned
- running
- completed
- blocked
- archived

---

## Indexing Rules

- Add one row per experiment.
- Keep `experiment_id` unique.
- Link the row to a single log file.
- Use the same `task_id` across repeated ablations when possible.
- If an experiment is rerun, keep the same base `experiment_id` and append a run suffix if needed.

---

## Recommended Usage

1. Create a new log from `SRP_EXPERIMENT_LOG_TEMPLATE.md`.
2. Fill in the experiment record.
3. Add a row here with the same `experiment_id`.
4. Archive the completed log file once the experiment is finalized.

---

## Research Question Map

### Measurement Infrastructure

- schema freeze
- controlled tasks
- lifecycle attribution

### Recovery Source Analysis

- text-only recovery
- structured-only recovery
- text-plus-structured recovery

### Recovery Policy Evaluation

- unrestricted reconstruction
- constrained reconstruction
- minimal sufficient reconstruction

### Repair Diagnostics

- repair constraint
- repair objective
- filter and repair interaction
