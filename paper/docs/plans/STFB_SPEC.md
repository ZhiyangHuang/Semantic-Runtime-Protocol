# Semantic Transition Failure Benchmark v0.1

## Purpose

This document defines the frozen STFB v0.1 benchmark boundary.

STFB is an independent benchmark specification for semantic runtime systems.
It defines semantic transition failure as a distinct evaluation problem and keeps that problem separate from any single solution such as SRP.

## 1. Objective

STFB asks a single question:

> How do semantic runtime systems fail when semantic state mutation lacks an explicit admission boundary?

The benchmark does not measure proposal quality.
It measures transition safety.

## 2. Formal Task Definition

A benchmark instance is:

```text
I = (S_t, O_t, Delta_t, E_t, Gamma_t)
```

where:

| Variable | Description |
| --- | --- |
| `S_t` | current semantic runtime state |
| `O_t` | incoming observation |
| `Delta_t` | proposed transition |
| `E_t` | evidence |
| `Gamma_t` | authority contract |

The system outputs:

```text
a in {accept, reject}
```

If accepted:

```text
S_(t+1) = T(S_t, Delta_t)
```

If rejected:

```text
S_(t+1) = S_t
```

## 3. Dataset Design

STFB organizes failures by transition mechanism, not by application domain.

### 3.1 Frozen Failure Taxonomy

- Unsupported Mutation
- Evidence-Authority Confusion
- Conflicting Evidence
- Temporal Regression
- Provenance Loss
- Rollback Failure

### 3.2 Difficulty Levels

- Atomic transition
- Multi-step drift
- Adversarial transition
- Mixed horizon

### 3.3 Instance Schema

The canonical instance shape is:

```text
I = (S_t, O_t, Delta_t, E_t, Gamma_t)
```

The benchmark is intended to support structured instances with explicit state, observation, proposal, evidence, authority, and expected-transition fields.

## 4. Baseline Comparison

STFB evaluates admission strategies for semantic transition safety.

### 4.1 Frozen Methods

| Baseline | Admission mechanism | Expected weakness |
| --- | --- | --- |
| Direct Mutation | always commit proposal | no governance boundary |
| Confidence Threshold | accept if confidence exceeds `tau` | confidence is not authority |
| Retrieval Verification | retrieve evidence before commit | evidence is not permission |
| Human Approval | external approval gate | high cost, limited scalability |
| SRP | validation plus governance boundary | proposed solution under test |

### 4.2 Baseline Interface

All baselines MUST accept the same transition instance shape and return an auditable decision with accept/reject, reason, audit, and state result fields.

### 4.3 Comparison Metrics

- Invalid Acceptance Rate
- Authority Violation Rate
- Authorized Retention Rate
- Semantic Drift
- Audit Completeness
- Admission Cost

### 4.4 Fairness Rules

- shared instance set
- shared proposal surface
- shared evidence budget
- no hidden labels
- no ground-truth mutation
- comparable audit surface

## 5. External Validation Track

The external validation track is adapter-first and freezes how existing benchmark environments are mapped into STFB-compatible semantic transition instances.

### 5.1 Included Environments

- LongMemEval
- ARC

### 5.2 Canonical External Cases

- LongMemEval temporal regression
- LongMemEval provenance loss
- LongMemEval evidence-authority confusion
- ARC unsupported inference
- ARC valid reasoning

### 5.3 Mapping Rules

External cases MUST be wrapped into the STFB transition schema.
The wrapper MAY add metadata, but MUST not modify core STFB semantics, runner contracts, or metrics.

### 5.4 Track Outputs

The external validation track SHOULD produce:

- a machine-readable report
- a compact summary
- a preserved evidence package

### 5.5 Success Criteria

- external cases map cleanly into STFB instances
- the frozen runner evaluates them without changing the core contract
- the frozen failure taxonomy covers the mapped cases
- baseline divergence is observable in the resulting reports

## 6. Relationship with SRP

STFB and SRP are intentionally separated.

### STFB

Defines:

```text
what failure means
```

### SRP

Defines:

```text
one approach to prevent failure
```

Therefore:

```text
STFB != SRP benchmark
```

Correct relationship:

```text
STFB
 |
 v
Semantic Transition Governance Problem
 |
+----------------+
|                |
SRP      Alternative Approaches
```

## 7. Freeze Statement

The v0.1 freeze boundary is:

- benchmark definition frozen
- dataset semantics frozen
- baseline semantics frozen
- external validation boundary frozen
- SRP claims unchanged

Future versions MAY extend implementation scope, but they should not redefine the STFB boundary retroactively.
