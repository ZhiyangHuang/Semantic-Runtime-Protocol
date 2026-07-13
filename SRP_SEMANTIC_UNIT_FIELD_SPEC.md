# SRP Semantic Unit Field Specification

This document freezes the field-level specification for `SemanticUnit`.
It is not an implementation spec.

The central question is:

> What does each `SemanticUnit` field mean, who owns it, what may mutate it, and what invariant must always hold?

This document is the last theory-level anchor before code mapping.

---

## 1. Field Specification Table

| Field | Category | Meaning | Mutable | Owner | Invariant |
| --- | --- | --- | --- | --- | --- |
| `unit_id` | identity | Unique semantic unit identity | No | Identity Manager / Runtime | Never reused |
| `canonical_name` | identity | Current preferred surface name | Yes | Consolidation | Exactly one canonical name at a time |
| `aliases` | identity | Historical or alternate forms | Yes | Consolidation | Unique, no loss of prior forms |
| `lineage` | identity | Origin and merge history chain | Append-only | Evolution | Not deleted |
| `semantic_description` | semantic | Current semantic meaning summary | Yes | Refinement | Must preserve source trace |
| `embedding` | semantic | Current semantic representation | Yes | Encoder | Version-bound |
| `historical_embeddings` | semantic | Prior reference representations | Append-only | Evaluation / Recovery | Preserves drift history |
| `reference_embeddings` | semantic | Reference vectors for comparison | Yes | Evaluation | Must correspond to named reference set |
| `relations` | structure | External semantic links | Yes | Relation Manager | References must be valid or explicitly placeholder-based |
| `activation` | memory | Current salience / recall strength | Yes | Lifecycle | `0 <= activation <= 1` |
| `last_used_round` | memory | Most recent usage round | Yes | Runtime | Monotonic increase |
| `decay_state` | memory | Current forgetting state | Yes | Forgetting | Must be one of the allowed states |
| `importance` | policy | Retention priority | Yes | Policy | Must be explainable |
| `confidence` | metadata | Evidence-based reliability | Yes | Validation / Recovery | `0 <= confidence <= 1` |
| `provenance` | metadata | Source trace and extraction lineage | Append-only | Ingestion | Must not be lost |
| `lifecycle_state` | lifecycle | Current lifecycle position | Yes | Lifecycle | Must satisfy state machine |
| `approximation_target` | evolution | Surrogate or replacement unit | Yes | Approximation | Must be traceable |
| `drift_score` | evolution | Cumulative semantic deviation | Append-only | Evaluation | Non-negative |
| `history_pointer` | history | Reference to event stream / summary | Yes | History | Must resolve to trace or archive |

---

## 2. Identity Fields

Identity fields define what the unit is.

### `unit_id`

- the primary immutable identity of the unit
- must not be derived from `canonical_name`
- may not be reused even if the unit is forgotten or collected

### `canonical_name`

- the current preferred surface form
- may change through canonicalization or consolidation
- does not define identity by itself

### `aliases`

- historical names, abbreviations, and equivalent forms
- must preserve prior observations
- should not overwrite prior forms

### `lineage`

- records origin, merge history, and inheritance path
- append-only
- crucial for identity continuity and recovery auditing

---

## 3. Semantic Fields

Semantic fields define what the unit means.

### `semantic_description`

- normalized description of the concept
- may be rewritten by refinement or recovery
- must preserve traceability to source evidence

### `embedding`

- current vector representation of the unit
- version-bound
- should not be treated as the only semantic truth

### `historical_embeddings`

- previous vector snapshots
- used for drift comparison and recovery validation
- append-only by default

### `reference_embeddings`

- comparison vectors used for recovery or drift evaluation
- may represent important historical or canonical states

---

## 4. Structure Fields

Structure fields define how the unit connects to other units.

### `relations`

- typed references to other units
- preserve dependency, hierarchy, causality, and equivalence links
- must remain valid or be replaced by an explicit placeholder strategy

Relation integrity rules:

- relation endpoints may not silently disappear
- relation rewrites must remain auditable
- identity merge and relation refinement must not be conflated

---

## 5. Memory Fields

Memory fields define how the unit changes over time.

### `activation`

- current salience or recall strength
- should increase with use and decrease with decay
- must remain in `[0, 1]`

### `last_used_round`

- most recent round in which the unit was referenced
- monotonic increase only

### `decay_state`

- the current forgetting state of the unit
- should be selected from a finite state set, such as:
  - `active`
  - `stable`
  - `inactive`
  - `dormant`
  - `approximate`
  - `forgotten`

### `importance`

- retention priority under budget pressure
- should be explainable from policy or value signals

---

## 6. Metadata Fields

Metadata fields support traceability and evaluation.

### `confidence`

- evidence-based reliability score
- used by validation, recovery, and consolidation
- must remain within `[0, 1]`

### `provenance`

- source trace, extraction lineage, and evidence chain
- append-only
- must survive canonicalization, merge, and recovery when possible

---

## 7. Lifecycle and Evolution Fields

### `lifecycle_state`

- current lifecycle state of the unit
- must follow the lifecycle state machine

### `approximation_target`

- references the surrogate used when the original unit is replaced by approximation
- must be traceable
- must not erase the original unit's identity

### `drift_score`

- cumulative semantic deviation from the original or reference state
- non-negative
- append-only by default

### `history_pointer`

- reference to event stream and evolution summary
- should point to a shared history record rather than embedding the full history inside the unit

---

## 8. Allowed Mutation Ownership

| Field Group | Primary Owner | Typical Mutator |
| --- | --- | --- |
| Identity | Consolidation / Evolution | canonicalization, merge, split |
| Semantic | Refinement / Recovery | refinement, recovery, extraction |
| Structure | Relation Manager | relation updates, graph repair |
| Memory | Lifecycle / Forgetting | activation, decay, state shift |
| Policy | Policy | importance and retention decisions |
| Metadata | Validation / Ingestion | confidence, provenance updates |
| Lifecycle | Lifecycle | state transitions |
| Evolution | Approximation / Evaluation | approximation target, drift |
| History | History / Runtime | event references and summary pointers |

This ownership is conceptual and should guide implementation boundaries later.

---

## 9. Unit-Level Invariants

The following invariants should hold whenever possible:

- one canonical name at a time
- aliases unique within the unit
- unit id never reused
- activation in `[0, 1]`
- confidence in `[0, 1]`
- last used round is monotonic
- provenance is append-only
- lineage is append-only
- approximation must record distance or error
- history must remain reachable through a pointer or summary reference
- relations must not point to invalid objects without explicit placeholder handling

---

## 10. Relationship to Other Layers

### Relationship to Semantic Unit Model

This document refines the semantic unit model into explicit fields.

### Relationship to Runtime Data Contract

The runtime data contract governs the behavior of these fields at the container level.

### Relationship to Runtime Event Contract

The event contract governs which events may mutate which fields.

### Relationship to Evolution Rules

The evolution rules govern when those field changes should happen.

---

## 11. Scope

This document freezes the field-level specification for `SemanticUnit`.

It does not define:

- the object model container
- the event schema
- the rule engine
- the code implementation

Those are covered by the neighboring SRP theory layers.
