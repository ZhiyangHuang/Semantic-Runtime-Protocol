# SRP Runtime Data Contract

This document defines the behavioral contract for SRP runtime objects.
It is not a schema spec and not an implementation spec.

The central question is:

> What do runtime fields mean, who may change them, what invariants must hold, and how do objects evolve over time?

This is the protocol layer between object shape and executable behavior.

---

## 1. Why a Data Contract

A schema tells us what fields exist.
A data contract tells us:

- what each field means
- who owns each field
- which module may update it
- what invariants must hold
- how events change the field over time
- how reference integrity is preserved

SRP needs this layer because it is a runtime protocol, not just a storage format.

The legal transition rules for these fields are defined in [Runtime Event Contract](SRP_RUNTIME_EVENT_CONTRACT.md).
The atomic unit model that owns these fields is defined in [Semantic Unit Model](SRP_SEMANTIC_UNIT_MODEL.md).
The field-level meaning of `SemanticUnit` is specified in [Semantic Unit Field Specification](SRP_SEMANTIC_UNIT_FIELD_SPEC.md).

---

## 2. Contract Scope

The contract applies to these runtime objects:

- `SemanticUnit`
- `RelationUnit`
- `RuntimeContext`
- `SemanticState`

It also defines the shared event and history model used across those objects.

---

## 3. SemanticUnit Contract

`SemanticUnit` is the core runtime object.

### Field contract

| Field | Type | Owner | Mutable | Updated By | Invariant |
| --- | --- | --- | --- | --- | --- |
| `id` | UUID | Runtime | No | Runtime | Never changes |
| `type` | Enum | Extraction | No | Extraction | Must be valid semantic type |
| `canonical_name` | String | Canonicalization | Yes | Canonicalization | Exactly one canonical name |
| `aliases` | List[String] | Consolidation | Yes | Consolidation | No duplicate aliases |
| `semantic_content` | Object | Representation | Yes | Extraction / Representation | Must remain semantically aligned |
| `relations` | List[Ref] | Representation | Yes | Representation | References must be valid |
| `activation` | Float | Evolution | Yes | Activation / Recovery | `0 <= activation <= 1` |
| `importance` | Float | Policy | Yes | Policy | Normalized score |
| `confidence` | Float | Recovery | Yes | Recovery / Validation | `0 <= confidence <= 1` |
| `lifecycle` | Enum | Lifecycle | Yes | Lifecycle | Valid state transition only |
| `evolution` | Enum or object | Evolution | Yes | Evolution | Must match evolution state machine |
| `provenance` | Object | Extraction | Yes | Extraction / Recovery | Must remain traceable |
| `created_round` | Int | Runtime | No | Runtime | Never changes |
| `updated_round` | Int | Runtime | Yes | Any mutating module | Must be monotonic |
| `lineage` | Ref or path | Runtime | No | Runtime | Must preserve origin chain |

### SemanticUnit rules

- `canonical_name` is the preferred surface name at any time.
- `aliases` must preserve historical names and equivalent forms.
- `activation` measures current recall strength, not permanent importance.
- `importance` measures retention priority under pressure.
- `confidence` measures trust in the unit as currently represented.
- `lifecycle` tracks runtime condition.
- `evolution` tracks semantic drift and state progression.

---

## 4. RelationUnit Contract

`RelationUnit` represents a typed semantic connection.

### Field contract

| Field | Type | Owner | Mutable | Updated By | Invariant |
| --- | --- | --- | --- | --- | --- |
| `id` | UUID | Runtime | No | Runtime | Never changes |
| `source` | Ref | Representation | Yes | Representation / Recovery | Must point to valid unit or approved placeholder |
| `target` | Ref | Representation | Yes | Representation / Recovery | Must point to valid unit or approved placeholder |
| `relation_type` | Enum | Representation | No | Extraction / Representation | Must be valid relation kind |
| `confidence` | Float | Recovery | Yes | Recovery / Validation | `0 <= confidence <= 1` |
| `criticality` | Float | Policy | Yes | Policy | Normalized score |
| `created_round` | Int | Runtime | No | Runtime | Never changes |
| `updated_round` | Int | Runtime | Yes | Any mutating module | Must be monotonic |

### Reference integrity rules

When a source or target is removed, the system must choose one of the following behaviors:

- cascade delete
- archive pointer
- unknown placeholder
- approximation replacement

The chosen behavior should be explicit and auditable.

---

## 5. RuntimeContext Contract

`RuntimeContext` carries the current runtime conditions.

### Field contract

| Field | Type | Owner | Mutable | Updated By | Invariant |
| --- | --- | --- | --- | --- | --- |
| `budget` | Number | Runtime | Yes | Runtime / Policy | Must be non-negative |
| `pressure` | Number | Runtime | Yes | Runtime / Policy | Must be normalized or documented |
| `current_round` | Int | Runtime | Yes | Runtime | Monotonic increase |
| `policy` | Object or Enum | Policy | Yes | Policy | Must refer to active policy |
| `memory_usage` | Number | Runtime | Yes | Runtime | Must reflect current state |
| `compression_level` | Number or Enum | Runtime | Yes | Compression | Must reflect current regime |

