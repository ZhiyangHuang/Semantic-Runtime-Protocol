# SRP Semantic Evolution Trace Model

This document defines how SRP records the causal path of semantic change over time.
It is a trace model document, not an implementation spec.

The central question is:

> How does a semantic unit evolve across rounds, events, approximations, recoveries, and drift?

This layer sits below the phase migration map and above replay-oriented implementation work.

---

## 1. Trace Definition

A semantic evolution trace is the causal record of how a semantic unit changes over time.

It is not just history.

- history summarizes what happened
- trace explains how the unit got there

Trace records should preserve:

- event order
- causal parent relationships
- state deltas
- drift accumulation
- recovery and approximation lineage

---

## 2. Trace Components

### 2.1 SemanticUnit identity

Every trace must anchor to a stable `unit_id`.

### 2.2 Event stream reference

Trace records should point to the event stream that caused the change.

### 2.3 State delta

Each step should record the change in semantic or lifecycle state rather than duplicating the entire object.

### 2.4 Drift summary

Trace should keep enough information to explain how far the unit has moved from its original semantic anchor.

### 2.5 Recovery lineage

If a unit is forgotten, approximated, or recovered later, the trace should preserve that causal chain.

---

## 3. Trace Vocabulary

The trace should distinguish between:

- `SemanticExtracted`
- `Canonicalized`
- `Merged`
- `ActivationUpdated`
- `Consolidated`
- `Approximated`
- `Forgotten`
- `Recovered`
- `LifecycleTransitioned`
- `ValidationPerformed`

These are not just event names.
They are trace points that explain semantic evolution.

---

## 4. Trace Shape

A trace can be modeled as:

```text
SemanticUnit
  -> TraceNode
  -> TraceEdge
  -> TraceSummary
```

### TraceNode

Represents a single transition point.

Fields may include:

- `event_id`
- `event_type`
- `round_id`
- `before`
- `after`
- `confidence`
- `drift_delta`

### TraceEdge

Represents causal linkage between nodes.

Fields may include:

- `parent_event_id`
- `child_event_id`
- `causal_reason`

### TraceSummary

Represents accumulated semantic evolution over time.

Fields may include:

- `current_drift`
- `accumulated_drift`
- `recovery_count`
- `approximation_count`
- `archive_count`
- `stability_score`

---

## 5. Example Trace

```text
unit_001
  SemanticExtracted
  Canonicalized
  ActivationUpdated
  Approximated
  Forgotten
  RecoveryRequested
  Recovered
```

This trace tells us:

- the unit was initially extracted
- its canonical form was established
- activation decayed over time
- it degraded into an approximation
- it was later forgotten
- it was requested again and recovered

That causal path is more informative than a summary alone.

---

## 6. Trace vs History

### History

History answers:

- what events occurred
- how many times did a transition happen
- what is the current summary

### Trace

Trace answers:

- what caused the current state
- how did the unit drift
- what was recovered, approximated, or lost
- which path led to the current semantic form

Trace is therefore more causal than history.

---

## 7. Trace Requirements

The trace model should preserve:

- identity continuity
- event ordering
- causal links
- state deltas
- drift direction and accumulation
- recovery provenance

The trace model should not require full state duplication at every step.

---

## 8. Relation to Replay

Replay reconstructs state from events.
Trace explains the meaningful path of evolution.

```text
EventStream
  -> Replay
  -> SemanticState

Trace
  -> Causal explanation of the path
```

Replay is about reconstruction.
Trace is about explanation.

---

## 9. Relationship to Other Documents

Recommended chain:

```text
Runtime Kernel Migration Checklist
  -> Runtime Kernel Phase Migration Map
  -> Semantic Evolution Trace Model
  -> Replay-Oriented Implementation Work
```

This trace model is the bridge between migration and replay.

---

## 10. Scope

This document defines semantic evolution tracing only.

It does not define:

- event storage implementation
- trace serialization
- kernel class design
- replay engine internals

Those belong to later implementation work.

