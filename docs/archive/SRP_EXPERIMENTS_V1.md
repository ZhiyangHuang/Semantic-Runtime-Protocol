# SRP Experiments V1

This document defines the experiments section structure for the SRP paper.
It is a paper artifact, not a new experiment, not a policy document, and not an optimization result.

## 1. Experimental Setup

The experiments validate the paper's claims under a fixed runtime baseline.

### 1.1 Research Questions

| RQ | Question | Evidence |
| --- | --- | --- |
| RQ1 | Can SRP observe semantic evolution variables? | Phase I |
| RQ2 | Can SRP identify and validate safe evolution regions? | Phase II |
| RQ3 | Can SRP select preferred configurations inside validated regions? | Phase III-A |
| RQ4 | Can stronger evidence improve verification without authority transfer? | Evidence Escalation |

### 1.2 Experimental Boundary

- runtime implementation remains fixed
- no online learning
- no autonomous mutation
- optimization outputs are advisory
- evidence backends do not control execution

## 2. Experiment 1: Parameter Observability

### Goal

Can semantic evolution variables be measured before optimization or adaptation?

### Setup

- monitored parameters
- transition events
- collected metrics
- state tracking

```text
Semantic Transition
    |
    v
Parameter Observation
    |
    v
Metric Collection
```

### Evaluation

- transition stability
- parameter drift
- state consistency
- replay consistency

### Result Interpretation

SRP establishes an observable parameter space that enables later validation and constrained optimization.

## 3. Experiment 2: Boundary Validation

### Goal

Can SRP identify feasible semantic evolution regions before allowing optimization?

### Setup

Let `theta` denote a parameter configuration and `F` denote the validated feasible region.

```text
F = { theta | invariant(theta) = true }
```

```text
Candidate Region
    |
    v
Invariant Checking
    |
    v
Closure Validation
    |
    v
Frozen Feasible Region
```

### Evaluation

- invariant preservation
- replay equivalence
- transition equivalence
- closure stability

### Result Interpretation

SRP determines where optimization is allowed to operate.

## 4. Experiment 3: Phase III-A Constrained Optimization

### Goal

Given a validated region, can SRP rank preferred configurations without controlling runtime?

### Setup

Candidate space:

- `activation_threshold`: `0.3` to `0.8`
- `recovery_min_evidence`: `1` to `3`

Total candidates:

- `18`

Objective:

```text
U(theta) = 0.4Q + 0.3R - 0.2C - 0.1I
```

Where:

- `Q`: semantic quality
- `R`: recovery success
- `C`: resource cost
- `I`: instability

### Results

| Rank | threshold | evidence | objective |
| --- | --- | --- | --- |
| 1 | `0.8` | `1` | `0.52` |
| 2 | `0.7` | `1` | `0.50` |
| 3 | `0.6` | `1` | `0.48` |

### Result Interpretation

Optimization selects.
Optimization does not mutate.

The result represents a preferred configuration under objective O1, not a globally optimal SRP configuration.

## 5. Experiment 4: Semantic Evidence Escalation

### Goal

Can SRP improve verification by adding evidence without increasing authority?

### Compared Systems

- Baseline: vector evidence only
- Variant: vector evidence plus semantic evidence

### Setup

Cases:

- paraphrase
- contradiction
- authority violation
- boundary cases

### Results

| Metric | Vector | Variant |
| --- | --- | --- |
| Accuracy | `0.5` | `0.6667` |
| Repeat stability | `1.0` | `1.0` |

Agreement:

- `0.8333`

### Escalation Example

```text
Vector Accept
    |
    v
Confidence Conflict
    |
    v
Semantic Evidence
    |
    v
Governance Review
```

The local model provides additional evidence; it does not decide.

## 6. Additional Analysis

### 6.1 Objective Sensitivity

Different objective weights can change the ranking.
That is expected and should be interpreted as objective dependence, not instability of the method.

### 6.2 Backend Cost

The current backend comparison validates the offline heuristic fallback package.
Live local-model cost measurement remains future work.

### 6.3 Robustness

Future work may evaluate:

- workload variation
- conflict density
- evidence volume

## 7. Experiment Summary

The experiments support the paper's core claims:

- validated boundaries
- governed optimization
- evidence-controlled verification

The experiments do not open Phase III-B.
They keep adaptation as future work.

