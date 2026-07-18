# SRP Runtime Event Contract

This document defines the legal transition layer for SRP runtime objects.
It is not a schema spec and not an implementation spec.

The central question is:

> What counts as a valid semantic transition, what fields may it change, and what must remain invariant?

This layer sits between the runtime data contract and the module-level protocol map.
The conditions that justify each event are defined in [Semantic Evolution Rules](SRP_SEMANTIC_EVOLUTION_RULES.md).
The engineering-facing event handling shape is defined in [Runtime Event Interface](SRP_RUNTIME_EVENT_INTERFACE.md).
The producer / validator / applier lifecycle is defined in [Runtime Event Processing Model](SRP_RUNTIME_EVENT_PROCESSING_MODEL.md).

---

## 1. Event Role

In SRP, an event is not a log entry.

An event is a permitted transition from one semantic state to another.

```text
Before State
    -> Event
    -> After State
```

Events are the only sanctioned way to mutate runtime semantic objects.

---

## 2. Event Object Contract

Every event should be treated as a first-class runtime object.

### Common event fields

| Field | Type | Meaning | Invariant |
| --- | --- | --- | --- |
| `event_id` | UUID | Unique event identity | Never changes |
| `event_type` | Enum | Transition family | Must be valid |
| `timestamp_or_round` | Int | When the event happened | Monotonic in stream |
| `actor` | String or Enum | Module or subsystem that emitted it | Must be traceable |
| `targets` | List[Ref] | Objects affected by the event | Must refer to valid or explicitly placeholder objects |
| `payload` | Object | Transition-specific details | Must satisfy event-specific schema |
| `before` | Object | Prior value or snapshot | Must match the affected fields before mutation |
| `after` | Object | Resulting value or snapshot | Must match the affected fields after mutation |
| `reason` | String | Why the event occurred | Human-auditable |
| `confidence` | Float | Certainty of the transition | `0 <= confidence <= 1` |
| `mutation_mode` | Enum | How the mutation applies | Must be valid for the event type |

### Event invariants

- every event must identify what it changes
- every event must identify who emitted it
- every event must be reversible in explanation, even if not reversible in execution
- event payloads must be specific enough for downstream validation

---

## 3. Event Kinds

The current SRP protocol can be expressed through these event families:

- `SemanticExtracted`
- `Canonicalized`
- `Merged`
- `Consolidated`
- `ActivationUpdated`
- `Approximated`
- `Forgotten`
- `Recovered`
- `CompressionSelected`
- `CompressedPackageProduced`
- `RecoveryRequested`
- `RecoveryResultProduced`
- `StructuredStatePackageProduced`
- `AllocationDecided`
- `ExecutionPayloadSelected`
- `ValidationPerformed`
- `RepairTriggered`
- `LifecycleTransitioned`
- `DriftMeasured`
- `HistorySummarized`

---

## 4. Canonical Event Schemas

### 4.1 `SemanticExtracted`

Creates a new semantic unit from raw input.

#### Typical trigger

```text
raw input -> semantic parser
```

#### Affected objects

- `SemanticUnit`
- `SemanticState`

#### Mutation mode

- `create`

#### Payload

| Field | Meaning |
| --- | --- |
| `semantic_unit_id` | Newly created unit id |
| `extracted_content` | Normalized semantic content |
| `source_reference` | Origin pointer into raw input |
| `confidence` | Extraction confidence |
| `extraction_model` | Parser or model used |
| `provenance` | Source and lineage metadata |

#### Invariants

- new `SemanticUnit` must carry provenance
- confidence must be in `[0, 1]`
- unit id must be unique

---

### 4.2 `Canonicalized`

Normalizes equivalent semantic forms into one canonical concept.

#### Typical trigger

```text
alias / synonym / equivalent form -> canonical concept
```

#### Affected objects

- `SemanticUnit`

#### Mutation mode

- `update`
- `merge`

#### Payload

| Field | Meaning |
| --- | --- |
| `canonical_id` | The surviving canonical unit |
| `merged_units` | Units absorbed into the canonical unit |
| `aliases` | Alias list preserved on the canonical unit |
| `rule` | Canonicalization rule used |
| `confidence` | Canonicalization confidence |

#### Invariants

- exactly one canonical name should remain active
- aliases must not duplicate canonical_name
- merged units must retain traceability in lineage or history

---

### 4.3 `Merged`

Combines semantically redundant units.

#### Affected objects

- `SemanticUnit`
- `RelationUnit` when relation endpoints collapse through merge

#### Mutation mode

- `merge`

#### Payload

| Field | Meaning |
| --- | --- |
| `primary_unit_id` | Surviving unit |
| `absorbed_unit_ids` | Removed or folded units |
| `alias_updates` | Alias list changes |
| `relation_updates` | Relation rewrites caused by merge |
| `supporting_evidence` | Evidence for merge decision |

#### Invariants

- merge must preserve provenance
- relation rewrites must remain valid
- merge should not silently delete origin identity

---

