# SRP Policy Mechanism Design

This document bridges runtime representation and evaluation by explaining how SRP decides what semantic information survives under constrained resources.
It is not an implementation spec.

The central question is:

> How does SRP allocate limited runtime resources so that semantic preservation objectives are maintained as much as possible?

Policy in SRP is not a single performance optimizer.
It is a preservation mechanism that trades off competing semantic goals under budget.

Policy should operate on the shared [Runtime Object Model](SRP_RUNTIME_OBJECT_MODEL.md), especially `SemanticUnit`, `RelationUnit`, and `RuntimeContext`, rather than on ad hoc module-specific fields.

---

## 1. Policy Role in SRP

Policy determines how runtime resources are assigned when the system cannot preserve everything.

Its purpose is to minimize semantic degradation under pressure.

That means policy should optimize for:

- semantic preservation
- continuity of important content
- structural coherence
- runtime stability

Policy should not be framed as a token maximizer or a generic score optimizer.

---

## 2. Policy Mechanism Decomposition

SRP policy can be decomposed into four mechanism families.

### 2.1 Selection Policy

Selection policy answers:

> What should survive?

Inputs:

- importance
- confidence
- activation
- relation criticality

Outputs:

- selected semantic units

This mechanism is directly related to semantic value-aware allocation.

It is the mechanism most closely associated with the current A1 evidence.

### 2.2 Structural Retention Policy

Structural retention policy answers:

> Which relationships must survive together?

Inputs:

- dependency
- constraint
- relation centrality

Outputs:

- retained relations
- retained relation bundles

This mechanism is directly related to structural coherence.

It is the mechanism most closely associated with the current A2 evidence.

### 2.3 Lifecycle Policy

Lifecycle policy answers:

> When should information change state?

Typical states:

- active
- compressed
- archived
- recovered
- validated

This mechanism supports long-horizon continuity and recovery.

It is the natural bridge to archive-driven and stability-driven future ablations.

### 2.4 Budget Allocation Policy

Budget allocation policy answers:

> How much resource should each semantic component receive?

Inputs:

- pressure
- budget
- objective priority

Outputs:

- allocation decision
- retention threshold
- compression threshold

This mechanism is the direct driver of preservation boundaries.

It explains why preservation begins to fail at specific budget regions.

---

## 3. Policy and Preservation Objective Mapping

Policy mechanisms should map to preservation objectives rather than to aggregate score alone.

| Policy Mechanism | Preserved Objective | Evidence |
| --- | --- | --- |
| importance weighting | semantic value-aware allocation | A1 |
| dependency retention | structural coherence | A2 |
| lifecycle / archive | runtime stability and recovery continuity | future A3 |
| budget allocation | preservation boundary behavior | boundary analysis |

This mapping is the core reason policy exists as a separate design layer.

---

## 4. Policy Trade-off Model

SRP operates under multi-objective preservation trade-offs.

This means:

- improving one objective can weaken another
- some decisions preserve structure at the cost of coverage
- some decisions preserve value at the cost of broad retention
- some decisions preserve continuity at the cost of additional overhead

This is why SRP should be evaluated as a Pareto-like policy space rather than a single optimal policy.

The policy layer therefore explains why the observed evaluation results are structured and not trivially reducible to one scalar metric.

---

## 5. Policy Attribution Interface

Policy attribution connects policy mechanisms to observable preservation outcomes.

### 5.1 Importance Weighting

Remove:

- importance weighting

Observe:

- selection overlap changes
- important-item capture changes
- composition changes more than boundary movement

Interpretation:

- importance weighting supports semantic selection preservation

### 5.2 Dependency Retention

Remove:

- dependency-aware retention

Observe:

- dependency coverage changes
- dependency F1 changes
- allocation remains comparatively stable

Interpretation:

- dependency retention supports structural coherence

### 5.3 Lifecycle Policy

Remove or weaken:

- archive support
- lifecycle tracking

Observe:

- recovery continuity weakens
- long-horizon stability weakens

Interpretation:

- lifecycle policy supports runtime continuity and recovery

### 5.4 Budget Policy

Change:

- active budget
- pressure regime

Observe:

- boundary position changes
- failure onset changes

Interpretation:

- budget policy governs where preservation begins to fail

---

## 6. Relationship to Evaluation

Policy is the mechanism layer that evaluation tests.

The evaluation stack asks:

- does policy preserve the right semantic properties
- at what pressure does preservation fail
- are those failures stable
- do those failures drift
- which mechanism causes which failure mode

This is why policy design sits between runtime representation and the evaluation objective matrix.

Without policy mechanism design, representation and evaluation are disconnected.

---

## 7. Scope

This document defines policy as a preservation mechanism, not as a final implementation.

It does not define:

- the full policy code path
- the exact benchmark suite
- the final Graph implementation
- the full external baseline matrix

Those belong to later implementation and evaluation documents.
