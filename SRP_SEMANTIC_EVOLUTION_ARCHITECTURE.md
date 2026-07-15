# SRP Semantic Evolution Architecture

This document is the architecture bible for SRP.
It describes how the SRP system is composed, how the subsystems collaborate, and what invariants must hold across the whole protocol stack.

It is not a theory map and not a document index.

The central question is:

> What systems make up SRP, how do they depend on one another, and how does semantic state move end-to-end through the architecture?

---

## 1. Architectural Purpose

SRP is a semantic evolution system.
It is composed of four orthogonal subsystems:

```text
Representation Layer
  -> Evolution Layer
  -> Execution Layer
  -> Evaluation Layer
```

These layers are not document categories.
They are system responsibilities.

The architecture exists to make the relationship between state, change, execution, and measurement explicit.

---

## 2. The Four Subsystems

### 2.1 Representation Layer

Question:

> What is the world?

Responsibilities:

- define semantic objects
- define semantic graphs
- define runtime objects
- define contracts for fields and relationships

Core assets:

- `SemanticUnit`
- `SemanticGraph`
- `RuntimeObject`
- `RuntimeDataContract`

This layer is read-heavy and structure-first.
It does not decide how things should change.

### 2.2 Evolution Layer

Question:

> How does the world change?

Responsibilities:

- define graph transformation operators
- define semantic constraints
- define evolution rules
- define semantic versioning

Core assets:

- `Semantic Graph Operators`
- `Semantic Constraint System`
- `Semantic Evolution Rules`
- `Semantic Versioning Model`

This layer decides legal and meaningful change at the theory level.
It does not directly mutate runtime state.

### 2.3 Execution Layer

Question:

> Who applies the change?

Responsibilities:

- define runtime events
- validate event legality
- apply transitions
- replay event histories
- build trace explanations
- record runtime evidence

Core assets:

- `RuntimeEvent`
- `Minimal Runtime Kernel`
- `Replay Engine`
- `Trace Builder`
- `Runtime Recording Layer`

This layer executes and records change.
It must preserve determinism and traceability.

### 2.4 Evaluation Layer

Question:

> How do we know SRP is good?

Responsibilities:

- define preservation metrics
- define attribution metrics
- define benchmark comparisons
- measure drift and recovery quality

Core assets:

- preservation metrics
- attribution framework
- benchmark suites
- ablation / comparison protocols

This layer does not mutate runtime behavior.
It observes and measures.

---

## 3. End-to-End Lifecycle

The architectural lifecycle should look like this:

```text
Semantic Input
  -> Representation
  -> Semantic Graph
  -> Constraint Check
  -> Graph Operator
  -> Semantic Version Commit
  -> Runtime Event
  -> Kernel Execution
  -> State Update
  -> Trace
  -> Replay
  -> Evaluation
```

This is the canonical SRP flow.

Each stage has a distinct responsibility:

- Representation constructs structure
- Evolution changes structure under rules
- Execution applies the allowed change
- Evaluation judges the outcome

---

## 4. Capability Dependencies

The subsystems are related by capability dependence, not by documentation order.

```text
Evaluation
  depends on Execution
Execution
  depends on Evolution
Evolution
  depends on Representation
```

This means:

- evaluation cannot be correct if execution is unclear
- execution cannot be correct if evolution rules are undefined
- evolution cannot be meaningful if representation is unstable

The dependency arrow is not a citation arrow.
It expresses runtime responsibility dependence.

---

## 5. Architectural Invariants

The following invariants must hold across the architecture.

### 5.1 Representation must not depend on Execution

Representation defines what exists.
It must not require the runtime kernel to define basic structure.

### 5.2 Evolution must not directly mutate state

Evolution defines what should change and when.
It must not bypass the event boundary.

### 5.3 Execution must not decide Policy

Execution applies the chosen transition.
It must not choose retention, compression, or recovery strategy on its own.

### 5.4 Evaluation must not mutate Runtime

Evaluation measures the system.
It must not rewrite semantic state, event history, or version history.

### 5.5 Constraints must override convenience

If a transition is convenient but illegal, it must be blocked.

### 5.6 Trace and Replay must remain separate

Trace explains causality.
Replay reconstructs state.
They are complementary, not interchangeable.

---

## 6. Replaceability Rules

One goal of the architecture is to allow substitution without collapsing the system.

### 6.1 Representation replaceability

Representation may change from:

- graph
- hypergraph
- other semantic structure

as long as the same semantic contract is preserved.

### 6.2 Evolution replaceability

Operators may evolve from:

- rule-based
- search-based
- embedding-assisted
- model-assisted

without changing the architectural role of the evolution layer.

### 6.3 Execution replaceability

The runtime kernel may later become:

- local
- distributed
- instrumented

as long as event legality, replayability, and traceability remain intact.

### 6.4 Evaluation replaceability

Metrics may evolve over time.
The evaluation layer should remain separable from the execution layer.

---

## 7. Architecture Invariants by Layer

### Representation Layer

- stable object identity
- explicit relations
- readable field contracts

### Evolution Layer

- legal transitions only
- constraints first
- operator order is meaningful

### Execution Layer

- single mutation boundary
- deterministic replay for valid streams
- traceable event application

### Evaluation Layer

- no side effects on runtime state
- attribution must be explainable
- benchmarks must be comparable

---

## 8. Architecture and the Current Project Structure

The current repository already contains all four subsystems in partial form.

Examples:

- Representation: semantic units, runtime objects, graphs, data contracts
- Evolution: operators, constraints, versioning, rules
- Execution: events, kernel interfaces, replay, trace, recording
- Evaluation: preservation metrics, attribution, benchmarks, experiments

The current codebase is therefore not a prototype of a single module.
It is an early projection of a complete architecture.

---

## 9. Volume Structure

The architecture can be organized into four volumes.

### Volume I - Foundations

Contains:

- Design Rationale
- Semantic State
- Semantic Graph
- Constraints
- Evolution Rules

### Volume II - Runtime

Contains:

- Semantic Unit Model
- Runtime Data Contract
- Runtime Event Contract
- Runtime Kernel
- Replay
- Trace
- Recording

### Volume III - Evaluation

Contains:

- Preservation
- Attribution
- Benchmarks
- Metrics

### Volume IV - Implementation

Contains:

- Protocol Map
- Alignment
- Adapter Plan
- Migration Checklist
- Callsite Map

The volumes are organizational.
They do not change the architecture itself.

---

## 10. Why This Is Not the Theory Map

The Theory Map answers:

- what documents exist
- what question each document answers
- how the documentation stack is ordered

This Architecture document answers:

- what subsystems exist
- how they depend on one another
- what invariants constrain them
- what can be replaced without breaking the system

The two documents serve different purposes.

---

## 11. Relationship to End-to-End Use

The architecture must support this chain:

```text
User Input
  -> Representation
  -> Evolution
  -> Execution
  -> Trace
  -> Replay
  -> Evaluation
```

This chain is the project-level lifecycle for SRP.

If any layer disappears, the system becomes incomplete:

- without Representation, there is no structured meaning
- without Evolution, there is no controlled change
- without Execution, there is no runtime behavior
- without Evaluation, there is no evidence of quality

---

## 12. Relationship to Other Documents

Recommended top-level chain:

```text
README
  -> SRP Semantic Evolution Architecture
  -> SRP Theory Map
  -> Specific Theory Documents
```

The architecture document is the conceptual anchor for the whole project.

---

## 13. Scope

This document defines system architecture only.

It does not define:

- individual schemas
- event schemas
- operator implementations
- kernel internals
- benchmark code

Those belong to the specific theory and implementation documents.
