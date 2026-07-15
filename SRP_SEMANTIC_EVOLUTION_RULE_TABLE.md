# SRP Semantic Evolution Rule Table

This document freezes the decision boundary for semantic evolution in SRP.
It is not an implementation spec.

The central question is:

> Given a runtime state and its signals, what semantic transition is allowed, which event should be emitted, and when must automatic handling be blocked?

This table is the operational bridge between the event contract and the evolution rules.

---

## 1. Decision Boundary

```text
Runtime State
    -> Rule Evaluation
    -> Event Selection
    -> Contract-Valid Mutation
    -> New Runtime State
```

The rule table defines:

- what signals trigger a rule
- what event the rule emits
- what state transition follows
- what invariants must hold
- whether the action is automatic or requires confirmation

---

## 2. Rule Priority

When rules compete, the default priority order is:

```text
Identity Preservation
  >
Structural Preservation
  >
Recovery Potential
  >
Value Allocation
  >
Garbage Collection
```

This ordering means:

- do not destroy identity if structure can still be preserved
- do not destroy structure if recovery can still repair it
- do not remove recoverable content if it still has value
- do not collect content if it still has meaningful references or likely reuse

Policy may override thresholds, but not these priority relations without an explicit design change.

---

## 3. Rule Table

| Rule | Trigger Condition | Input Signals | Event | State Transition | Invariants | Auto / Manual |
| --- | --- | --- | --- | --- | --- | --- |
| Alias Consolidation | Multiple units represent the same surface identity | `semantic_similarity`, `context_usage_overlap`, `entity_type_match`, alias history | `Canonicalized` | Many forms -> one canonical unit + aliases | one canonical name, aliases unique, provenance preserved | Auto when confidence is high |
| Identity Merge | Two units are likely the same identity, not merely similar | `identity_confidence`, context evidence, relation consistency, lineage overlap | `Merged` | Entity A + Entity B -> unified entity with lineage | no merge without lineage, no silent identity loss | Auto only above strict threshold |
| Concept Refinement | One concept is broader / narrower / structured relative to another | `is_a` evidence, relation evidence, type compatibility | `Consolidated` | Concept family strengthened; broader/narrower relation added | do not collapse distinct concepts, preserve relational distinction | Auto if relation evidence is strong |
| Activation Decay | Unit unused for a decay window or repeatedly unused | `current_round`, `last_used_round`, `usage_count`, `importance`, `confidence` | `ActivationUpdated` | activation decreases, retention priority may decrease | `0 <= activation <= 1` | Auto |
| Approximation | Activation is low and a close semantic surrogate exists | `activation`, replacement candidate confidence, semantic distance, context fit | `Approximated` | Original concept -> surrogate placeholder / approximation | approximation must record distance, must remain non-identical | Auto if surrogate confidence passes threshold |
| Soft Forgetting | Low activation, low recovery value, no strong dependency, or explicit forget request | `activation`, recovery value, dependency centrality, archive state, user intent | `Forgotten` | Active -> dormant / forgotten / archived-with-reference | forgetting must preserve traceability unless hard deletion is explicit | Auto for decay; manual for explicit user forget |
| Recovery Candidate Generation | Missing or approximate concept encountered | graph neighbors, prior events, embeddings, historical contexts, alias history | `RecoveryRequested` | Missing concept -> candidate set | candidates must be evidence-backed | Auto |
| Recovery Validation | Candidate has 3 or more independent supporting contexts or passes confidence threshold | candidate similarity, context agreement, variance penalty, provenance match | `Recovered` | Approximate / missing -> restored concept | no recovery without provenance, no low-confidence silent overwrite | Auto if threshold is met; otherwise manual |
| Preservation-First Retention | Content is still structurally important or identity-critical | dependency centrality, relation criticality, lineage relevance, usage recency | `ActivationUpdated` or no-op | retention priority increased or preserved | identity and structure outrank value trimming | Auto |
| Garbage Collection | No active references, no meaningful relations, low recovery value, negligible preservation impact | reference count, relation degree, recovery probability, drift impact | `GarbageCollected` | Archived / dormant -> collected | must not collect while required references remain | Manual or gated auto only |
| Validation Failure Response | Recovered output fails contract or drift gates | drift, coverage, dependency coverage, leakage, critical failures | `RepairTriggered` | validation failure -> repair path | repair must remain auditable and bounded | Auto if repair is enabled |

