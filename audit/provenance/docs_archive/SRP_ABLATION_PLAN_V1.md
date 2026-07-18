# SRP Ablation Plan V1

This document defines the paper-facing ablation plan for SRP.
It is a planning artifact, not a new experiment, not a mechanism design, and not a policy document.

## 1. Why Ablation

The SRP evidence chain already supports the main claims:

- semantic observability
- validated feasible regions
- governed optimization inside validated regions
- evidence-controlled verification

The remaining question is not whether the framework works.
It is why each separation is necessary.

This ablation plan is designed to test the necessity of:

- boundary validation before optimization
- evidence escalation without authority transfer
- governance separation between recommendation and execution

## 2. Ablation Principle

The ablation experiments should not collapse SRP into a single score.
They should test which separation breaks when one layer is removed.

The central hypothesis is:

```text
Observation
    ->
Validation
    ->
Optimization
    ->
Governance
    ->
Execution
```

is more stable and safer than:

```text
Observation
    ->
Optimization
    ->
Execution
```

## 3. Planned Ablation Axes

### 3.1 No Boundary Validation

Remove the Phase II boundary filter and allow optimization to evaluate the full candidate set.

Expected effect:

- candidate space expands
- invalid candidate ratio increases
- search reduction disappears
- objective ranking may still exist, but it is no longer constrained by a frozen feasible region

What it tests:

> Whether Phase III-A still has the governed-optimization property without Phase II.

### 3.2 No Evidence Escalation

Remove the semantic evidence escalation layer and rely on vector evidence only.

Expected effect:

- verification accuracy drops in boundary-sensitive cases
- disagreement resolution becomes weaker
- false acceptance may increase

What it tests:

> Whether stronger evidence improves verification without changing authority.

### 3.3 No Governance Separation

Route optimization output directly into runtime execution without a governance approval step.

Expected effect:

- recommendation and execution collapse into one step
- decision trace loses review boundary
- boundary violations become harder to prevent

What it tests:

> Whether recommendation must remain distinct from execution.

### 3.4 No Objective-Feasibility Decoupling

Treat objective weights as if they redefine feasibility instead of ranking.

Expected effect:

- feasible region becomes unstable under objective changes
- ranking and boundary become entangled
- interpretation of optimization becomes ambiguous

What it tests:

> Whether Phase II and Phase III-A remain separable as boundary and ranking layers.

## 4. Metrics

The ablation report should reuse the frozen metrics from the main evidence chain.

Primary metrics:

- feasible candidate count
- invalid candidate ratio
- search reduction
- top-candidate preservation
- verification accuracy
- disagreement resolution rate
- boundary consistency

Secondary metrics:

- objective rank correlation
- false acceptance
- false rejection
- review count

## 5. Reporting Template

The final ablation report should summarize:

| Variant | Removed Separation | Main Expected Effect | Supports Claim |
| --- | --- | --- | --- |
| SRP-full | None | All separations preserved | Baseline |
| SRP-no-boundary | Phase II filtering | Search expands and invalid candidates reappear | Boundary validation is necessary |
| SRP-no-evidence | Evidence escalation | Verification quality drops | Evidence is useful but not authoritative |
| SRP-no-governance | Approval boundary | Recommendation collapses into execution | Governance separation is necessary |
| SRP-no-decoupling | Objective-feasibility split | Ranking and boundary entangle | Phase II and Phase III-A are distinct layers |

## 6. Evidence Figure

The paper should include a compact evidence-chain figure:

```text
Semantic State
    |
    v
Phase I
Observation
    |
    v
Phase II
Validation
    |
    v
Phase III-A
Optimization
    |
    v
Evidence Escalation
    |
    v
Governance
    |
    v
Execution
```

The figure should annotate:

- Validation fixes feasibility
- Optimization changes preference
- Governance changes authority

## 7. Relation to Existing Protocols

This plan is aligned with:

- [SRP Mechanism Attribution / Ablation Protocol](SRP_MECHANISM_ATTRIBUTION_ABLATION_PROTOCOL.md)
- [SRP Evaluation Objective Matrix](SRP_EVALUATION_OBJECTIVE_MATRIX.md)

Those documents describe the deeper experimental mechanics.
This document freezes the paper-facing ablation story.

## 8. Next Use

This ablation plan is intended to support the paper's discussion and limitations sections after the main results summary.
