# SRP Evaluation Objective Matrix

This document connects SRP's design objectives to measurable evaluation targets.
It is not an implementation spec.

The central question is:

> How do we measure whether SRP preserves semantic properties under constrained runtime resources?

This matrix is the bridge between design rationale, runtime representation, policy, and empirical evaluation.

---

## 1. Evaluation Philosophy

SRP evaluation should not ask only whether a system performs well.
It should ask which semantic preservation objective the system supports, which one it weakens, and under what pressure that behavior appears.

The main evaluation dimensions are:

- identity preservation
- structural preservation
- semantic value-aware allocation
- runtime stability

These dimensions are measured across policy, boundary, robustness, drift, attribution, and ablation analyses.

---

## 2. Objective-to-Metric Matrix

### 2.1 Identity Continuity

Question:

> Does the system preserve entity identity across compression and recovery?

Representative metrics:

- identity retention rate
- reference continuity
- alias preservation
- recovery accuracy

Representative failure modes:

- entity split
- entity merge
- broken reference chain
- identity drift

Representative benchmark types:

- multi-turn entity tracking
- recovery tasks with repeated entities
- long-horizon continuity tasks

Representative ablations:

- remove archive
- remove identity links
- weaken provenance tracking

---

### 2.2 Structural Coherence

Question:

> Does the system preserve meaningful relations among semantic units?

Representative metrics:

- dependency coverage
- dependency F1
- structural coherence score
- relation preservation rate

Representative failure modes:

- broken dependency chain
- lost constraint
- relation collapse
- relation mismatch after recovery

Representative benchmark types:

- dependency-pressure tasks
- validation-pressure tasks
- relation-heavy structured tasks

Representative ablations:

- remove dependency retention
- remove relation-aware compression
- remove structural archive support

---

### 2.3 Semantic Value-aware Allocation

Question:

> Does the system preserve what matters most under limited budget?

Representative metrics:

- active retention ratio
- weighted retention
- important-item capture rate
- selection overlap
- selection rank shift

Representative failure modes:

- important but low-frequency content dropped first
- high-surface-frequency content retained instead of high-value content
- selection composition drifts without semantic justification

Representative benchmark types:

- memory-saturation tasks
- pressure-sensitive selection tasks
- distractor-heavy selection tasks

Representative ablations:

- remove importance weighting
- flatten selection priority
- uniform retention

---

### 2.4 Runtime Stability

Question:

> Are preservation behaviors stable across seeds, cycles, and runtime evolution?

Representative metrics:

- boundary midpoint variance
- detection rate
- drift magnitude
- robustness across seeds

Representative failure modes:

- unstable thresholds
- cycle-dependent boundary movement
- seed-sensitive preservation collapse
- inconsistent recovery under repeated updates

Representative benchmark types:

- seed robustness runs
- cycle-based drift runs
- repeated pressure sweeps

Representative ablations:

- disable archive
- flatten lifecycle thresholds
- weaken lifecycle history tracking

---

## 3. Evaluation Layers

SRP evaluation is organized as a stack rather than a single score.

### 3.1 Policy Evaluation

Measures how resource allocation affects preservation.

Examples:

- Pareto analysis
- policy intervention
- sensitivity analysis

### 3.2 Boundary Analysis

Measures where preservation begins to degrade under pressure.

Examples:

- allocation boundary
- dependency boundary
- dependency-F1 boundary

### 3.3 Robustness Analysis

Measures whether preservation behavior is stable across perturbations.

Examples:

- seed robustness

### 3.4 Drift Analysis

Measures whether preservation degrades over long-horizon runtime evolution.

Examples:

- cycle-based drift analysis

### 3.5 Mechanism Attribution

Measures which mechanism supports which objective.

Examples:

- importance weighting -> semantic value-aware allocation
- dependency-aware retention -> structural coherence
- archive policy -> runtime stability and recovery continuity

### 3.6 Ablation Analysis

Measures how objective-specific behavior changes when a mechanism is removed.

Examples:

- remove importance weighting
- remove dependency retention
- remove archive policy
- flatten lifecycle policy

---

## 4. Baseline Matrix

SRP should be compared against baselines that test different preservation capabilities.

### 4.1 Retrieval-based Memory

Tests:

- retrieval continuity
- recall under sparse access

### 4.2 Summary-based Memory

Tests:

- compression preservation
- abstraction loss

### 4.3 Vector Memory

Tests:

- semantic selection quality
- similarity-driven retention

### 4.4 Graph-based Memory

Tests:

- structural coherence
- relation preservation

### 4.5 Agent Memory Frameworks

Tests:

- long-horizon runtime stability
- recovery after repeated updates

The baseline matrix should ask which preservation objective each approach is strongest at, not just which one has the highest aggregate score.

---

## 5. Scope and Freeze Rules

This matrix is intended to keep theory, representation, policy, and evaluation aligned.

Freeze rules:

- do not add new objectives without a measurable target
- do not add new benchmarks without a mapping to an objective
- do not add new metrics without a preservation interpretation
- do not add new baselines without a comparison purpose

This keeps the evaluation framework tied to the design rationale rather than drifting into metric accumulation.

