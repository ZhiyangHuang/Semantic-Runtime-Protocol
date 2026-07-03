# Experiment Task Plan

This task plan defines the next actions in the order most likely to finish the first paper within one semester.

## Phase 1: Structure Stabilization

1. Freeze canonical entrypoints.
2. Freeze canonical benchmark layer.
3. Freeze the main five-method comparison family.
4. Mark diagnostic tools as secondary.

## Phase 2: Evidence Hygiene

1. Keep formal evidence namespace separate from smoke/debug outputs.
2. Preserve partial-run crash records and repeat metadata.
3. Keep paper-facing tables and figures under stable paths.

## Phase 3: Main Experimental Execution

1. run smoke slices
2. run formal single-repeat slices
3. run repeated formal slices
4. aggregate mean/std/count
5. generate long-horizon report

## Phase 4: Paper Binding

1. bind figures to Results text
2. bind tables to Results text
3. bind benchmark and baseline definitions to Methods
4. bind freeze evidence to submission audit

## Phase 5: Submission Freeze

1. compile pass
2. artifact pass
3. reviewer-facing inspection pass
4. reproducibility pass
5. final package generation

## Stop Doing

- adding new baselines without changing the paper claim
- adding new benchmark families before the current paper is locked
- treating every script as a primary entrypoint
- letting smoke/debug outputs sit beside formal evidence without labeling
