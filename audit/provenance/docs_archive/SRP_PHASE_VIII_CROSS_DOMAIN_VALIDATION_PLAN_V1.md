# SRP Phase VIII Cross-Domain Validation Plan V1

This document freezes the Phase VIII cross-domain validation boundary for SRP.
It is a planning artifact, not an experiment result, not a runtime policy, and not a new mechanism design.

## 1. Objective

Validate whether SRP's governed semantic evolution principles remain effective across different semantic workloads.

The question is not which domain performs best.
The question is:

> Does SRP preserve semantic fidelity, relation structure, and governance stability across heterogeneous semantic tasks?

## 2. Frozen SRP Core

Keep the SRP governance stack fixed:

```text
observe
validate
optimize
verify
recover
recommend
govern
execute
```

Do not add:

- a new recovery algorithm
- a new optimizer
- a new authority layer
- an RL controller

Phase VIII changes only the semantic workload domain and, separately, the model/parser backend for cross-model validation.

## 3. Validation Tracks

Phase VIII is split into two tracks.

### 3.1 Phase VIII-A: Cross-Domain Validation

Keep the SRP mechanism fixed and vary only the semantic workload domain.

Recommended domains:

1. Code evolution memory
2. Knowledge / entity reasoning
3. Agent planning memory

### 3.2 Phase VIII-B: Cross-Model Validation

Keep the workload fixed and vary the encoder, parser, or backend model.

This track answers whether SRP depends on a specific embedding stack or parser stack.

## 4. Domain Selection

### 4.1 Code evolution memory

Why:

- tests dependency preservation
- tests bug / commit / file relations
- resembles practical agent memory

Semantic units:

- file
- function
- bug
- commit
- dependency
- decision

Primary relations:

- commit -> modifies -> file
- bug -> caused_by -> function
- function -> depends_on -> library

### 4.2 Knowledge / entity reasoning

Why:

- tests facts, sources, and multi-hop entity relations
- exposes provenance and conflicting evidence

Semantic units:

- entity
- fact
- source
- claim
- event

Primary relations:

- entity -> located_in -> place
- event -> caused_by -> event

### 4.3 Agent planning memory

Why:

- tests long dependency chains
- tests changing constraints
- most closely resembles runtime evolution

Semantic units:

- goal
- constraint
- action
- state
- observation

Primary relations:

- action -> requires -> resource
- action -> blocks -> action
- state -> satisfies -> goal

## 5. Evaluation Matrix

Reuse the existing SRP metrics rather than inventing a new evaluation language.

### Fidelity

- `semantic_coverage`
- `semantic_drift`
- `fact_accuracy`
- `relation_accuracy`
- `recovery_accuracy`

### Structure

- `closure_accuracy`
- `path_preservation`
- `neighborhood_completeness`
- `hallucinated_relation_rate`

### Governance

- `recommendation_stability`
- `parameter_sensitivity`
- `evidence_cost`

## 6. Baselines

Use a minimal baseline set.

### Baseline 1: Vector-only recovery

```text
embedding
+ top-k retrieval
```

### Baseline 2: Chunk or summary retrieval

Represents conventional memory compression without relation-aware reconstruction.

### Baseline 3: SRP relation-aware recovery

```text
anchor
+ relation expansion
+ closure validation
```

## 7. Hypothesis

Do not claim that SRP wins every workload.

Claim instead:

> SRP maintains consistent structural fidelity improvements across heterogeneous semantic workloads.

Expected pattern:

- code memory: dependency closure improves
- knowledge reasoning: multi-hop relation fidelity improves
- planning memory: constraint preservation improves

## 8. Relation to Phase VIII-B

Cross-domain and cross-model validation should be separated.

- Phase VIII-A: same SRP, different workloads
- Phase VIII-B: same workload, different models or parsers

This separation prevents domain effects from being conflated with model-backend effects.

## 9. Non-Goals

Do not treat this phase as:

- a runtime default update policy
- an adaptive learning controller
- a replacement for Phase VII-B
- a universal memory benchmark winner claim

## 10. Relation to the Paper

Phase VIII extends the evidence chain beyond parameter behavior:

- Phase I: observability
- Phase II: boundary validation
- Phase III-A: governed optimization
- Evidence Escalation: verification improvement
- Phase V: semantic fidelity measurement
- Phase VI-A: structure-preserving reconstruction
- Phase VII-A: recommendation stability
- Phase VII-B: parameter sensitivity and governance tradeoff analysis
- Phase VIII-A: cross-domain validation
- Phase VIII-B: cross-model validation

