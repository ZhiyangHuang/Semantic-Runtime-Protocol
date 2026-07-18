# SRP Core Assumptions

This document records the core assumptions that ground SRP's theory.
It is not an implementation spec.

These assumptions are intentionally small in number.
They are the minimum premises needed for the rest of the framework.

---

## 1. Runtime Resources Are Limited

Long-running semantic systems cannot preserve every semantic unit indefinitely.

Therefore, runtime systems must choose what to retain, compress, archive, or discard.

This assumption motivates policy and preservation objectives.

---

## 2. Semantic Loss Is Non-Uniform

Different kinds of semantic loss have different consequences.

Losing identity is not the same as losing a low-value detail.
Losing a dependency chain is not the same as losing a surface description.

Therefore, runtime degradation must be analyzed by failure mode rather than by aggregate size alone.

---

## 3. Preservation Is Multi-Objective

No single policy score captures all preservation goals.

SRP must preserve:

- identity continuity
- structural coherence
- semantic value-aware allocation
- runtime stability

These objectives can trade off against each other.

Therefore, the policy space should be treated as Pareto-like rather than single-objective.

---

## 4. Runtime Decisions Must Be Attributable

If a semantic property changes, the system must be able to explain why.

That means preservation behavior should be attributable to specific mechanisms such as:

- importance weighting
- dependency retention
- archive policy
- lifecycle tracking
- budget allocation

Without attribution, the framework can observe degradation but cannot explain or improve it.

---

## 5. Semantic State Must Be Explicit

The runtime state cannot remain implicit in raw text or hidden model activations.

SRP requires an explicit semantic state with:

- entities
- relations
- importance
- lifecycle
- provenance
- confidence
- history

Without an explicit state, representation and policy cannot be reasoned about consistently.

---

## 6. Preservation Must Be Measurable

Design objectives are not useful unless they can be evaluated.

The framework therefore assumes that preservation can be measured through:

- identity metrics
- structural metrics
- value-aware allocation metrics
- stability metrics
- boundary, drift, robustness, attribution, and ablation analyses

This assumption makes the rest of the SRP theory empirically testable.

---

## 7. Scope

These assumptions are the current theoretical basis for SRP.

They are not universal claims about all memory systems.

They define the design space in which SRP is intended to operate.

