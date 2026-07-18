# SRP Runtime Event Interface

This document defines the engineering-facing interface for SRP events.
It is not an implementation spec.

The central question is:

> How should semantic state changes be expressed safely, replayably, and without conflating decision, event, and mutation?

This layer sits between the event contract and future handler implementations.
The detailed producer / validator / applier flow is defined in [Runtime Event Processing Model](SRP_RUNTIME_EVENT_PROCESSING_MODEL.md).

---

## 1. Event Lifecycle

SRP event handling should follow a three-stage model:

```text
Decision
   -> Event
   -> Mutation
```

These stages are intentionally separate.

- `Decision` decides whether a transition should happen
- `Event` represents the authorized transition
- `Mutation` applies the event to state

Important rule:

- `Decision != Event`
- `Event != Mutation`

This separation keeps policy, legality, and state change independent.

---

## 2. Interface Purpose

The runtime event interface should make it possible to:

- create an event from a decision
- validate whether an event may mutate a target
- apply the event to the semantic state
- record a compact replayable trace
- reconstruct or replay the state transition later

It should not store the entire object snapshot for every event.
It should store the delta or the event-specific change set.

---

## 3. RuntimeEvent Shape

An interface-level `RuntimeEvent` should conceptually contain:

```text
RuntimeEvent
{
  event_id,
  event_type,
  timestamp_round,
  actor,
  targets,
  trigger,
  reason,
  confidence,
  before_state,
  after_state,
  payload,
  mutation_mode
}
```

### Field notes

- `event_id`: unique and immutable event identity
- `event_type`: event family or transition kind
- `timestamp_round`: round or cycle at which the event occurred
- `actor`: module, subsystem, or handler that produced the event
- `targets`: affected unit or relation references
- `trigger`: rule or condition that led to the event
- `reason`: human-auditable justification
- `confidence`: certainty or evidence strength
- `before_state`: compact pre-mutation delta
- `after_state`: compact post-mutation delta
- `payload`: event-specific data
- `mutation_mode`: allowed mutation style such as `create`, `update`, `merge`, `replace`, `restore`, `partition`

---

## 4. Before / After Rules

Events should not store full object copies unless absolutely necessary.

Prefer compact state deltas:

```text
before:
  activation: 0.8
  lifecycle: active

after:
  activation: 0.3
  lifecycle: dormant
```

This keeps the event stream small and replayable.

### Delta rules

- only record the fields the event changed
- avoid embedding the full unit state unless replay requires it
- preserve enough context to explain the change

---

## 5. Event Categories

Events should be grouped into four categories.

### 5.1 Creation Events

Creation events introduce a semantic unit or a new canonical form.

Examples:

- `SemanticExtracted`
- `Canonicalized`

Primary field effects:

- identity
- semantic payload
- provenance

### 5.2 Evolution Events

Evolution events refine, merge, approximate, or reweight a unit.

Examples:

- `Merged`
- `Consolidated`
- `Approximated`
- `ActivationUpdated`

Primary field effects:

- aliases
- activation
- representation
- lifecycle
- evolution metadata

### 5.3 Preservation Events

Preservation events handle pressure, compression, archiving, and forgetting.

Examples:

- `CompressionSelected`
- `CompressedPackageProduced`
- `Forgotten`
- `GarbageCollected`

Primary field effects:

- lifecycle
- memory state
- archive state

### 5.4 Validation Events

Validation events evaluate recovery, repair, and continuity.

Examples:

- `RecoveryRequested`
- `RecoveryResultProduced`
- `ValidationPerformed`
- `RepairTriggered`

Primary field effects:

- confidence
- drift
- recovery metadata
- repair metadata

---

## 6. Event Permission Matrix

Each event type should have a clear permission boundary.

| Event | Identity | Relations | Activation | Lifecycle | Embedding | Provenance | Confidence | Drift |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `SemanticExtracted` | ✓ | - | - | - | ✓ | ✓ | ✓ | - |
| `Canonicalized` | ✓ | - | - | - | - | ✓ | ✓ | - |
| `Merged` | ✓ | ✓ | - | - | - | ✓ | ✓ | ✓ |
| `Consolidated` | ✓ | ✓ | ✓ | - | - | ✓ | ✓ | ✓ |
| `ActivationUpdated` | - | - | ✓ | - | - | - | - | - |
| `Approximated` | - | ✓ | ✓ | ✓ | ✓ | - | ✓ | ✓ |
| `Forgotten` | - | - | ✓ | ✓ | - | - | - | ✓ |
| `Recovered` | - | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `CompressionSelected` | - | - | - | - | - | - | - | - |
| `CompressedPackageProduced` | - | - | - | - | - | ✓ | - | - |
| `RecoveryRequested` | - | - | - | - | - | - | - | - |
| `RecoveryResultProduced` | - | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `ValidationPerformed` | - | - | - | - | - | - | ✓ | ✓ |
| `RepairTriggered` | - | ✓ | - | - | ✓ | ✓ | ✓ | ✓ |
| `LifecycleTransitioned` | - | - | - | ✓ | - | - | - | - |
| `DriftMeasured` | - | - | - | - | - | - | - | ✓ |
| `HistorySummarized` | - | - | - | - | - | - | ✓ | ✓ |

Legend:

- `✓` means the event may modify or attach that field family
- `-` means the event should not directly modify that field family

This matrix is a conceptual boundary, not a literal code permission system yet.

---

## 7. Mutation Boundary

The event interface must preserve the distinction between authorization and mutation.

Suggested flow:

```text
Rule Evaluation
  -> Decision
  -> RuntimeEvent
  -> apply_event()
  -> State Mutation
```

The event is the legal transition artifact.
The mutation is the concrete application of that artifact to state.

---

## 8. Event Replay

The event stream should support replay.

Replay means:

```text
Initial State + Event Stream = Reconstructed State
```

This matters for:

- debugging
- reproducibility
- mechanism attribution
- drift analysis
- recovery audits

### Replay rules

- event order must be preserved
- replay should reconstruct the same state when the same event stream is applied
- replay may use compact deltas, not full snapshots
- event summaries may be used for fast inspection, but the replay path should remain available

---

## 9. Event Stream vs History

The runtime event interface should not collapse event stream and history into one thing.

- `EventStream` is ordered, replayable, and fine-grained
- `History` is summarized, evolution-aware, and suitable for drift analysis

The event interface writes to the event stream.
The data contract may reference history summaries.

---

## 10. Relation to Other Layers

### Relation to Data Contract

The data contract defines what fields exist and what they mean.

### Relation to Event Contract

The event contract defines which event kinds exist and what they may mutate.

### Relation to Evolution Rules

The evolution rules define when a decision should produce an event.

### Relation to Implementation

The implementation will eventually realize this interface as event objects, handlers, validators, and appliers.

---

## 11. Scope

This document defines the interface shape for SRP events.

It does not define:

- the handler implementation
- the actual factory or dispatcher
- the storage format
- the execution engine

Those belong to later runtime implementation work.
