# SRP Execution Trace Format

This note defines the execution trace and logging standard for SRP.

The purpose is simple:

> if a reviewer asks "can I inspect state transitions?", the repo should have a direct answer.

The execution trace is the bridge between the runtime protocol and the paper evidence. It makes state transitions inspectable, reproducible, and easy to visualize.

## Why This Layer Exists

SRP is not only a benchmarked system. It is a runtime abstraction with explicit state transitions. That means the paper should expose not just final outputs, but the path from one state to the next.

Without a trace layer:

- the runtime looks opaque
- state transitions are hard to inspect
- commit / rollback decisions are difficult to audit
- figures become detached from execution behavior

With a trace layer:

- each cycle becomes visible
- each transition is reproducible
- each decision can be explained
- the paper can support a reviewer-friendly "state evolution" figure

## Design Goal

The trace format should capture:

- what state entered the cycle
- what transformation produced the compressed state
- what state was recovered
- how validation scored the recovered state
- whether the state committed or rolled back
- how much drift, alignment, and contract satisfaction were observed

The trace should be compact enough for logging and rich enough for debugging and figures.

## Core Principle

The trace should record runtime behavior, not just task outputs.

That means the trace must make the following visible:

- state in
- state out
- compression package
- recovery package
- validation outcome
- commit decision
- cycle-level metrics

## Canonical Trace Object

Each cycle should emit one trace object.

```json
{
  "task_id": "iterative_cycles",
  "method": "srp",
  "cycle": 3,
  "runtime": {
    "input_state": {},
    "compressed_state": {},
    "recovered_state": {},
    "updated_state": {}
  },
  "validation": {
    "validation_score": 0.81,
    "contract_satisfaction": 0.81,
    "passed": true,
    "drift": 0.0,
    "drift_risk": "low",
    "drift_blocks_commit": false,
    "coverage": 1.0,
    "alignment": 1.0,
    "leakage_detected": false
  },
  "decision": {
    "state_committed": true,
    "commit_reason": "contract satisfied and drift within budget",
    "rollback_reason": null
  },
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0,
    "latency_seconds": 0.0
  },
  "evaluation": {
    "evaluation_query": "...",
    "query_answer": "...",
    "query_success": 1.0,
    "judge_score": 1.0
  },
  "notes": "semantic runtime protocol"
}
```

## Trace Fields

### Identity

- `task_id`
- `method`
- `cycle`

These identify the experiment unit.

### Runtime State

- `input_state`
- `compressed_state`
- `recovered_state`
- `updated_state`

These are the core protocol objects.

### Validation

- `validation_score`
- `contract_satisfaction`
- `passed`
- `drift`
- `drift_risk`
- `drift_blocks_commit`
- `coverage`
- `alignment`
- `leakage_detected`

These explain why the runtime committed or rolled back.

### Decision

- `state_committed`
- `commit_reason`
- `rollback_reason`

These are the protocol outcome fields.

### Usage

- `prompt_tokens`
- `completion_tokens`
- `total_tokens`
- `latency_seconds`

These support efficiency analysis and runtime cost plots.

### Evaluation

- `evaluation_query`
- `query_answer`
- `query_success`
- `judge_score`

These tie runtime behavior to the external task protocol.

## Logging Standard

The repository should log execution traces at three levels:

### 1. Per-cycle trace

One trace object per cycle, stored in the detailed results file.

### 2. Per-task trace summary

A task-level summary that aggregates cycle traces into:

- mean drift
- mean task success
- mean query success
- mean token cost
- commit rate
- rollback rate

### 3. Batch-level summary

A batch-level report that compares methods across tasks and cycle depths.

## Visualization Standard

The trace format should support three paper-facing visualizations:

- drift vs cycles
- token cost versus drift Pareto frontier
- contract stability / commit behavior across cycles

The figure layer should be generated directly from trace-derived summaries, not manually reconstructed from notes.

## What Reviewers Should Be Able To Inspect

The trace should make it possible to answer:

- what state was compressed
- what state was recovered
- why the state was accepted or rejected
- how contract satisfaction changed over cycles
- where the first divergence appeared

If the answer to these questions requires reading the entire codebase, the trace format is too weak.

## Relationship To The Current Repo

The current experiment results already expose much of this information, but the execution trace standard makes the structure explicit and paper-facing.

The trace layer should sit between:

- the SRP runtime implementation
- the qualification gate
- the paper figures and tables

## Recommended Next Implementation Step

If this trace format is adopted, the next implementation step is:

1. formalize the trace object in code
2. emit trace files per task and per cycle
3. generate the main figure directly from trace summaries
4. preserve the trace files as qualified evidence

This gives the first paper a strong audit layer without expanding the protocol itself.
