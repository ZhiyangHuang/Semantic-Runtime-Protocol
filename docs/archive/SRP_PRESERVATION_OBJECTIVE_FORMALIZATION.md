# SRP Preservation Objective Formalization

This document defines how SRP's semantic preservation objectives are represented and measured.
It is not a mathematical proof document.

The central question is:

> How can SRP express semantic preservation in a way that is measurable across runtime transitions?

SRP does not require a single scalar objective.
It preserves a vector of semantic properties across constrained runtime evolution.

---

## 1. Preservation as a Transition Property

SRP should not be evaluated by asking whether the runtime state stays exactly the same.

The runtime state changes by design:

```text
S_t -> S_(t+1)
```

The relevant question is whether the transition preserved the semantic properties that mattered.

This means preservation is a relation between states, not a static label.

---

## 2. Preservation Vector

SRP preservation can be summarized as a vector:

```text
P(S_t, S_(t+1)) =
[
  Identity,
  Structure,
  Value,
  Stability
]
```

Each component captures a different aspect of runtime preservation.

The purpose of the vector is not to force a single score.
The purpose is to keep the objectives separable.

---

## 3. Identity Continuity

Identity continuity asks:

> Does the runtime preserve what is the same thing?

### 3.1 Formal View

Identity preservation can be viewed as:

```text
P_identity =
preserved identity mappings /
required identity mappings
```

### 3.2 What It Measures

- entity matching
- alias consistency
- lineage recovery
- reference continuity

### 3.3 What It Fails On

- split entities
- merged entities
- broken references
- identity drift

### 3.4 Relation to Evaluation

Identity continuity is what recovery and long-horizon continuity should preserve.

---

## 4. Structural Coherence

Structural coherence asks:

> Does the runtime preserve meaningful relationships among semantic units?

### 4.1 Formal View

Structural preservation can be viewed as:

```text
P_structure =
preserved critical relations /
required critical relations
```

### 4.2 What It Measures

- dependency preservation
- constraint preservation
- relation integrity
- relation recovery

### 4.3 What It Fails On

- broken dependency chains
- missing constraints
- relation collapse
- inconsistent relation reconstruction

### 4.4 Relation to Evaluation

Structural coherence is what dependency-aware retention and dependency-focused benchmarks should preserve.

---

## 5. Semantic Value-aware Allocation

Semantic value-aware allocation asks:

> Under limited budget, does SRP preserve high-value information first?

### 5.1 Formal View

Value preservation can be viewed as:

```text
P_value =
retained semantic value /
total semantic value
```

### 5.2 What It Measures

- important-item capture
- weighted retention
- selection overlap
- selection rank shift

### 5.3 What It Fails On

- important but low-frequency content lost first
- high-surface-frequency content retained instead of high-value content
- selection composition drifts without semantic justification

### 5.4 Relation to Evaluation

Value-aware allocation is what importance weighting should support and what A1 tests.

---

## 6. Runtime Stability

Runtime stability asks:

> Does preservation behavior remain stable across runtime evolution?

### 6.1 Formal View

Stability can be treated as inverse variance over preservation outcomes:

```text
P_stability = 1 - variance(preservation behavior)
```

### 6.2 What It Measures

- boundary midpoint variance
- detection rate stability
- drift magnitude
- seed sensitivity

### 6.3 What It Fails On

- unstable thresholds
- cycle-dependent changes
- inconsistent archive/recovery behavior
- seed-sensitive preservation collapse

### 6.4 Relation to Evaluation

Stability is what boundary robustness and drift tests should preserve.

---

## 7. Objective Decomposition

These preservation objectives map naturally to the current mechanism evidence.

| Preservation Objective | Main Mechanism Evidence |
| --- | --- |
| Identity continuity | archive / recovery / lineage support |
| Structural coherence | dependency retention |
| Semantic value-aware allocation | importance weighting |
| Runtime stability | lifecycle and budget policy |

This table is not a final theorem.
It is a working formalization that keeps theory and evidence aligned.

---

## 8. Why a Vector Instead of a Scalar

SRP should not collapse preservation into a single score because the objectives are not perfectly aligned.

For example:

- preserving more content can weaken selectivity
- preserving structure can increase budget cost
- preserving continuity can require archive overhead
- preserving stability can reduce aggressiveness

This is why the Pareto-like policy space observed in evaluation is expected.

The preservation vector keeps the objectives separable and lets policy trade them off explicitly.

---

## 9. Relationship to the Rest of SRP

The preservation objective formalization connects:

- the semantic state model
- the degradation model
- the runtime representation
- the policy mechanism design
- the runtime lifecycle design
- the evaluation objective matrix

This document is the bridge that turns descriptive objectives into measurable runtime targets.

---

## 10. Scope

This document defines the current preservation objective language for SRP.

It does not define:

- the final benchmark suite
- the concrete graph implementation
- the complete attribution protocol
- the external baseline matrix

Those belong to later implementation and evaluation documents.

