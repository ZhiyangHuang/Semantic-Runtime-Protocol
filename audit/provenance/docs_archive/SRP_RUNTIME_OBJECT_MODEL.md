# SRP Runtime Object Model

This document defines the shared runtime object model for SRP.
It is not an implementation spec.

The central question is:

> What runtime objects exist in SRP, what fields do they own, and which subsystems are allowed to modify them?

This layer is the bridge between abstract semantic theory and concrete runtime modules.

---

## 1. Purpose

SRP needs a common object model so that state, representation, policy, lifecycle, recovery, and consolidation all operate on the same contract.

Without this layer, each subsystem tends to invent its own fields and drift away from the shared theory.

The runtime object model solves that by defining:

- the canonical runtime objects
- their owned fields
- immutable vs mutable data
- module write permissions
- shared evolution semantics

The detailed field semantics, invariants, event stream rules, and reference integrity constraints are specified in [Runtime Data Contract](SRP_RUNTIME_DATA_CONTRACT.md).
The atomic semantic unit definition is specified in [Semantic Unit Model](SRP_SEMANTIC_UNIT_MODEL.md).

---

## 2. Core Objects

SRP should center on four runtime object families:

1. `SemanticUnit`
2. `RelationUnit`
3. `RuntimeContext`
4. `SemanticState`

These are the primary objects that the rest of SRP reads and updates.

---

## 3. SemanticUnit

`SemanticUnit` is the core runtime atom.

It represents one semantic concept, entity, task, event, or other preserved unit.

### Suggested fields

```text
SemanticUnit
{
  id,
  type,
  canonical_name,
  aliases,
  semantic_content,
  relations,
  activation,
  importance,
  confidence,
  lifecycle,
  evolution,
  provenance
}
```

### SemanticUnit responsibilities

- carry the canonical identity of the concept
- retain aliases and alternate forms
- store semantic content and supporting evidence
- track activation and decay
- record lifecycle and evolution state
- retain provenance and confidence

### Recommended subfields

- `canonical_name`: current preferred name
- `aliases`: alternate names and equivalence forms
- `semantic_content`: normalized semantic payload
- `relations`: relation references involving this unit
- `activation`: current salience or recall strength
- `importance`: preservation priority
- `confidence`: reliability score
- `lifecycle`: state in the runtime lifecycle
- `evolution`: state in the semantic evolution machine
- `provenance`: origin and lineage information

---

## 4. RelationUnit

`RelationUnit` represents a typed semantic connection between units.

Relations should not be stored as plain strings.
They need their own object so the runtime can preserve dependency and structure.

### Suggested fields

```text
RelationUnit
{
  id,
  source,
  target,
  relation_type,
  confidence,
  criticality,
  created_round,
  updated_round
}
```

### Relation types

Relation types may include:

- dependency
- constraint
- ownership
- causality
- temporal ordering
- equivalence
- reference

### RelationUnit responsibilities

- preserve structural links
- support dependency-aware retention
- support graph recovery and structural reconstruction
- record relation confidence and criticality

---

## 5. RuntimeContext

`RuntimeContext` stores the current operating conditions of SRP.

Policy should read this object rather than reaching into unrelated state.

### Suggested fields

```text
RuntimeContext
{
  budget,
  pressure,
  current_round,
  policy,
  memory_usage,
  compression_level
}
```

### RuntimeContext responsibilities

- expose the current resource regime
- provide pressure and budget signals
- carry the active policy mode
- provide round/time information for evolution rules

---

## 6. SemanticState

`SemanticState` is the container that holds the runtime world.

### Suggested fields

```text
SemanticState
{
  units,
  relations,
  context,
  history
}
```

### SemanticState responsibilities

- hold all semantic units and relations
- hold the active runtime context
- retain transition history
- expose the full state for evaluation and auditing

SemanticState is a container, not the source of truth for every field.
The source of truth lives in the owned objects.

---

## 7. State Ownership

Each runtime object should own its own mutable data whenever possible.

This avoids having one module rewrite all state through a single monolithic blob.

Recommended ownership model:

- `SemanticUnit` owns semantic identity, activation, confidence, lifecycle, and evolution
- `RelationUnit` owns relation structure and criticality
- `RuntimeContext` owns runtime conditions
- `SemanticState` owns collection-level orchestration and history

---

## 8. Immutable and Mutable Fields

The object model should distinguish immutable fields from mutable fields.

### Immutable fields

These should not change after creation:

- `id`
- `created_round`
- `origin`
- `lineage`

### Mutable fields

These may evolve over time:

- `canonical_name`
- `aliases`
- `semantic_content`
- `relations`
- `activation`
- `importance`
- `confidence`
- `lifecycle`
- `evolution`
- `updated_round`

Immutable fields preserve continuity and make recovery auditable.

---

## 9. Write Permissions

The runtime object model should make it clear which subsystem is allowed to modify which fields.

### Suggested write matrix

| Module | Allowed Writes |
| --- | --- |
| Extraction | `semantic_content`, `confidence`, `provenance` |
| Canonicalization | `canonical_name`, `aliases`, `lineage` |
| Representation | `relations`, `semantic_content` |
| Activation | `activation`, `last_used_round` |
| Consolidation | `aliases`, `relations`, `importance`, `activation` |
| Maintenance | `decay_state`, `replacement_candidate`, `activation` |
| Policy | `importance`, `retention_state`, `selection_priority` |
| Lifecycle | `lifecycle` |
| Recovery | `confidence`, `activation`, `semantic_content` |
| Garbage Collection | `deleted` |

This matrix is intentionally conceptual.
The key idea is that ownership must be explicit.

---

## 10. Evolution Fields

Evolution should be represented as data attached to the unit rather than as a separate hidden store.

Suggested evolution fields:

- `state`
- `last_used_round`
- `decay_rate`
- `reactivation_bonus`
- `forget_threshold`
- `consolidation_score`
- `replacement_candidate`

This lets policy and recovery read the same evolution metadata.

---

## 11. Semantic Unit State Machine

A semantic unit should support a dedicated state machine.

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

This state machine is distinct from the runtime lifecycle.

- runtime lifecycle describes how a state package moves through SRP
- semantic unit state machine describes how one concept changes over time

---

## 12. Runtime Lifecycle vs Evolution

The runtime lifecycle and the semantic evolution layer serve different jobs.

### Runtime lifecycle

Tracks how the whole state package moves through:

- extraction
- canonicalization
- representation update
- compression
- archive
- recovery
- validation

### Semantic evolution

Tracks how one semantic unit changes through:

- activation
- consolidation
- maintenance
- forgetting
- approximation
- recovery
- garbage collection

The object model should support both views without mixing them into one field.

---

## 13. Scope

This document defines the shared runtime object contract for SRP.

It does not define:

- the exact storage backend
- the final schema format
- the execution engine
- the benchmark suite
- the implementation of any module

Those belong to later design and implementation documents.
