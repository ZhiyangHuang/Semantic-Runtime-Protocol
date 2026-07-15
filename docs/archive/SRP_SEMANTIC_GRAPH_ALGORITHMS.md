# SRP Semantic Graph Algorithms

This document defines the graph transformation operators used by SRP.
It is not a generic algorithm catalog and not an implementation spec.

The central question is:

> How does a semantic graph transform from one valid state to another under constraints, evolution rules, and runtime pressure?

This layer sits on top of the semantic graph model and below operator algebra.

---

## 1. Why Operators Instead of a Function List

SRP needs a stable abstraction for graph computation.

The important unit is not "an algorithm" in isolation.
The important unit is a graph transformation operator:

```text
Graph_in
  -> Operator
  -> Graph_out
```

Operators are more stable than implementation details because the underlying method may change over time.

For example, a recovery operator may be implemented with:

- rules
- embeddings
- search
- GNNs
- LLM-assisted ranking

but the operator remains the same at the theory level.

---

## 2. Operator Families

The graph algorithm layer should be organized as a family of transformation operators.

```text
Semantic Graph Operators
  -> Canonicalization
  -> Merge
  -> Split
  -> Approximation
  -> Recovery
  -> Pruning / GC
  -> Graph Diff
  -> Neighborhood Search
```

Each operator transforms a graph while respecting the semantic constraint system.

---

## 3. Canonicalization Operator

### Purpose

Normalize equivalent surface forms into a canonical node while preserving aliases.

### Input

- a graph
- one or more candidate nodes
- canonicalization evidence

### Output

- updated graph
- canonical node
- preserved alias set

### Operator contract

- identity should become more stable
- aliases should be preserved, not erased
- provenance should remain traceable

### Example

```text
Apple Inc.
Apple Company
Apple
  -> canonical node
  -> alias set
```

### Typical event linkage

- `Canonicalized`

---

## 4. Merge Operator

### Purpose

Combine semantically redundant nodes into a single node.

### Input

- graph
- merge candidates
- evidence
- lineage information

### Output

- graph with merged identity
- preserved origin lineage
- rewritten aliases and relations

### Operator contract

- merge is not a simple union
- lineage must be preserved
- relation rewrites must remain valid
- origin identity must not be silently erased

### Example

```text
Node A + Node B
  -> Node C
```

### Typical event linkage

- `Merged`

---

## 5. Split Operator

### Purpose

Separate a node into multiple nodes when identity, role, or semantic evidence diverges.

### Input

- graph
- ambiguous node
- divergence evidence

### Output

- graph with separated nodes
- updated lineage
- relation redistribution

### Operator contract

- split must preserve origin references
- split must not destroy provenance
- split should be explainable by evidence divergence

### Example

```text
Apple
  -> Apple (company)
  -> Apple (fruit)
```

### Typical event linkage

- `Consolidated` or a future split-specific event family if needed

---

## 6. Approximation Operator

### Purpose

Replace a missing or degraded node with a semantically close surrogate while preserving traceability.

### Input

- graph
- degraded node or missing node slot
- neighborhood context
- semantic distance estimates

### Output

- graph with approximation node or surrogate
- drift annotation
- approximation target reference

### Operator contract

- approximation must preserve type boundaries
- approximation must record distance or error
- approximation must remain distinguishable from identity equivalence

### Example

```text
Unknown
  -> nearby candidate node
```

### Typical event linkage

- `Approximated`

---

## 7. Recovery Operator

### Purpose

Reconstruct a semantic node or subgraph using graph evidence, event history, and constraints.

### Input

- graph
- neighborhood
- candidate ranking output
- constraints
- validation targets

### Output

- updated graph
- recovered node or subgraph
- recovery provenance

### Operator contract

- recovery is not approximation
- recovery must be validated
- recovery must respect constraints
- recovery must preserve provenance and lineage

### Example pipeline

```text
Candidate Ranking
  -> Constraint Check
  -> Validation
  -> Recovered
```

### Typical event linkage

- `Recovered`
- `RecoveryResultProduced`

---

## 8. Pruning / GC Operator

### Purpose

Reduce graph size under resource pressure while minimizing preservation loss.

### Input

- graph
- budget
- retention priorities
- constraint set

### Output

- reduced graph
- removed or archived nodes and edges
- preservation-loss report

### Operator contract

- pruning must respect identity and reference constraints
- GC must not remove required provenance
- pruning should seek minimum preservation loss under budget

### Example

```text
10000 nodes
  -> budget-constrained reduced graph
```

### Typical event linkage

- `Archived`
- `Forgotten`
- future GC-specific event if needed

---

## 9. Graph Diff Operator

### Purpose

Compute semantic differences between two graphs.

### Input

- graph A
- graph B
- comparison scope

### Output

- node-level diff
- edge-level diff
- relation-level diff
- path-level diff

### Operator contract

- diff should preserve identity matching
- diff should separate node changes from relation changes
- diff should be explainable without relying only on embeddings

### Example

```text
Tom likes Apple
Tom likes Orange
```

Graph diff should expose:

- unchanged subject node
- unchanged predicate / relation
- changed target node

### Typical uses

- replay comparison
- trace explanation
- evaluation

---

## 10. Neighborhood Search Operator

### Purpose

Find the local semantic context around a node or query.

### Input

- graph
- seed node or query
- radius or budget

### Output

- neighborhood subgraph
- ranked candidates
- contextual evidence

### Operator contract

- search should respect structural constraints
- search should preserve neighborhood provenance
- search output should be usable by merge, approximation, and recovery

### Example

```text
Apple
  -> radius-2 neighborhood
```

### Typical uses

- candidate ranking
- alias search
- recovery search
- approximation search

---

## 11. Operator Pipeline

Operators can be composed into a pipeline.

Recommended conceptual pipeline:

```text
Canonicalize
  -> Merge
  -> Constraint Check
  -> Approximation
  -> Recovery
  -> Pruning
  -> Validation
```

The pipeline is not fixed forever, but the operator boundaries should remain stable.

---

## 12. Operator Metadata Template

Each operator should be describable using a shared template.

| Field | Meaning |
| --- | --- |
| `Operator Name` | Stable operator label |
| `Purpose` | What the operator is for |
| `Input` | Graph and auxiliary data required |
| `Output` | Updated graph or projection |
| `Constraints` | Semantic constraints that must hold |
| `Events` | Event families associated with the operator |
| `Trace` | How the operator appears in trace |
| `Replay` | Replay requirements or determinism properties |
| `Complexity` | Optional computational characterization |

This template makes the operator layer compatible with the rest of the SRP protocol stack.

---

## 13. Relation to Operator Algebra

The operators in this document are the basis for a later semantic operator algebra.

That algebra may define:

- commutativity
- ordering constraints
- idempotence
- parallelizability
- identity-preserving vs identity-changing operators
- structure-preserving vs structure-changing operators

This document intentionally stops at operator definition.

---

## 14. Relation to Current Implementation

The current graph-related implementation already exposes pieces of these operators:

- graph construction
- dependency closure
- constraint-aware recovery
- graph integrity validation
- lifecycle-aware node tracking

The implementation is an early projection of the operator layer.

---

## 15. Relationship to Other Documents

Recommended chain:

```text
Semantic Graph Model
  -> Semantic Constraint System
  -> Semantic Graph Algorithms
  -> Semantic Operator Algebra
  -> Runtime Recording Layer Alignment
```

This document provides the computational side of the graph theory stack.

---

## 16. Scope

This document defines graph transformation operators only.

It does not define:

- storage format
- neural model choice
- concrete search implementation
- kernel internals

Those belong to later implementation work.

