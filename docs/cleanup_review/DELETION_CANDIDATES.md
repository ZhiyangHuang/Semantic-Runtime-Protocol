# Deletion Candidates

This file classifies repository files into:

- safe now
- review first
- keep

It is meant to support audited cleanup, not impulsive deletion.

## Hard Safety Rule

Do **not** mass-delete `.py` source files.

For this repository, Python source files are treated as:

- execution logic
- reproducibility logic
- provenance-preserving utilities
- reviewer-inspection support

So the default policy is:

- keep `.py` files
- audit them for role overlap
- demote or document duplicates
- only delete a Python file after explicit line-by-line review and a confirmed canonical replacement

Also do **not** delete the reproducibility layer by default.

See:

- `docs/strategy/Reproducibility_Layer_Management.md`
- `docs/cleanup_review/REPRODUCIBILITY_PROTECTION_CHECKLIST.md`

## Safe Now

These are safe to delete now without harming canonical experiment governance, formal evidence, or benchmark provenance.

### Cleanup-review artifacts after approval

- `docs/cleanup_review/temporary1.md`
- `docs/cleanup_review/temporary2.md`
- `docs/cleanup_review/temporary3.md`
- `docs/cleanup_review/CLEANUP_REVIEW_MANIFEST.md`
- `docs/cleanup_review/DELETION_CANDIDATES.md`
- `docs/cleanup_review/README.md`

Condition:

- only after you confirm the cleanup structure is accepted

### Launcher-generated session configs

- `srp_experiment/configs/generated/raw_prompt__group_1__formal__20260701_193522.json`
- `srp_experiment/configs/generated/raw_prompt__group_1__formal__20260701_195340.json`

Condition:

- safe once you no longer need those exact launcher sessions for rerun reproducibility

Rationale:

- generated configs are explicitly non-canonical session artifacts

## Review First

These are candidates for deletion, but only after explicit review because they preserve history, diagnostics, or alternative output chains.

### Exploratory config layer

- `srp_experiment/configs/comparison_pack_local.json`
- `srp_experiment/configs/risk_test_srp_vs_hybrids_5_7.json`
- `srp_experiment/configs/risk_test_refactored_srp_vs_hybrids_5_7.json`

Rationale:

- these are no longer canonical semester configs
- but they still preserve exploratory or pre-refactor comparison history

### Top-level risk-test result chain

- `srp_experiment/results/risk_test_srp_vs_hybrids_5_7_summary.json`
- `srp_experiment/results/risk_test_srp_vs_hybrids_5_7_summary.csv`
- `srp_experiment/results/risk_test_srp_vs_hybrids_5_7_summary.md`

Rationale:

- the refactored chain is already marked canonical
- the older chain is preserved history

### Runtime-equivalence patch chain

- `srp_experiment/results/runtime_equivalence_all_tasks.json`
- `srp_experiment/results/runtime_equivalence_all_tasks_after_mock_patch.json`
- `srp_experiment/results/runtime_equivalence_all_tasks_after_mock_patch_v2.json`
- `srp_experiment/results/runtime_equivalence_all_tasks_after_mock_patch_v3.json`
- `srp_experiment/results/runtime_equivalence_all_tasks_after_mock_patch_v4.json`
- `srp_experiment/results/runtime_equivalence_pref_low_latency.json`
- `srp_experiment/results/runtime_equivalence_pref_low_latency_after_mock_patch.json`
- `srp_experiment/results/runtime_equivalence_pref_low_latency_after_mock_patch_v2.json`
- `srp_experiment/results/runtime_equivalence_pref_low_latency_after_mock_patch_v3.json`
- `srp_experiment/results/runtime_equivalence_pref_low_latency_after_mock_patch_v4.json`

Rationale:

- `runtime_equivalence_all_tasks_with_exit_criteria.json` is already canonical
- these files are still useful as repair history

### Secondary qualification/debug signals

- `srp_experiment/results/qualification_report.json`
- `srp_experiment/results/eq_debug_report.json`

Rationale:

- they are secondary to `experiment_qualification_report.json`
- but may still help if you need to audit the qualification path

### Archived smoke / latency / duplicate snapshots

