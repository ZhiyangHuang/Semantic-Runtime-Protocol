# Temporary 2: Data Cleanup Guardrail

This file exists to prevent two failure modes during data-layer cleanup:

1. cleaning too little, leaving duplicated data namespaces and confused task sources
2. cleaning too aggressively, losing formal evidence, benchmark provenance, or reproducibility metadata

It is a temporary execution guardrail, not a paper-facing document.

## Scope Of This Cleanup

This cleanup targets the data-facing experiment layer:

- `srp_experiment/data/`
- `srp_experiment/results/`
- batch manifests
- benchmark task partitions
- repeated summary outputs

It does **not** authorize uncontrolled deletion of:

- formal evidence
- LongBench import provenance
- submission artifacts
- qualification reports
- runtime equivalence records

## Current Canonical Data Split

### Protocol Validation Layer

Keep as canonical:

- `srp_experiment/data/task_a.json`
- `srp_experiment/data/task_b.json`
- `srp_experiment/data/task_c.json`

Role:

- toy protocol validation
- SRP semantic validation debugging
- bounded internal sanity checks

### Public Benchmark Evidence Layer

Keep as canonical:

- `srp_experiment/data/longbench_v2/tasks.json`
- `srp_experiment/data/longbench_v2/manifest.json`

Role:

- frozen public benchmark evidence
- reusable external evaluation space

### Execution Partition Layer

Keep as canonical execution partitions:

- `srp_experiment/data/longbench_v2/tasks_group_1.json`
- `srp_experiment/data/longbench_v2/tasks_group_2.json`
- `srp_experiment/data/longbench_v2/tasks_group_3.json`

Role:

- launcher-friendly batching
- 100-task staged runs

### Adapter Layer

Keep as canonical:

- `srp_experiment/data/longbench_v2/import_longbench_v2.py`
- `srp_experiment/data/longbench_v2/split_task_groups.py`

Role:

- external benchmark normalization
- deterministic group generation

## Current Canonical Results Split

### Formal Evidence Layer

Keep in primary namespace:

- `srp_experiment/results/batch_runs/`
- `srp_experiment/results/paper_figure_core_local/`
- `srp_experiment/results/paper_figure_pack/`
- `srp_experiment/results/long_horizon_report/`
- `srp_experiment/results/submission_audit/`
- top-level formal summary tables

### Preserved But Non-Primary Layer

Keep preserved, but demoted:

- `srp_experiment/results/archive/`
- risk-test summaries
- runtime equivalence traces
- protocol behavior traces
- debug artifacts

These are valuable, but they are not the cleanest paper-facing namespace.

## Cleanup Rules

### Rule 1

If two files serve the same paper-facing role, keep one as canonical and demote the other through:

- archive
- index demotion
- explicit labeling

Do not silently keep both as if they are equally primary.

### Rule 2

Do not delete provenance-bearing files without preserving:

- source benchmark
- selection strategy
- imported count
- grouping rule
- output namespace

### Rule 3

Do not move formal evidence into archive unless a replacement primary location is already indexed.

### Rule 4

Do not treat wrapper-generated configs as canonical semester configs.

Generated launcher configs belong to:

- `srp_experiment/configs/generated/`

and should remain session artifacts only.

## What Is Still Safe To Simplify Later

The following can still be simplified later without harming the paper, as long as indexes remain accurate:

- duplicated summary exports
- stale risk-test markdown/csv/json triplets
- repeated runtime equivalence snapshots after one canonical preserved chain is selected
- launcher session clutter inside `results/batch_runs/`

## Do-Not-Lose Checklist

Before any future cleanup of data/results, verify that these still exist:

- `srp_experiment/data/longbench_v2/manifest.json`
- `srp_experiment/data/longbench_v2/tasks.json`
- `srp_experiment/results/FORMAL_EVIDENCE_INDEX.md`
- `srp_experiment/results/batch_summary_table.json`
- `srp_experiment/results/paper_table.md`
- `srp_experiment/results/camera_ready_table.md`
- `srp_experiment/results/paper_figure_pack/main_3panel_figure.png`
- `first_paper/submission/submission_audit_report.json`

## Practical Cleanup Order

If another cleanup round is needed later, use this order:

1. relabel and index
2. archive and demote
3. verify provenance and evidence references
4. only then consider deletion of true duplicates

This file should stay short and operational. Its purpose is to keep cleanup reversible and evidence-safe.
