# SRP Semantic Backend Comparison Protocol

This document freezes the protocol for semantic backend comparison in SRP.
It defines how SRP may compare evidence sources without transferring runtime authority.
It does not define optimization, calibration, or adaptive policy learning.

---

## 1. Position

The semantic backend comparison study runs alongside Phase III-A, but it does not replace parameter optimization.
It evaluates whether a local semantic evidence backend improves verification quality relative to a vector-only baseline.

```text
Phase II
  Validated Feasible Region
  Boundary Stability
        ->
Phase III-A
  Constrained Parameter Optimization
        ->
Semantic Backend Comparison
  Evidence Source Augmentation
        ->
Phase III-B
  Adaptive Semantic Evolution
```

---

## 2. Purpose

The purpose of this study is to determine when SRP should escalate from vector evidence to local-model evidence during verification.

It answers:

> When is vector evidence sufficient, and when does local semantic evidence improve boundary verification?

It does not answer:

> How should the runtime mutate parameters online?

---

## 3. Experimental Boundary

Allowed:

- compare vector-only evidence against vector-plus-local-model evidence
- measure boundary agreement and disagreement
- measure verification quality
- measure cost tradeoffs
- preserve runtime authority separation

Disallowed:

- runtime self-modification
- autonomous deployment
- parameter optimization
- policy learning
- evidence-backed mutation authority

---

## 4. Compared Backends

Baseline:

- vector-only similarity and boundary check

Variant:

- vector evidence plus local semantic evidence
- the local model may provide evidence or fallback to a deterministic heuristic if the model endpoint is unavailable

The local model is an evidence provider, not a controller.

---

## 5. Candidate Set

The comparison uses a fixed semantic case set containing:

- paraphrase cases
- contradiction cases
- authority-violation cases
- boundary cases

The case set is fixed so the backend comparison can isolate evidence-source effects.

---

## 6. Metrics

The first comparison report uses four metric groups:

- boundary agreement
- boundary detection quality
- cost tradeoff
- stability

Boundary agreement compares baseline and variant decisions on the same cases.
Boundary detection quality compares decisions against fixed expected verdicts.
Cost tradeoff compares latency and evidence overhead.
Stability checks whether repeated runs preserve decisions.

---

## 7. Authority Constraints

The comparison layer respects the SRP authority split:

- `Runtime` executes
- `Evidence` informs verification
- `Governance` decides

The local model does not:

- mutate runtime state
- approve deployment
- rewrite history
- override governance

---

## 8. Output Contract

The study may produce:

- `boundary_agreement_report`
- `verification_quality_summary`
- `cost_tradeoff_analysis`
- `authority_preservation_summary`

The study does not produce autonomous runtime updates.

---

## 9. Non-goals

This protocol does not include:

- reinforcement learning
- online adaptation
- policy learning
- runtime self-modification
- parameter optimization

Those concerns remain separate from semantic backend comparison.

---

## 10. Relation to Experiment Infrastructure

This protocol is implemented in the `experiments/evaluation/semantic_backend_comparison/` stack and reads its configuration from `configs/semantic_backend_comparison.env`.

For the generated evidence report, see [SRP Semantic Backend Comparison Report](SRP_SEMANTIC_BACKEND_COMPARISON_REPORT.md).
