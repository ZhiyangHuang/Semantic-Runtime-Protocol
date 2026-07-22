# STFB Implementation Roadmap v0.1

## Purpose

This document defines the implementation order after the STFB v0.1 specification freeze.

It does not modify:

- benchmark definition
- dataset semantics
- baseline semantics
- SRP claims

It only describes implementation milestones.

## Milestone 1 - Instance Generator

Goal:

- Generate reproducible semantic transition failure instances.

Required fields:

```text
I = (S_t, O_t, Delta_t, E_t, Gamma_t)
```

Supported initial failure classes:

- Unsupported Mutation
- Evidence-Authority Confusion
- Conflicting Evidence
- Temporal Regression
- Provenance Loss
- Rollback Failure

Output:

- STFB instance files

## Milestone 2 - Baseline Harness

Implement the frozen comparison interface:

```text
Instance
    |
    v
Admission Method
    |
    v
Decision
    |
    v
Metrics
```

Initial methods:

- Direct Mutation
- Confidence Threshold
- Retrieval Verification
- Human Approval
- SRP Adapter

No method-specific input changes are allowed.

## Milestone 3 - Evaluation Metrics

Implement:

### Primary

- Invalid Acceptance Rate (IAR)
- Authority Violation Rate (AVR)
- Authorized Retention Rate (ARR)

### Secondary

- Semantic Drift
- Audit Completeness
- Admission Cost

## Milestone 4 - Long Horizon Evaluation

Evaluate:

```text
T = 10
T = 50
T = 100
```

Measure:

- cumulative drift
- failure accumulation
- recovery behavior
- provenance degradation

## Milestone 5 - Optional Extensions

Deferred:

- LLM proposal sources
- external datasets
- larger benchmark scale
- adaptive failure generation

## Non-goals

STFB implementation does not:

- redefine SRP
- modify SRP v1.0 claims
- become a benchmark leaderboard initially
- optimize admission methods

## Boundary Statement

STFB v0.1 remains the frozen specification boundary.
This roadmap only records the implementation order for later execution.
