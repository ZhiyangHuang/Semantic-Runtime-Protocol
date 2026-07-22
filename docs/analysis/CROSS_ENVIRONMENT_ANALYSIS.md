# Cross-Environment Analysis Framework

## Objective

This document provides a unified analytical framework for interpreting STFB external validation results across heterogeneous semantic stress environments.

It introduces no new benchmark definition, taxonomy, metrics, or admission policy.

Its purpose is to organize existing evidence so that LongMemEval, ARC, and future external environments can be interpreted through the same admission-semantics lens.

## Cross-Environment Mechanism Matrix

The table below summarizes the current frozen evidence surface.

| Environment | Canonical Case | Semantic Pressure | Direct Mutation | Confidence Threshold | SRP | Expected Admission | Mechanism |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LongMemEval | `lme_001` | Temporal Regression | Commit | Reject | Reject | Reject | Temporal integrity |
| LongMemEval | `lme_002` | Evidence-Authority Confusion | Commit | Commit | Reject | Reject | Authority validation |
| ARC | `arc_001` | Unsupported Inference | Commit | Commit | Reject | Reject | Unsupported mutation |
| ARC | `arc_002` | Valid Reasoning | Commit | Commit | Commit | Commit | Legitimate transition |

Interpretation:

- The same admission policy is being evaluated under different semantic stress environments.
- The table is not a performance leaderboard.
- The key question is whether admission semantics remain consistent across environments.

## Divergence Analysis

The following divergence types are used to interpret representative cases.

| Divergence Type | Meaning |
| --- | --- |
| Baseline Accept -> SRP Reject | Unauthorized transition blocked |
| Threshold Sensitive | Confidence alone is insufficient |
| All Accept | Legitimate transition preserved |

### Representative Cases

| Case | Divergence Type | Interpretation |
| --- | --- | --- |
| `lme_001` | Baseline Accept -> SRP Reject | Unauthorized temporal update prevented |
| `lme_002` | Threshold Sensitive | Confidence does not substitute for authority |
| `arc_001` | Baseline Accept -> SRP Reject | Unsupported reasoning transition blocked |
| `arc_002` | All Accept | Legitimate transition preserved |

Interpretation:

- Divergence is driven by admission policy, not wrapper identity.
- The cases show both rejection of unsupported transitions and preservation of valid transitions.
- SRP is therefore acting as a governance boundary rather than as a blanket refusal mechanism.

## Failure Mapping

The matrix below maps observed failure mechanisms across environments.

| Failure Mechanism | LongMemEval | ARC |
| --- | --- | --- |
| Temporal regression | ✓ | — |
| Evidence-authority confusion | ✓ | — |
| Unsupported inference | — | ✓ |
| Valid transition preservation | ✓ | ✓ |

Interpretation:

- Different benchmark environments expose different semantic pressures.
- Those pressures still map onto the same STFB admission semantics.
- The environments are therefore not being compared as tasks; they are being used as stress environments for the same governance abstraction.

## Discussion

### Mechanisms that appear consistent across environments

- Unsupported transitions are blocked when authority is not satisfied.
- Valid transitions are preserved when authority is satisfied.
- Confidence alone does not establish mutation permission.

### Divergence that is expected

- Confidence-threshold admission can behave differently depending on the confidence surface of the environment.
- Direct mutation can preserve valid transitions while also admitting unsupported ones.
- SRP can reject unsupported transitions without blocking supported ones.

### Mechanisms not yet covered

- Multi-source authority hierarchy.
- Contradictory evidence reconciliation.
- Knowledge revision conflict beyond the current ARC and LongMemEval slices.

## Out of Scope

This framework does not:

- define new benchmark tasks;
- introduce new admission metrics;
- compare benchmark difficulty;
- establish statistical claims across environments.

It is an analysis layer for organizing existing evidence, not a new specification.

