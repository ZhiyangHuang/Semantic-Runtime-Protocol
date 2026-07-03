# Experiment Stage Freeze

This document defines what is frozen for the current first-paper stage.

## Frozen For The Current Paper

### 1. Public Benchmark Layer

- `LongBench v2`
- frozen imported sample count: `300`
- grouped execution slices of `100 + 100 + 100`

### 2. Main Comparison Family

- `raw_prompt`
- `summarization`
- `rag`
- `srp`
- `rag_srp_v2`

### 3. Main Evaluation Regime

- shared token-bounded execution regime
- shared query rotation
- shared repeat aggregation
- shared long-horizon reporting format

### 4. Canonical Outputs

- `results/batch_runs/`
- `results/paper_figure_pack/`
- `results/paper_figure_core_local/`
- `results/long_horizon_report/`

## Not Frozen Yet

- exact model list for cross-model replication
- exact repeat count used for the final reported table
- whether the final paper shows 100 only, 1000 only, or both
- whether exploratory hybrids remain appendix-only

## Allowed Changes

- bug fixes that improve reproducibility
- crash-safe logging improvements
- clearer namespace separation
- launcher usability improvements
- baseline wording corrections that make Methods more honest

## Not Allowed Without Explicit Re-baselining

- changing the benchmark family
- changing the main five comparison methods
- changing the shared token-budget framing
- silently mixing smoke outputs with formal evidence

## Freeze Rule

If a change would force the paper to reinterpret all major figures, it should be treated as a re-baselining decision, not as a routine refactor.
