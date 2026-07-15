# SRP Semantic Time Model

This document defines semantic time in SRP.
It is not a physical clock model and not a scheduling spec.

The central question is:

> How does SRP measure age, recency, drift, version depth, and recovery distance in a way that is meaningful for semantic evolution?

This layer sits between runtime semantics and minimal runtime execution.

---

## 1. Why Semantic Time

SRP uses many time-like quantities:

- round
- last_used
- activation decay
- history length
- version depth
- recovery distance
- drift accumulation

These quantities are not always the same as physical time.

Semantic time describes how the meaning-bearing state ages, not how many seconds passed.

---

## 2. Semantic Time Coordinates

For a semantic unit `U`, semantic time may be represented as a coordinate tuple:

```text
Tau(U) = (r, a, v, d, rec)
```

Where:

- `r` = runtime round / logical step index
- `a` = semantic age
- `v` = version depth or version lineage distance
- `d` = drift accumulation
- `rec` = recovery distance or recovery latency in logical terms

This is not the only possible representation.
It is a useful conceptual basis.

---

## 3. Semantic Age

Semantic age measures how far a unit has moved from its most recent active or canonical state.

### Suggested abstraction

```text
Age(U) = f(round_gap, activation, reuse, recovery_distance, version_depth)
```

The exact function may be learned, rule-based, or hybrid.

### Interpretation

- a recently used unit has low semantic age
- a long-unused unit has higher semantic age
- recovery may reduce semantic age
- approximation may preserve age while degrading fidelity

---

## 4. Round Time

Round time is the logical progression of runtime steps.

It is not physical seconds.

Round time is useful for:

- event ordering
- decay updates
- history indexing
- replay alignment

Round time should be monotonic in a valid runtime sequence.

---

## 5. Version Time

Version time measures depth or distance in the semantic version DAG.

Version time is useful for:

- branch comparison
- rollback selection
- merge analysis
- replay alignment

Version time is not simply event count.
It is path-dependent.

---

## 6. Drift Time

Drift time measures cumulative semantic divergence.

It may be derived from:

- approximation events
- merge events
- recovery mismatch
- structural loss
- confidence decay

Drift time is useful for deciding when a unit should be approximated, archived, or recovered.

---

## 7. Recovery Time

Recovery time measures the logical distance between a degraded state and a recovered state.

This may include:

- number of rounds since degradation
- number of candidate search steps
- confidence change during recovery
- version lineage distance to a valid ancestor

Recovery time helps distinguish a quick restore from a long-latency reconstruction.

---

## 8. Activation and Semantic Time

Activation and semantic time are coupled.

As semantic age increases, activation may decrease.
When a unit is used or recovered, activation may increase and semantic age may reset or decrease.

This gives a causal interpretation for maintenance behavior:

- decay increases age
- use decreases age pressure
- recovery may partially reset age
- approximation may carry age forward

---

## 9. Semantic Time Operations

Semantic time should support several operations.

### 9.1 Advance

```text
Advance(Tau) -> Tau'
```

Logical aging after a runtime step.

### 9.2 Reset

```text
Reset(Tau) -> Tau'
```

Used by recovery or reactivation paths.

### 9.3 Branch

```text
Branch(Tau) -> Tau1, Tau2
```

Used when semantic versions diverge.

### 9.4 Merge

```text
Merge(Tau1, Tau2) -> Tau'
```

Used when diverged semantic paths are reconciled.

---

## 10. Semantic Time and Lifecycle

Lifecycle states often depend on semantic time.

Examples:

- `active` -> low age
- `stable` -> moderate age with good reuse
- `dormant` -> high age and low reuse
- `approximate` -> high age with degraded fidelity
- `forgotten` -> age beyond recovery threshold without support

Lifecycle is therefore a semantic time projection.

---

## 11. Semantic Time and Replay

Replay needs semantic time because replay must reconstruct not only the state but the timing relationships among transitions.

Replay should be able to restore:

- round order
- activation decay trajectory
- version branch timing
- drift accumulation timing

This makes replay more faithful than a simple state snapshot restore.

---

## 12. Semantic Time and Trace

Trace can reference semantic time to explain when and how a unit evolved.

Trace may answer:

- when did a unit become dormant?
- how long was it forgotten?
- at what semantic age was it recovered?
- how much drift accumulated before approximation?

This is why semantic time is useful for explanation.

---

## 13. Semantic Time and Metric Space

Semantic time can participate in semantic distance.

For example, history distance or drift distance may be partially driven by semantic age and version depth.

Semantic time is therefore a feature of the metric space, but it deserves its own model because it is more than just a single scalar.

---

## 14. Relation to Current Implementation

The current project already tracks time-like signals such as:

- round ids
- last used / verification round
- history length
- drift count
- lifecycle stage
- version-like summaries

This document explains how those signals should be interpreted as semantic time rather than physical time.

---

## 15. Relationship to Other Documents

Recommended chain:

```text
Formal Semantics
  -> Semantic Metric Space
  -> Runtime Semantics
  -> Semantic Time Model
  -> Minimal Runtime Kernel
```

Semantic time also connects to:

- Semantic Versioning Model
- Replay Spec
- Semantic Evolution Trace Spec
- Runtime Recording Layer Alignment

---

## 16. Scope

This document defines semantic time only.

It does not define:

- physical timestamps
- scheduler behavior
- queue implementation
- kernel internals

Those belong to runtime implementation details.

