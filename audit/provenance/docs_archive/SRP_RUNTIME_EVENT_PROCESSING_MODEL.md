# SRP Runtime Event Processing Model

This document defines how SRP events are produced, validated, applied, and recorded.
It is not an implementation spec.

The central question is:

> Who creates an event, who validates it, who applies it, and how does the event move through its lifecycle?

This layer sits on top of the runtime event interface and prepares the eventual handler implementation.
The target execution boundary for these responsibilities is defined in [Runtime Kernel Target](SRP_RUNTIME_KERNEL_TARGET.md).
The callable kernel surface is defined in [Runtime Kernel Interface](SRP_RUNTIME_KERNEL_INTERFACE.md).

---

## 1. Processing Model

SRP event processing should be modeled as:

```text
Rule Engine
   -> Decision
   -> Event Producer
   -> RuntimeEvent
   -> Event Validator
   -> Event Applier
   -> SemanticState
```

This means:

- the rule engine decides whether a transition is justified
- the producer emits a structured event proposal
- the validator checks legality and invariants
- the applier mutates the state if the event is accepted

The processing model keeps these responsibilities separate.

---

## 2. Core Roles

### 2.1 Event Producer

The event producer discovers or proposes what happened.

Examples:

- `semantic_parser.py` proposes `SemanticExtracted`
- `state_lifecycle.py` proposes `ActivationUpdated`
- `recover.py` or `recover_runtime.py` proposes `RecoveryResultProduced`

Producer responsibilities:

- observe the current state or input
- create an event proposal
- attach trigger, reason, and payload

Producer limitations:

- must not directly mutate semantic state
- must not decide legality by itself

### 2.2 Event Validator

The event validator determines whether the event is legal.

Validator responsibilities:

- check event schema version
- check required fields
- check field-level invariants
- check whether the targets exist or are allowed placeholders
- check whether the mutation mode is permitted
- check causal consistency when applicable

Validator limitations:

- must not perform the mutation
- must not invent event content

### 2.3 Event Applier

The event applier performs the actual state mutation.

Applier responsibilities:

- apply the before/after delta
- update the relevant unit, relation, or state container
- attach the accepted event to the event stream
- update history summaries when required

Applier limitations:

- must not decide whether the event is justified
- must not change event meaning
- must not rewrite event evidence after acceptance

---

## 3. Event Lifecycle

Events should move through a clear lifecycle.

```text
PROPOSED
  -> VALIDATING
  -> ACCEPTED
  -> APPLIED
  -> RECORDED
```

Optional rejection path:

```text
PROPOSED
  -> VALIDATING
  -> REJECTED
```

### Lifecycle notes

- `PROPOSED` means the event has been generated but not yet checked
- `VALIDATING` means invariant and legality checks are running
- `ACCEPTED` means the event passed validation
- `APPLIED` means the semantic state was mutated
- `RECORDED` means the event was written to the stream or replay log
- `REJECTED` means the event failed validation and must not mutate state

---

## 4. RuntimeEvent Required Interface Fields

The interface-level `RuntimeEvent` should include the following core fields:

```text
RuntimeEvent
{
  event_id,
  schema_version,
  event_type,
  timestamp_round,
  actor,
  targets,
  trigger,
  reason,
  confidence,
  causal_parent,
  before_state,
  after_state,
  payload,
  mutation_mode,
  lifecycle_state
}
```

### Field notes

- `schema_version`: version of the event schema, required for replay and evolution
- `causal_parent`: one or more prior events that caused this event
- `lifecycle_state`: current processing stage of the event

---

## 5. `schema_version`

Every event must carry a schema version.

Why it matters:

- SRP will evolve over time
- old event streams must remain replayable
- event payload shape may change between versions

Suggested rule:

- `schema_version` must be explicit and immutable once emitted
- replay should branch based on schema version when needed

Example:

```text
schema_version: event.v1
```

---

## 6. `causal_parent`

Every event should retain causal ancestry when available.

Why it matters:

- drift analysis
- mechanism attribution
- debugging
- recovery provenance

Examples:

```text
Merge
  -> ActivationUpdate
  -> RelationUpdate
```

```text
RecoveryRequested
  -> RecoveryResultProduced
  -> ValidationPerformed
```

Suggested rule:

- store a causal parent id or list of ids when the event is generated from prior events or event chains

---

## 7. Event Producer Interface

Producers should follow a proposal shape:

```text
EventProposal
{
  decision_ref,
  candidate_event,
  observed_signals,
  justification
}
```

Producer responsibilities:

- observe signals
- emit a candidate event
- annotate the proposal with why it should exist

Producers do not apply the event.

---

## 8. Event Validator Interface

Validators should check:

- schema version support
- event type validity
- field presence
- target validity
- permission boundary
- invariants from the event contract
- rule compatibility

Suggested validator output:

```text
ValidationResult
{
  accepted: bool,
  reasons: [...],
  rejected_fields: [...],
  invariant_violations: [...],
  normalized_event: RuntimeEvent | null
}
```

If validation fails, the event must not be applied.

---

## 9. Event Applier Interface

Appliers should consume accepted events and mutate state.

Suggested applier behavior:

```text
apply_event(event, state) -> updated_state
```

Applier responsibilities:

- update only the fields authorized by the event contract
- preserve or update history references
- return a state that reflects the event's after-state

Applier limitations:

- no rule evaluation
- no validation logic
- no policy selection

---

## 10. Component Responsibility Matrix

| Component | Create Event | Validate | Apply | Record |
| --- | --- | --- | --- | --- |
| Parser / Extraction | ✓ | - | - | - |
| Policy | ✓ | - | - | - |
| Evolution Rule Engine | ✓ | - | - | - |
| Validator | - | ✓ | - | - |
| State Manager | - | - | ✓ | ✓ |
| Recovery | ✓ | ✓ | - | - |
| History / Recorder | - | - | - | ✓ |

Notes:

- a component may also propose a decision that later becomes an event
- only the validator decides whether the proposal is acceptable
- only the applier mutates state

---

## 11. Record / Replay Boundary

The processing model should preserve a clean record/replay contract.

Record:

- append accepted events to the event stream
- update summary/history pointers as needed

Replay:

- re-run the event stream against an initial state
- use `schema_version` to interpret event shape
- use `causal_parent` and payload metadata for attribution and debugging

Replay should never depend on hidden side effects.

---

## 12. Relation to Other Layers

### Relation to Runtime Event Interface

The interface defines the shape and permission boundary of events.

### Relation to Runtime Event Contract

The contract defines what events are legal.

### Relation to Semantic Evolution Rules

The rules define when the event should be proposed.

### Relation to Implementation

The eventual code will realize this model as producers, validators, appliers, and recorders.

---

## 13. Scope

This document defines the event processing model for SRP.

It does not define:

- the concrete event class implementation
- the dispatcher implementation
- the storage backend

Those belong to the later runtime implementation phase.
