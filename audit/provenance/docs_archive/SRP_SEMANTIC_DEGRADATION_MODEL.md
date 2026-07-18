# SRP Semantic Degradation Model

This document defines how semantic loss occurs in long-running runtime systems.
It is not an implementation spec.

The central question is:

> What does semantic degradation look like when runtime resources are constrained?

SRP is designed to detect, measure, and reduce the main degradation modes.

---

## 1. Degradation Overview

Semantic degradation happens when the runtime state after pressure, compression, or recovery no longer preserves the semantic properties that mattered in the source state.

In practice, degradation can occur even when the system still returns a fluent output.

That is why SRP distinguishes semantic preservation from surface realization.

---

## 2. Identity Degradation

Identity degradation occurs when entities are split, merged, renamed incorrectly, or lose reference continuity.

Example:

```text
before:
Alice = Entity_1

after:
Alice_1 + Alice_2
```

Symptoms:

- broken reference chains
- duplicate entities
- entity fragmentation
- identity drift

Why it matters:

- long-horizon continuity fails
- later recovery cannot reliably reconstruct the same entity

---

## 3. Structural Degradation

Structural degradation occurs when important relations are lost, weakened, or mismatched.

Example:

```text
before:
A -> dependency -> B -> constraint -> C

after:
A
B
C
```

Symptoms:

- broken dependency chains
- missing constraints
- relation collapse
- inconsistent relation recovery

Why it matters:

- the state still contains objects, but the semantic structure is gone

---

## 4. Selection Degradation

Selection degradation occurs when the wrong content survives constrained retention.

Example:

```text
100 semantic units -> 20 retained
```

If the retained set drops important but low-frequency information first, selection has degraded.

Symptoms:

- important content is removed
- low-value content is kept
- selection composition drifts without semantic justification

Why it matters:

- the runtime state is still non-empty, but it no longer preserves what matters

---

## 5. Runtime Degradation

Runtime degradation occurs when repeated cycles produce inconsistent preservation behavior.

Example:

```text
cycle 1: retain X
cycle 10: drop X
```

Symptoms:

- drift
- seed sensitivity
- unstable thresholds
- inconsistent archive/recovery behavior

Why it matters:

- long-running systems cannot rely on stable preservation behavior

---

## 6. Preservation Loss as a Transition Failure

Degradation can be framed as a transition failure:

```text
S_t -> S_(t+1)
```

If the transition does not preserve identity, structure, value, or stability, the system has degraded.

This is the key link between degradation and the semantic state model.

---

## 7. Relationship to Evaluation

The degradation model tells evaluation what to measure.

The evaluation matrix should test:

- whether identity loss occurred
- whether structural loss occurred
- whether value-aware selection failed
- whether runtime behavior drifted

This is why boundary, robustness, drift, attribution, and ablation are all preservation tests rather than generic performance tests.

---

## 8. Relationship to Policy and Representation

Representation tries to keep the state interpretable and recoverable.
Policy tries to decide which parts of the state survive under pressure.

Both are responses to degradation.

Without a degradation model, the rationale for representation and policy is incomplete.

---

## 9. Scope

This document defines the failure modes that SRP is built to reduce.

It does not define:

- the concrete state schema
- the runtime implementation
- the benchmark suite
- the full attribution protocol

Those belong to later design and evaluation documents.

