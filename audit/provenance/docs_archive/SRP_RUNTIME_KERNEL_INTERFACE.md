# SRP Runtime Kernel Interface

This document defines the external interface of the SRP runtime kernel.
It is not an implementation spec.

The central question is:

> How does the runtime kernel interact with the outside world while remaining a replaceable semantic execution boundary?

This layer sits on top of the kernel target and below the implementation alignment layer.

---

## 1. Interface Definition

The Runtime Kernel provides controlled semantic state evolution through validated events.

Its core input is:

- `RuntimeEvent`

Its core outputs are:

- `EventResult`
- `ValidationResult`
- `StateTransitionResult`
- `SemanticStateView`

The kernel should not accept raw text, embeddings, policy scores, or model outputs directly.

Those must be transformed into events or views before entering the kernel boundary.

---

## 2. Public Interfaces

The minimal public interface should conceptually include:

### 2.1 `submit_event`

```text
submit_event(event: RuntimeEvent) -> EventResult
```

Responsibilities:

- accept an event proposal
- route it into validation
- return acceptance or rejection status

Limitations:

- must not directly mutate state
- must not skip validation

### 2.2 `validate_event`

```text
validate_event(event: RuntimeEvent) -> ValidationResult
```

Responsibilities:

- check schema compatibility
- check permission boundaries
- check invariants
- check causal dependencies

Limitations:

- must not apply the mutation
- must not invent or rewrite the event

### 2.3 `apply_event`

```text
apply_event(event: RuntimeEvent) -> StateTransitionResult
```

Responsibilities:

- apply the accepted mutation
- update `SemanticState`
- update history or evolution summaries as needed

Limitations:

- must not decide whether the event is justified
- must not perform policy selection

### 2.4 `get_state`

```text
get_state(query) -> SemanticStateView
```

Responsibilities:

- return a read-only or projection-based view of current semantic state

Limitations:

- must not mutate state
- must not infer hidden updates

### 2.5 `replay`

```text
replay(event_stream) -> SemanticState
```

Responsibilities:

- reconstruct semantic state evolution from the initial state and event stream
- use schema version and causal metadata when needed

Limitations:

- must not depend on hidden side effects
- must be deterministic for a valid stream

---

## 3. Kernel Interface Data Types

### 3.1 `RuntimeEvent`

The kernel consumes the event shape defined in the event interface and event contract layers.

It should at minimum include:

- `event_id`
- `schema_version`
- `event_type`
- `actor`
- `targets`
- `trigger`
- `payload`
- `before_state`
- `after_state`
- `confidence`
- `mutation_mode`
- `causal_parent`

### 3.2 `EventResult`

```text
EventResult
{
  event_id,
  status,
  reason,
  affected_units,
  drift_delta
}
```

Suggested statuses:

- `accepted`
- `rejected`
- `applied`
- `failed`

### 3.3 `ValidationResult`

```text
ValidationResult
{
  accepted,
  reasons,
  rejected_fields,
  invariant_violations,
  normalized_event
}
```

### 3.4 `StateTransitionResult`

```text
StateTransitionResult
{
  previous_state_hash,
  new_state_hash,
  changed_units,
  changed_relations,
  generated_events
}
```

### 3.5 `SemanticStateView`

A state view is a read-only projection for querying or evaluation.

It may include:

- selected units
- selected relations
- summary metadata
- history summaries

It must not expose mutable write access by default.

---

## 4. Kernel Permission Boundary

The kernel is allowed to:

- modify state
- update lifecycle fields
- write event streams
- update evolution summaries
- enforce invariants

The kernel is not allowed to:

- decide importance scores
- generate embeddings
- choose compression strategy
- generate recovery candidates
- run model inference

### Boundary summary

- Policy decides
- Kernel executes
- Model produces semantic representations
- Evaluation measures the outcome

---

## 5. State Transition Flow

The public interface should enforce the following progression:

```text
submit_event
  -> validate_event
  -> accept or reject
  -> apply_event
  -> record
  -> update summary
```

Reject path:

```text
submit_event
  -> validate_event
  -> reject
```

Failure path:

```text
apply_event
  -> failed
  -> emit repair or validation failure artifact
```

---

## 6. Error Handling

The kernel should distinguish between:

- validation rejection
- application failure
- replay failure

### Rejection

```text
PROPOSED
  -> VALIDATING
  -> REJECTED
```

Rejected events must not mutate state.

### Application failure

```text
ACCEPTED
  -> APPLYING
  -> FAILED
```

Failed application should not silently continue.
It must surface a repair or validation failure artifact.

### Replay failure

Replay failures should be explicit and attributable to a schema mismatch, missing parent, or invariant violation.

---

## 7. Replay Guarantee

Any valid event stream should deterministically reconstruct the semantic state evolution.

```text
Initial State
  + Event Stream
  = Current State
```

This guarantee supports:

- debugging
- reproducibility
- drift analysis
- attribution
- audit trails

Replay should branch on `schema_version` when required.

---

## 8. Interface and Policy Relationship

Policy must not mutate state directly.

Recommended flow:

```text
Policy Layer
  -> Decision
  -> RuntimeEvent
  -> Runtime Kernel
  -> SemanticState
```

The policy layer chooses among valid options.
The kernel executes an accepted event.

Direct mutation by policy is forbidden at the target architecture level.

---

## 9. Kernel and External World

The kernel should be treated as a replaceable execution boundary.

It may be called by:

- event producers
- policy decision layers
- recovery systems
- lifecycle controllers
- test harnesses

It should expose only the minimal read/write surface needed for semantic state evolution integrity.

---

## 10. Relationship to Other Layers

### Relation to Runtime Kernel Target

The target layer defines the kernel's conceptual boundary.
This document defines the kernel's callable interface.

### Relation to Runtime Event Processing Model

The processing model defines producer, validator, and applier roles.

### Relation to Runtime Event Contract

The contract defines what events are legal to submit.

### Relation to Implementation Alignment

The alignment documents map current modules toward this interface.

---

## 11. Scope

This document defines the external interface of the SRP runtime kernel.

It does not define:

- the concrete class implementation
- the event store implementation
- the dispatcher implementation
- the replay engine implementation

Those belong to later code-level work.
