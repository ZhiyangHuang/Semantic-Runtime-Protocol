# SRP Replay Spec

This document defines deterministic semantic state reconstruction from Runtime Event history in SRP.
It is not a log replay spec and not a generic debugging transcript spec.

The central question is:

> Given an initial state and an event history, how do we reconstruct a semantic state at time t?

This layer sits beside the trace model and below implementation mapping for replay-oriented work.

---

## 1. Replay Definition

Replay reconstructs a semantic state from:

- an initial state
- an ordered event stream
- schema version information
- rule version information

Core shape:

```text
Replay(EventStream, InitialState)
  -> SemanticState_t
```

Replay should restore, as needed:

- SemanticState
- SemanticUnit lifecycle
- Relations
- Metadata evolution

---

## 2. Replay Input Contract

### ReplayInput

```text
ReplayInput
{
  initial_state_reference,
  event_stream,
  schema_version,
  rule_version,
  replay_mode
}
```

### event_stream requirements

The event stream must be composed of `RuntimeEvent` records and should include at least:

- `event_id`
- `causal_parent`
- `before_state_reference`
- `after_state_reference`
- `mutation_mode`

### rule_version requirement

Replay must know which rule set was in effect.

Reason:

```text
same event
  + different rule version
  = potentially different reconstructed state
```

So event history alone is not sufficient for deterministic reconstruction.

---

## 3. Replay Pipeline

Recommended replay pipeline:

```text
Load Initial State
  -> Validate Event Schema
  -> Order Events
  -> Apply Event
  -> Validate Transition
  -> Generate New State Version
  -> Compare Expected State
  -> Produce Replay Result
```

Replay should be explicit about each stage so failure points are visible.

---

## 4. Replay Event Ordering

Event ordering must not depend on timestamp alone.

Recommended priority:

```text
causal dependency
  >
timestamp_round
  >
event_id
```

### Ordering rule

- if causal dependencies exist, they take precedence
- if causal dependencies are equal, compare round information
- if round information is equal, use event id as a stable tie-breaker

This prevents ambiguous reconstruction when multiple events occur in the same round.

---

## 5. Replay Result

Replay should return more than a reconstructed state.

### ReplayResult

```text
ReplayResult
{
  reconstructed_state,
  applied_events,
  failed_events,
  divergence_points,
  replay_drift,
  validation_result
}
```

### Why this matters

- `reconstructed_state` is the main output
- `applied_events` support auditability
- `failed_events` explain partial reconstruction issues
- `divergence_points` support analysis
- `replay_drift` supports evaluation
- `validation_result` supports correctness checking

---

## 6. Replay Failure Model

Replay failures should be explicit and classifiable.

### Schema failure

The event cannot be interpreted due to a schema mismatch or missing field contract.

### Causal failure

An event appears without a required causal predecessor.

Example:

```text
RecoveryApplied
  without
RecoveryRequested
```

### State conflict

The event expects a state condition that is no longer true.

Example:

```text
delete unit A
```

when `A` does not exist.

### Rule conflict

An event is valid under one rule set but not another.

Example:

```text
Forgotten
```

under a newer rule set that forbids the same forgetting path.

---

## 7. Replay vs Trace

Replay and trace are related but distinct.

| Aspect | Replay | Trace |
| --- | --- | --- |
| Goal | Reconstruct | Explain |
| Input | EventStream | Event + Rule + State Reference |
| Output | State | Causal Path |
| Focus | Correctness | Explainability |
| Use | Recovery, validation | Analysis, attribution |

### Replay side

Replay answers:

- what state should exist after the event history is applied?

### Trace side

Trace answers:

- why did that state emerge?

---

## 8. Replay and Drift

Replay can measure divergence between expected and reconstructed states.

### Replay drift

```text
Expected State
  compared with
Replayed State
  -> Replay Drift
```

Replay drift helps evaluate whether the event history and rule set are sufficient for exact or near-exact reconstruction.

### Relation to trace

- replay measures drift
- trace attributes drift

This separation is important for SRP analysis.

---

## 9. Replay Quality Targets

Replay should ideally support:

- deterministic ordering
- deterministic application
- deterministic reconstruction for valid streams
- explicit failure reporting for invalid streams
- comparison against expected state

---

## 10. Relationship to Other Documents

Recommended chain:

```text
Runtime Kernel Migration Checklist
  -> Runtime Kernel Phase Migration Map
  -> Semantic Evolution Trace Spec
  -> Replay Spec
  -> Replay-Oriented Implementation Work
```

This spec is intended to freeze replay requirements before mapping the trace and replay layers to current records and summaries.

---

## 11. Scope

This document defines replay behavior only.

It does not define:

- event storage implementation
- trace serialization
- kernel class design
- runtime database schema

Those belong to later implementation work.

