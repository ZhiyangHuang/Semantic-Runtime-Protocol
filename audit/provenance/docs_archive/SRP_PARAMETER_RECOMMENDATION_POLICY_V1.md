# SRP Parameter Recommendation Policy V1

This document freezes the interpretation rules for SRP parameter recommendations.
It is an evaluation-policy artifact, not a new experiment, not a mechanism design, and not a runtime update rule.

## 1. Purpose

SRP does not output a runtime default update.
It outputs a governed recommendation derived from the validated feasible region, a declared objective, and available evidence.

The core distinctions are:

```text
Recommendation != Default Configuration
Recommendation != Autonomous Update
Recommendation != Global Optimum
```

This policy exists so that Phase III-A results are interpreted as governed recommendations rather than as automatic parameter replacement.

## 2. Recommendation Source

A recommendation must come from:

```text
Validated Feasible Region
    +
Declared Objective
    +
Available Evidence
```

Formally:

```text
theta* = argmax_{theta in F} U(theta)
```

where:

- `F` is the Phase II validated feasible region
- `U(theta)` is the declared objective function
- `theta*` is a recommendation, not a runtime mutation

The objective may change the recommended configuration, but it does not change the feasible region.

## 3. Recommendation Lifecycle

The only approved lifecycle is:

```text
Observation
    |
    v
Boundary Validation
    |
    v
Constrained Optimization
    |
    v
Recommendation
    |
    v
Governance Decision
    |
    v
(Optional) Runtime Update
```

The lifecycle is not:

```text
Optimization
    |
    v
Automatic Update
```

Governance remains the only approval boundary for applying a recommendation.

## 4. Parameter Status Classification

The paper should treat parameter states as one of the following:

| Status | Meaning |
| --- | --- |
| Frozen Baseline | The current default configuration used for evaluation |
| Recommended Configuration | A candidate configuration preferred under a declared objective |
| Future Adaptive Configuration | A configuration that would require additional governance for automatic adoption |

For the current SRP baseline:

- Frozen Baseline: the current fixed runtime profile
- Recommended Configuration: objective-dependent candidate selected inside the validated feasible region
- Future Adaptive Configuration: not enabled in the current baseline

## 5. Evaluation Rule

All experiments should obey the following interpretation rules:

- baseline configurations do not change automatically after optimization
- objective sensitivity changes ranking, not feasibility
- evidence improvement changes verification quality, not authority
- recommendations do not directly execute

These rules protect the separation between:

- evaluation
- recommendation
- governance
- runtime execution

## 6. Relation to the Paper

This policy supports the paper's core claims:

- Phase II defines where optimization is allowed to operate
- Phase III-A determines which candidate is preferred inside that region
- governance decides whether a recommendation becomes a runtime update

The policy therefore keeps Phase III-A evidence readable as governed recommendation, not as a new default configuration.

