# SRP Semantic State Model

This document defines the abstract semantic state that SRP preserves and updates over time.
It is not an implementation spec.

The central question is:

> What is the semantic runtime state that evolves inside SRP?

SRP should be understood as a state transition framework.
Each runtime step transforms one semantic state into another while trying to preserve important semantic properties.

The runtime state should be implemented through the shared [Runtime Object Model](SRP_RUNTIME_OBJECT_MODEL.md), so that entities, relations, context, and history all follow one contract.

---

## 1. State Definition

The runtime state is not raw text.
It is a structured semantic object describing what the system currently knows, how confident it is, and how that knowledge evolved.

A simplified state view is:

```text
S_t =
{
  Entities,
  Relations,
  Importance,
  Lifecycle,
  Provenance,
  Confidence,
  History
}
```

This definition is intentionally abstract.
Different implementations may realize the state as a graph, layered IR, tables, or hybrid structures.

The important point is that the runtime state is explicit and updateable.

---

## 2. State Components

### 2.1 Entities

Entities are semantic units that should remain identifiable across updates.

Examples:

- people
- objects
- concepts
- tasks
- events

Entity state captures:

- identity
- label
- aliases
- lineage

### 2.2 Relations

Relations connect semantic units and express how they depend on one another.

Examples:

- dependency
- constraint
- ownership
- causality
- temporal ordering

Relation state captures:

- source
- target
- relation type
- relation criticality
- relation confidence

### 2.3 Importance

Importance records what should survive first under pressure.

It captures:

- semantic value
- selection priority
- relative salience

### 2.4 Lifecycle

Lifecycle records the runtime condition of each semantic unit.

It captures:

- active
- compressed
- archived
- recovered
- validated

### 2.5 Provenance

Provenance records where semantic content came from and how it entered the system.

It captures:

- source origin
- extraction path
- update path
- recovery path

### 2.6 Confidence

Confidence records how reliable a semantic unit or relation is.

It captures:

- extraction confidence
- relation confidence
- recovery confidence
- validation confidence

### 2.7 History

History records how the state changed over time.

It captures:

- prior decisions
- archive events
- recovery events
- drift history

---

## 3. State Transition View

SRP should be modeled as a transition system:

```text
S_t -> S_(t+1)
```

The transition is driven by:

- new semantic input
- canonicalization
- representation update
- policy decision
- retention / compression / archive
- recovery / validation

This means the state is not static.
It evolves through runtime pressure and policy action.

---

## 4. Preservation Targets

The semantic state model is designed to preserve:

- identity continuity
- structural coherence
- semantic value-aware allocation
- runtime stability

These are the preservation objectives the state must support.

If a state transition violates them, degradation has occurred.

---

## 5. Failure Modes at the State Level

The state model helps explain what failure looks like.

### 5.1 Identity Failure

The same entity cannot be reliably recognized across updates.

### 5.2 Structural Failure

Important relations are lost or become inconsistent.

### 5.3 Value Failure

The wrong semantic content survives pressure.

### 5.4 Stability Failure

Repeated transitions produce inconsistent or drifting states.

---

## 6. Relationship to Representation and Policy

The semantic state model is the anchor for both representation and policy.

- representation stores the state
- policy manipulates the state under constraints
- evaluation measures whether the state preserved the right properties

Without an explicit state model, representation and policy do not have a shared target.

---

## 7. Scope

This document defines the abstract runtime state used by SRP.

It does not define:

- the concrete graph structure
- the full policy code path
- the benchmark suite
- the evaluation matrix

Those belong to later design and evaluation documents.
