# SRP Formal Semantics

This document defines the mathematical core of SRP.
It is not an implementation spec and not a notation glossary.

The central question is:

> What are the formal objects, relations, operators, and transition laws that SRP uses to describe semantic evolution?

This layer sits beneath the architecture and above the metric space, runtime kernel, and implementation layers.

---

## 1. Purpose

SRP needs a formal basis so that its core concepts cannot be misread.

This document formalizes:

- semantic units
- semantic graphs
- semantic states
- operators
- constraints
- events
- traces
- replay
- versioning

The goal is not mathematical ornamentation.
The goal is to make SRP definitions precise enough to support theory, implementation, and verification.

---

## 2. Notation

We use a few basic conventions:

- `U` denotes a semantic unit
- `G` denotes a semantic graph
- `S` denotes a semantic state
- `e` denotes a runtime event
- `T` denotes an operator
- `C` denotes a constraint predicate
- `V` denotes a semantic version
- `Tr` denotes a trace
- `R` denotes replay when used as a function name

Where needed, ordered tuples are written with parentheses and sets with braces.

---

## 3. Semantic Unit

A semantic unit is the atomic evolvable object in SRP.

### 3.1 Definition

```text
U = (I, P, Rel, M, L)
```

Where:

- `I` = identity kernel
- `P` = semantic payload
- `Rel` = relation set or relation references
- `M` = memory-related attributes
- `L` = lifecycle attributes

### 3.2 Intuition

- `I` answers: what is this?
- `P` answers: what does it mean?
- `Rel` answers: what connects it?
- `M` answers: how available or active is it?
- `L` answers: what stage of evolution is it in?

### 3.3 Semantic unit identity

The identity kernel must remain stable across allowed evolution.

Formally, for a unit `U`, identity is an invariant under legal transitions:

```text
I(U_t) = I(U_{t+1})
```

unless an explicit identity-splitting or identity-merging operation is authorized.

---

## 4. Semantic Relation

A semantic relation is a typed link between units.

### 4.1 Definition

```text
Rel_i = (src, tgt, type, conf, prov)
```

Where:

- `src` = source unit reference
- `tgt` = target unit reference
- `type` = relation type
- `conf` = relation confidence
- `prov` = provenance / evidence pointer

### 4.2 Relation invariants

- relation endpoints must be valid under the current graph
- relation type must be semantically valid
- relation provenance must remain traceable

---

## 5. Semantic Graph

The semantic graph is the structural arrangement of semantic units and relations.

### 5.1 Definition

```text
G = (V, E)
```

Where:

- `V = {U_1, U_2, ..., U_n}`
- `E = {Rel_1, Rel_2, ..., Rel_m}`

### 5.2 Graph invariants

- each node corresponds to a semantic unit or a unit view
- each edge corresponds to a typed semantic relation
- the graph must preserve identity continuity
- the graph must preserve reference integrity

### 5.3 Derived graph structures

The graph also supports:

- neighborhoods
- subgraphs
- semantic paths
- dependency closures

---

## 6. Semantic State

Semantic state is the runtime configuration of the semantic graph plus its context and metadata.

### 6.1 Definition

One useful form is:

```text
S = (G, Ctx, Meta)
```

Where:

- `G` = semantic graph
- `Ctx` = runtime context
- `Meta` = runtime metadata / histories / summaries

### 6.2 State invariants

- state must contain a valid graph
- state must expose a valid runtime context
- state metadata must be consistent with the graph and event history

---

## 7. Runtime Event

A runtime event is a permitted transition description.

### 7.1 Definition

```text
e = (id, type, round, actor, targets, parent, trigger, reason, conf, before, after, payload, mode)
```

Where:

- `id` = event identity
- `type` = event family
- `round` = round or timestamp reference
- `actor` = emitter or responsible subsystem
- `targets` = affected object references
- `parent` = causal parent event reference
- `trigger` = what initiated the event
- `reason` = auditable justification
- `conf` = transition confidence
- `before` = reference to prior state or prior field values
- `after` = reference to resulting state or resulting field values
- `payload` = event-specific details
- `mode` = mutation mode

### 7.2 Event semantics

