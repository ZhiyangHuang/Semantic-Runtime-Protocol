# Results

This directory stores experiment outputs, but not every subfolder has the same paper status.

## Primary Namespaces

- `batch_runs/` - canonical multi-run experiment namespace
- `paper_figure_core_local/` - current formal local paper evidence
- `paper_figure_pack/` - current paper-facing figure namespace
- `long_horizon_report/` - long-round analysis namespace

## Repeated-Family Resolution

- `RESULT_FAMILY_CANONICAL_MAP.md` identifies which top-level repeated files are canonical and which are preserved history.

## Preserved But Secondary

- `archive/smoke/` - protocol and qualification smoke evidence
- `archive/comparison/` - comparison or exploratory tables
- `archive/latency/` - latency-specific exploratory outputs
- `archive/debug/` - preserved debug outputs
- `archive/generated/` - generated config artifacts tied to older runs

## Accidental / Duplicate Paths

- `archive/duplicate_namespace/srp_experiment_results_snapshot/` is the preserved snapshot of the accidental duplicate namespace created by earlier path handling bugs

## Canonical Reduction Path

For paper-facing reporting, the preferred sequence is:

1. `batch_run.py`
2. `collect_batch_summary.py`
3. `repeat_aggregate.py`
4. `long_horizon_report.py`
5. paper table / figure generation

## Minimum Expected Files For A Single Formal Run

- `results.json`
- `summary.json`
- `run_metadata.json`

## Minimum Expected Files For A Crash-Safe Run

- `results.partial.json`
- `summary.partial.json`
- `crash_report.json`
