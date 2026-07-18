# SRP Mechanism Attribution Framework

This document defines how SRP attributes preservation behavior to individual runtime mechanisms.
It is not an experiment report.

The central question is:

> When preservation changes, which SRP mechanism is responsible, and which preservation objective did it affect?

SRP is a multi-mechanism system.
Attribution is therefore required to explain preservation changes rather than simply observe them.

---

## 1. Attribution Motivation

SRP contains multiple interacting mechanisms:

- importance weighting
- dependency retention
- lifecycle tracking
- archive and recovery
- budget allocation

Observed preservation behavior is not caused by one mechanism alone.
Attribution is needed to explain which mechanism is responsible for which change.

This makes attribution an explanation layer, not a ranking layer.

---

## 2. Attribution Model

The basic attribution chain is:

```text
Mechanism
  -> State transition behavior
  -> Preservation objective change
  -> Observable metric
```

This means a metric change is only the surface signal.
The theoretical question is which preservation objective changed and which mechanism caused it.

Example:

```text
importance weighting
  -> selection decision
  -> value preservation
  -> important-item capture
```

---

## 3. Mechanism Attribution Matrix

SRP mechanisms should be mapped to the preservation objectives they primarily support.

| Mechanism | Primary Objective | Secondary Effect | Typical Failure Mode |
| --- | --- | --- | --- |
| importance weighting | semantic value-aware allocation | selection composition | important content loss |
| dependency retention | structural coherence | validation continuity | relation collapse |
| archive policy | identity continuity | runtime stability | recovery failure |
| lifecycle tracking | runtime stability | recovery quality | drift |
| budget allocation | global preservation trade-off | all objectives | boundary shift |

This matrix is the conceptual basis for later attribution experiments.

---

## 4. Current Attribution Evidence

### 4.1 Importance Weighting

Mechanism:

- `remove_importance_weighting`

Observed:

- selection composition changes
- overlap changes
- important-item capture changes
- allocation boundary remains relatively stable on the current frozen sweep

Interpretation:

- importance weighting primarily supports semantic selection preservation

### 4.2 Dependency Retention

Mechanism:

- `remove_dependency_retention`

Observed:

- dependency coverage decreases
- dependency F1 decreases
- allocation remains comparatively stable

Interpretation:

- dependency retention primarily supports structural coherence

---

## 5. Future Attribution Directions

The attribution framework is not complete without the lifecycle and archive mechanisms.

### 5.1 Archive Policy

Expected effect:

- identity continuity decreases when archive support is removed
- recovery accuracy decreases
- long-horizon stability weakens

Primary objective:

- identity continuity

### 5.2 Lifecycle Tracking

Expected effect:

- drift increases
- boundary stability weakens
- recovery consistency weakens

Primary objective:

- runtime stability

These remain future attribution targets until the corresponding experiments are completed.

---

## 6. Attribution Is Not Optimization

Attribution should not be interpreted as searching for the best mechanism.

SRP already shows that preservation objectives are in trade-off.
Therefore attribution answers:

- which mechanism supports which objective
- which objective degrades when a mechanism is removed
- which metric change is the observable consequence

Attribution is explanation, not mechanism ranking.

---

## 7. Connection to Evaluation

The evaluation stack uses different layers for different questions:

- Boundary: where does preservation begin to fail
- Robustness: how stable is the preservation behavior
- Drift: how does preservation change over time
- Attribution: which mechanism caused the change

Together these form a complete preservation analysis stack.

---

## 8. Scope

This document defines the theoretical attribution framework for SRP.

It does not define:

- the exact experiment runner
- the final benchmark set
- the concrete graph implementation
- the external baseline matrix

Those belong to later implementation and evaluation documents.

