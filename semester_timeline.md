# Semester Timeline

## Purpose

One undergraduate semester. One short paper. One reproducible experiment.

## Current Stage

- [x] local backend pilot is real and runnable
- [x] public evaluation layer is frozen
- [x] main SRP line has moved to anchor-guided recovery
- [x] next stage is no longer scaffold building
- [ ] next stage is first-paper experiment execution

## Fixed Scope

- [ ] one main model only at the start
- [ ] cycle settings fixed to `3`, `5`, `7`
- [ ] main comparison fixed to raw prompt, summarization, retrieval, and SRP
- [ ] ablations fixed to structure, validation, and recovery
- [ ] failure block fixed to vocabulary corruption, validator failure, recovery collapse, and concept explosion

## Experiment Priority

### `P0` Must Run

- [ ] one `Long Context` benchmark
- [ ] one `Memory` benchmark
- [ ] four-method main comparison:
  - [ ] `raw_prompt`
  - [ ] `summarization`
  - [ ] `rag`
  - [ ] `srp`
- [ ] cycle settings fixed to:
  - [ ] `3`
  - [ ] `5`
  - [ ] `7`
- [ ] report these core metrics:
  - [ ] `drift`
  - [ ] `task_success`
  - [ ] `query_success`
  - [ ] `tokens`
  - [ ] `latency`

### `P1` Strongly Recommended

- [ ] repeated runs with:
  - [ ] `mean`
  - [ ] `std`
  - [ ] `95% CI`
- [ ] at least one SRP ablation:
  - [ ] no anchor
  - [ ] no validation
  - [ ] lighter vs heavier recovery
- [ ] retrieval diagnostics for the `rag` baseline:
  - [ ] `recall`
  - [ ] `precision`
  - [ ] optional `MRR`

### `P2` If Time Allows

- [ ] one small agent-style runtime case
- [ ] one small cross-model case
- [ ] explicit failure taxonomy with grouped examples

### Not Priority For Paper 1

- [ ] broad knowledge benchmarks
- [ ] GSM8K / MATH / GPQA style reasoning sweeps
- [ ] HumanEval / MBPP / SWE-bench style coding sweeps
- [ ] multi-model leaderboard framing

## Execution Rule

- [ ] keep the public evaluation layer fixed
- [ ] only change `srp/` during SRP tuning
- [ ] keep exploratory hybrids out of the paper main table
- [ ] use toy tasks for debugging, not as final benchmark evidence

## Week 1

- [ ] finalize the first-paper benchmark shortlist
- [ ] confirm `P0` metrics and reporting format
- [x] confirm one reproducible local command path
- [x] confirm output folder naming for paper runs
- [x] lock the first-paper batch config

## Week 2

- [ ] run the `P0` four-method comparison at `3`, `5`, `7`
- [ ] verify `results.json`, `summary.json`, and `run_metadata.json`
- [ ] record the first paper-facing drift plot
- [ ] record the first token and latency table

## Week 3

- [ ] repeat the `P0` runs for stability
- [ ] report `mean`, `std`, and `95% CI`
- [ ] keep prompt templates and configs fixed
- [ ] stabilize the main comparison table

## Week 4

- [ ] run SRP ablations
- [ ] compare anchor vs no anchor
- [ ] compare validation vs no validation
- [ ] compare lighter vs heavier recovery

## Week 5

- [ ] run `RAG` diagnostics
- [ ] measure retrieval `recall` and `precision`
- [ ] relate retrieval quality to drift and task preservation
- [ ] decide whether `MRR` is worth keeping

## Week 6

- [ ] run failure block
- [ ] collect failure examples
- [ ] decide which failures go into the paper

## Week 7

- [ ] draft introduction
- [ ] draft related work
- [ ] draft formalization
- [ ] draft experiment section
- [ ] draft limitations

## Week 8

- [ ] tighten claims
- [ ] simplify wording
- [ ] make figure captions publication-ready
- [ ] clean tables

## Week 9

- [ ] prepare professor-facing version
- [ ] prepare one-page pitch
- [ ] collect feedback notes

## Week 10

- [ ] cut unsupported claims
- [ ] finalize short paper draft
- [ ] finalize reproducible repo
- [ ] finalize figure/table package

## Hard Rule

- [ ] if the schedule slips, cut `P2` first
- [ ] then cut extra ablations
- [ ] then cut extra figures
- [ ] then cut extra theory
- [ ] never cut the `P0` four-method main comparison

## End Condition

- [ ] one credible short paper draft
- [ ] one clean experiment repo
- [ ] one main drift figure
- [ ] one token-efficiency table
- [ ] one faculty-reviewable research package