---

## 4. Rule Details

### 4.1 Alias Consolidation

Alias consolidation is used when different spellings, abbreviations, or surface forms point to the same unit.

Examples:

- `Open AI`
- `OpenAI`
- `OAI`

Trigger:

```text
semantic_similarity > θ1
AND context_usage_overlap > θ2
AND entity_type_match = true
```

Allowed state change:

- preserve one canonical unit
- preserve aliases in metadata or description

Forbidden:

- destroying provenance
- producing multiple canonical ids for the same confirmed identity

### 4.2 Identity Merge

Identity merge is stricter than alias consolidation.

Examples:

- `John Smith`
- `the CEO`

Trigger:

```text
identity_confidence > θ1
AND evidence_sufficient = true
AND relation_consistency = true
```

Allowed state change:

- unify identities
- preserve lineage chain

Forbidden:

- merge without lineage
- merge based on vector similarity alone

### 4.3 Concept Refinement

Concept refinement is not aliasing.
It is a relation-preserving structural update.

Examples:

- `vehicle`
- `Tesla`

Trigger:

```text
broader_concept_match = true
AND relation_evidence > θ
```

Allowed state change:

- add or strengthen `is-a` style relations
- keep both concepts distinct

Forbidden:

- semantic collapse
- treating hierarchy as aliasing

### 4.4 Activation Decay

Activation decay should be gradual and usage-aware.

Trigger:

```text
current_round - last_used_round > decay_window
```

Allowed state change:

- lower activation
- lower retention priority when appropriate

Forbidden:

- dropping to zero without a rule
- deleting active or structurally necessary units by default

### 4.5 Approximation

Approximation is controlled degradation.

Trigger:

```text
activation < approximation_threshold
AND replacement_candidate_confidence > threshold
```

Allowed state change:

- replace with a semantically close surrogate
- record approximation distance and confidence

Forbidden:

- equating surrogate with original identity
- omitting the approximation gap

### 4.6 Soft Forgetting

Soft forgetting is allowed when the unit is unlikely to be recovered and no longer carries useful structural load.

Trigger:

```text
activation low
AND recovery_value low
AND dependency_centrality low
```

Allowed state change:

- mark dormant or forgotten
- preserve optional archive reference

Forbidden:

- forgetting a unit that still has required references
- hard deletion by default

### 4.7 Recovery

Recovery is evidence-based restoration.

Trigger:

```text
missing_reference = true
OR unknown_placeholder encountered
OR approximation needs validation
```

Candidate generation inputs:

- graph neighbors
- prior events
- embeddings
- historical contexts
- alias history

Validation rule:

```text
supporting_contexts >= 3
AND recovery_confidence >= threshold
```

Allowed state change:

- emit `Recovered`
- restore content and provenance trail

Forbidden:

- recovery without provenance
- auto-recovery below confidence threshold without confirmation

### 4.8 Garbage Collection

Garbage collection is the final and most restrictive transition.

Trigger:

```text
active_reference_count = 0
AND relation_degree = 0
AND recovery_probability low
AND preservation_impact negligible
```

Allowed state change:

- collected / removed from active runtime storage

Forbidden:

- collecting referenced content
- collecting content with meaningful recovery utility

### 4.9 Validation Failure Response

Validation failure does not directly mutate semantic meaning.
It opens a repair path.

Trigger:

- drift above threshold
- coverage below threshold
- leakage detected
- critical failure detected

Allowed state change:

- emit `RepairTriggered`
- construct a bounded repair package

Forbidden:

- silent mutation
- untracked repair

---

## 5. Invariant Summary

The rule table assumes these invariants:

- `activation` must remain within `[0, 1]`
- `confidence` must remain within `[0, 1]`
- canonical identity requires exactly one preferred canonical name
- aliases must be unique within a unit
- recovery must have provenance
- approximation must have recorded error or distance
- hard deletion must be explicit and distinguishable from forgetting
- collection must not occur while references remain

---

## 6. Relation to Policy

Policy chooses among valid options under pressure.
The rule table defines which options are valid at all.

That means:

- policy may prefer retention over approximation
- policy may prefer approximation over forgetting
- policy may prefer forgetting over garbage collection
- but policy may not violate event legality or invariants

---

## 7. Scope

This document freezes the decision boundary for semantic evolution.

It does not define:

- handler implementation
- scoring functions
- event serialization

Those belong to later protocol and code layers.
