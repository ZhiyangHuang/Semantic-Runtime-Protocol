# SRP v1.1 Evidence Surface

## Purpose

This document consolidates empirical evidence supporting SRP without modifying the frozen STFB benchmark definition.

The evidence surface consists of:

- mechanism validation
- external transition validation
- broad capability stress evaluation

This document does not introduce:

- new benchmarks
- new metrics
- new taxonomy
- new evaluation protocol

It is an evidence aggregation layer for the frozen release boundary.

## 1. Evidence Layers

### Layer 1: Mechanism Evidence

Source:

- STFB v0.1

Purpose:

- validate admission semantics under controlled failure conditions

Evidence:

| Failure Type | Baseline Behavior | SRP Behavior |
| --- | --- | --- |
| temporal regression | commit | reject |
| evidence-authority confusion | commit | reject |
| unsupported inference | commit | reject |
| valid transition | commit | commit |

Interpretation:

SRP changes admission behavior under semantic pressure while preserving valid transitions.

### Layer 2: External Validation Evidence

#### LongMemEval

Role:

- memory/state transition validation

Evidence:

| Metric | Value |
| --- | ---: |
| official score | 0.888021 |
| SRP diagnostic score | 1.0 |
| semantic drift | 0.1 |
| fact accuracy | 1.0 |
| relation accuracy | 1.0 |
| recovery accuracy | 1.0 |
| closure accuracy | 1.0 |

Observed mechanism:

- provenance preservation
- state recovery
- relation integrity

Boundary:

The official LongMemEval scorer remains authoritative.

#### ARC

Role:

- reasoning transition validation

Evidence:

| Variant | Accuracy |
| --- | ---: |
| baseline | 0.904461 |
| SRP | 0.883838 |

Interpretation:

The small reduction indicates stricter admission behavior, not general reasoning failure.

Canonical divergence:

- unsupported inference:
  - baseline: commit
  - SRP: reject

- valid reasoning:
  - baseline: commit
  - SRP: commit

### Layer 3: Capability Stress Evidence

#### MMLU

Role:

- knowledge transition stress

Evidence:

| Variant | Accuracy |
| --- | ---: |
| baseline | 0.653183 |
| SRP | 0.626193 |

Interpretation:

MMLU exposes the cost of semantic admission constraints when evidence authority is ambiguous.

This should be interpreted as:

- controlled rejection
- governance overhead

not accuracy optimization.

#### HumanEval

Role:

- executable transition validation

Evidence:

| Variant | pass@1 |
| --- | ---: |
| baseline | 0.987805 |
| SRP | 1.0 |

Interpretation:

Execution authority provides a stronger validation boundary, allowing SRP to preserve executable artifacts.

## 2. Cross-Environment Summary

| Environment | Transition Type | SRP Role |
| --- | --- | --- |
| STFB | synthetic failure | admission mechanism validation |
| LongMemEval | memory transition | provenance governance |
| ARC | reasoning transition | inference control |
| MMLU | knowledge transition | evidence boundary |
| HumanEval | executable artifact | execution authority |

## 3. Mechanism View

The evidence surface supports a single semantic admission view across environments:

| Environment | Semantic Pressure | Direct Mutation | Confidence Threshold | SRP | Expected Admission |
| --- | --- | --- | --- | --- | --- |
| LongMemEval | temporal regression | commit | reject | reject | reject |
| LongMemEval | evidence-authority confusion | commit | mixed | reject | reject |
| ARC | unsupported inference | commit | commit | reject | reject |
| ARC | valid reasoning | commit | commit | commit | commit |
| MMLU | knowledge revision stress | commit | strict/varies | reject or commit depending on authority | environment-dependent |
| HumanEval | executable transition | commit | commit | commit | commit |

Interpretation:

- The environments are not being compared as tasks.
- They are being used as stress environments for the same governance abstraction.
- The evidence surface is strongest when admission semantics remain interpretable across all rows.

## 4. Discussion

### Mechanisms that appear consistent across environments

- Unsupported transitions are blocked when authority is not satisfied.
- Valid transitions are preserved when authority is satisfied.
- Confidence alone does not establish mutation permission.

### Divergence that is expected

- Confidence-threshold admission can behave differently depending on the confidence surface of the environment.
- Direct mutation can preserve valid transitions while also admitting unsupported ones.
- SRP can reject unsupported transitions without blocking supported ones.

### Mechanisms not yet covered

- Multi-source authority hierarchy
- Contradictory evidence reconciliation
- Knowledge revision conflict beyond the current slices

## 5. Research Boundary

Included:

- evidence consolidation
- mechanism interpretation
- cross-environment analysis

Not included:

- benchmark ranking
- accuracy optimization claim
- STFB modification
- new metrics

This document is a consolidation layer for the frozen release state, not a new specification.

