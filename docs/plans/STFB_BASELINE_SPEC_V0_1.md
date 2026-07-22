# STFB Baseline Specification v0.1

Version:

```text
STFB v0.1
```

Status:

- Frozen specification

Scope:

- Defines the v0.1 baseline comparison boundary
- Implementation is deferred

This document freezes the baseline evaluation model for Semantic Transition Failure Benchmark (STFB).
It defines what strategies are compared, how they are invoked, and what fairness constraints apply.

STFB evaluates admission strategies for semantic transition safety.
This spec does not define a single solution method.
It defines the comparison surface for methods that decide whether a proposed semantic transition should be admitted.

## 1. Baseline Objective

Given the same semantic transition instance, how do different admission strategies handle unsafe semantic state changes?

The benchmark compares failure containment capability, not proposal quality or retrieval quality.

The key question is:

> Can the method distinguish a plausible semantic proposal from an admissible semantic transition?

## 2. Baseline Matrix

The v0.1 comparison set is frozen as follows:

| Baseline | Admission mechanism | Expected weakness |
| --- | --- | --- |
| Direct Mutation | always commit proposal | no governance boundary |
| Confidence Threshold | accept if confidence exceeds `tau` | confidence is not authority |
| Retrieval Verification | retrieve evidence before commit | evidence is not permission |
| Human Approval | external approval gate | high cost, limited scalability |
| SRP | validation plus governance boundary | proposed solution under test |

These are not treated as "weak methods vs SRP".
They are different admission boundary designs.

## 3. Baseline Interface

All baselines MUST accept the same transition instance shape.

### 3.1 Input Contract

```python
TransitionInstance(
    S_t,
    O_t,
    Delta_t,
    E_t,
    Gamma_t
)
```

Where:

- `S_t` is the current semantic runtime state
- `O_t` is the incoming observation
- `Delta_t` is the proposed transition
- `E_t` is the evidence package
- `Gamma_t` is the authority contract

### 3.2 Output Contract

Each baseline MUST return a decision object with at least the following fields:

```yaml
decision: accept | reject
reason: optional string
audit:
  evidence_used: optional
  authority_checked: optional
  provenance_recorded: optional
state_result:
  unchanged: S_t | null
  updated: S_(t+1) | null
```

The exact internal representation MAY vary, but the semantic fields above MUST be recoverable for evaluation and audit.

## 4. Expected Evaluation Table

The report format is frozen as a method comparison table with the following columns:

| Method | IAR | AVR | ARR | Drift | Audit |
| --- | --- | --- | --- | --- | --- |
| Direct Mutation |  |  |  |  |  |
| Confidence Threshold |  |  |  |  |  |
| Retrieval Verification |  |  |  |  |  |
| Human Approval |  |  |  |  |  |
| SRP |  |  |  |  |  |

The benchmark MAY include additional summary rows, but the above rows are the frozen v0.1 core set.

## 5. Cost Dimension

Admission cost is a first-class comparison dimension.

The benchmark SHOULD report at least one cost signal for each method:

- latency
- external interaction cost
- computation cost
- evidence requirement cost

This matters because a high-safety baseline may be unusable if its admission cost is too high.

Human approval is included specifically so the benchmark can compare automated governance against a strong but expensive reference gate.

## 6. Fairness Rules

All baselines MUST be evaluated under the same comparison conditions.

### 6.1 Shared Instance Set

Every method MUST receive the same benchmark instances.

### 6.2 Shared Proposal Surface

The benchmark MUST NOT change the proposal generator per baseline.

### 6.3 Shared Evidence Budget

If evidence is budgeted, the budget MUST be identical across methods unless the experiment explicitly studies evidence cost as the independent variable.

### 6.4 No Hidden Labels

Baselines MUST NOT access hidden gold labels, oracle state, or test-only annotations.

### 6.5 No Ground Truth Mutation

Baselines MUST NOT modify the gold answer, the contract definition, or the failure taxonomy.

### 6.6 Comparable Audit Surface

Each method SHOULD expose a comparable audit trace so the benchmark can measure provenance, authority checks, and decision rationale.

## 7. Baseline Semantics

### 7.1 Direct Mutation

Direct Mutation represents the absence of an admission boundary.
It commits the proposal by default.

### 7.2 Confidence Threshold

Confidence Threshold admits a transition when a scalar confidence score exceeds a threshold.
This baseline tests the claim that confidence is not the same as authority.

### 7.3 Retrieval Verification

Retrieval Verification performs evidence retrieval and similarity checks before commit.
This baseline tests the claim that evidence presence is not the same as permission to mutate state.

### 7.4 Human Approval

Human Approval routes the decision through an external reviewer or oracle.
This baseline provides a strong but costly reference gate.

### 7.5 SRP

SRP applies explicit validation plus a governance boundary.
It is evaluated as one admission strategy among others, not as the benchmark definition.

## 8. Reporting Expectations

The benchmark report SHOULD summarize:

- invalid acceptance rate
- authority violation rate
- authorized retention rate
- semantic drift
- audit completeness
- admission cost

The benchmark report MAY include additional breakdowns, but these metrics are the frozen v0.1 comparison core.

## 9. Relationship with STFB

STFB evaluates admission strategies.

SRP is one evaluated governance mechanism, not the definition of the benchmark.

The benchmark is intentionally neutral over solution families.
It should be possible to add new admission mechanisms later without changing the benchmark identity.

## 10. Freeze Statement

The v0.1 baseline freeze boundary is:

- baseline matrix frozen
- input contract frozen
- output contract frozen
- fairness rules frozen
- comparison metrics frozen
- admission cost dimension frozen

Future versions MAY add:

- additional governance baselines
- multi-agent admission strategies
- hierarchical or multi-stage review policies
- adaptive evidence budgets

Those additions belong to later benchmark versions, not to v0.1.
