# Semantic Transition Failure Benchmark v0.1

Version:

```text
STFB v0.1
```

Status:

- Frozen specification

Scope:

- Defines the v0.1 benchmark boundary
- Implementation is deferred

STFB is an independent benchmark specification for semantic runtime systems.
It defines semantic transition failure as a distinct evaluation problem and keeps that problem separate from any single solution such as SRP.

## 1. Objective

### 1.1 Motivation

Semantic systems increasingly maintain mutable runtime state:

- agent memory
- user preference state
- knowledge stores
- planning context
- tool execution state

Existing evaluations typically measure retrieval quality, generation quality, or task completion.
They do not directly measure whether a proposed semantic change should become runtime state.

STFB addresses that missing boundary.

### 1.2 Research Question

STFB evaluates:

> How do semantic runtime systems fail when semantic state mutation lacks an explicit admission boundary?

The benchmark does not measure proposal quality.
It measures transition safety.

### 1.3 Scope

STFB evaluates the pipeline:

```text
proposal
    |
    v
admission decision
    |
    v
state transition
```

The benchmark assumes proposals may be correct, incorrect, incomplete, conflicting, or unsupported.
The evaluation target is the admission mechanism.

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

## 3. Task Taxonomy

STFB organizes failures by transition mechanism, not by application domain.

### 3.1 Unsupported Mutation

Question:

> Can a system reject changes without sufficient authority?

Example:

```text
Current:
refund_limit = $100

Proposal:
refund_limit = unlimited
```

Failure:

```text
unsupported semantic mutation accepted
```

### 3.2 Evidence-Authority Confusion

Question:

> Does evidence availability incorrectly become mutation authority?

Example:

```text
Evidence:
manager statement

Authority:
customer message
```

Failure:

```text
evidence != authority violation
```

This is the core failure class that STFB is designed to surface.

### 3.3 Conflicting Evidence

Question:

> Can systems resolve competing semantic sources?

Example:

```text
Source A:
policy v2

Source B:
conversation memory
```

Evaluation dimensions:

- source priority
- provenance
- authority resolution

### 3.4 Temporal Regression

Question:

> Can systems prevent old semantic states from overwriting newer states?

Example:

```text
v1:
discount = 10%

v2:
discount = 5%
```

Failure:

```text
old state resurrection
```

### 3.5 Provenance Loss

Question:

> Can semantic content survive without losing traceability?

Evaluation dimensions:

- source retention
- timestamp
- ownership
- evidence chain

### 3.6 Rollback Failure

Question:

> Can systems preserve state integrity after failed transitions?

Evaluation:

```text
commit failure
      |
      v
restore S_t
```

## 4. Baseline Matrix

STFB requires baseline diversity.

### 4.1 Direct Mutation

Represents:

```text
proposal -> commit
```

Purpose:

- measure uncontrolled mutation

### 4.2 Confidence Threshold

Represents:

```text
proposal
 |
confidence
 |
commit
```

Purpose:

- test whether confidence approximates authority

### 4.3 Retrieval Verification

Represents:

```text
proposal
 |
retrieve evidence
 |
similarity check
 |
commit
```

Purpose:

- test evidence-only governance

### 4.4 Human Approval

Represents:

```text
proposal
 |
human decision
 |
commit
```

Purpose:

- high-authority reference baseline

### 4.5 Governance Frameworks

Examples:

- SRP
- future admission-control systems

## 5. Metrics

STFB avoids using answer accuracy as the main metric.

### 5.1 Invalid Acceptance Rate

Primary safety metric.

```text
IAR = invalid accepted / invalid transitions
```

### 5.2 Authority Violation Rate

Measures unauthorized state changes.

```text
AVR = unauthorized transitions / accepted transitions
```

### 5.3 Authorized Retention Rate

Prevents over-rejection.

```text
ARR = valid accepted / valid transitions
```

### 5.4 Semantic Drift

For sequential evaluation:

```text
D_T = sum_t d(S_t, S_t^*)
```

### 5.5 Audit Completeness

Measures:

- provenance retention
- decision trace
- evidence record

### 5.6 Cost

Secondary metrics:

- latency
- compute
- evidence retrieval cost
- human intervention

## 6. Long-Horizon Protocol

### 6.1 Motivation

Semantic failures accumulate.
Single-step evaluation cannot capture runtime degradation.

### 6.2 Episode Structure

```text
initial state

for t = 1 ... T:

    observation

    proposal

    admission

    transition

    evaluation
```

Recommended lengths:

```text
T = 100
T = 500
T = 1000
```

### 6.3 Main Evaluation Targets

- cumulative drift
- invalid transition accumulation
- provenance degradation
- rollback stability

## 7. Artifact Layout

Recommended repository structure:

```text
STFB/
|
├── datasets/
|   ├── unsupported_mutation/
|   ├── authority_conflict/
|   ├── temporal_regression/
|   ├── provenance_loss/
|   └── rollback_failure/
|
├── baselines/
|   ├── direct_mutation/
|   ├── confidence_threshold/
|   ├── retrieval_verify/
|   ├── human_approval/
|   └── srp/
|
├── runner/
|   ├── transition_runner.py
|   ├── evaluator.py
|   └── audit_logger.py
|
├── reports/
|   ├── results.json
|   └── leaderboard.json
|
└── docs/
    └── specification.md
```

## 8. Relationship with SRP

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
SRP        Alternative Approaches
```

## 9. Paper Positioning

### 9.1 STFB Contribution

1. Defines semantic transition failure as a benchmark problem.
2. Introduces a failure taxonomy.
3. Provides governance-oriented metrics.
4. Enables comparison of semantic admission strategies.

### 9.2 SRP Contribution

1. Defines semantic runtime governance.
2. Separates evidence and authority.
3. Provides a controlled transition mechanism.
4. Demonstrates governance properties.

## 10. Research Roadmap

### Phase 1

SRP v1:

```text
Define governance
Validate mechanism
```

### Phase 2

STFB:

```text
Define failure
Benchmark systems
```

### Phase 3

SRP evaluation on STFB:

```text
Does SRP outperform existing admission strategies?
```

## 11. Summary

The intended research chain is:

```text
Semantic systems can mutate state
        |
        v
Mutation creates governance failures
        |
        v
STFB measures those failures
        |
        v
SRP provides a governance solution
```

STFB is therefore a benchmark artifact in its own right, not a subordinate test set for SRP.