### 4.4 `Consolidated`

Turns repeated co-activation into stable structure.

#### Affected objects

- `SemanticUnit`
- `RelationUnit`

#### Mutation mode

- `update`
- `stabilize`

#### Payload

| Field | Meaning |
| --- | --- |
| `unit_ids` | Units entering consolidation |
| `structure_id` | Consolidated structure identifier |
| `alias_updates` | New aliases or family grouping |
| `relation_updates` | Consolidated relation links |
| `consolidation_score` | Stability score |

#### Invariants

- consolidation should only strengthen semantically supported groupings
- consolidation must not contradict provenance

---

### 4.5 `ActivationUpdated`

Updates a unit's salience or recall strength.

#### Affected objects

- `SemanticUnit`
- `RuntimeContext` when activation is tracked globally

#### Mutation mode

- `update`

#### Payload

| Field | Meaning |
| --- | --- |
| `unit_id` | Target semantic unit |
| `old_activation` | Previous activation value |
| `new_activation` | Updated activation value |
| `reason` | Why activation changed |
| `decay_source` | Recency / frequency / pressure / usage |
| `reactivation_bonus` | Bonus from successful reuse |

#### Invariants

- activation must stay within `[0, 1]`
- activation updates must be monotonic only if the rule says so; otherwise they may rise or fall
- each update must preserve the trail explaining why the change happened

---

### 4.6 `Approximated`

Replaces a weak or forgotten concept with a semantically similar surrogate.

#### Affected objects

- `SemanticUnit`
- `RelationUnit` if endpoints are approximated

#### Mutation mode

- `replace`

#### Payload

| Field | Meaning |
| --- | --- |
| `original_unit_id` | Concept being approximated |
| `approximation_unit_id` | Surrogate concept |
| `approximation_error` | Distance from original |
| `replacement_vector_distance` | Embedding distance or semantic gap |
| `replacement_reason` | Why approximation occurred |

#### Invariants

- approximation must preserve non-identical status
- surrogate must be marked as approximation, not as original
- error and distance must be recorded

---

### 4.7 `Forgotten`

Soft-forgets a unit under decay or explicit user intent.

#### Affected objects

- `SemanticUnit`

#### Mutation mode

- `deprecate`
- `hide`
- `soft_delete`

#### Payload

| Field | Meaning |
| --- | --- |
| `forgotten_unit_id` | Target unit |
| `replacement_id` | Approximation or placeholder, if any |
| `memory_strength` | Remaining activation or recall strength |
| `forget_reason` | Decay threshold, user request, or policy decision |

#### Invariants

- forgetting should not remove traceability by default
- hard deletion is a separate event family or a later stage

---

### 4.8 `Recovered`

Restores a forgotten or approximate concept from evidence.

#### Affected objects

- `SemanticUnit`
- `RelationUnit`

#### Mutation mode

- `restore`

#### Payload

| Field | Meaning |
| --- | --- |
| `recovered_unit_id` | Restored target |
| `candidate_ids` | Possible reconstructions |
| `supporting_contexts` | Evidence contexts used |
| `agreement_score` | Cross-evidence score |
| `confidence` | Recovery confidence |

#### Invariants

- recovery should be evidence-based
- low-confidence recovery must not silently overwrite the original
- if agreement is below threshold, user confirmation is required

---

### 4.9 `CompressionSelected`

Selects objects or spans to preserve under compression pressure.

#### Affected objects

- `SemanticState`
- `SemanticUnit`
- `RelationUnit`

#### Mutation mode

- `select`

#### Payload

| Field | Meaning |
| --- | --- |
| `selected_ids` | Retained items |
| `rejected_ids` | Dropped items |
| `selection_scores` | Why each item survived |
| `selection_reason` | Compression rationale |

#### Invariants

- selection must be explainable
- retained critical items should be traceable

---

### 4.10 `CompressedPackageProduced`

Creates the compact package used for recovery.

#### Mutation mode

- `materialize`

#### Payload

| Field | Meaning |
| --- | --- |
| `package_id` | Output package id |
| `compressed_state_ref` | Reference to compact state |
| `selected_ids` | Included objects |
| `loss_notes` | Known losses or risks |

#### Invariants

- package must remain recoverable within the supported budget
- package should preserve essential provenance and constraints

---

### 4.11 `RecoveryRequested`

Requests recovery from a compressed or degraded package.

#### Affected objects

- `SemanticState`

#### Mutation mode

- `request`

#### Payload

| Field | Meaning |
| --- | --- |
| `package_ref` | Package to recover from |
| `anchor_memory` | Stable anchor text |
| `recovery_policy` | Policy selected |
| `goal` | Recovery objective |

#### Invariants

- request must specify the recovery context
- recovery policy must be explicit

---

### 4.12 `RecoveryResultProduced`

Emits the structured result of recovery.

#### Affected objects

- `SemanticState`

#### Mutation mode

- `produce`

#### Payload

