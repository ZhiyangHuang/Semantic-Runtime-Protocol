# SRP External Validation Implementation Plan V1

This document freezes the external-validation implementation contract for SRP.
It is a planning artifact, not an experiment result, not a runtime policy, and not a new mechanism design.

## 1. Objective

Translate the frozen external-validation boundary into an implementation contract that can be executed without reopening the theory boundary.

The question is not whether SRP can be made to run on public workloads.
The question is:

> Can public benchmarks, baselines, and evaluation metrics be adapted into a stable SRP-facing contract without changing SRP's governance semantics?

## 2. Frozen Implementation Boundary

Keep the following fixed:

- the SRP governance stack
- the recovery hierarchy
- the benchmark family set
- the baseline matrix
- the evaluation goals
- the failure categories
- the reproducibility requirements

Do not introduce:

- benchmark-specific SRP logic
- benchmark-specific theory branches
- new recovery algorithms
- new optimizer layers
- new authority layers
- RL controllers

## 3. Benchmark Adapter Layer

All public benchmarks must pass through a semantic adapter layer before they enter SRP.

Adapter flow:

```text
benchmark format
    |
    v
semantic adapter
    |
    v
SRP state representation
    |
    v
recovery and governance evaluation
```

The adapter layer exists to keep benchmark-specific formats from leaking into SRP internals.
The adapter should preserve the minimum semantic structure needed for recovery, evaluation, and failure analysis.

Benchmark adapters may differ in extraction details, but they should produce the same SRP-facing semantic contract:

- semantic units
- relations
- temporal updates
- evidence pointers where available
- benchmark task metadata

## 4. Baseline Adapter Layer

All baselines must implement a shared memory interface so comparison stays fair.

Reference interface:

```python
class MemoryBaseline:
    def ingest(history):
        pass

    def retrieve(query):
        pass

    def reconstruct():
        pass
```

Concrete baseline families:

- FullContextMemory
- SlidingWindowMemory
- SummaryMemory
- VectorMemory
- GraphMemory
- SRPMemory

The adapter layer must keep the same benchmark inputs and the same evaluation outputs visible across all baseline families.

### 4.1 Baseline capability matrix

The baseline capability contract is frozen in [SRP External Validation Baseline Capability Matrix V1](SRP_EXTERNAL_VALIDATION_BASELINE_CAPABILITY_MATRIX_V1.md).

The matrix is used to document which capabilities are core, partial, implicit, or absent for each baseline family before the benchmark results are interpreted.
It is not a ranking table and it is not an optimization target.

## 5. Runtime Contract

The external-validation pipeline is split into two non-overlapping layers:

### 5.1 Calibration layer

```text
benchmark data
    |
    v
adapter
    |
    v
SemanticState
    |
    v
diagnostic evaluator
```

The calibration layer does not depend on a generation endpoint.
It exists to validate adapter correctness, semantic translation, and failure attribution before evidence promotion.

### 5.2 Evidence run layer

```text
benchmark data
    |
    v
adapter
    |
    v
MemorySystem
    |
    v
shared LLM generation
    |
    v
official metric + SRP diagnostics
```

All evidence runs must use the same generation backend across baselines and SRP.
The runtime contract for the shared backend is frozen as:

```yaml
model_environment:
  provider: local_vllm
  endpoint: http://172.25.253.78:8000
  model: Qwen/Qwen3-4B-AWQ

runtime_policy:
  same_endpoint_across_baselines: true
  baseline_generation_backend: shared
  srp_generation_backend: shared
```

Each evidence run must emit a `runtime_manifest.json` that records the model environment, the shared generation policy, the benchmark name, the seed set, and the frozen baseline set.
This manifest is part of the evidence bundle and is not optional.

## 5. Evaluation Protocol

Each benchmark should be evaluated with the same reporting structure whenever possible:

- 3 random seeds
- mean and standard deviation
- 95% confidence interval where applicable
- official benchmark metric(s)
- SRP analysis metrics

### Official benchmark metrics

Use the benchmark's own community-recognized metrics when they exist.

### SRP analysis metrics

Use the SRP mechanism-level metrics to explain why benchmark performance differs:

- semantic coverage
- semantic drift
- fact accuracy
- relation accuracy
- closure accuracy
- neighborhood completeness
- hallucinated relation rate
- evidence cost
- recommendation stability where applicable

The official benchmark metrics measure task performance.
The SRP analysis metrics measure mechanism behavior.

## 6. Benchmark-Specific Framing

### 6.1 LoCoMo

Use LoCoMo as a long-term conversational memory workload.
It should test retention, multi-session memory, factual consistency, and drift.

### 6.2 LongMemEval

Use LongMemEval as a long-term interactive memory workload.
It should test information extraction, multi-session reasoning, temporal reasoning, knowledge updates, and abstention.

### 6.3 TGB 2.0

Use TGB 2.0 as a structured temporal evolution workload.
It should test relation preservation, temporal update handling, and recovery behavior under temporal relational change.
It should not be framed as a link-prediction leaderboard target for SRP.

## 7. Vertical Slice Order

Implement and validate the benchmark pipeline in a narrow order:

1. LoCoMo vertical slice
2. LongMemEval vertical slice
3. TGB 2.0 vertical slice

For the first slice, keep the baseline set minimal if needed so the adapter contract can be validated before broadening the matrix.

## 8. Failure and Artifact Requirements

Each benchmark run should emit:

- raw benchmark inputs or references
- SRP-adapted semantic state
- baseline inputs and outputs
- metric exports
- failure summaries
- reproduction metadata

Failure cases should be grouped by the frozen analysis categories:

- parser failure
- representation failure
- relation failure
- evidence failure
- cost failure
- domain mismatch
- long-chain dependency failure

## 9. Non-Goals

Do not treat this stage as:

- a new theory phase
- a benchmark-specific SRP redesign
- a retrieval-only benchmark study
- a universal memory claim
- an RL proposal study

Do not change:

- the governance stack
- the recovery hierarchy
- the representation invariance boundary
- the implementation independence boundary
- the authority separation rules

## 10. Relation to the Paper

This implementation plan turns the frozen external-validation boundary into an executable protocol.

It extends the evidence chain after Phase VIII:

- Phase VIII-A: workload generality
- Phase VIII-B: representation invariance
- Phase VIII-C: implementation independence
- External Validation: public benchmark comparison, strong baselines, failure analysis, and reproducibility

This stage is meant to move SRP from external-validity intent to external-validity execution.
