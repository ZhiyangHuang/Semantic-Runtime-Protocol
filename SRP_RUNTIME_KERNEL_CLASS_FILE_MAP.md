# SRP Runtime Kernel Class File Map

This document freezes the reference implementation dependency graph for Milestone 1.
It maps the interface spec to Python module ownership before any package skeleton is generated.

The goal is to prevent accidental circular dependencies and keep the reference implementation small and deterministic.

---

## 1. Package Boundary

The intended reference package layout is:

```text
srp_runtime/
  semantic/
    unit.py
    graph.py
    state.py
  event/
    runtime_event.py
  constraints/
    constraint_engine.py
  operators/
    base.py
    identity.py
    activation.py
    relation.py
    merge.py
    approximation.py
    split.py
    recovery.py
    forgetting.py
    garbage_collection.py
  metric/
    semantic_metric.py
  kernel/
    runtime_kernel.py
    transition.py
    commit.py
  trace/
    trace_builder.py
  replay/
    replay_engine.py
  tests/
    test_event.py
    test_kernel.py
    test_replay.py
    test_trace.py
```

This layout is the first-reference target. It is not a commitment to later expansion.

---

## 2. Dependency Direction

The dependency flow should be one-way and should not cycle back into policy or experiment code.

Recommended logical dependency chain:

```text
Semantic Objects
  -> RuntimeEvent
  -> ConstraintEngine
  -> SemanticMetric
  -> Operators
  -> RuntimeKernel
  -> TraceBuilder
  -> ReplayEngine
```

Supporting references:

```text
SemanticState
  -> SemanticGraph
  -> SemanticUnit
```

The important rule is:

- lower-level modules may be imported by higher-level orchestration modules
- higher-level orchestration modules should not be imported back into lower-level semantic objects

---

## 3. Module Ownership

### 3.1 `semantic/unit.py`

Owns:

- `SemanticUnit`

Responsibilities:

- atomic semantic object representation
- identity and payload storage
- runtime-facing mutable fields

Forbidden:

- event handling
- operator execution
- graph mutation logic

---

### 3.2 `semantic/graph.py`

Owns:

- `SemanticGraph`
- relation storage helpers

Responsibilities:

- node lookup
- edge lookup
- neighborhood query
- relation adjacency management

Forbidden:

- implicit merge decisions
- recovery logic
- garbage collection policy
- embedding generation

---

### 3.3 `semantic/state.py`

Owns:

- `SemanticState`
- `SemanticStateView`

Responsibilities:

- current semantic runtime container
- version reference
- timestamp round tracking

Forbidden:

- direct transition logic
- policy selection
- event creation

---

### 3.4 `event/runtime_event.py`

Owns:

- `RuntimeEvent`
- `EventResult`

Responsibilities:

- event identity
- schema versioning
- causal references
- mutation mode description
- serialization-friendly event shape

Forbidden:

- event execution
- state mutation
- kernel orchestration

---

### 3.5 `constraints/constraint_engine.py`

Owns:

- `ConstraintEngine`
- `ConstraintResult`

Responsibilities:

- legality checks
- identity constraints
- structural constraints
- semantic constraints
- runtime invariant checks

Forbidden:

- policy ranking
- state mutation
- trace recording

---

### 3.6 `metric/semantic_metric.py`

Owns:

- `SemanticMetric`

Responsibilities:

- distance computation
- similarity computation
- candidate ranking support
- drift support

Forbidden:

- mutation
- policy decisions
- trace creation

---

### 3.7 `operators/base.py`

Owns:

- `SemanticOperator`

Responsibilities:

- operator interface definition
- apply contract

Forbidden:

- direct persistence
- policy derivation
- replay control

---

### 3.8 `operators/identity.py`

Owns:

- `IdentityUpdateOperator`

Responsibilities:

- controlled identity field updates

---

### 3.9 `operators/activation.py`

Owns:

- `ActivationUpdateOperator`

Responsibilities:

- controlled activation updates

---

### 3.10 `operators/relation.py`

Owns:

- `RelationUpdateOperator`

Responsibilities:

- controlled relation updates

---

### 3.11 `operators/merge.py`

Owns:

- `MergeOperator`

Responsibilities:

- constrained semantic merge
- lineage-preserving unit consolidation

---

### 3.12 `operators/approximation.py`

Owns:

