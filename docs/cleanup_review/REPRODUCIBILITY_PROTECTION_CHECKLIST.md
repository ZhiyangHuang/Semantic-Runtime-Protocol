# Reproducibility Protection Checklist

Use this checklist before deleting any experiment-support files.

## Keep By Default

### Environment / qualification

- `srp_experiment/check_env_alignment.py`
- `srp_experiment/check_local_backend.py`
- `srp_experiment/experiment_qualification.py`
- `srp_experiment/run_qualified_experiment.py`
- `srp_experiment/run_qualified_batch.py`

### Benchmark provenance

- `srp_experiment/data/longbench_v2/manifest.json`
- `srp_experiment/data/longbench_v2/tasks.json`
- `srp_experiment/data/longbench_v2/tasks_group_1.json`
- `srp_experiment/data/longbench_v2/tasks_group_2.json`
- `srp_experiment/data/longbench_v2/tasks_group_3.json`
- `srp_experiment/data/longbench_v2/import_longbench_v2.py`
- `srp_experiment/data/longbench_v2/split_task_groups.py`

### Runtime inspection

- `srp_experiment/runtime_equivalence_test.py`
- `srp_experiment/protocol_behavior_trace.py`
- `srp_experiment/results/runtime_equivalence_all_tasks_with_exit_criteria.json`
- `srp_experiment/results/protocol_behavior_trace_iterative_cycles.json`

### Submission audit

- `first_paper/submission_audit.py`
- `first_paper/submission/`

## Review Questions

Before deleting any candidate, ask:

1. Does it support reproducibility?
2. Does it preserve benchmark provenance?
3. Does it preserve runtime inspection?
4. Does it preserve formal-audit evidence?

If any answer is yes, do not delete by default.
