# SRP Runtime Component Interface Spec

This document freezes the minimal interfaces for the first executable runtime components in SRP:

- `runtime_event.py`
- `trace_builder.py`
- `replay_engine.py`

It is an interface specification, not an implementation spec.

The central question is:

> What is the smallest stable interface set that can express event identity, causal tracing, and deterministic replay without re-opening the full kernel design?

This layer sits below the protocol documents and above any code-level runtime implementation.

---

## 1. Component Roles

### 1.1 `runtime_event.py`

Responsible for defining the event object.

It does not:

- produce events
- decide policy
- validate policy choices
- mutate state

Its job is to define the transition record.

### 1.2 `trace_builder.py`

Responsible for constructing trace structures from events and state references.

It does not:

- mutate state
- re-run policy selection
- create new events

Its job is to explain why a transition occurred.

### 1.3 `replay_engine.py`

Responsible for deterministic reconstruction from an initial state plus event history.

It does not:

- invent missing events
- change policy rules
- replace the event stream with summaries

Its job is to rebuild state from valid transitions.

---

## 2. Component Relationship

The three components should form the smallest runtime protocol triangle:

```text
RuntimeEvent
  -> ReplayEngine
  -> SemanticState

RuntimeEvent
  -> TraceBuilder
  -> Evolution Explanation
```

Trace should not go through replay.
Replay should not require trace.

The components are related but independent.

---

## 3. `runtime_event.py` Interface

### 3.1 Purpose

`runtime_event.py` defines the canonical event object used throughout the runtime protocol.

### 3.2 Core object

```python
RuntimeEvent
{
    event_id,
    event_type,
    schema_version,
    timestamp_round,
    actor,
    targets,
    causal_parent,
    trigger,
    reason,
    confidence,
    before_state_reference,
    after_state_reference,
    payload,
    mutation_mode
}
```

### 3.3 Required principles

- an event describes a transition
- an event does not execute a transition
- an event must be serializable
- an event must be comparable by identity
- an event should carry enough reference data to support replay and trace construction

### 3.4 Suggested helper surface

The minimal helper surface may include:

- event serialization
- event deserialization
- schema validation
- causal metadata validation

### 3.5 Event invariants

- `event_id` is stable
- `schema_version` is explicit
- `causal_parent` is preserved when applicable
- `before_state_reference` and `after_state_reference` should be present when the transition is stateful
- `mutation_mode` must describe how the event is intended to change state

---

## 4. `trace_builder.py` Interface

### 4.1 Purpose

`trace_builder.py` converts event and state-reference information into a queryable causal explanation.

### 4.2 Core call shape

```python
build_trace(event, before_state, after_state) -> TraceRecord
```

### 4.3 Trace outputs

The trace builder should be able to produce:

- `TraceNode`
- `TraceEdge`
- `TraceRecord`

### 4.4 Trace builder rules

- the trace builder must not mutate state
- the trace builder must not generate policy decisions
- the trace builder must not invent new events
- the trace builder should consume references rather than full duplicated state when possible

### 4.5 Trace requirements

- a transition should yield a causal explanation
- `event_id` and `rule_id` should remain distinct in the trace path
- the trace should preserve enough linkage to explain drift, recovery, approximation, and lifecycle transitions

### 4.6 Trace consistency principle

For a single event, the trace builder should produce one primary causal edge unless the transition model explicitly allows branching.

---

## 5. `replay_engine.py` Interface

### 5.1 Purpose

`replay_engine.py` reconstructs semantic state deterministically from initial state and event history.

### 5.2 Core call shape

```python
replay(initial_state, event_stream, rule_version) -> ReplayResult
```

### 5.3 Replay result

```python
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

### 5.4 Replay rules

- replay must be deterministic for a valid stream and a fixed rule version
- replay must validate schema before applying events
- replay must order events by causal dependency first, then round, then event id
- replay must surface failure instead of silently continuing

### 5.5 Replay invariants

- given the same `initial_state`, `event_stream`, and `rule_version`, the replay output should be stable
- replay should distinguish schema failure, causal failure, state conflict, and rule conflict
- replay should expose drift rather than hide it

---

## 6. Interface Boundary Summary

The minimal split is:

```text
runtime_event.py
  -> defines event identity and transition metadata

trace_builder.py
  -> explains the transition causally

replay_engine.py
  -> reconstructs state deterministically
```

This split intentionally avoids kernel submission APIs for now.
The kernel can be layered on top later.

---

## 7. Testing Targets

The first tests for these interfaces should verify protocol behavior rather than benchmark behavior.

### Event serialization

```text
event -> json -> event
```

The round-trip should preserve identity and schema fields.

### Replay determinism

```text
initial_state + event_stream
```

Running replay twice should yield equivalent results for the same rule version.

### Trace consistency

For a single event:

- a trace record should be produced
- the trace should include at least one causal edge
- the trace should not silently lose the event identity

---

## 8. Relationship to Other Documents

Recommended chain:

```text
Runtime Event Contract
  -> Runtime Event Interface
  -> Replay Spec
  -> Semantic Evolution Trace Spec
  -> Runtime Component Interface Spec
  -> Runtime Kernel Interface
```

This document is the bridge from frozen protocol concepts to the first minimal executable interfaces.

---

## 9. Scope

This document defines the smallest runtime component interfaces only.

It does not define:

- kernel dispatcher internals
- policy engine implementation
- runtime storage format
- code-level module wiring

Those belong to later implementation work.

