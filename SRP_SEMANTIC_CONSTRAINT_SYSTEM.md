# SRP Semantic Constraint System

This document defines the semantic constraints that must never be violated by SRP runtime evolution.
It is not a validation rule list and not an implementation spec.

The central question is:

> What must never happen, regardless of policy, rule selection, or runtime pressure?

This layer sits above event legality and below runtime behavior.

---

## 1. Constraint Purpose

SRP needs a constraint layer because rules describe what should happen, while constraints describe what must never be violated.

### Policy

Policy answers:

- what should be preferred under pressure?
- what should be retained?
- what should be compressed?

### Rule

Rules answer:

- when should a transition occur?
- under what conditions should the event be emitted?

### Constraint

Constraints answer:

- what is always forbidden?
- what must remain true even after evolution?

Constraints are therefore more fundamental than rules.

---

## 2. Constraint Layers

The system should be organized into five layers.

```text
Identity Constraints
  -> Structural Constraints
  -> Semantic Constraints
  -> Evolution Constraints
  -> Runtime Constraints
```

Each layer protects a different kind of correctness.

---

## 3. Identity Constraints

Identity constraints protect the stable identity of semantic objects.

### Examples

- `unit_id` must be globally unique
- a `SemanticUnit` may have only one identity kernel
- aliases may not become independent identities
- merge may not create multiple active canonical identities
- recovery may not invent a new identity when an identity already exists

### Identity invariants

- identity is stable across lifecycle transitions
- approximation cannot change identity
- recovery cannot silently replace identity
- merge must preserve lineage to the original identities

### Practical effect

Identity constraints preserve continuity across extraction, merge, forgetting, recovery, and replay.

---

## 4. Structural Constraints

Structural constraints protect graph and relation integrity.

### Examples

- relation endpoints must exist unless an explicit placeholder is allowed
- relation ids must remain valid and unique
- directed relations must preserve direction
- acyclic relations must not form cycles
- deleted nodes must not leave forbidden dangling references

### Structural invariants

- edges must connect valid endpoints
- node removal must trigger one of the approved reference-handling behaviors
- structural rewrites must remain auditable

### Approved reference handling behaviors

- cascade delete
- archive pointer
- unknown placeholder
- approximation replacement

---

## 5. Semantic Constraints

Semantic constraints protect meaning, type, and role consistency.

### Examples

- a unit of type `Fruit` must not be approximated into a unit of type `Animal`
- recovery must not violate semantic type constraints
- synonym consolidation must not collapse incompatible semantic categories
- relation types must remain semantically valid after transformation

### Semantic invariants

- type compatibility must be preserved
- role compatibility must be preserved
- semantic replacement must remain within an allowed semantic neighborhood
- approximation must respect semantic type boundaries

### Practical effect

Semantic constraints prevent embeddings or surface similarity from overriding meaning.

---

## 6. Evolution Constraints

Evolution constraints protect the validity of semantic transitions over time.

### Examples

- approximation must be accompanied by increased drift or reduced fidelity
- recovery must not bypass the known degradation path unless the archive or provenance allows it
- forgetting must preserve traceability unless explicit hard deletion policy exists
- merge must preserve lineage
- split must preserve origin references

### Evolution invariants

- `Deleted -> Recovered` is not allowed unless archive or restoration provenance exists
- approximation must record distance or error
- recovery must not silently reduce identity quality
- merge must keep origin lineage

### Practical effect

Evolution constraints preserve the causal shape of semantic drift and restoration.

---

## 7. Runtime Constraints

Runtime constraints protect execution correctness.

### Examples

- replay must be deterministic for a valid stream and fixed rule version
- events should be applied once in the kernel boundary
- replay must not mutate history
- replay must not regenerate embeddings as a side effect
- direct mutation outside the kernel should not exist in the target architecture

### Runtime invariants

- event stream application must be ordered and reproducible
- kernel mutation must be centralized
- history must remain append-only or versioned
- replay and trace must be read-oriented

### Practical effect

Runtime constraints keep the execution model trustworthy and reproducible.

---

## 8. Constraint Engine

The system should include a dedicated constraint engine.

This engine answers:

```text
Is this transition allowed at all?
```

### Constraint pipeline placement

```text
Policy Decision
  -> Rule Evaluation
  -> Runtime Event
  -> Constraint Engine
  -> Validation
  -> Mutation
  -> Trace / Replay
```

### Constraint engine responsibilities

- evaluate hard prohibitions
- classify violations
- block illegal transitions before mutation
- emit constraint failure artifacts when needed

The constraint engine is not the same as validation.

---

## 9. Constraint vs Validation

### Constraint

Constraint asks:

- may this happen at all?

### Validation

Validation asks:

- did it happen correctly?

### Example

For a recovery transition:

- constraint checks whether recovery is allowed
- validation checks whether the recovered state satisfies the expected quality and provenance requirements

These must remain separate.

---

## 10. Constraint Severity

Constraints should be classifiable by severity.

### Severity levels

- `ERROR`
- `WARNING`
- `INFO`

### Suggested handling

- `ERROR` blocks mutation or replay continuation
- `WARNING` allows continuation but records a violation
- `INFO` records explanatory context only

Severity should be visible in trace and replay diagnostics.

---

## 11. Constraint Catalog

Each constraint should have a stable id.

### Example ids

- `SC-001` Identity unique
- `SC-014` Relation endpoint exists
- `SC-022` Approximation must preserve type
- `SC-030` Replay determinism

### Constraint record fields

- `constraint_id`
- `constraint_name`
- `severity`
- `scope`
- `applies_to`
- `violation_description`
- `resolution_policy`

Stable ids allow trace, replay, validation, and repair to point to the same correctness rule.

---

## 12. Relation to Current Implementation

Current implementation already contains partial constraint signals in several places:

- graph validation
- runtime data invariants
- event contract invariants
- lifecycle checks
- replay and summary consistency checks

The semantic constraint system explains how those signals should be unified into one top-level contract.

---

## 13. Relationship to Other Documents

Recommended chain:

```text
Semantic Unit Model
  -> Semantic Graph Model
  -> Semantic Constraint System
  -> Semantic Evolution Rules
  -> Runtime Data Contract
  -> Runtime Event Contract
  -> Replay Spec
```

The constraint system should act as the shared correctness base for:

- validation
- repair
- replay
- trace
- graph algorithms

---

## 14. Scope

This document defines semantic constraints only.

It does not define:

- policy selection
- rule triggers
- event schemas
- graph storage implementation

Those belong to their respective layers.

