# SRP External Validation Plan V1

This document freezes the external-validation boundary for SRP.
It is a planning artifact, not an experiment result, not a runtime policy, and not a new mechanism design.

## 1. Objective

Validate SRP against established public workloads and strong baselines so the paper can measure external validity rather than only internal consistency.

The key question is not whether SRP works inside the frozen SRP prototype.
The key question is:

> Does SRP preserve its governance advantage and structure-preserving recovery behavior on public workloads compared with established memory and retrieval baselines?

## 2. Frozen SRP Core

Keep the SRP governance stack fixed:

```text
observe
validate
optimize
verify
recover
recommend
govern
execute
```

Do not introduce:

- a new recovery algorithm
- a new optimizer
- a new authority layer
- an RL controller
- a new benchmark-specific theory branch

The external-validation stage only varies the workload family, baseline family, and evaluation framing.

## 3. Validation Tracks

External validation is split into three tracks.

### 3.1 Public benchmark validation

Test SRP on community-recognized workloads that expose retention, recovery, consistency, and drift.

Frozen benchmark family set:

1. LoCoMo for long-term conversational memory
2. LongMemEval for agent memory and temporal update handling
3. TGB 2.0 for knowledge evolution and relation update structure

These benchmarks were chosen because they cover distinct external-validity questions without collapsing SRP into a single retrieval or QA benchmark.

### 3.2 Strong baseline comparison

Compare SRP against a compact set of representative memory strategies under comparable semantic budgets.

The baseline family is frozen in four layers:

- Tier 0: context upper bounds
- Tier 1: retrieval-first memory
- Tier 2: structured memory
- Tier 3: agent memory systems

### 3.3 Failure analysis

Record when and why SRP fails so the paper boundary is explicit and reproducible.

### 3.4 Baseline freeze

The paper-level baseline matrix is frozen as:

- Full context
- Sliding window
- Summarization memory
- Vector retrieval / RAG-style memory
- Graph or structured memory
- SRP

The tiered system-baseline layer is frozen as:

- MemGPT / Letta
- Mem0
- Graphiti
- MemMachine, when benchmark format and runtime constraints make it meaningful

The baselines are grouped as follows:

#### Tier 0: Context upper bounds

- Full context
- Sliding window

#### Tier 1: Retrieval-first memory

- Summarization memory
- Vector retrieval / RAG-style memory

#### Tier 2: Structured memory

- Graph or structured memory
- Mem0
- Graphiti

#### Tier 3: Agent memory systems

- MemGPT / Letta
- MemMachine, when benchmark format and runtime constraints make it meaningful

Per benchmark, the active subset may be reduced only when a baseline is not meaningful for the benchmark format.
The benchmark-specific subset should still preserve the same conceptual ordering between ungoverned memory and governed recovery.

## 4. Benchmark Selection Criteria

Prefer benchmarks that expose at least one of the following:

- long-horizon retention
- temporal update handling
- relation preservation
- drift under repeated access
- partial recovery under budget constraints

Benchmark selection should prioritize tasks where semantic state changes can be evaluated, not only answer accuracy.

## 5. Baseline Matrix

Use a small but representative baseline set.

### Baseline 1: Full context

Represents the upper-bound memory access baseline.

### Baseline 2: Sliding window

Represents standard context truncation behavior.

### Baseline 3: Summarization memory

Represents compression-based memory maintenance.

### Baseline 4: Vector retrieval / RAG-style memory

Represents retrieval-first memory without governance-first structure reconstruction.

### Baseline 5: Graph or structured memory

Represents relation-aware retrieval without SRP governance separation.

### Baseline 6: SRP

Represents the governed semantic evolution baseline.

The comparison should emphasize same or comparable semantic budgets whenever possible.

### Tier 2: Strong memory systems

These baselines are included to test SRP against current state-of-practice memory systems rather than only classic memory strategies.

- MemGPT / Letta
- Mem0
- Graphiti
- MemMachine, when feasible

## 6. Evaluation Goals

External validation should measure whether the following remain meaningful on public workloads:

- semantic coverage
- semantic drift
- fact accuracy
- relation accuracy
- closure accuracy
- neighborhood completeness
- hallucinated relation rate
- evidence cost
- recommendation stability where applicable

The core goal is not to maximize a single score.
The core goal is to test whether SRP preserves its relative advantage as a governed semantic evolution framework.

## 7. Failure Analysis

Record failure cases in a structured way.

Suggested categories:

- parser failure
- representation failure
- relation failure
- evidence failure
- cost failure
- domain mismatch
- long-chain dependency failure

Failure analysis is not optional.
It is the mechanism that keeps the paper claim boundary honest.

## 8. Reproducibility Package

External validation should be accompanied by:

- config files for each benchmark and baseline
- exact run commands
- fixed seeds where possible
- result exports
- a short reproduction guide
- an artifact bundle summary

## 9. Non-Goals

Do not treat this stage as:

- a new theory phase
- a benchmark-wins-all claim
- a runtime authority update policy
- an RL proposal study
- a universal memory claim

Do not change:

- the governance stack
- the recovery hierarchy
- the representation invariance boundary
- the implementation independence boundary
- the authority separation rules

## 10. Relation to the Paper

External validation extends the evidence chain after Phase VIII:

- Phase VIII-A: workload generality
- Phase VIII-B: representation invariance
- Phase VIII-C: implementation independence
- External Validation: public workload comparison, strong baselines, failure analysis, and reproducibility

This stage is meant to move SRP from internal validity to externally verifiable evidence.
