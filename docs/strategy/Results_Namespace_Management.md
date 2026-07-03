# Results Namespace Management

This document records how to keep experiment outputs organized without over-deleting evidence.

## Canonical Namespaces

Use these as the current official lanes:

- `srp_experiment/results/batch_runs/`
- `srp_experiment/results/paper_figure_core_local/`
- `srp_experiment/results/paper_figure_pack/`
- `srp_experiment/results/long_horizon_report/`
- `srp_experiment/results/submission_audit/`

## Preserved Secondary Namespaces

These should be kept, but explicitly treated as non-primary:

- `srp_experiment/results/archive/smoke/`
- `srp_experiment/results/archive/comparison/`
- `srp_experiment/results/archive/latency/`
- `srp_experiment/results/archive/debug/`
- `srp_experiment/results/archive/generated/`

## Duplicate / Bug-Created Namespace

- `srp_experiment/results/archive/duplicate_namespace/srp_experiment_results_snapshot/`

This snapshot is preserved for auditability, but should already be treated as non-canonical.

## Management Rule

Do not delete a result namespace unless all three conditions hold:

1. its role is documented elsewhere
2. its paper-relevant information is preserved in a better namespace
3. it is not referenced by the current draft, freeze report, or submission package

## Semester Rule

During the current paper cycle:

- prefer relabeling before deleting
- prefer archive moves over destructive cleanup
- prefer canonical-path citation over aggressive cleanup

The objective is to reduce confusion without risking evidence loss.