- `ApproximationOperator`

Responsibilities:

- activation-guided semantic approximation
- approximation loss tracking

---

### 3.13 `operators/split.py`

Owns:

- `SplitOperator`

Responsibilities:

- lineage-preserving split of semantic units
- controlled restoration of semantic branches

---

### 3.14 `operators/recovery.py`

Owns:

- `RecoveryOperator`

Responsibilities:

- evidence-based semantic restoration
- recoverable state reconstitution

---

### 3.15 `operators/forgetting.py`

Owns:

- `ForgettingOperator`

Responsibilities:

- active representation reduction
- evidence-preserving forgetting
- relation archival for recoverability

---

### 3.16 `operators/garbage_collection.py`

Owns:

- `GarbageCollectionOperator`

Responsibilities:

- terminal semantic removal
- archive compaction
- irreversible storage release

---

### 3.17 `kernel/runtime_kernel.py`

Owns:

- `RuntimeKernel`

Responsibilities:

- submit event
- validate event
- apply event
- commit transition
- query state
- coordinate trace recording

Forbidden:

- policy learning
- embedding generation
- direct experiment orchestration

---

### 3.18 `kernel/transition.py`

Owns:

- `TransitionResult`
- transition helpers

Responsibilities:

- state transition bookkeeping
- before/after version references

---

### 3.19 `kernel/commit.py`

Owns:

- commit helpers

Responsibilities:

- version update
- commit record assembly

---

### 3.20 `trace/trace_builder.py`

Owns:

- `TraceBuilder`
- `TraceRecord`

Responsibilities:

- causal explanation artifact assembly
- event/version linkage

Forbidden:

- state mutation
- event generation

---

### 3.21 `replay/replay_engine.py`

Owns:

- `ReplayEngine`
- `ReplayResult`

Responsibilities:

- deterministic reconstruction
- divergence detection
- replay drift reporting

Forbidden:

- resampling semantics
- hidden mutation
- policy changes

---

## 4. Class Relationship Sketch

The class graph should remain simple:

```text
RuntimeEvent
    |
    v
ConstraintEngine
    |
    v
SemanticMetric
    |
    v
SemanticOperator
    |
    v
RuntimeKernel
    |
    +----------------+
    |                |
    v                v
TraceBuilder      ReplayEngine
```

Semantic data flows upward through the kernel, but semantic objects should remain isolated from orchestration code.

---

## 5. Forbidden Dependencies

The first reference implementation must not introduce these dependencies:

- `kernel -> policy`
- `kernel -> LLM`
- `kernel -> embedding model`
- `kernel -> database`
- `semantic -> kernel`
- `event -> operator implementation`
- `trace -> state mutation`
- `replay -> policy`

These restrictions preserve a clean reference boundary.

---

## 6. First Milestone File Order

Recommended file creation order:

1. `srp_runtime/semantic/unit.py`
2. `srp_runtime/semantic/graph.py`
3. `srp_runtime/semantic/state.py`
4. `srp_runtime/event/runtime_event.py`
5. `srp_runtime/constraints/constraint_engine.py`
6. `srp_runtime/metric/semantic_metric.py`
7. `srp_runtime/operators/base.py`
8. `srp_runtime/operators/identity.py`
9. `srp_runtime/operators/activation.py`
10. `srp_runtime/operators/relation.py`
11. `srp_runtime/operators/merge.py`
12. `srp_runtime/operators/approximation.py`
13. `srp_runtime/operators/split.py`
14. `srp_runtime/operators/recovery.py`
15. `srp_runtime/operators/forgetting.py`
16. `srp_runtime/operators/garbage_collection.py`
17. `srp_runtime/kernel/transition.py`
18. `srp_runtime/kernel/commit.py`
19. `srp_runtime/kernel/runtime_kernel.py`
20. `srp_runtime/trace/trace_builder.py`
21. `srp_runtime/replay/replay_engine.py`

This order avoids circular imports and makes the interface dependency graph explicit.

---

## 7. Relation to Milestone 1 Interface Spec

This document is the file-and-class dependency companion to:

- [SRP Runtime Kernel Milestone 1 Interface Spec](SRP_RUNTIME_KERNEL_MILESTONE_1_INTERFACE_SPEC.md)

Use the interface spec to define the public contract.
Use this file map to define module ownership and import direction.
