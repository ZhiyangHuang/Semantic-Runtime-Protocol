# Strategy Index

This folder stores the strategy-side notes for semester scope, personal positioning, and long-term design.
It belongs to the long-term design side, not the first-paper package.

Strategy total goal:

This is the first SRP paper, the first top-conference-oriented paper in my undergraduate research path, and it must be finished within one semester of focused refinement.

Strategy protocol principle:

> Runtime verification SHALL operate on typed semantic representations rather than directly on lexical surface forms.

The current strategy navigation uses a shared disclosure vocabulary:

- formal evidence
- legacy archive
- refactor rerun

## Contents

- `Semester_Experiment_Governance.md` - single-entry semester governance page for the whole experiment system
- `Experiment_Master_Plan.md` - global experiment charter and canonical stack
- `Experiment_Progress_Report.md` - current status, main risks, and stabilization direction
- `Experiment_Task_Plan.md` - next-step execution order for the semester
- `Experiment_Stage_Freeze.md` - frozen and not-yet-frozen boundaries for the current paper
- `Experiment_File_Canonical_Map.md` - file-level deduplication map and canonical entrypoint list
- `Results_Namespace_Management.md` - canonical vs preserved result namespace policy
- `Config_Layer_Management.md` - canonical vs secondary vs exploratory config roles
- `Execution_Entrypoint_Stabilization.md` - primary experiment entrypoints vs wrappers vs diagnostics
- `Data_Layer_Management.md` - protocol-validation data vs public-benchmark evidence vs execution partitions
- `Baseline_Layer_Management.md` - canonical five-method comparison vs exploratory hybrids
- `Evaluation_Layer_Management.md` - primary paper metrics vs supporting and diagnostic metrics
- `Reproducibility_Layer_Management.md` - protected reproducibility layer for environment, provenance, inspection, and audit
- `One_Semester_Execution_Checklist.md` - semester scope and execution plan
- `Local_Qwen_Pilot_Tuning_Log.md` - preserved pilot history, including formal evidence and legacy archive volumes
- `Formal_Experiment_Runbook.md` - formal paper-facing execution contract, output namespaces, and rerun separation
- `SRP_Risk_Classification_Checklist.md` - formal evidence retention, legacy archive classification, and refactor rerun rules
- `SRP_Leakage_And_Cheating_Risk_Report.md` - scope-limited leakage and cheating risk report
- `SRP_Anti_Leakage_Modification_Plan.md` - implementation plan for inference-time anti-leakage refactors
- `Temporary_Table_Expansion_Plan.md` - temporary table-expansion plan and token/cost roadmap
- `summery.md` - long-form design notes

## Use It When

- Use `Experiment_Master_Plan.md` when you need the canonical global view.
- Use `Semester_Experiment_Governance.md` when you want the fastest one-page orientation across the whole experiment system.
- Use `Experiment_Progress_Report.md` when you need the current state in one page.
- Use `Experiment_Task_Plan.md` when you need the next actionable sequence.
- Use `Experiment_Stage_Freeze.md` when deciding whether a change is still in scope.
- Use `Experiment_File_Canonical_Map.md` when deciding which file to keep as the primary implementation.
- Use `Results_Namespace_Management.md` when deciding how to preserve or demote outputs without losing evidence.
- Use `Config_Layer_Management.md` when deciding which config should drive a run.
- Use `Execution_Entrypoint_Stabilization.md` when deciding which script is the true execution entry and which scripts are only wrappers.
- Use `Data_Layer_Management.md` when deciding where a task set, benchmark import, or task partition belongs.
- Use `Baseline_Layer_Management.md` when deciding whether a method belongs to the main paper comparison or to diagnostics only.
- Use `Evaluation_Layer_Management.md` when deciding which metrics define the paper claim and which only support or diagnose it.
- Use `Reproducibility_Layer_Management.md` when deciding whether a file belongs to the protected reproducibility layer and should not be deleted by routine cleanup.
- Use `One_Semester_Execution_Checklist.md` for the semester plan.
- Use `Local_Qwen_Pilot_Tuning_Log.md` for preserved local pilot history, tuning comparisons, and error-boundary tracking.
- Use the split pilot volumes linked from `Local_Qwen_Pilot_Tuning_Log.md` when you need the preserved round-by-round record.
- Use `Formal_Experiment_Runbook.md` for the canonical formal workflow, comparison workflow, and output-naming rules.
- Use `SRP_Risk_Classification_Checklist.md` for separating formal evidence, legacy archive outputs, and refactor reruns.
- Use `SRP_Leakage_And_Cheating_Risk_Report.md` and `SRP_Anti_Leakage_Modification_Plan.md` for leakage-scope framing and anti-cheating refactor planning.
- Use `Temporary_Table_Expansion_Plan.md` for the stepwise reporting expansion roadmap.
- Use `summery.md` for long-term design context.

## Data And Disclosure Structure

The strategy notes now use three layers of disclosure:

1. `Local_Qwen_Pilot_Tuning_Log.md` plus its split volumes for the full preserved pilot history
2. `Formal_Experiment_Runbook.md` for formal evidence, output-namespace rules, and rerun separation
3. `SRP_Risk_Classification_Checklist.md` and the leakage reports for formal evidence retention, legacy archive labeling, and refactor rerun rules

This structure is meant to keep:

- formal evidence
- legacy archive outputs
- refactor reruns

in separate, explicitly documented lanes.

For the current cleanup phase, the four primary management documents are:

1. `Semester_Experiment_Governance.md`
2. `Experiment_Master_Plan.md`
3. `Experiment_Progress_Report.md`
4. `Experiment_Task_Plan.md`
5. `Experiment_Stage_Freeze.md`
6. `Experiment_File_Canonical_Map.md`
7. `Results_Namespace_Management.md`
8. `Config_Layer_Management.md`
9. `Execution_Entrypoint_Stabilization.md`
10. `Data_Layer_Management.md`
11. `Baseline_Layer_Management.md`
12. `Evaluation_Layer_Management.md`
13. `Reproducibility_Layer_Management.md`
