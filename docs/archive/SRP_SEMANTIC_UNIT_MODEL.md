# SRP Semantic Unit Model

This document defines the atomic semantic object used by SRP.
It is not an implementation spec.

The central question is:

> What is the smallest semantically meaningful unit that can evolve, retain identity, decay, recover, and participate in relations?

The answer is `SemanticUnit`.

---

## 1. Purpose

`SemanticState` is the whole runtime state.
`SemanticUnit` is the smallest object that can be individually preserved, mutated, recovered, and measured.

The field-level specification for this atom is defined in [Semantic Unit Field Specification](SRP_SEMANTIC_UNIT_FIELD_SPEC.md).

The Semantic Unit Model freezes:

- the unit's identity kernel
- the unit's semantic payload
- the unit's memory / evolution fields
- the unit's lifecycle fields
- the unit's mutable vs immutable boundary

This is the atom that every rule, event, and policy ultimately acts on.

---

## 2. Semantic Identity Kernel

Every `SemanticUnit` should carry an identity kernel rather than just text or embedding data.

The identity kernel is the stable core of the unit.

Suggested components:

- canonical identity
- aliases
- lineage
- provenance
- type

Example:

```text
SemanticUnit
  identity:
    canonical: Alice
    aliases: [Alicia]
    lineage: [...]
    provenance: [...]
    type: person
```

### Identity kernel rules

- exactly one canonical identity should be active at a time
- aliases must preserve alternate surface forms and historical names
- lineage must preserve origin and merge history
- provenance must remain attached unless hard deletion is explicitly allowed

---

## 3. Semantic Payload

The semantic payload stores what the unit means.

It is not just a string.

Suggested components:

- normalized description
- extracted content
- relation hints
- evidence pointers
- confidence on meaning

Example:

```text
semantic:
  description: person involved in project X
  evidence: [memory:1, memory:4]
  confidence: 0.88
```

### Payload rules

- payload should remain semantically aligned with the identity kernel
- payload may change as the unit is refined or recovered
- payload changes must remain auditable

---

## 4. Unit Fields

A semantic unit can be represented with these conceptual field groups:

### 4.1 Identity fields

- `id`
- `canonical_name`
- `aliases`
- `lineage`
- `type`

### 4.2 Semantic fields

- `semantic_content`
- `description`
- `evidence`
- `relations`

### 4.3 Memory fields

- `activation`
- `importance`
- `last_used_round`
- `decay_rate`
- `reactivation_bonus`
- `forget_threshold`

### 4.4 Lifecycle fields

- `lifecycle_state`
- `evolution_state`
- `archive_state`

### 4.5 Confidence fields

- `identity_confidence`
- `meaning_confidence`
- `recovery_confidence`

---

## 5. Mutable and Immutable Boundaries

### Immutable fields

These should not change after creation unless an explicit split or hard reset is performed:

- `id`
- `created_round`
- `origin`
- `type`
- `lineage` root

### Mutable fields

These may evolve over time:

- `canonical_name`
- `aliases`
- `semantic_content`
- `relations`
- `activation`
- `importance`
- `last_used_round`
- `decay_rate`
- `reactivation_bonus`
- `forget_threshold`
- `lifecycle_state`
- `evolution_state`
- `archive_state`
- `identity_confidence`
- `meaning_confidence`
- `recovery_confidence`
- `updated_round`

The boundary between immutable and mutable fields is part of the protocol, not an implementation detail.

---

## 6. Semantic Unit State Machine

Each semantic unit should support a dedicated state machine.

```text
active
  -> stable
  -> inactive
  -> dormant
  -> approximate
  -> forgotten
  -> deleted
```

Reactivation should be possible from non-terminal states when evidence is sufficient.

### State machine rules

- `active` means the unit is immediately usable and salient
- `stable` means the unit is supported by recent or repeated use
- `inactive` means the unit remains valid but is not currently salient
- `dormant` means the unit is preserved but low priority
- `approximate` means the unit is represented by a surrogate
- `forgotten` means the unit is weakly retained or soft-hidden
- `deleted` means the unit has been removed according to policy

---

## 7. Relations

Semantic units participate in relations, but relations are not the same as identity.

Common relation types:

- dependency
- constraint
- ownership
- causality
- temporal ordering
- equivalence
- reference
- `is-a`

### Relation rules

- a unit may have many relations
- relation preservation is important for structural coherence
- relation collapse must not erase identity without explicit merge logic
- relation updates should be reversible in explanation, even if not always reversible in execution

---

## 8. Evolution Hooks

The unit model must support the following evolution hooks:

- canonicalization
- consolidation
- activation update
- approximation
- forgetting
- recovery
- garbage collection

These hooks are the places where events and evolution rules apply.

---

## 9. Unit-Level Invariants

The following invariants should hold whenever possible:

- one canonical name at a time
- aliases unique within the unit
- activation within `[0, 1]`
- confidence values within `[0, 1]`
- approximation must record distance or error
- recovery must preserve provenance
- forgetting must not silently destroy traceability unless explicitly allowed
- merge operations must preserve lineage
- relations must not point to invalid objects without an explicit placeholder strategy

---

## 10. Relationship to Other Layers

### Relationship to Semantic State

`SemanticState` contains many `SemanticUnit` objects.

### Relationship to Runtime Object Model

`SemanticUnit` is the most important concrete object family in the object model.

### Relationship to Data Contract

The data contract defines the exact field meanings and invariants for unit fields.

### Relationship to Event Contract

The event contract defines which event may mutate which unit field.

### Relationship to Evolution Rules

The evolution rules define when a unit transition should happen.

---

## 11. Scope

This document defines the atomic semantic unit used by SRP.

It does not define:

- the full runtime state container
- the recovery engine
- the policy engine
- the serialization format

Those belong to the other layers already defined in SRP.
