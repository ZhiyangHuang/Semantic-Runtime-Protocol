# SRP Limitations V1

This document freezes the limitation boundary for the current SRP paper baseline.
It is a paper-facing interpretation artifact, not a new experiment, not a mechanism design, and not a policy document.

## 1. No Autonomous Semantic Adaptation

The current SRP baseline does not implement:

- online learning
- policy evolution
- self-modifying runtime
- autonomous semantic mutation

Phase III-A produces a:

```text
recommended configuration
```

It does not produce a:

```text
learned policy
```

Adaptive semantic evolution remains future work and requires additional governance boundaries.

## 2. Workload Dependence

The validated feasible region and objective ranking depend on:

- the evaluated transition space
- the selected invariants
- the workload distribution
- the declared objective

Therefore:

```text
F_current != F_universal
```

SRP validates:

> a governed feasible region under a fixed experimental boundary

It does not claim:

> a universal boundary for all semantic workloads

## 3. Objective Dependence

Phase III-A objective sensitivity shows that ranking changes when the objective changes.

Therefore:

```text
best configuration
```

should be interpreted as:

```text
best configuration under objective U
```

This is consistent with the paper's recommendation policy:

- the objective changes ranking
- the objective does not change feasibility
- the objective does not update runtime defaults

## 4. Evidence Backend Cost

The evidence escalation study shows that additional semantic evidence can improve verification.
However, the current paper baseline does not fully measure:

- local model latency
- inference cost
- energy cost
- deployment overhead

The future tradeoff remains:

```text
verification gain vs evidence cost
```

## 5. Boundary Discovery Scalability

Phase II boundary discovery currently uses:

- parameter sampling
- invariant checking
- closure validation

This is sufficient for the current frozen parameter space, but larger or higher-dimensional spaces may require:

- adaptive sampling
- surrogate modeling
- formal verification support

The current paper therefore claims stable boundaries for the evaluated space, not a fully general boundary discovery algorithm.

## 6. Governance Authority Assumption

The current SRP baseline assumes that governance authority exists outside the runtime.

SRP does not resolve:

- who defines governance
- how governance policies are created
- conflicts between governance authorities

It only answers:

> given governance authority, how can semantic evolution remain controlled?

## 7. Summary

SRP should be interpreted as a governed semantic evolution framework that establishes controlled transition boundaries and evidence-aware recommendations.
It does not claim autonomous semantic adaptation or universal optimality.
