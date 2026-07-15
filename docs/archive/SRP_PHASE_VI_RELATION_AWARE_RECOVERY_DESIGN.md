# SRP Phase VI Relation-Aware Recovery Design V1

This document freezes the next preservation-focused design boundary for SRP.
It is a design artifact, not an experiment result, not a runtime policy, and not a GraphRAG reproduction.

## 1. Purpose

Phase V showed that semantic fidelity can be measured after governed transition, but the baseline results also exposed a structural weakness:

- fact accuracy was relatively strong
- relation accuracy was materially weaker

That pattern suggests the next design step should not focus on recovering isolated semantic units only.
Instead, SRP should recover a semantic neighborhood: the connected semantic units, relations, and closure conditions that make a recovered state meaningful rather than merely lexical.

The design question is:

> How can SRP recover a complete semantic neighborhood instead of a set of disconnected semantic fragments?

This phase does not change authority boundaries.
It improves reconstruction quality inside the existing SRP governance model.

## 2. Design Motivation

Vector-only retrieval is good at finding similar content, but it does not guarantee relation closure.
For SRP, the key failure mode is not only missing facts; it is missing the relation structure that makes facts interpretable as a coherent semantic state.

The design therefore targets:

- relation preservation
- closure recovery
- neighborhood completeness
- reconstruction consistency

The objective is not to maximize raw token retention.
The objective is to preserve semantic structure under governed recovery.

## 3. Design Principles

### 3.1 Recover the neighborhood, not just the node

Recovery should start from a semantic anchor and expand to related units that complete the local semantic neighborhood.

### 3.2 Prefer closure over isolated similarity

If a candidate unit is individually similar but disconnects the relation graph, the recovery layer should treat that as incomplete.

### 3.3 Keep reconstruction separate from authority

Recovery may reconstruct a semantic state, but it must not become execution authority.

### 3.4 Preserve provenance and relation evidence

Recovered structure should carry the evidence trail used to justify inclusion.

## 4. Relation-Aware Recovery Pipeline

SRP relation-aware recovery should follow a two-stage reconstruction path.

```text
Query / Recovery Need
    |
    v
Semantic Anchor Extraction
    |
    v
Anchor Retrieval
    |
    v
Relation Expansion
    |
    v
Semantic Closure Validation
    |
    v
Semantic Reconstruction
    |
    v
Governed Output
```

### 4.1 Semantic anchor extraction

The recovery layer identifies one or more anchor units that best represent the semantic intent of the recovery request.

Anchors should capture:

- key entities
- key facts
- dependency hints
- temporal or causal constraints

### 4.2 Anchor retrieval

The system retrieves the strongest anchor candidates using vector similarity, but only as the first step.

### 4.3 Relation expansion

From each anchor, the system expands to directly connected semantic units:

- dependency neighbors
- causal neighbors
- temporal neighbors
- same-entity variants
- constraint-linked units

This step is what distinguishes SRP relation-aware recovery from isolated unit retrieval.

### 4.4 Semantic closure validation

The candidate neighborhood is checked for closure:

- are required relations present?
- are critical paths preserved?
- did the expansion introduce hallucinated edges?
- does the recovered subgraph still satisfy the semantic constraints?

### 4.5 Semantic reconstruction

Only after closure validation should the recovery layer reconstruct the output state.
This can be rendered as text, structured state, or a graph-backed semantic package.

## 5. Representation Model

SRP already has enough structure to support relation-aware recovery:

- `SemanticFact`
- `SemanticRelation`
- `SemanticStateSnapshot`
- `SemanticRuntimeGraph`
- `archive_relations`
- `preserve_evidence`

A relation-aware recovery layer should extend the recovery package with explicit relation metadata.

Suggested semantic unit shape:

```json
{
  "id": "alice",
  "content": "Alice works on Project X",
  "embedding": "...",
  "relations": [
    {
      "target_id": "project_x",
      "relation_type": "worked_on",
      "confidence": 0.95
    }
  ],
  "provenance": {
    "evidence_refs": ["..."],
    "archive_refs": ["..."]
  }
}
```

This keeps the design aligned with the existing Phase V schema while making relation closure first-class.

## 6. Relation-Aware Scoring

The recovery layer should not rely on vector similarity alone.

A candidate score can combine:

- semantic similarity
- relation relevance
- neighborhood coverage gain
- provenance consistency

One possible form is:

```text
score = α * semantic_similarity
      + β * relation_relevance
      + γ * neighborhood_coverage_gain
      + δ * provenance_consistency
```

The weights are not fixed by this document.
They are part of later evaluation.

The key design rule is that relation completeness must contribute to retrieval priority, not just textual similarity.

## 7. Recovery Metrics

Phase VI should measure recovery quality with relation-sensitive metrics, not only token or fact recovery.

Primary metrics:

- `semantic_coverage`
- `semantic_drift`
- `fact_accuracy`
- `relation_accuracy`
- `recovery_accuracy`
- `evidence_cost`

Added relation-aware diagnostics:

- `path_preservation`
- `closure_accuracy`
- `relation_recall`
- `neighborhood_completeness`
- `hallucinated_relation_rate`

These metrics should distinguish:

- isolated fact recovery
- relation-preserving recovery
- full neighborhood closure

## 8. Integration with Current Phase V

Phase V already established that relation preservation is a bottleneck.

This design uses that result to justify the next recovery layer:

- `archive_relations` becomes the structural retention boundary
- `preserve_evidence` stabilizes the proof trail
- `recovery_min_evidence` controls strictness
- `activation_threshold` controls transition gating

In SRP terms:

- Phase V measures semantic fidelity after transition
- Phase VI improves the reconstruction path for relation-rich states

## 9. Non-Goals

Do not treat this design as:

- a GraphRAG clone
- a new runtime authority layer
- a default parameter update policy
- a universal graph requirement for all SRP workloads

This design is specifically about relation-aware recovery inside governed semantic state reconstruction.

## 10. Suggested Experiment Family

The next experimental boundary should compare at least three recovery modes:

- vector-only recovery
- vector plus relation expansion
- relation-closure recovery

Suggested metrics:

- relation accuracy
- closure accuracy
- semantic drift
- recovery accuracy
- retrieval cost

The expected pattern is:

- vector-only may preserve facts but miss relations
- relation expansion should improve closure
- closure recovery should reduce semantic drift at higher cost

## 11. Relation to the Paper

Phase VI would extend the evidence chain beyond retention measurement:

- Phase I: semantic variables are observable
- Phase II: allowed boundaries are validated
- Phase III-A: configurations are selected inside validated regions
- Evidence Escalation: verification quality improves without authority transfer
- Phase V: semantic fidelity after governed transition becomes measurable
- Phase VI: relation-preserving recovery can reconstruct semantic neighborhoods rather than isolated units

