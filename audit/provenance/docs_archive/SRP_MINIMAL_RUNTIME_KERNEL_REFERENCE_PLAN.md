# SRP Minimal Runtime Kernel Reference Plan

This document freezes the reference implementation boundary for SRP before code is written.
It is not a theory document and not a full architecture essay.

The central question is:

> What is the smallest standalone reference package that can execute the operational semantics defined by SRP?

The goal is to separate the experimental implementation from the reference model:

- `srp_experiment/srp/` remains the empirical and historical evidence layer.
- `srp_runtime/` is the future reference implementation boundary.

---

## 1. Purpose

The reference plan exists to define:

- package boundaries
- component ownership
- execution flow
- first milestone scope
- non-goals

The reference kernel should be:

- passive with respect to policy
- deterministic for valid inputs
- small enough to reason about directly
- independent of any one model, encoder, or storage backend

It should realize the operational semantics of SRP, not re-derive the theory.

---

## 2. Core Design Decisions

### 2.1 Kernel is passive, not predictive

The kernel should not decide what to do next.

It should only accept an externally produced event or primitive and then:

1. validate it
2. evaluate constraints and metric gates
3. execute the selected operator
4. commit the resulting state
5. record trace and replay evidence

The kernel does not own policy.

### 2.2 State ownership stays external to the kernel object

The first reference kernel should not become a monolithic state object.

Recommended shape:

```text
RuntimeKernel
  -> StateStore
  -> EventStore
  -> TraceStore
```

The kernel orchestrates transitions.
The stores own persistence and versioned references.

### 2.3 Evolution remains operator-driven

The first reference kernel should not embed full evolution strategy logic.

In particular, it should not contain hard-coded policy logic such as:

```text
if activation < threshold:
    forget()
```

Instead, evolution rules are supplied as context to operators and validators.

---

## 3. Reference Package Boundary

The intended reference package is:

```text
srp_runtime/
  kernel/
    runtime_kernel.py
    transition.py
    lifecycle.py
  event/
    event.py
    validator.py
  semantic/
    unit.py
    graph.py
    state.py
  operators/
    merge.py
    approximate.py
    recover.py
  constraints/
    engine.py
  metric/
    semantic_metric.py
  trace/
    builder.py
  replay/
    engine.py
```

Optional internal storage helpers may later be added under:

```text
srp_runtime/storage/
```

but storage is not required for the first milestone.

### 3.1 Kernel layer

The kernel layer owns:

- event submission
- validation orchestration
- transition application
- commit
- replay coordination
- query routing

### 3.2 Event layer

The event layer owns:

- runtime event identity
- schema versioning
- causal linkage
- mutation scope
- serialization and deserialization

### 3.3 Semantic layer

The semantic layer owns:

- semantic units
- semantic graphs
- semantic states
- version references
- history references

### 3.4 Operator layer

The operator layer owns:

- merge
- split
- approximation
- recovery
- pruning / GC

### 3.5 Constraint layer

The constraint layer owns:

- identity constraints
- structural constraints
- semantic constraints
- evolution constraints
- runtime constraints

### 3.6 Metric layer

The metric layer owns:

- semantic distance
- similarity scoring
- candidate ranking
- drift scoring support

### 3.7 Trace layer

The trace layer owns:

- trace nodes
- trace edges
- trace records
- causal explanation artifacts

### 3.8 Replay layer

The replay layer owns:

- deterministic reconstruction
- ordering
- divergence reporting
- replay drift measurement

---

## 4. Minimal Execution Flow

The reference model should follow this execution path:

```text
event
  -> validate
  -> constraint
  -> metric
  -> operator
  -> transition
  -> commit
  -> trace
```

Replay uses the same semantic foundations but runs in reconstruction mode:

```text
initial_state
  + event_stream
  -> replay
  -> reconstructed_state
```

The flow must preserve determinism for valid inputs.

---

## 5. Component Responsibility Matrix

| Component | Responsibility | Forbidden |
| --- | --- | --- |
| `RuntimeKernel` | Orchestrate submit, validate, execute, commit, query, replay | Decide policy, generate embeddings, infer semantic intent |
| `RuntimeEvent` | Describe a transition and its causal metadata | Execute mutation directly |
| `ConstraintEngine` | Check legality and invariant satisfaction | Rank candidates by policy objective |
| `SemanticMetric` | Score similarity and distance | Commit mutations |
| `OperatorExecutor` | Apply the selected graph/state transformation | Choose policy on its own |
| `TraceBuilder` | Build causal explanation artifacts | Mutate state |
| `ReplayEngine` | Reconstruct state deterministically | Re-sample semantics or change history |
| `SemanticUnit` | Hold atomic semantic identity and payload | Own the entire runtime |
| `SemanticGraph` | Represent structural relations between units | Encode policy decisions |
| `SemanticState` | Hold the current versioned semantic runtime state | Serve as the kernel itself |

---

## 6. Non-goals

The reference kernel is not responsible for:

- LLM inference
- embedding generation
- retrieval strategy design
- graph database integration
- policy learning
- autonomous evolution strategy search
- benchmark orchestration
- experimental ablation management

These may appear in the broader project, but they are not part of the first reference package.

---

## 7. First Milestone

The first reference milestone should implement only the minimum protocol-bearing surface:

- `RuntimeEvent`
- `SemanticUnit`
- `SemanticGraph`
- `SemanticState`
- `ConstraintEngine`
- `RuntimeKernel.submit_event()`
- `RuntimeKernel.validate_event()`
- `RuntimeKernel.apply_event()`
- `ReplayEngine`
- `TraceBuilder`

This milestone should not require a complete evolution engine.

The first implementation goal is:

> A valid event can be submitted, checked, applied, recorded, replayed, and explained.

---

## 8. Validation Plan

The first reference implementation should be validated by protocol tests, not only by end-task metrics.

### 8.1 Event replay equality

The same initial state and event stream should produce the same reconstructed state.

### 8.2 Deterministic transition

For valid inputs, repeated application should produce equivalent resulting states.

### 8.3 Constraint rejection

Illegal transitions should be rejected before mutation.

### 8.4 Trace consistency

Each committed transition should produce a trace artifact that explains the causal path.

### 8.5 Boundary isolation

Policy decisions must not directly mutate semantic state.

---

## 9. Migration Relationship

The reference package should be introduced without breaking the experimental implementation.

Recommended relation:

```text
srp_experiment/srp/
  -> empirical evidence and current pipeline behavior

srp_runtime/
  -> reference protocol implementation
```

The two layers should coexist.

The experimental package remains useful for measurement, while the reference package becomes the platform-independent executable model.

---

## 10. Future Direction

If the reference primitives stabilize, they may later be formalized as a Semantic Runtime Instruction Set.

That future direction is intentionally not required now.

The current objective is narrower:

> Freeze the smallest reference model that can execute SRP operational semantics without absorbing policy or experimental baggage.

