# Formal Evidence Index

This file identifies which current result namespaces are most appropriate for paper-facing use.

## Current Primary Paper-Facing Evidence

- `paper_figure_core_local/`
  - current local formal figure-producing run bundle
- `paper_figure_pack/`
  - paper-facing figure pack
- `batch_runs/first_paper_formal_local/`
  - current formal local batch namespace

## Current Reporting Products

- `batch_summary_table.json`
- `batch_summary_table.csv`
- `batch_summary_table.md`
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

## Long-Horizon Reporting

- `long_horizon_report/`

Use this namespace for stage summaries, drift curves, consistency tables, and repeat-aware reporting.

## Qualification / Freeze Evidence

- `experiment_qualification_report.json`
- `submission_audit/`
- `srp_submission_package.zip`

## Canonical Repeated-Family Resolution

- `RESULT_FAMILY_CANONICAL_MAP.md`

Use this file when several summary, trace, or risk-test outputs appear to overlap.

## Preserved But Not Main Formal Evidence

- `archive/smoke/`
- `archive/comparison/`
- `archive/debug/`
- `archive/latency/`
- `archive/generated/`

These remain useful for diagnosis, protocol iteration history, or narrow side analyses, but they should not be cited as the core paper evidence unless explicitly reclassified.

## Accidental Duplicate Namespace

- `archive/duplicate_namespace/srp_experiment_results_snapshot/`

Treat this as an accidental duplicate output root snapshot created by earlier path handling bugs. Do not use it as canonical evidence.

## Rule

If a result file exists both in a canonical namespace and a smoke/duplicate namespace, cite the canonical namespace only.