Everything already in:

- `srp_experiment/results/archive/smoke/`
- `srp_experiment/results/archive/latency/`
- `srp_experiment/results/archive/comparison/`
- `srp_experiment/results/archive/generated/`
- `srp_experiment/results/archive/duplicate_namespace/`

Rationale:

- these are already safely demoted
- the next question is retention, not classification

## Keep

These should not be deleted in the current phase.

### Canonical governance and system maps

- `docs/strategy/*.md`
- `srp_experiment/ENTRYPOINT_EXECUTION_MAP.md`
- `srp_experiment/TOOLS_INDEX.md`
- `srp_experiment/configs/CANONICAL_CONFIG_MAP.md`
- `srp_experiment/data/DATA_FAMILY_CANONICAL_MAP.md`
- `srp_experiment/results/RESULT_FAMILY_CANONICAL_MAP.md`

### Canonical configs

- `srp_experiment/configs/longbench_v2_multimodel_100_1000.json`
- `srp_experiment/configs/longbench_v2_multimodel_100_1000_smoke.json`
- `srp_experiment/configs/first_paper_formal_local.json`

### Canonical data

- `srp_experiment/data/task_a.json`
- `srp_experiment/data/task_b.json`
- `srp_experiment/data/task_c.json`
- `srp_experiment/data/longbench_v2/tasks.json`
- `srp_experiment/data/longbench_v2/manifest.json`
- `srp_experiment/data/longbench_v2/tasks_group_1.json`
- `srp_experiment/data/longbench_v2/tasks_group_2.json`
- `srp_experiment/data/longbench_v2/tasks_group_3.json`
- `srp_experiment/data/longbench_v2/import_longbench_v2.py`
- `srp_experiment/data/longbench_v2/split_task_groups.py`

### Canonical experiment entrypoints and reducers

- `srp_experiment/longbench_launcher.py`
- `srp_experiment/run_experiment.py`
- `srp_experiment/run_qualified_experiment.py`
- `srp_experiment/batch_run.py`
- `srp_experiment/collect_batch_summary.py`
- `srp_experiment/repeat_aggregate.py`
- `srp_experiment/long_horizon_report.py`

### Audited Python Support Layer

Keep these because they prevent later duplicate wheel-building and preserve system logic:

- `srp_experiment/check_env_alignment.py`
- `srp_experiment/check_local_backend.py`
- `srp_experiment/progress_popup.py`
- `srp_experiment/evidence_pipeline.py`
- `srp_experiment/experiment_qualification.py`
- `srp_experiment/run_qualified_batch.py`
- `srp_experiment/runtime_equivalence_test.py`
- `srp_experiment/protocol_behavior_trace.py`
- `srp_experiment/data/longbench_v2/import_longbench_v2.py`
- `srp_experiment/data/longbench_v2/split_task_groups.py`

These are not all equal in importance, but they should be audited as reusable logic, not deleted as clutter.

### Canonical paper-facing evidence

- `srp_experiment/results/batch_summary_table.json`
- `srp_experiment/results/batch_summary_table.csv`
- `srp_experiment/results/batch_summary_table.md`
- `srp_experiment/results/paper_table.md`
- `srp_experiment/results/paper_table.tex`
- `srp_experiment/results/quality_table.*`
- `srp_experiment/results/efficiency_table.*`
- `srp_experiment/results/guardrail_table.*`
- `srp_experiment/results/camera_ready_table.*`
- `srp_experiment/results/paper_figure_pack/`
- `srp_experiment/results/experiment_qualification_report.json`
- `srp_experiment/results/runtime_equivalence_all_tasks_with_exit_criteria.json`
- `srp_experiment/results/protocol_behavior_trace_iterative_cycles.json`
- `srp_experiment/results/submission_audit/`
- `srp_experiment/results/srp_submission_package.zip`

## Deletion Rule

Delete only from `Safe Now` without further discussion.

Delete from `Review First` only after an explicit follow-up approval.

For `.py` files, require an additional rule:

1. identify the canonical replacement
2. confirm no unique logic is lost
3. confirm no paper/reproducibility path still references it
4. only then consider deletion
