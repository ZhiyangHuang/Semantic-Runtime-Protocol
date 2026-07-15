# SRP Semantic Operator Algebra

This document defines the composition laws for semantic graph operators in SRP.
It is not an implementation spec and not an operator catalog.

The central question is:

> How do graph transformation operators compose, commute, constrain one another, and preserve or change identity, structure, and meaning?

This layer sits above graph algorithms and below future implementation-specific orchestration.

---

## 1. Purpose

Semantic Graph Algorithms define what operators exist.
Semantic Operator Algebra defines how operators interact.

The algebra is useful for reasoning about:

- operator order
- operator commutativity
- operator idempotence
- operator parallelism
- identity-preserving transformations
- structure-preserving transformations

This abstraction makes SRP more stable when the underlying algorithms change.

---

## 2. Operator Classes

Operators may be classified by what they change.

### Identity-changing operators

Examples:

- merge
- split
- canonicalization

### Structure-changing operators

Examples:

- pruning
- recovery
- neighborhood expansion
- graph diff projection

### Metadata-changing operators

Examples:

- confidence adjustment
- lifecycle annotation
- provenance attachment

### Drift-changing operators

Examples:

- approximation
- forgetting
- recovery

---

## 3. Composition Laws

### 3.1 Sequential composition

Operator A followed by operator B is written conceptually as:

```text
B(A(Graph))
```

The output of A becomes the input of B.

### 3.2 Commutativity

Some operators may commute.

```text
A(B(Graph)) = B(A(Graph))
```

But many semantic operators do not commute.

Examples:

- canonicalization before merge is often not the same as merge before canonicalization
- pruning before recovery is not usually the same as recovery before pruning

### 3.3 Idempotence

An operator is idempotent if applying it more than once produces the same result as applying it once.

Examples of likely idempotent candidates under stable constraints:

- canonicalization
- some pruning passes

### 3.4 Associativity

Some operator groupings may be reassociated without changing result, but this should be treated cautiously because graph semantics often depend on order.

---

## 4. Ordering Laws

Certain operator orders should be preferred.

Recommended precedence examples:

- canonicalization before merge
- constraint check before mutation
- recovery validation before acceptance
- neighborhood search before approximation

These are not arbitrary implementation preferences.
They are semantic ordering laws.

---

## 5. Parallelism Laws

Some operators may run in parallel if they operate on disjoint subgraphs or independent constraints.

Parallel execution is allowed only when:

- the operators do not conflict on identity
- the operators do not rewrite the same relation set
- the operators do not violate constraint dependencies

Parallelism should always be constrained by the semantic constraint system.

---

## 6. Preservation Laws

### Identity preservation

Some operator chains must preserve identity lineage even when structure changes.

### Structure preservation

Some transformations may change representation while preserving dependency shape.

### Meaning preservation

Operators may degrade representation, but they should preserve recoverable meaning when possible.

### Trace preservation

Operators should preserve enough provenance to explain what changed and why.

---

## 7. Non-Commutativity Examples

### Canonicalization vs merge

Canonicalizing first may reduce duplicate candidates and make merge safer.
Merging first may lose alias distinctions that canonicalization would otherwise preserve.

### Recovery vs pruning

Pruning before recovery may destroy evidence required for reconstruction.

### Approximation vs recovery

Approximation may produce a surrogate that recovery later needs to refine.
The order matters.

---

## 8. Operator Equivalence

Two operators may be considered equivalent under a constrained view if they produce the same semantic effect on a defined scope.

For example:

- two different recovery implementations may be equivalent if they reconstruct the same constrained subgraph and preserve provenance
- two different pruning algorithms may be equivalent if they satisfy the same preservation-loss budget and constraint set

Equivalence is scope-dependent.

---

## 9. Algebraic Metadata

Each operator should be annotated with algebraic properties when known.

Suggested properties:

- `commutative`
- `associative`
- `idempotent`
- `parallelizable`
- `identity_preserving`
- `structure_preserving`
- `drift_increasing`
- `drift_decreasing`

These annotations would help future runtime orchestration and replay reasoning.

---

## 10. Relation to Constraints, Events, and Replay

### Constraints

Constraints determine whether an operator may be applied at all.

### Events

Events record the semantic result of operator application.

### Replay

Replay may need to replay operators in a specific order to reconstruct the same graph state.

### Trace

Trace may use the operator chain to explain how the graph changed.

---

## 11. Relation to Current Implementation

The current graph recovery and validation pipeline already suggests an implicit operator order:

- canonicalize
- validate
- recover
- compare
- summarize

This document makes those ordering and composition principles explicit.

---

## 12. Relationship to Other Documents

Recommended chain:

```text
Semantic Graph Model
  -> Semantic Constraint System
  -> Semantic Graph Algorithms
  -> Semantic Operator Algebra
  -> Replay Spec
```

This algebra is the theoretical layer for reasoning about how graph operators compose.

---

## 13. Scope

This document defines composition laws only.

It does not define:

- implementation details
- search models
- neural backends
- kernel execution code

Those belong to later implementation work.

