# SRP Runtime Semantics

This document defines the execution semantics of SRP.
It is not an implementation spec and not a kernel API spec.

The central question is:

> Given a formal semantic state and an admissible event, how does SRP define the next runtime state in a way that is independent of a particular programming language or kernel implementation?

This layer sits beneath semantic metric space and above the minimal runtime kernel.

---

## 1. Purpose

Formal semantics define the objects and transition laws.
Runtime semantics define how those laws are executed over time.

This document formalizes:

- runtime configuration
- runtime step semantics
- event processing order
- constraint gating
- metric-guided candidate selection
- deterministic state transition
- replay compatibility

The runtime semantics are the execution model of SRP.
The kernel is only one possible implementation of that model.

---

## 2. Runtime Configuration

One useful abstraction is:

```text
R = (S, Q, P, C, M)
```

Where:

- `S` = current semantic state
- `Q` = event queue or pending event set
- `P` = active policies
- `C` = active constraints
- `M` = metric space or metric service

This configuration describes the current runtime situation.

---

## 3. Runtime Step

A runtime step advances the runtime configuration.

### 3.1 Step function

```text
step(R) = R'
```

or, when the step is event-driven:

```text
delta_runtime : (R, e) -> R'
```

Where:

- `R` = current runtime configuration
- `e` = admissible runtime event
- `R'` = next runtime configuration

### 3.2 Step semantics

A runtime step is not arbitrary mutation.
It is the result of:

- event selection
- constraint checking
- metric evaluation
- operator application
- state transition
- recording

---

## 4. Runtime Transition Pipeline

The execution pipeline should be conceptually ordered as:

```text
Event
  -> Constraint Check
  -> Metric Evaluation
  -> Operator Selection
  -> State Transition
  -> Record Update
```

### 4.1 Event

An event proposes a semantic change.

### 4.2 Constraint check

The transition is blocked if the required constraints do not hold.

### 4.3 Metric evaluation

The runtime may rank candidate transitions or candidate targets using the semantic metric space.

### 4.4 Operator selection

The runtime chooses the operator that will realize the change if the candidate is admissible.

### 4.5 State transition

The state changes only after the transition is authorized.

### 4.6 Record update

The runtime records the transition in history, trace, or replay-oriented storage.

---

## 5. Runtime Determinism

Runtime semantics should be deterministic for valid inputs and fixed rule / constraint versions.

If the same runtime configuration and admissible event are supplied, the runtime should produce the same next state.

```text
delta_runtime(R, e) = R'
```

for the same valid inputs and fixed semantics.

Determinism is essential for replay and attribution.

---

## 6. Runtime Invariants

The runtime must preserve several invariants.

### 6.1 Constraint invariance

No transition may violate the active constraint system.

### 6.2 Traceability invariance

Every applied transition must be explainable by an event and a causal record.

### 6.3 Replay compatibility

Valid event histories should remain replayable under the same rule and constraint versions.

### 6.4 History integrity

Event history should be append-only or versioned.

### 6.5 Separation invariance

The runtime must not collapse policy, constraints, metrics, and mutation into one undifferentiated action.

---

## 7. Runtime and Metrics

The runtime may consult the semantic metric space, but it must not let metrics override constraints.

### Rule

```text
constraints > metrics > operator ranking
```

Metrics may guide candidate ranking and selection.
Constraints decide legality.

---

## 8. Runtime and Events

Events are the runtime's transition interface.

The runtime should treat events as:

- ordered
- typed
- constrained
- traceable
- replayable

An event does not become a transition until it passes runtime semantics.

---

## 9. Runtime and Replay

Replay is the reconstruction of runtime semantics from a valid event history.

Therefore runtime semantics and replay must share:

- ordering rules
- constraint rules
- operator semantics
- version semantics

If runtime semantics and replay semantics diverge, replay loses meaning.

---

## 10. Runtime and Kernel

The minimal runtime kernel is an implementation of runtime semantics.

The runtime semantics define:

- what a valid step is
- what counts as a legal transition
- what must be recorded
- what determinism means

The kernel implements that behavior in code.

This separation matters because the kernel may change while the semantics remain stable.

---

## 11. Relation to Current Implementation

The current system already has runtime-like behavior:

- event construction
- recovery and repair paths
- validation and drift measurement
- state transition and summary updates

This document provides the common execution semantics that those paths should converge toward.

---

## 12. Relationship to Other Documents

Recommended chain:

```text
Formal Semantics
  -> Semantic Metric Space
  -> Runtime Semantics
  -> Semantic Time Model
  -> Minimal Runtime Kernel
```

Runtime semantics also connect to:

- Replay Spec
- Semantic Evolution Trace Spec
- Runtime Recording Layer Alignment

---

## 13. Scope

This document defines execution semantics only.

It does not define:

- concrete event handlers
- kernel implementation code
- database or queue implementation
- benchmark code

Those belong to later implementation work.