| Field | Meaning |
| --- | --- |
| `recovered_state_package` | Structured recovered state |
| `usage` | Token or resource usage |
| `policy_name` | Recovery policy used |
| `metrics` | Recovery metrics |

#### Invariants

- recovered package must match the recovery policy contract
- metrics must be consistent with the output state

---

### 4.13 `StructuredStatePackageProduced`

Exports the structured state package used by downstream modules.

#### Affected objects

- `SemanticState`

#### Mutation mode

- `materialize`

#### Invariants

- package must be internally consistent
- package should preserve object ids, typed representation, and inventory links

---

### 4.14 `AllocationDecided`

Partitions recovered objects into active, latent, and discard subsets.

#### Affected objects

- `SemanticState`

#### Mutation mode

- `partition`

#### Invariants

- allocation must not mutate object semantics
- allocation must not merge or repair objects

---

### 4.15 `ExecutionPayloadSelected`

Selects the object subset passed to execution.

#### Affected objects

- `SemanticState`

#### Mutation mode

- `project`

#### Invariants

- execution payload must reflect the selected allocation source
- payload projection must not invent new semantic facts

---

### 4.16 `ValidationPerformed`

Compares recovered or executed output against the source target.

#### Affected objects

- `SemanticState`
- `RuntimeContext`

#### Mutation mode

- `measure`

#### Invariants

- validation must be deterministic for a given input and target set
- validation output must include drift, alignment, and pass/fail evidence

---

### 4.17 `LifecycleTransitioned`

Moves a unit between lifecycle states.

#### Affected objects

- `SemanticUnit`

#### Mutation mode

- `transition`

#### Invariants

- only valid lifecycle transitions are allowed
- lifecycle transitions must be explainable by verification or policy

---

### 4.18 `DriftMeasured`

Captures semantic drift between successive states.

#### Affected objects

- `SemanticState`
- `SemanticUnit`

#### Mutation mode

- `measure`

#### Invariants

- drift values must be consistent with the comparison basis used
- drift should be decomposable into identity, relation, approximation, and confidence components when possible

---

### 4.19 `HistorySummarized`

Updates aggregate history and drift summaries.

#### Affected objects

- `SemanticUnit`
- `SemanticState`

#### Mutation mode

- `summarize`

#### Invariants

- history summary must retain event trace linkage
- summary must preserve current drift and accumulated drift if available

---

### 4.20 `RepairTriggered`

Creates a repair path after validation failure.

#### Affected objects

- `SemanticState`

#### Mutation mode

- `repair`

#### Invariants

- repair must be explicitly tied to validation failure
- repair may patch or constrain, but it must remain auditable

---

## 5. Mutation Rules by Event

The allowed mutation scope should be explicit.

| Event | Allowed Object Changes |
| --- | --- |
| `SemanticExtracted` | create `SemanticUnit`, set provenance, initial confidence |
| `Canonicalized` | change `canonical_name`, update `aliases`, update lineage |
| `Merged` | update aliases, relations, lineage, confidence |
| `Consolidated` | update alias families, relations, activation, stability metadata |
| `ActivationUpdated` | update activation and supporting activation metadata |
| `Approximated` | replace with surrogate, attach approximation error, mark non-identical status |
| `Forgotten` | lower visibility or strength, attach replacement or placeholder |
| `Recovered` | restore content, confidence, activation, and supporting evidence |
| `CompressionSelected` | mark selected/rejected sets, no semantic rewrite |
| `CompressedPackageProduced` | materialize package, no semantic invention |
| `RecoveryRequested` | no object mutation by itself |
| `RecoveryResultProduced` | materialize recovered package |
| `StructuredStatePackageProduced` | materialize structured package |
| `AllocationDecided` | partition only, no semantic mutation |
| `ExecutionPayloadSelected` | project only, no semantic mutation |
| `ValidationPerformed` | write validation metrics and audit data |
| `LifecycleTransitioned` | update lifecycle state |
| `DriftMeasured` | update drift metrics |
| `HistorySummarized` | update history summary fields |
| `RepairTriggered` | create repair package and repair context |

---

## 6. Field Invariant Examples

Common invariants include:

- `activation` must stay in `[0, 1]`
- `confidence` must stay in `[0, 1]`
- `canonical_name` should be exactly one preferred name at a time
- `aliases` must be unique within a unit
- `event_id` must never change
- `timestamp_or_round` must be monotonic per event stream
- `updated_round` must not go backwards
- deleted or forgotten units must preserve traceability unless hard deletion is explicitly allowed

---

## 7. Event to Contract Relationship

Events are the legal transitions.
The runtime data contract defines the fields those transitions may touch.

So the relationship is:

```text
Data Contract
  -> defines fields and invariants
Event Contract
  -> defines legal transitions over those fields
Protocol Map
  -> shows which module emits or consumes each event
```

---

## 8. Scope

This document defines the transition contract for SRP runtime objects.

It does not define:

- the concrete event class hierarchy
- the serialization format
- the implementation of event handlers

Those belong to later implementation documents.
