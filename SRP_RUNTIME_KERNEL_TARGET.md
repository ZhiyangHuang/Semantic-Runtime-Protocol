# SRP Runtime Kernel Target

This document defines the target runtime kernel for SRP.
It is not an implementation spec.

The central question is:

> What is the minimal execution layer responsible for semantic state transition integrity?

The runtime kernel is the target boundary that future code should move toward.
The callable interface of that boundary is defined in [Runtime Kernel Interface](SRP_RUNTIME_KERNEL_INTERFACE.md).

---

## 1. Kernel Definition

The Runtime Kernel is the minimal execution layer responsible for semantic state transition integrity.

It is responsible for:

- accepting only legal events
- validating events before mutation
- applying state transitions
- recording evolution traces
- preserving replayability
- supporting attribution

It is not responsible for:

- embedding generation
- benchmark execution
- policy strategy search
- graph implementation details
- LLM prompting or generation control

Those belong to model, policy, evaluation, or representation layers.

---

## 2. Kernel Core Components

The target kernel should be composed of the following conceptual components:

```text
Runtime Kernel
  ├── Event Dispatcher
  ├── Event Validator
  ├── State Transition Engine
  ├── Lifecycle Manager
  ├── History Recorder
  ├── Replay Engine
  └── Attribution Tracker
```

### Component responsibilities

| Component | Responsibility |
| --- | --- |
| Event Dispatcher | Route proposed events to the correct validation and application path |
| Event Validator | Check event legality, schema support, invariants, and permissions |
| State Transition Engine | Apply accepted mutations to `SemanticState` and its units |
| Lifecycle Manager | Control active / dormant / archived / recovered state transitions |
| History Recorder | Persist the event stream and evolution summaries |
| Replay Engine | Reconstruct state from an initial snapshot and an event stream |
| Attribution Tracker | Explain which events and rules caused state changes |

---

## 3. Kernel Ownership Boundaries

The kernel owns the following concerns:

- state mutation
- event acceptance
- transition ordering
- history recording
- invariant enforcement

The kernel does not own:

- policy choice
- semantic extraction models
- similarity scoring models
- benchmark scoring
- graph storage design

### Ownership separation

- Policy decides what should happen under pressure.
- The kernel decides whether the transition is legal and applies it.
- Models produce semantic representations or candidate outputs.
- Evaluation measures the resulting preservation behavior.

This boundary is required to keep SRP from collapsing into a generic memory system.

---

## 4. Target Control Flow

The target control flow should look like this:

```text
Policy
  -> Decision
  -> Event
  -> Runtime Kernel
  -> SemanticState
  -> Evaluation
```

More explicitly:

```text
Rule / Policy
  -> Decision
  -> RuntimeEvent
  -> Validate
  -> Apply
  -> Record
  -> Update Evolution Summary
```

The kernel is the execution boundary between event authorization and state mutation.

---

## 5. Kernel State Transition Model

The kernel should process transitions in this order:

```text
Receive Event
  -> Validate
  -> Accept or Reject
  -> Apply Mutation
  -> Update Evolution Summary
  -> Record Event
  -> Emit StateChanged
```

### Transition notes

- rejected events must not mutate state
- accepted events must be applied before recording as committed history
- evolution summaries should be updated after mutation or alongside record writing

---

## 6. Kernel Invariants

The kernel must guarantee the following invariants.

### Identity invariant

```text
unit_id cannot change
```

### History invariant

```text
Applied event must exist in EventStream
```

### Replay invariant

```text
Replay(EventStream, InitialState) == CurrentState
```

### Lifecycle invariant

- `deleted` cannot directly become `active`
- `unknown` must pass through recovery before becoming valid again
- invalid transitions must be rejected before mutation

### Mutation invariant

- only accepted events may mutate state
- all mutations must be attributable to an event

---

## 7. Kernel Does Not Own

The kernel is not:

- a memory optimizer
- a retrieval system
- a graph database
- an LLM controller
- a compression algorithm

It is the semantic state evolution execution layer.

---

## 8. Relationship to Current Layers

### Relation to Runtime Event Processing Model

The processing model describes producers, validators, and appliers.
The kernel target defines the execution boundary that will host those roles.

### Relation to Runtime Event Interface

The interface defines event shape, permissions, replay, and mutation boundaries.

### Relation to Evolution Rules

The rules define when a transition should be proposed.

### Relation to Policy

Policy decides which valid path to prefer under resource pressure.

### Relation to Evaluation

Evaluation measures how well the kernel preserves semantic state over time.

---

## 9. Migration Boundary

The current experimental code should be interpreted as an early projection of the future kernel.

### Current experimental layer

```text
srp_experiment
  -> implicit transitions
  -> direct mutation
  -> mixed responsibility
```

### Target kernel layer

```text
runtime kernel
  -> explicit events
  -> validated transitions
  -> attributable mutations
```

### Migration order

1. Event abstraction
2. Mutation isolation
3. Lifecycle extraction
4. Replay support
5. Attribution support

This migration should happen conceptually before any structural refactor.

---

## 10. Scope

This document defines the target runtime kernel boundary for SRP.

It does not define:

- the concrete kernel code
- the dispatcher implementation
- the storage engine
- the event class implementation

Those belong to later implementation work.
