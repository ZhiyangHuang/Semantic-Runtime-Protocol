# SRP Runtime Representation Design

This document bridges the design rationale and the concrete runtime representation.
It is not an implementation spec.

The central question is:

> What information must a runtime representation store in order to preserve SRP's semantic preservation objectives under constrained resources?

SRP does not require a graph specifically.
Graph is one viable implementation of the runtime representation layer.

The concrete runtime objects used by any representation should conform to the shared [Runtime Object Model](SRP_RUNTIME_OBJECT_MODEL.md).

---

## 1. Representation Principles

The runtime representation should be designed around preservation requirements rather than around a fixed data structure.

The representation must:

- preserve identity continuity
- preserve structural coherence
- support semantic value-aware allocation
- make lifecycle state explicit
- attach provenance and confidence to preserved content

This means the representation is responsible for maintaining semantic continuity across extraction, compression, recovery, validation, and update.

---

## 2. Identity Representation

Identity representation tracks whether a semantic entity remains the same across runtime transitions.

It should support:

- entity identifiers
- aliases
- reference chains
- lineage tracking

Useful questions:

- Is this still the same entity?
- Has the entity been split, merged, or renamed?
- Can the system recover the same identity after compression?

Identity representation is the basis for continuity across updates.

---

## 3. Relation Representation

Relation representation tracks how semantic units are connected.

It should support:

- dependency
- constraint
- causal relation
- temporal relation
- ownership or part-of style relation

Useful questions:

- Which relations must survive for the state to remain coherent?
- Which edges are critical for structural preservation?
- Which relation types are most likely to be lost under pressure?

Relation representation is the basis for structural coherence.

---

## 4. Importance Representation

Importance representation tracks which semantic units should survive first when resources are limited.

It should support:

- importance
- confidence
- activation
- selection priority

Useful questions:

- Which semantic units are high-value?
- Which units should survive compression?
- Which units should be retained even when the budget is tight?

Importance representation is the basis for semantic value-aware allocation.

---

## 5. Lifecycle Representation

Lifecycle representation tracks the runtime state of each semantic unit.

It should support:

- extracted
- canonicalized
- merged
- compressed
- recovered
- validated
- updated
- archived

Useful questions:

- Where did this semantic unit come from?
- Has it been compressed or restored before?
- Is it active, archived, or stale?

Lifecycle representation is the basis for explicit state transitions and preservation auditing.

---

## 6. Runtime Metadata

Runtime metadata is not the semantic content itself.
It is the maintenance information used to support preservation.

The main metadata types are:

- provenance
- confidence
- activation history
- restore history
- lifecycle history

Metadata should help answer:

- how reliable is this semantic content
- how was it produced
- how often has it survived recovery
- how stable is it under runtime pressure

---

## 7. Representation to Policy Interface

The runtime representation must expose enough structure for policy to make informed decisions.

Policy consumes:

- identity signals
- relation signals
- importance signals
- lifecycle signals
- metadata signals

Policy produces:

- retention decisions
- allocation decisions
- archive decisions
- recovery decisions

This is where the representation and policy layers meet.

---

## 8. Representation to Evaluation Interface

The representation should be inspectable at every stage of the lifecycle.

This enables evaluation of:

- identity retention
- structural coherence
- value-aware allocation
- boundary behavior under pressure
- drift across time
- attribution across mechanisms

The evaluation layer does not merely score outcomes.
It tests whether the representation preserves the right semantic properties.

---

## 9. Relationship to Graph-based Implementations

Graph-based representation is a practical realization of the runtime representation design.

It is useful because graphs naturally encode:

- identity links
- relation structure
- dependency chains
- lifecycle transitions

However, Graph is not the theoretical contribution.
The theoretical contribution is the runtime representation design that preserves semantic properties under constrained resources.

---

## 10. Scope

This document covers the representation bridge between the design rationale and a concrete implementation.

It does not define:

- benchmark policy
- ablation protocol
- external baselines
- full Graph v2 implementation details

Those belong to later specification and evaluation documents.
