# SRP Runtime Kernel Adapter Plan

This document defines how SRP transitions from the current experimental runtime into an event-driven runtime kernel architecture.
It is a migration strategy document, not an implementation spec.

The central question is:

> How do we wrap and gradually migrate the current experiment layer without breaking evidence, preservation behavior, or existing experimental flow?

This document sits between the kernel API map and concrete implementation migration.

---

## 1. Migration Principle

The experiment layer should not be replaced abruptly.
It should be wrapped, observed, and gradually migrated.

```text
Do not replace the experiment layer.
Wrap and gradually migrate it.
```

Current shape:

```text
srp_experiment
  -> semantic objects
  -> state mutation
  -> compression
  -> recovery
  -> validation
```

Target shape:

```text
Runtime Kernel
  -> RuntimeEvent
  -> validated transition
  -> SemanticState
```

The adapter layer is the bridge between these two shapes.

---

## 2. Adapter Layer Role

The adapter layer does not introduce new semantic policy, new memory logic, or new reasoning algorithms.

It is responsible for:

- wrapping existing outputs into `RuntimeEvent`
- routing legacy mutation into kernel-style transitions
- exposing query surfaces through read-only views
- preserving experiment behavior while events are introduced

It is not responsible for:

- inventing new policy logic
- changing the underlying representation strategy
- replacing the experiment runtime in one step

Adapter flow:

```text
Existing Component
  -> RuntimeEvent Adapter
  -> Kernel API
```

---

## 3. Migration Architecture

Recommended migration stack:

```text
Policy Layer
  ->
Event Adapter Layer
  ->
Runtime Kernel
  ->
Semantic State
```

Interpretation:

- policy still makes decisions
- adapter converts legacy outputs into events
- kernel validates and applies transitions
- semantic state is mutated only through the kernel boundary

This keeps the current experiment usable while the runtime protocol is introduced.

---

## 4. Phase Migration

Migration should happen in phases rather than as a full rewrite.

### Phase 0: Observation Layer

Goal:

- do not change behavior
- observe existing transitions
- log mutation intent
- measure drift and preservation signals

Current:

```text
function
  -> mutation
```

Phase 0 target:

```text
function
  -> event observation
  -> mutation
```

This phase is purely observational.

### Phase 1: Event Wrapping

Goal:

- make current module outputs produce `RuntimeEvent` proposals
- keep legacy mutation behavior temporarily available

Example:

```text
compress()
  -> CompressionSelected
  -> submit_event()
```

At this stage, the event stream exists even if mutation still happens through legacy paths.

### Phase 2: Mutation Routing

Goal:

- stop direct external mutation
- route state changes through `Kernel.apply_event()`

Old shape:

```text
compress.py
  -> state
```

New shape:

```text
compress.py
  -> RuntimeEvent
  -> Kernel.apply_event()
  -> state
```

### Phase 3: Lifecycle Migration

Goal:

- move archive, forgetting, approximation, and recovery transitions under event control
- ensure these transitions are represented in `EventStream` and `History`

This phase is important because these transitions depend heavily on:

- event history
- replay
- attribution
- drift accumulation

### Phase 4: Replay Enablement

Goal:

- make the event stream sufficient to reconstruct the current semantic state

Target property:

```text
Initial State
  + Event Stream
  = Current State
```

Replay is the maturity signal for the kernel architecture.

---

## 5. Adapter Types

The adapter layer can be decomposed into three conceptual adapter families.

### 5.1 Event Producer Adapter

Responsibility:

```text
Legacy Output
  -> RuntimeEvent
```

Typical sources:

- parser outputs
- compression selections
- recovery outputs
- lifecycle decisions

### 5.2 Mutation Adapter

Responsibility:

```text
legacy mutation
  -> kernel transition
```

Typical sources:

- state mutation paths
- lifecycle updates
- recovery materialization

### 5.3 Query Adapter

Responsibility:

```text
legacy state access
  -> get_state()
```

Typical sources:

- object inventory reads
- semantic state reads
- validation reads
- recovery candidate reads

---

## 6. Migration Constraints

The adapter layer must preserve important constraints.

### 6.1 Do not change experiment results early

Phase 0 and Phase 1 should be observational or wrapping only.
The experiment must remain usable.

### 6.2 Do not let policy mutate directly

Policy still decides, but it must not own direct state mutation in the target architecture.

```text
Policy
  -> Decision
  -> RuntimeEvent
  -> Kernel
```

### 6.3 Do not bind the kernel to a graph implementation

Graph is a representation choice, not the kernel itself.

The adapter plan must remain independent of:

- graph storage
- table storage
- IR format
- embedding backend

---

## 7. Success Criteria

The adapter plan is successful when the following hold:

### Event completeness

Important state changes are represented by events.

### Mutation isolation

External code no longer mutates semantic state directly once routed through the kernel boundary.

### Replay capability

The event stream is sufficient to reconstruct state evolution.

### Attribution capability

Each change can be traced to:

- which mechanism
- which event
- which objective

---

## 8. Relationship to Existing Documents

This document sits on top of the target kernel boundary and below implementation mapping.

Recommended chain:

```text
Runtime Kernel Interface
  -> Runtime Kernel API Map
  -> Runtime Kernel Adapter Plan
  -> Implementation Migration
```

It is the bridge from abstract kernel design to controlled migration.

---

## 9. Scope

This document defines migration strategy only.

It does not define:

- concrete adapter classes
- function-level callsites
- directory restructuring
- new mutation algorithms

Those belong to later implementation work.

