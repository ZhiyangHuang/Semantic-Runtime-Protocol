# SRP Semantic Versioning Model

This document defines semantic versioning for SRP.
It is not a snapshot spec and not a generic source-control spec.

The central question is:

> What is a semantic version, how do semantic versions relate to each other, and how do they support branch, merge, rollback, replay, and trace?

This layer sits above semantic graph operators and below replay-oriented implementation work.

---

## 1. Why Semantic Versioning

SRP needs more than events, traces, and replay.

It needs a way to say:

- which semantic state is current
- which semantic state came before
- which semantic state branched into another one
- which version is the result of merge or recovery

Replay tells us how to reconstruct state.
Trace tells us why state changed.
Versioning tells us which semantic state instance we are looking at and how it relates to others.

---

## 2. Semantic Version Definition

A semantic version is a named, referenceable semantic state identity within an evolution graph.

It is not:

- an event number
- a mere timestamp
- a full state copy

A semantic version is closer to a semantic commit than to a raw snapshot.

### Semantic version properties

- stable version identity
- parent version references
- operator provenance
- rule and constraint version stamps
- state reference
- event reference set
- replayability

---

## 3. Version Graph Model

Semantic versions should form a DAG.

```text
V1
  -> V2
  -> V3
      -> V4
      -> V5
```

Version graphs should support:

- branching
- merging
- rollback
- checkout
- replay from any version root that has a valid event history

Version graphs should not require every node to store the full state.
They should store references.

---

## 4. Semantic Commit Model

The core version node should behave like a semantic commit.
For the dedicated commit-layer contract, see [SRP Semantic Commit Model](SRP_SEMANTIC_COMMIT_MODEL.md).

### Suggested fields

- `version_id`
- `parent_versions`
- `operator`
- `rule_version`
- `constraint_version`
- `event_ids`
- `state_reference`
- `graph_reference`
- `trace_reference`
- `replay_reference`
- `created_round`
- `actor`
- `status`

### Commit invariants

- `version_id` must be stable
- parent references must be explicit
- the commit should not duplicate the full state unless required by the storage layer
- every commit must remain traceable to events and operators
- every commit must be compatible with replay and trace

---

## 5. Version and Identity

Semantic versioning must be decoupled from semantic identity.

### Identity

Identity answers:

- what entity or concept is this?

### Version

Version answers:

- which state of that entity or concept is this?

The same `SemanticUnit` may have many semantic versions.

Example:

```text
SemanticUnit: Apple
  Version V1: Apple
  Version V2: Apple Inc.
  Version V3: Apple Company
```

The unit remains the same identity kernel while its version history evolves.

---

## 6. Version Operations

### 6.1 Commit

Create a new semantic version from a valid transformation.

Typical sources:

- canonicalization
- merge
- split
- approximation
- recovery
- pruning

### 6.2 Branch

Create a divergent semantic version line from a shared parent.

Branching is useful when:

- two interpretations compete
- a recovery path is uncertain
- a temporary approximation must be preserved without overwriting the original

### 6.3 Merge

Combine two or more version lines when semantic compatibility and constraints allow it.

Merge should preserve:

- lineage
- provenance
- operator history
- conflict resolution metadata

### 6.4 Checkout

Load a specific semantic version reference for inspection or replay.

Checkout is a read-oriented semantic operation.

### 6.5 Rollback

Move back to a prior semantic version when a later transition fails or must be reverted.

Rollback should not silently erase the rolled-forward path.
It should preserve rollback provenance.

---

## 7. Version Graph Semantics

### Branch semantics

Branches allow the system to preserve competing semantic hypotheses instead of collapsing them too early.

### Merge semantics

Merge is a semantic reconciliation, not a raw graph union.

### Rollback semantics

Rollback is a controlled return to a prior version, often after failed recovery, failed validation, or a constraint violation.

### Fork semantics

Forking is a branch creation under a new context or operator lineage.

---

## 8. Version Relation to Operators

Semantic graph operators naturally produce version commits.

Examples:

- canonicalization -> new semantic version
- merge -> new semantic version
- split -> new semantic version branch
- approximation -> new semantic version with drift annotation
- recovery -> new semantic version with provenance and validation metadata
- pruning -> new semantic version or archived version depending on policy

Operator output should therefore be version-aware.

---

## 9. Version Relation to Replay

Replay should reconstruct semantic state through the version graph and its event history.

Replay should be able to:

- start from an initial version
- apply the commit / event history
- reconstruct a target version
- compare the replayed version with the stored target

Versioning helps replay answer:

```text
which semantic state is this?
```

and:

```text
how did this semantic state arise?
```

---

## 10. Version Relation to Trace

Trace and versioning are linked but distinct.

- versioning identifies the semantic state instance
- trace explains the causal path that produced it

Trace can point to a version commit.
Versioning can store a trace reference.

This linkage allows:

- branch-aware explanation
- merge-aware explanation
- rollback-aware explanation

---

## 11. Version Relation to Constraints and Rules

Semantic version operations must obey:

- identity constraints
- structural constraints
- semantic constraints
- evolution constraints
- runtime constraints

Rules decide when a version may be created or advanced.
Constraints decide what version transitions are forbidden.

---

## 12. Version Graph and Persistent State

Semantic versioning should behave like a persistent data structure:

- units persist across versions
- versions branch without destroying the prior branch
- history is preserved through references
- state instances remain inspectable

This is why versioning should be reference-based rather than snapshot-only.

---

## 13. Versioning and Current Implementation

The current runtime already has ingredients that can later support versioning:

- state snapshots
- history summaries
- recovery packages
- lifecycle summaries
- trace and replay references
- graph-aware projections

The present implementation does not yet expose a full semantic version graph.
This document defines the theory layer for that graph.

---

## 14. Relationship to Other Documents

Recommended chain:

```text
Semantic Graph Model
  -> Semantic Constraint System
  -> Semantic Graph Algorithms
  -> Semantic Operator Algebra
  -> Semantic Versioning Model
  -> Semantic Time Model
  -> Runtime Semantics
  -> Runtime Data Contract
  -> Runtime Event Contract
  -> Replay Spec
```

Versioning also connects naturally to:

- Semantic Evolution Trace Spec
- Runtime Recording Layer Alignment
- Semantic Evolution Architecture

---

## 15. Scope

This document defines semantic versioning only.

It does not define:

- storage format
- commit persistence implementation
- kernel internals
- UI or visualization

Those belong to later implementation work.
