# SRP Semantic Graph Model

This document defines the semantic graph as SRP's structural substrate for units, relations, neighborhoods, paths, recovery, and traceability.
It is not an implementation spec.

The central question is:

> How do SemanticUnits compose into a recoverable, traceable, and constraint-aware graph of meaning?

This layer sits on top of the semantic unit model and supports trace, replay, recovery, approximation, and graph-based validation.

---

## 1. Purpose

The semantic graph is the structural form of semantic state.

It is not merely a knowledge graph and not merely a visualization.
It is the runtime structure that connects:

- semantic units
- relations
- subgraphs
- neighborhoods
- semantic paths
- recovery candidates
- trace explanations

The graph provides the topology needed to reason about:

- identity continuity
- dependency preservation
- semantic proximity
- path-based recovery
- structural drift

---

## 2. Graph Definition

A semantic graph is a typed graph over semantic units and their relations.

Core shape:

```text
SemanticGraph
  -> Node
  -> Edge
  -> Subgraph
  -> Neighborhood
  -> Semantic Path
```

The graph should preserve the distinction between:

- nodes as semantic entities or unit views
- edges as typed semantic relations
- paths as ordered semantic transitions or dependency chains
- neighborhoods as local semantic context

---

## 3. Graph Node Model

### 3.1 Node role

A node represents a semantic entity, a canonicalized unit, a contract concept, a recovered artifact, or another graph-visible semantic object.

### 3.2 Suggested node fields

- `node_id`
- `node_type`
- `label`
- `identity`
- `attributes`
- `lifecycle`
- `importance`
- `confidence`
- `importance_profile`

### 3.3 Node semantics

- `node_id` is the graph identifier
- `identity` captures canonical name and aliases when available
- `attributes` captures structured semantic metadata
- `lifecycle` captures graph-visible lifecycle state
- `importance` and `confidence` capture salience and trust

### 3.4 Node categories

The graph may contain nodes such as:

- semantic unit nodes
- constraint nodes
- contract nodes
- recovered nodes
- hallucination nodes
- anchor nodes
- dependency nodes
- query expectation nodes

### 3.5 Node example

```text
Apple
  type: entity
  identity: { canonical_name: Apple, aliases: [Apple Inc.] }
  lifecycle: active
  importance: high
```

---

## 4. Graph Edge Model

### 4.1 Edge role

An edge represents a typed semantic relation between two nodes.

### 4.2 Suggested edge fields

- `edge_id`
- `source`
- `target`
- `relation`
- `strength`
- `confidence`
- `evidence_pointer`
- `attributes`
- `lifecycle`

### 4.3 Edge semantics

Edges should preserve relation type explicitly.

Examples of edge types include:

- `depends_on`
- `constrains`
- `derived_from`
- `temporal_before`
- `same_entity`
- `refers_to`
- `causes`
- `is_a`
- `part_of`
- `similar_to`

### 4.4 Edge example

```text
Apple
  -- is_a -->
Fruit
```

### 4.5 Edge invariants

- an edge should connect valid nodes
- edge direction should be explicit
- confidence should be recorded when the relation is uncertain
- evidence pointers should be preserved when available

---

## 5. Subgraph Model

A subgraph is a constrained local graph slice with a specific semantic role.

Subgraphs may represent:

- an entity neighborhood
- a task-relevant dependency closure
- a recovery candidate region
- a traceable semantic episode
- a constraint closure

Subgraph properties:

- localized scope
- queryable boundary
- preservation of internal relation structure
- optional projection into summaries

Subgraphs are important because replay, recovery, and trace often operate on local neighborhoods rather than the whole graph.

---

## 6. Neighborhood Model

A neighborhood is the local context around one node or a small set of nodes.

Neighborhoods support:

- recovery candidate ranking
- alias consolidation
- approximate replacement
- structural validation
- local trace explanation

Neighborhood types may include:

- one-hop neighborhood
- multi-hop dependency neighborhood
- constraint neighborhood
- recovery neighborhood
- temporal neighborhood

The neighborhood is the graph form of local semantic context.

---

## 7. Semantic Path Model

A semantic path is an ordered traversal through the graph.

Paths support:

- trace explanation
- recovery reasoning
- dependency closure
- semantic drift analysis
- version lineage

Examples:

- `SemanticExtracted -> Canonicalized -> Approximated -> Forgotten -> Recovered`
- `constraint -> dependency -> recovered node`
- `source object -> compressed view -> recovered view -> executed view`

Paths are essential because SRP cares about how meaning changes over time, not only which nodes exist.

---

## 8. Graph Operations

The graph model should support a small set of structural operations.

### 8.1 Canonicalization

Multiple surface forms collapse into a single canonical node while preserving aliases.

### 8.2 Merge

Two nodes become one if the identity and evidence constraints are strong enough.

### 8.3 Split

A node separates into multiple nodes when identity or role evidence diverges.

### 8.4 Approximation

A node is replaced by a semantically close surrogate while retaining traceability.

### 8.5 Recovery

A missing or degraded node is reconstructed from graph evidence and event history.

### 8.6 Pruning / GC

Nodes or edges with no recovery value, no dependency value, and no structural importance may be pruned under policy.

These operations must always remain constraint-aware.

---

## 9. Graph Lifecycle

Graph objects should have lifecycle states.

Suggested lifecycle values:

- `created`
- `active`
- `compressed`
- `recovered`
- `verified`
- `retained`
- `approximate`
- `archived`
- `hallucinated`

Lifecycle should be visible at the node and graph levels.

Graph lifecycle is not the same as semantic unit lifecycle, but it should reflect it.

---

## 10. Relation to Current Implementation

The current `srp_experiment.srp.semantic_graph` package is an early projection of this model.

Current implementation concepts include:

- `SemanticGraphNode`
- `SemanticGraphEdge`
- `SemanticRuntimeGraph`
- lifecycle tracking
- integrity validation
- dependency closure

Current validation signals include:

- `object_survival_rate`
- `dependency_recall`
- `constraint_accuracy`
- `hallucination_rate`
- `graph_integrity_score`

The existing graph implementation is intentionally minimal.
It exposes:

- nodes
- edges
- lifecycle
- validation

The semantic graph model defined here is the theory layer that explains why those elements matter.

---

## 11. Relation to Replay, Trace, and Recovery

The semantic graph is the shared substrate for several runtime behaviors.

### Replay

Replay uses graph structure to reconstruct semantic state and validate dependency continuity.

### Trace

Trace uses graph paths and causal edges to explain how a state changed.

### Recovery

Recovery uses graph neighborhoods and dependency closures to find candidates for reconstruction.

### Approximation

Approximation uses graph distance and neighborhood similarity to choose a surrogate.

The graph is therefore the structural bridge between state, event, and explanation.

---

## 12. Graph Constraints

The graph should obey basic semantic constraints such as:

- node identity stability
- edge endpoint validity
- relation type validity
- recovery provenance preservation
- constraint node retention
- hallucination visibility

These constraints should later connect to the constraint system document.

---

## 13. Relationship to Other Documents

Recommended chain:

```text
Semantic Unit Model
  -> Semantic Graph Model
  -> Semantic Constraint System
  -> Semantic Graph Algorithms
  -> Semantic Versioning Model
```

This model is also a structural dependency for:

- Semantic Evolution Trace Spec
- Replay Spec
- Runtime Recording Layer Alignment
- Graph Recovery Plan

---

## 14. Scope

This document defines the semantic graph structure only.

It does not define:

- graph storage implementation
- graph algorithm implementation
- database schema
- kernel internals

Those belong to later implementation work.
