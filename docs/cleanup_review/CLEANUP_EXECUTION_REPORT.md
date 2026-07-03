# Cleanup Execution Report

This report is the short-term execution view of the cleanup state.

It answers only three questions:

1. what should be deleted now
2. what should be moved or further demoted
3. what must remain in place

It is intentionally operational rather than architectural.

## Status Summary

Current cleanup state:

- governance documents are already separated from execution code
- cleanup-review files are already separated into `docs/cleanup_review/`
- smoke/debug/latency outputs are already demoted into `srp_experiment/results/archive/`
- canonical maps now exist for data and results

The remaining cleanup work is mostly:

- deleting short-lived review/session artifacts
- deciding whether older result chains should be retained or removed
- optionally moving root scratch notes into review/archive space

## Delete Now

These can be deleted immediately with low risk.

### Launcher-generated session configs

- `srp_experiment/configs/generated/raw_prompt__group_1__formal__20260701_193522.json`
- `srp_experiment/configs/generated/raw_prompt__group_1__formal__20260701_195340.json`

Reason:

- session-specific generated configs
- not canonical
- already documented as non-primary

### Cleanup-review folder after approval

- `docs/cleanup_review/`

Reason:

- short-lived review namespace by design
- safe only after you confirm the current cleanup structure is accepted

## Move Or Further Demote

These should not be deleted first; they should either stay archived or be moved into an even clearer historical lane later.

### Top-level older runtime-equivalence chain

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

Recommended action:

- keep for now
- optionally move later into a dedicated archive subfolder such as `archive/runtime_equivalence_history/`

### Older risk-test chain

- `srp_experiment/results/risk_test_srp_vs_hybrids_5_7_summary.json`
- `srp_experiment/results/risk_test_srp_vs_hybrids_5_7_summary.csv`
- `srp_experiment/results/risk_test_srp_vs_hybrids_5_7_summary.md`

Recommended action:

- keep for now
- optionally move later into `archive/risk_history/`

### Root scratch note

- `temporary.md`

Recommended action:

- do not delete yet
- either keep as the live scratchpad
- or move later into `docs/cleanup_review/` or another reviewed notes folder if it is no longer active

## Keep In Place

These should remain where they are.

### Root-level stable project files

- `README.md`
- `LICENSE`
- `semester_timeline.md`

### Canonical experiment code and maps

- all canonical `.py` entrypoints and reducers
- all canonical governance docs in `docs/strategy/`
- all canonical family maps in `srp_experiment/data/` and `srp_experiment/results/`

### Canonical data and provenance

- `srp_experiment/data/task_a.json`
- `srp_experiment/data/task_b.json`
- `srp_experiment/data/task_c.json`
- `srp_experiment/data/longbench_v2/tasks.json`
- `srp_experiment/data/longbench_v2/manifest.json`
- `srp_experiment/data/longbench_v2/tasks_group_1.json`
- `srp_experiment/data/longbench_v2/tasks_group_2.json`
- `srp_experiment/data/longbench_v2/tasks_group_3.json`

### Canonical paper-facing result layer

- `srp_experiment/results/batch_summary_table.*`
- `srp_experiment/results/paper_table.*`
- `srp_experiment/results/quality_table.*`
- `srp_experiment/results/efficiency_table.*`
- `srp_experiment/results/guardrail_table.*`
- `srp_experiment/results/camera_ready_table.*`
- `srp_experiment/results/paper_figure_pack/`
- `srp_experiment/results/experiment_qualification_report.json`
- `srp_experiment/results/runtime_equivalence_all_tasks_with_exit_criteria.json`
- `srp_experiment/results/protocol_behavior_trace_iterative_cycles.json`

## Recommended Next Physical Actions

If you want a conservative cleanup sequence, do it in this order:

1. delete the two generated configs in `srp_experiment/configs/generated/`
2. keep `temporary.md` where it is unless you decide to retire it
3. keep all older runtime-equivalence and risk-test chains until after paper submission or after a dedicated archive move
4. delete `docs/cleanup_review/` only after you approve the cleanup structure

## Final Short Recommendation

Delete now:

- generated configs in `srp_experiment/configs/generated/`

Do not delete yet:

- `temporary.md`
- old runtime-equivalence chain
- old risk-test chain
- anything in the reproducibility layer

Delete later as one unit:

- `docs/cleanup_review/`
