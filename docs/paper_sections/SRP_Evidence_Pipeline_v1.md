# SRP Evidence Pipeline v1.0

This note defines the evidence pipeline that turns SRP runs into paper-facing artifacts.

The point of the pipeline is to move the project from:

- "we ran experiments"

to:

- "here is the full execution history behind each claim"

## Why This Layer Exists

The first SRP paper already has multiple qualified evidence sources:

- qualification-gated runs
- runtime equivalence traces
- formal batch summaries
- figures
- tables

What the paper still needs is a stable pipeline that turns those sources into a single reviewer-friendly evidence package.

This pipeline is the bridge between the runtime trace layer and the submission package.

## Pipeline Components

### 1. Trace Writer

The trace writer is the run-level logging layer.

It should preserve:

- per-cycle state transitions
- validation outcomes
- commit / rollback decisions
- usage statistics
- evaluation query outcomes

The existing `results.json` files already function as the detailed execution record. The trace writer formalizes that role and keeps it paper-facing.

### 2. Results Reducer

The reducer collapses run-level traces into method-level and batch-level summaries.

Its output should support:

- mean drift
- mean task success
- mean query success
- mean tokens
- mean latency
- commit rate
- validation drift

This is the layer that powers the paper tables.

### 3. Benchmark Aggregator

The benchmark aggregator groups evidence by:

- benchmark family
- method
- cycle depth
- model/backend

This is the layer that lets the paper compare public benchmarks, toy protocol-validation tasks, and formal batch evidence under one reporting structure.

### 4. Figure Generator Schema

The figure generator should consume the reducer output and the trace layer to build:

- drift vs cycles
- token cost versus drift Pareto frontier
- contract stability

The figure layer should not reconstruct results by hand. It should read the trace and reducer outputs directly.

### 5. Reviewer-Ready Logging Format

The logging format should expose:

- state in
- state out
- validation
- decision
- usage
- query outcome

If a reviewer asks whether state transitions can be inspected, the answer should be yes without additional code changes.

## Canonical Evidence Flow

```text
run_experiment / run_qualified_experiment
    -> per-cycle results.json
    -> execution trace log
    -> results reducer
    -> batch summary
    -> figure generator
    -> tables and camera-ready outputs
    -> manifest
```

## Relationship To Benchmarks

The evidence pipeline does not replace benchmark selection. It sits above benchmark selection.

That means:

- benchmark adapter selects the input space
- evidence pipeline preserves the output space
- SRP runtime executes the state transitions in between

## Relationship To The First Paper

For the first paper, the pipeline is especially important because it gives the submission a visible audit boundary.

The paper should be able to say:

> we did not just run a model; we preserved the full execution history behind each qualified result

That claim is stronger than "we ran experiments" and more concrete than a purely narrative methods section.

## Recommended Output Contract

The pipeline should ultimately emit:

- `execution_trace_log.json`
- `execution_trace_table.json`
- `batch_summary_table.json`
- `paper_table.md` / `.tex`
- `quality_table.md` / `.tex`
- `efficiency_table.md` / `.tex`
- `guardrail_table.md` / `.tex`
- `camera_ready_table.md` / `.tex`
- `main_3panel_figure.png`
- a single manifest tying the artifacts together

## Implementation Rule

The pipeline should preserve the current experiment logic and wrap it, not replace it.

That keeps the first paper safe:

- the protocol stays the same
- the evidence layer becomes stronger
- the submission package becomes easier to inspect

## Next Step

The next step is to keep the pipeline runnable as a single command and to use it as the only path to paper-facing artifacts.
