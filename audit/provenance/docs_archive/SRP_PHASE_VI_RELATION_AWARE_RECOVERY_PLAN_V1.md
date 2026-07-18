# SRP Phase VI Relation-Aware Recovery Plan V1

This document freezes the minimal Phase VI-A experiment boundary for SRP.
It is a planning artifact, not an experiment result, not a runtime policy, and not a GraphRAG reproduction.

## 1. Objective

Validate whether relation-aware recovery reduces semantic loss during reconstruction under the same information budget.

The key question is not whether relation-aware recovery can outperform vector-only retrieval in the abstract.
The key question is:

> Given the same recovered semantic budget, does relation-aware recovery preserve more semantic structure and reduce drift?

## 2. Frozen Variables

Keep fixed:

- original semantic state
- available memory units
- evidence budget
- workload family
- evaluation schema

Only the recovery strategy should change.

## 3. Recovery Variants

Phase VI-A should compare three recovery modes:

### 3.1 Vector-only recovery

Baseline path:

```text
Query
    |
Embedding similarity
    |
Top-k semantic units
    |
Recovery
```

This variant measures how much semantic structure is preserved when recovery depends only on similarity search.

### 3.2 Vector + relation expansion

Expansion path:

```text
Query
    |
Anchor retrieval
    |
Relation expansion
    |
Recovery
```

This variant tests whether adding relation neighbors helps preserve structural context without explicit closure validation.

### 3.3 Relation-closure recovery

Closure path:

```text
Query
    |
Anchor retrieval
    |
Relation expansion
    |
Closure validation
    |
Conflict filtering
    |
Recovery
```

This variant tests whether explicit closure checks further reduce semantic drift and hallucinated relations.

## 4. Semantic Unit Model

The experiment should use a lightweight SRP semantic graph representation with:

- nodes
- edges
- relation types
- confidence values

Recommended minimal structure:

```python
SemanticNode(id, content, embedding)
SemanticEdge(source, target, relation_type, confidence)
SemanticGraph(nodes, edges)
```

The representation should remain small enough for controlled evaluation.

## 5. Experiment Cases

Use the Phase V retention categories as the starting point, then expand them for relation-aware recovery:

- fact-preserving relation loss
- multi-hop relation recovery
- conflicting neighbors
- boundary-sensitive relation closure

These cases should expose whether relation-aware recovery reconstructs semantic neighborhoods rather than isolated units.

## 6. Metrics

Primary metrics:

- `semantic_coverage`
- `semantic_drift`
- `fact_accuracy`
- `relation_accuracy`
- `recovery_accuracy`
- `evidence_cost`

Relation-aware diagnostics:

- `closure_accuracy`
- `path_preservation`
- `relation_recall`
- `neighborhood_completeness`
- `hallucinated_relation_rate`

The central hypothesis is:

> Relation-aware recovery improves structural semantic fidelity by preserving relational dependencies during reconstruction.

## 7. Analysis Plan

The analysis should report:

- fact retention versus relation retention
- closure gain from relation expansion
- closure gain from explicit validation
- cost increase from added structure

The output should preserve the tradeoff surface rather than collapse the study into a single best score.

## 8. Non-Goals

Do not treat this experiment as:

- a GraphRAG clone
- a full knowledge-graph benchmark
- a runtime authority update policy
- a universal graph requirement for all SRP workloads

Do not change:

- `activation_threshold`
- `recovery_min_evidence`
- `preserve_evidence`
- `archive_relations`

unless they are explicitly being swept in a separate sensitivity run.

## 9. Relation to the Paper

Phase VI-A extends the evidence chain after Phase V:

- Phase I: semantic variables are observable
- Phase II: allowed boundaries are validated
- Phase III-A: configurations are selected inside validated regions
- Evidence Escalation: verification quality improves without authority transfer
- Phase V: semantic fidelity after governed transition becomes measurable
- Phase VI-A: relation-aware recovery tests whether semantic neighborhoods can be reconstructed more faithfully than isolated units

