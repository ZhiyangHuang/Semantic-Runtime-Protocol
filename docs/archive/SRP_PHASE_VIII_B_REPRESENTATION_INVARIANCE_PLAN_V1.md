# SRP Phase VIII-B Representation Invariance Plan V1

This document freezes the Phase VIII-B representation-invariance boundary for SRP.
It is a planning artifact, not an experiment result, not a runtime policy, and not a new mechanism design.

## 1. Objective

Validate whether SRP's governed semantic evolution principles remain effective when the semantic representation pipeline changes.

The key question is not whether SRP can be re-implemented with a different stack.
The key question is:

> Does SRP preserve its governance semantics under representation changes?

In this work, representation invariance does not require identical absolute performance across representations.
Instead, it requires that the governance principles and recovery hierarchy remain stable under representation changes.

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

Do not introduce:

- a new recovery algorithm
- a new optimizer
- a new authority layer
- an RL controller

Phase VIII-B only varies the representation layer.

## 3. Variation Axes

### 3.1 Embedding encoder variation

Test whether SRP is sensitive to the embedding model used for similarity and anchor retrieval.

Suggested variants:

- lightweight sentence encoder
- stronger semantic encoder
- sparse or lexical baseline

### 3.2 Parser variation

Test whether SRP depends on a specific semantic extraction pipeline.

Suggested variants:

- rule-based parser
- LLM-based parser
- hybrid structured extractor

## 4. Experimental Question

Phase VIII-B is a single-question study:

> Does SRP preserve its governance semantics under representation changes?

The experiment does not ask which representation is best.
It asks whether the same SRP hierarchy remains intact when representation changes.

## 5. Experimental Design

Phase VIII-B has three experiments.

### 5.1 Experiment 1: Embedding Invariance

Fix:

- parser
- storage backend
- workload

Vary only:

- `e5-small-v2`
- `bge-small-en-v1.5`
- `bge-base-en-v1.5`
- `all-MiniLM-L6-v2`

### 5.2 Experiment 2: Parser Invariance

Fix:

- embedding
- storage backend
- workload

Vary only:

- rule-based parser
- hybrid parser
- LLM parser

### 5.3 Experiment 3: Combined Representation Invariance

Fix:

- storage backend
- workload

Vary embedding and parser jointly.

## 6. Evaluation Goals

Phase VIII-B should measure whether the following remain stable across representation variants:

- semantic coverage
- semantic drift
- relation accuracy
- closure accuracy
- neighborhood completeness
- hallucinated relation rate
- recommendation stability
- evidence cost

## 6.1 Representation Invariance Criteria

SRP satisfies representation invariance if:

1. Hierarchy stability remains intact:

   - `relation_closure > relation_expansion > vector_only`
   - this ordering holds across representation variants

2. Parameter semantics remain stable:

   - `relation_depth` continues to control structural recovery
   - `archive_relations` continues to control relation retention
   - `activation_threshold` continues to control the governance boundary

3. Governance pipeline remains fixed:

   - `observe -> validate -> optimize -> verify -> recover -> recommend -> govern -> execute`
   - the recovery and governance roles do not change across representations

4. Parameter semantics remain invariant in role:

   - a parameter exhibits semantic invariance if its functional role remains unchanged across representation backends, even when absolute performance varies
   - `relation_depth` continues to control structural recovery
   - `archive_relations` continues to control relation retention
   - `activation_threshold` continues to control the governance boundary
   - `preserve_evidence` continues to control evidence provenance

5. Measured gain remains positive:

   - SRP should preserve a relative advantage over vector-only recovery
   - absolute scores may change, but the recovery ordering should not invert

The main goal is not to maximize one metric.
The main goal is to determine whether SRP preserves its relative recovery advantage and governance behavior across representation choices.

The primary scientific question is hierarchy stability:

```text
vector-only
    <
relation_expansion
    <
relation_closure
```

If this ordering remains stable while the representation changes, then SRP is representation-robust in the sense relevant to the paper.

## 7. Frozen Baselines

Use the same baselines as the rest of the recovery chain:

- vector-only recovery
- relation expansion
- relation closure

The recovery hierarchy should remain unchanged.
Only the representation layer varies in Phase VIII-B.

## 8. Metrics

Phase VIII-B reports the standard recovery metrics first:

- semantic coverage
- semantic drift
- relation accuracy
- closure accuracy
- neighborhood completeness
- hallucinated relation rate
- recommendation stability
- evidence cost

To evaluate representation invariance, we additionally report two SRP-specific analysis metrics:

### 8.1 Hierarchy Consistency Rate

Hierarchy Consistency Rate (HCR) measures how often the recovery ordering remains intact.

```text
HCR = count(relation_closure > relation_expansion > vector_only) / total_runs
```

### 8.2 Governance Consistency Rate

Governance Consistency Rate (GCR) measures how often the governance pipeline and parameter semantics remain unchanged across representation variants.

```text
GCR = count(governance_pipeline_preserved and parameter_semantics_preserved) / total_runs
```

Storage backend variation is intentionally excluded from Phase VIII-B.
It should be evaluated separately as an implementation-independence question in Phase VIII-C.

## 9. Non-Goals

Do not treat this study as:

- a GraphRAG reproduction
- a parser benchmark
- a retrieval benchmark
- a runtime authority update policy
- a universal memory claim

Do not change:

- the governance stack
- the recovery hierarchy
- the evaluation metrics
- the authority separation rules

## 10. Relation to the Paper

Phase VIII-B extends the evidence chain after Phase VIII-A:

- Phase VIII-A: SRP's relation-aware hierarchy preserves its relative advantage across heterogeneous workloads
- Phase VIII-B: the same hierarchy should be tested against variation in encoder and parser implementations
- Phase VIII-C: storage backend variation should be evaluated separately from representation invariance

This phase is meant to separate workload generality from representation invariance, leaving backend independence for a separate implementation study.
