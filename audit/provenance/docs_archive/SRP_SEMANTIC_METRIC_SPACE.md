# SRP Semantic Metric Space

This document defines the semantic distance and similarity framework for SRP.
It is not a generic embedding spec and not an implementation benchmark.

The central question is:

> How do we measure semantic closeness between units, graphs, states, versions, and contexts in a way that SRP operators can rely on?

This layer sits on top of formal semantics and supports merge, split, approximation, recovery, diff, and ranking.

---

## 1. Purpose

SRP needs a metric layer so that its operators do not rely only on heuristics.

The metric layer provides:

- semantic distance
- semantic similarity
- structural distance
- history distance
- activation distance
- context distance

This allows SRP to rank candidates and compare alternatives in a principled way.

---

## 2. Metric Domain

The metric space should be able to measure distance over:

- semantic units
- relations
- semantic graphs
- semantic states
- semantic versions
- runtime contexts

In practice, the metric may be a family of related distances rather than one single scalar over every object type.

---

## 3. Semantic Feature Map

For a semantic unit `U`, define a feature map:

```text
phi(U) = (d_id, d_sem, d_rel, d_hist, d_act, d_ctx)
```

Where:

- `d_id` = identity component
- `d_sem` = semantic payload component
- `d_rel` = relational / structural component
- `d_hist` = history / lineage component
- `d_act` = activation / confidence / salience component
- `d_ctx` = runtime context component

The feature map is the basis for the distance function.

---

## 4. Semantic Distance

### 4.1 Unit distance

Define the semantic distance between two units as:

```text
D(U_a, U_b) = w_id * D_id + w_sem * D_sem + w_rel * D_rel + w_hist * D_hist + w_act * D_act + w_ctx * D_ctx
```

Where each component is normalized to a compatible range.

### 4.2 Similarity

Similarity may be defined from distance by normalization:

```text
Sim(U_a, U_b) = 1 - D(U_a, U_b)
```

when the distance is normalized into `[0, 1]`.

### 4.3 Interpretation

- smaller distance means stronger semantic closeness
- larger distance means stronger semantic divergence

---

## 5. Distance Components

### 5.1 Identity distance

Identity distance measures whether two objects are the same semantic identity.

Example:

- same identity kernel -> distance near `0`
- different identity kernels -> distance near `1`

Identity distance should be constrained by identity rules.

### 5.2 Semantic payload distance

Semantic payload distance measures the difference in meaning-bearing content.

This may compare:

- canonical names
- typed semantic content
- attributes
- role labels

### 5.3 Relation distance

Relation distance measures structural mismatch.

It may compare:

- neighbors
- edge types
- path coverage
- dependency closure

### 5.4 History distance

History distance measures lineage divergence.

It may compare:

- version ancestry
- drift accumulation
- approximation count
- recovery count

### 5.5 Activation distance

Activation distance measures current availability, salience, and trust.

It may compare:

- activation
- confidence
- importance
- recency

### 5.6 Context distance

Context distance measures whether the runtime situation supports treating two objects as close.

It may compare:

- current round
- policy regime
- task context
- recovery context
- execution context

---

## 6. Graph Distance

For graphs, the metric should compare structure as well as labels.

### 6.1 Graph distance shape

```text
D(G_a, G_b) = w_v * D_V + w_e * D_E + w_p * D_P + w_c * D_C
```

Where:

- `D_V` = node distance
- `D_E` = edge distance
- `D_P` = path distance
- `D_C` = constraint-context distance

### 6.2 Graph matching requirement

Graph distance depends on a node and edge alignment step.
The metric should therefore be defined over matched structures or a known alignment policy.

### 6.3 Practical use

Graph distance is useful for:

- graph diff
- recovery ranking
- approximation ranking
- merge candidate evaluation
- replay comparison

---

## 7. Version Distance

Semantic versions form a DAG, so distance may be defined along ancestry and divergence.

### 7.1 Version distance terms

- path length to common ancestor
- operator divergence
- drift accumulation
- conflict count

### 7.2 Use

Version distance is useful for:

- branching analysis
- rollback selection
- merge cost estimation
- recovery ranking

---

## 8. Constraint-Aware Distance

Distance must not override constraints.

Even if two objects are semantically close, they may still be illegal to merge or substitute.

Therefore:

```text
distance supports ranking
constraint supports legality
```

The metric space may rank candidates, but the constraint system decides whether the candidate is allowed.

---

## 9. Operator Dependence

The metric space directly supports graph operators:

- canonicalization chooses nearest canonical form
- merge checks whether distance is below a threshold
- split checks whether divergence exceeds a threshold
- approximation chooses the nearest valid surrogate
- recovery ranks candidate reconstructions
- pruning estimates preservation loss
- diff measures structural divergence

The metric layer therefore provides the computational substrate for semantic graph algorithms.

---

## 10. Metric Axioms

For practical SRP use, the semantic distance family should ideally satisfy:

- non-negativity
- identity compatibility
- symmetry for comparable objects
- boundedness after normalization

Strict triangle inequality may not always hold if graph matching, aliasing, or approximation policies introduce domain-specific behavior.

Therefore SRP may use a metric family or pseudo-metric family where appropriate.

---

## 11. Metric and Semantic Energy

The metric space can later support an energy formulation.

For now, energy is a future extension, not a required core concept.

Distance is sufficient to start with:

- candidate ranking
- operator selection
- recovery scoring
- approximation scoring

---

## 12. Relation to Current Implementation

The current repository already contains partial signals for distance-like reasoning:

- embedding-based similarity
- drift scores
- confidence scores
- graph validation metrics
- retention and survival metrics
- recovery ranking heuristics

This document defines the theory layer that can unify those signals.

---

## 13. Relationship to Other Documents

Recommended chain:

```text
Formal Semantics
  -> Semantic Metric Space
  -> Semantic Graph Algorithms
  -> Semantic Operator Algebra
  -> Semantic Versioning Model
  -> Runtime Semantics
  -> Semantic Time Model
  -> Runtime Kernel
```

The metric space is the shared computational base for many operators.

---

## 14. Scope

This document defines semantic distance and similarity only.

It does not define:

- embedding model choice
- nearest-neighbor implementation
- search backend
- kernel internals

Those belong to later implementation work.