### RuntimeContext rules

- Policy reads `RuntimeContext`.
- Evolution reads `current_round`.
- Maintenance reads pressure and budget to decide decay and replacement.
- Recovery may use context to decide whether to auto-recover or ask for confirmation.

---

## 6. SemanticState Contract

`SemanticState` is the container contract for the runtime world.

### Field contract

| Field | Type | Owner | Mutable | Updated By | Invariant |
| --- | --- | --- | --- | --- | --- |
| `units` | List[SemanticUnit] | State | Yes | Multiple modules | All unit ids unique |
| `relations` | List[RelationUnit] | State | Yes | Multiple modules | All relation ids unique |
| `context` | RuntimeContext | State | Yes | Runtime / Policy | Must exist |
| `history` | HistoryObject | State | Yes | Multiple modules | Must be internally consistent |

### SemanticState rules

- The state object is a container, not the source of truth for every field.
- Mutable objects inside the state own their own evolution data.
- Collection-level history belongs here.

---

## 7. History Contract

`History` should not mean only "past events".
It should be the evolution record for a semantic unit or state package.

History has two parts:

1. `EventStream`
2. `EvolutionSummary`

### 7.1 EventStream

Event stream stores fine-grained changes in order.

Typical events:

- `Extracted`
- `Canonicalized`
- `Merged`
- `Activated`
- `Archived`
- `Recovered`
- `Forgotten`
- `Approximated`
- `Deleted`

### 7.2 EvolutionSummary

Evolution summary stores aggregate drift and maintenance statistics.

Suggested fields:

- `origin_vector`
- `current_vector`
- `current_drift`
- `accumulated_drift`
- `recovery_count`
- `approximation_count`
- `archive_count`
- `merge_count`
- `activation_integral`
- `average_confidence`

### 7.3 History rules

- EventStream is for explanation and replay.
- EvolutionSummary is for drift analysis and fast inspection.
- History must preserve both the trace and the summary.
- EventStream may be compacted, but EvolutionSummary should remain available.

---

## 8. Event Contract

Events are first-class protocol objects.

### Generic event fields

| Field | Type | Owner | Mutable | Updated By | Invariant |
| --- | --- | --- | --- | --- | --- |
| `event_id` | UUID | Runtime | No | Runtime | Never changes |
| `event_type` | Enum | Runtime | No | Runtime | Must be valid event type |
| `timestamp_or_round` | Int | Runtime | No | Runtime | Monotonic per stream |
| `target` | Ref | Runtime | No | Runtime | Must refer to object in scope |
| `before` | Object | Runtime | No | Runtime | Captures prior value or state |
| `after` | Object | Runtime | No | Runtime | Captures resulting value or state |
| `reason` | String | Runtime | Yes | Multiple modules | Human-auditable rationale |
| `confidence` | Float | Recovery | Yes | Recovery / Validation | `0 <= confidence <= 1` |

### Event model rule

An event records a transition.
History records the evolution caused by those transitions.

---

## 9. Capability Matrix

This matrix defines which object families support which operations.

| Object | Archive | Forget | Recover | Consolidate | Approximate |
| --- | --- | --- | --- | --- | --- |
| `SemanticUnit` | Yes | Yes | Yes | Yes | Yes |
| `RelationUnit` | Yes | Yes | Yes | Limited | No |
| `RuntimeContext` | No | No | No | No | No |
| `SemanticState` | Yes | Yes | Yes | Yes | Yes |

Notes:

- Relation consolidation is limited because some relations should not be merged automatically.
- RuntimeContext should not be treated as a memory object.

---

## 10. Reference Integrity

Reference integrity is a protocol requirement.

If one object points to another object, the reference must remain valid or be replaced through an explicit policy.

Allowed resolution strategies:

- `cascade_delete`
- `archive_pointer`
- `unknown_placeholder`
- `approximation`

This must be chosen explicitly so downstream modules can interpret the result correctly.

---

## 11. Module Contract Surface

Each module should consume and produce explicit object changes.

Suggested flow:

```text
SemanticUnit
  -> ActivationModel emits ActivationEvent
  -> Policy emits RetentionDecision
  -> Lifecycle emits LifecycleTransition
  -> Evolution emits EvolutionUpdate
  -> Recovery emits RecoveryEvent
  -> History updates EventStream and EvolutionSummary
```

This is the protocol shape SRP should expose.

---

## 12. Scope

This document defines the behavioral contract for SRP runtime objects.

It does not define:

- the exact JSON or Python schema syntax
- the storage engine
- the implementation of event emission
- the benchmark suite

Those belong to later implementation documents.
