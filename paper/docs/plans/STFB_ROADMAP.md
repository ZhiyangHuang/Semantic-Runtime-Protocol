# STFB Roadmap

This is the single STFB planning entry point for implementation and research expansion.

## Purpose

This roadmap connects the frozen STFB v0.1 specification to the implementation work and the next research expansion.

It does not change:

- the benchmark definition
- the frozen taxonomy
- the baseline contract
- the external validation boundary

## Part I: Implementation Plan

### Milestone 0: Prototype Contract

Before adding new benchmark breadth, freeze the shared contract used by the reference runner and later implementation work.

#### Objective

Define the minimum object model for semantic transition failure evaluation.

#### Scope

- instance generator contract
- baseline runner contract
- auditable decision format
- reproducible artifact layout

#### Core Contract

```python
class TransitionCase:
    state_before
    delta
    evidence
    authority
    expected_decision


class TransitionResult:
    accepted
    reason
    audit
    state_after
```

#### Success Criteria

- all benchmark cases share the same instance shape
- all baselines return comparable accept/reject decisions
- the contract stays aligned with the frozen STFB specification

### Milestone 1: Instance Generator

Goal:

- generate reproducible semantic transition failure instances

### Milestone 2: Baseline Harness

Goal:

- run the frozen baseline set against the shared instance contract

### Milestone 3: Evaluation Metrics

Primary:

- Invalid Acceptance Rate
- Authority Violation Rate
- Authorized Retention Rate

Secondary:

- Semantic Drift
- Audit Completeness
- Admission Cost

### Milestone 4: Long-Horizon Evaluation

Goal:

- evaluate whether the same failure taxonomy remains stable over longer transition chains

### Milestone 5: Optional Extensions

Possible extensions:

- more synthetic instance coverage
- stronger failure coverage within the frozen boundary
- additional external environments when they introduce new semantic pressure

## Part II: v0.2 Research Expansion

STFB v0.2 focuses on research expansion, not redefinition.

### In Scope

- larger synthetic instance coverage
- stronger failure coverage within the frozen STFB taxonomy boundary
- statistical evaluation over more cases
- additional external environments only if they introduce new semantic pressure
- cross-environment consistency analysis

### Out of Scope

- changing the STFB core schema
- changing the frozen STFB taxonomy
- changing the frozen baseline contract
- changing the Milestone 0 prototype contract
- turning external validation into a new benchmark family

### Success Criteria

STFB v0.2 should provide evidence that:

- semantic transition failures are not limited to the current canonical slices
- the admission semantics remain interpretable across environments
- new environments only enter when they add new semantic pressure

### Non-Goals

STFB v0.2 does not:

- replace SRP as the governance framework
- redefine the core benchmark identity
- collapse external validation into benchmark ranking
- claim universal optimality for any admission policy

### Version Boundary

This roadmap is a research planning artifact only.
It does not modify the frozen STFB v0.1 specification, the Milestone 0 checkpoint, or the external validation freeze.
