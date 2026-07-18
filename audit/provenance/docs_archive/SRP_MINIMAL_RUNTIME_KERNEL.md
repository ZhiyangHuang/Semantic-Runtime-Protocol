# SRP Minimal Runtime Kernel

This document defines the operational semantics of the minimal SRP runtime.
It is not an architecture essay and not a full kernel implementation spec.

The central question is:

> What is the smallest set of runtime primitives and transition rules that can realize SRP runtime semantics in a platform-independent way?

This document sits below runtime semantics and semantic time, and above any concrete implementation.

---

## 1. Purpose

The minimal runtime kernel is the smallest executable reference model for SRP.

It exists to:

- realize runtime semantics
- preserve deterministic transition behavior
- provide a stable target for replay and trace
- expose a small, platform-independent primitive set

The kernel is not the theory itself.
It is the operational realization of the theory.

---

## 2. Runtime Primitives

The minimal runtime should expose a small primitive set.

```text
Submit(Event)
Validate(Event)
Evaluate(Metric)
Execute(Operator)
Commit(State)
Replay(Stream)
Query(State)
```

These are runtime primitives, not Python APIs.

They describe what the runtime must be able to do.

### 2.1 Submit

Submit inserts an event or event proposal into the runtime boundary.

Properties:

- does not mutate state directly
- creates a candidate for validation
- preserves event identity

### 2.2 Validate

Validate checks whether an event is allowed under the active constraint set and event contract.

Properties:

- constraint-first
- legality gate
- no state mutation

### 2.3 Evaluate

Evaluate scores candidate transitions or candidate targets using the semantic metric space.

Properties:

- ranking only
- no mutation
- no policy creation

### 2.4 Execute

Execute applies an authorized operator to the current semantic state.

Properties:

- uses a valid operator
- respects constraints
- produces a new state candidate

### 2.5 Commit

Commit makes the resulting state current and records the transition.

Properties:

- updates current state reference
- appends event / version / trace evidence
- keeps lineage visible

### 2.6 Replay

Replay reconstructs state from an initial state and ordered history.

Properties:

- deterministic for valid inputs
- no hidden mutation
- no re-sampling of semantics

### 2.7 Query

Query returns a read-only projection of the current state or a versioned state reference.

Properties:

- read-only
- no side effects
- no hidden update

---

## 3. Operational State Machine

The minimal runtime can be modeled as a small state machine.

```text
Idle
  -> Pending
  -> Validating
  -> Evaluating
  -> Executing
  -> Committed
```

Auxiliary runtime modes:

```text
Replaying
RollingBack
Recovering
```

These modes are not separate theories.
They are operational states of the runtime.

### 3.1 Idle

No pending event is currently being processed.

### 3.2 Pending

An event or proposal has been received.

### 3.3 Validating

The runtime is checking constraints and event legality.

### 3.4 Evaluating

The runtime is scoring candidate transitions, if needed.

### 3.5 Executing

The runtime is applying the selected operator.

### 3.6 Committed

The transition has been applied and recorded.

### 3.7 Replaying

The runtime is reconstructing state from history.

### 3.8 RollingBack

The runtime is returning to a previous semantic version or valid state.

### 3.9 Recovering

The runtime is restoring a degraded or missing semantic structure.

---

## 4. Runtime Transition Semantics

The minimal runtime transition can be described as:

```text
delta_runtime : (R, Primitive) -> R'
```

Where:

- `R` = runtime configuration
- `Primitive` = one of the runtime primitives
- `R'` = next runtime configuration

### 4.1 Runtime configuration

One useful abstraction is:

```text
R = (S, Q, P, C, M, T)
```

Where:

- `S` = semantic state
- `Q` = pending event queue
- `P` = active policies
- `C` = active constraints
- `M` = semantic metric space
- `T` = semantic time state

### 4.2 Step semantics

A runtime step is a constrained transition:

```text
Submit
  -> Validate
  -> Evaluate
  -> Execute
  -> Commit
```

Replay, rollback, and recovery are specialized runtime modes that still obey the same core legality and determinism rules.

---

## 5. Instruction View

The primitive set can later be formalized as a semantic runtime instruction set.

For now, this is only a design direction, not a new theory requirement.

Possible future instruction families:

- `MERGE`
- `SPLIT`
- `RECOVER`
- `FORGET`
- `APPROX`
- `ACTIVATE`
- `VALIDATE`
- `COMMIT`
- `CHECKOUT`
- `ROLLBACK`
- `TRACE`
- `REPLAY`
- `QUERY`

This future formalization may be called SRIS, but SRIS is not required for the current theory stack.

---

## 6. State Semantics

The minimal runtime should guarantee:

- semantic state changes only through authorized primitives
- event legality is checked before mutation
- metric evaluation never overrides constraints
- commit preserves version and trace references
- replay reconstructs valid state without hidden side effects

### 6.1 Determinism

For fixed inputs and fixed rule / constraint versions:

```text
delta_runtime(R, Primitive) = R'
```

must be stable for valid inputs.

### 6.2 Safety

Illegal transitions must be blocked before commit.

---

## 7. Primitive to Runtime Mapping

The primitive layer can be interpreted as:

- `Submit` -> event entry
- `Validate` -> constraint gate
- `Evaluate` -> metric-guided ranking
- `Execute` -> operator application
- `Commit` -> state/version update
- `Replay` -> reconstruction
- `Query` -> read-only projection

This mapping is the operational semantics of the runtime.

---

## 8. Runtime Invariants

The minimal runtime must preserve:

- event identity stability
- constraint priority over convenience
- traceability of every commit
- replay determinism for valid streams
- append-only or versioned history behavior
- read-only query behavior

---

## 9. Relationship to Runtime Semantics

Runtime semantics define how transitions are allowed in principle.
The minimal runtime kernel defines one reference implementation of those semantics.

The kernel may later be replaced or optimized, but the operational semantics should remain stable.

---

## 10. Relationship to Current Implementation

The current experimental code already provides partial realizations of these primitives:

- submit-like behavior in pipeline coordination
- validate-like behavior in validation modules
- evaluate-like behavior in metric computation
- execute-like behavior in recovery / repair / lifecycle transitions
- commit-like behavior in state update and record building
- replay-like behavior in recovery reconstruction
- query-like behavior in state and projection helpers

This document defines the minimal reference target for those behaviors.

---

## 11. Relationship to Other Documents

Recommended chain:

```text
Formal Semantics
  -> Semantic Metric Space
  -> Runtime Semantics
  -> Semantic Time Model
  -> Minimal Runtime Kernel
  -> Runtime Kernel Interface
```

The minimal kernel is the first executable reference model for the runtime semantics stack.

---

## 12. Scope

This document defines operational semantics only.

It does not define:

- concrete Python classes
- dispatch mechanics
- storage backends
- distributed execution

Those belong to later implementation work.

