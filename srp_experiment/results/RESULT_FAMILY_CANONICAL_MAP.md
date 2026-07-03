# Result Family Canonical Map

This file resolves repeated result families into canonical vs preserved variants.

Its purpose is to prevent paper-facing evidence from becoming entangled with:

- iteration snapshots
- side-risk summaries
- repeated patch-state traces
- older exploratory exports

## Rule

For each repeated result family:

- keep one canonical file or namespace for paper-facing use
- preserve the others as historical or diagnostic artifacts
- do not silently cite every version as if they were equally current

## Family 1: Batch Summary Outputs

Canonical:

- `batch_summary_table.json`
- `batch_summary_table.csv`
- `batch_summary_table.md`

Role:

- canonical reduced batch summary layer

Preserved related derivatives:

- `paper_table.md`
- `paper_table.tex`
- `quality_table.md`
- `quality_table.tex`
- `efficiency_table.md`
- `efficiency_table.tex`
- `guardrail_table.md`
- `guardrail_table.tex`
- `camera_ready_table.md`
- `camera_ready_table.tex`
- `token_breakdown_table.md`
- `token_breakdown_table.tex`

Interpretation:

- these are canonical reporting products derived from the batch summary, not competing summary sources

## Family 2: Runtime Equivalence Chain

Canonical:

- `runtime_equivalence_all_tasks_with_exit_criteria.json`

Role:

- final reviewer-facing runtime-equivalence status view

Preserved historical chain:

- `runtime_equivalence_all_tasks.json`
- `runtime_equivalence_all_tasks_after_mock_patch.json`
- `runtime_equivalence_all_tasks_after_mock_patch_v2.json`
- `runtime_equivalence_all_tasks_after_mock_patch_v3.json`
- `runtime_equivalence_all_tasks_after_mock_patch_v4.json`
- `runtime_equivalence_pref_low_latency.json`
- `runtime_equivalence_pref_low_latency_after_mock_patch.json`
- `runtime_equivalence_pref_low_latency_after_mock_patch_v2.json`
- `runtime_equivalence_pref_low_latency_after_mock_patch_v3.json`
- `runtime_equivalence_pref_low_latency_after_mock_patch_v4.json`

Interpretation:

- preserve these as the repair history
- cite the exit-criteria file as the canonical settled version

## Family 3: Protocol Behavior Trace

Canonical:

- `protocol_behavior_trace_iterative_cycles.json`

Role:

- canonical first-divergence trace artifact

Interpretation:

- keep as a reviewer-inspection artifact
- it is diagnostic evidence, not the main paper result table

## Family 4: Risk-Test Summary Chain

Canonical:

- `risk_test_refactored_srp_vs_hybrids_5_7_summary.json`
- `risk_test_refactored_srp_vs_hybrids_5_7_summary.csv`
- `risk_test_refactored_srp_vs_hybrids_5_7_summary.md`

Preserved predecessor:

- `risk_test_srp_vs_hybrids_5_7_summary.json`
- `risk_test_srp_vs_hybrids_5_7_summary.csv`
- `risk_test_srp_vs_hybrids_5_7_summary.md`

Interpretation:

- use the refactored chain if this comparison family is needed
- keep the older chain as pre-refactor history only

## Family 5: Qualification / Freeze Signals

Canonical:

- `experiment_qualification_report.json`
- `submission_audit/`
- `srp_submission_package.zip`

Secondary:

- `qualification_report.json`
- `eq_debug_report.json`

Interpretation:

- use `experiment_qualification_report.json` for the stable qualification signal
- treat `qualification_report.json` and `eq_debug_report.json` as secondary or run-specific support

## Family 6: Single-Run Legacy Top-Level Files

Top-level files that should not be treated as the main current paper namespace by default:

- `results.json`
- `summary.json`
- `run_metadata.json`

Interpretation:

- these may be legitimate remnants of earlier formal local runs
- prefer namespace-scoped run bundles such as `paper_figure_core_local/` or `batch_runs/...` when citing current evidence

## Family 7: Figures

Canonical paper-facing figure namespace:

- `paper_figure_pack/`

Secondary but still legitimate:

- `paper_figure_core_local/`
- top-level `drift_plot.png`

Interpretation:

- prefer the figure-pack namespace for current paper packaging

## Practical Rule

When a repeated family exists, cite:

1. the canonical file named here
2. the canonical namespace from `FORMAL_EVIDENCE_INDEX.md`

Treat all other versions as preserved history unless explicitly promoted again.