An event describes a transition.
It does not itself execute the transition.

### 7.3 Event invariant

An event is valid only if it is compatible with the current constraint set and event contract.

---

## 8. Semantic Operator

An operator is a graph transformation law.

### 8.1 Definition

```text
T : G -> G
```

More generally, an operator may act on a state:

```text
T : S -> S
```

if the state contains graph and metadata changes.

### 8.2 Operator types

Operators may be:

- canonicalization operators
- merge operators
- split operators
- approximation operators
- recovery operators
- pruning operators
- diff operators
- neighborhood search operators

### 8.3 Operator legality

An operator may be applied only when the relevant constraint predicate holds:

```text
C(G) = True
```

Otherwise the transformation is illegal.

---

## 9. Constraint Predicate

A constraint is a predicate over graph or state validity.

### 9.1 Definition

```text
C : G -> {True, False}
```

or, when needed:

```text
C : S -> {True, False}
```

### 9.2 Constraint role

Constraints define what must never be violated.
They are not the same as rules.

---

## 10. Semantic Version

A semantic version is a referenceable state identity inside an evolution DAG.

### 10.1 Definition

```text
V = (version_id, parents, operator, rule_version, constraint_version, event_ids, state_ref)
```

### 10.2 Version invariants

- version ids must be stable
- parent references must be explicit
- version nodes should store references rather than full state copies

---

## 11. Trace

A trace is a causal structure over semantic evolution.

### 11.1 Definition

```text
Tr = (N, E_c)
```

Where:

- `N` = trace nodes
- `E_c` = causal edges

### 11.2 Trace semantics

Trace explains why a state changed.
It is not a replay log.

---

## 12. Replay

Replay is deterministic reconstruction from initial state and event history.

### 12.1 Definition

```text
R(S_0, E, ρ) = S_t
```

Where:

- `S_0` = initial semantic state
- `E` = ordered event stream
- `ρ` = rule version or replay regime
- `S_t` = reconstructed target state

### 12.2 Replay requirements

- replay must be deterministic for valid inputs
- replay must preserve ordering rules
- replay must report divergence when reconstruction differs from expectation

---

## 13. Transition Semantics

SRP transitions should be modeled as partial functions over valid state-event pairs.

### 13.1 Transition function

```text
δ : (S, e) -> S'
```

where `δ` is defined only when the event is valid under the current constraints.

### 13.2 Illegal transitions

If the constraint predicate fails, `δ` is undefined.

This is the formal basis for blocking illegal transitions before mutation.

---

## 14. Preservation Semantics

Preservation can be modeled as a property of transitions.

For a preservation objective `P`, a transition is acceptable if it satisfies the desired preservation relation:

```text
Preserve(P, S, S') = True
```

This is not yet a full metric.
It is the formal placeholder for later metric-space construction.

---

## 15. Bridge to Metric Space

This formalization intentionally stops short of a full metric definition.

However, it prepares the ground for a semantic metric space by specifying:

- the objects whose distances will be measured
- the attributes that may participate in distance
- the transition laws that the metric will help evaluate

The metric space can later define:

- identity distance
- structural distance
- semantic distance
- history distance
- activation distance
- context distance

---

## 16. Relation to Current Implementation

The current repository already exposes partial formal counterparts:

- semantic units in parser and object layers
- graphs in semantic graph modules
- events in runtime contracts and interfaces
- traces in recording and summary layers
- replay in recovery and state reconstruction paths

This document makes the underlying mathematics explicit so those implementations can be reasoned about uniformly.

---

## 17. Relationship to Other Documents

Recommended chain:

```text
Semantic Graph Model
  -> Semantic Constraint System
  -> Semantic Graph Algorithms
  -> Semantic Operator Algebra
  -> Semantic Versioning Model
  -> Formal Semantics
  -> Semantic Metric Space
  -> Runtime Semantics
  -> Semantic Time Model
  -> Runtime Kernel
```

This document is the formal base for the rest of the theory stack.

---

## 18. Scope

This document defines formal semantic objects and transition laws only.

It does not define:

- concrete data schemas
- database storage formats
- implementation classes
- benchmark code

Those belong to the runtime and implementation layers.
