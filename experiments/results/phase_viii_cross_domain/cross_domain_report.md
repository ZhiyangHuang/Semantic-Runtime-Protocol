# SRP Phase VIII Cross-Domain Validation Report

This report freezes the Phase VIII-A cross-domain validation evidence package for SRP.
It is an evaluation report, not a calibration artifact, not a runtime policy, and not a new mechanism design.

## 1. Purpose

Phase VIII-A measures whether SRP's governed semantic evolution principles remain effective across heterogeneous semantic workloads.

## 2. Frozen Scope

| Setting | Value |
| --- | --- |
| Phase | `phase_viii_cross_domain` |
| Evaluation mode | `cross_domain_validation` |
| Domains | `code_memory, knowledge_reasoning, agent_planning` |
| Recovery modes | `vector_only, relation_expansion, relation_closure` |
| Baseline top_k | `2` |
| Baseline relation depth | `1` |
| Baseline closure validation | `True` |

The protocol keeps the SRP governance stack fixed.
Only the semantic workload domain changes across tracks.

## 3. Metrics Schema

- Schema version: `phase_viii_cross_domain_metrics_schema.v1`
- Coverage definition: matched semantic units divided by original semantic units
- Drift definition: weighted combination of fact drift, relation drift, and hallucinated relation rate
- Closure definition: preserved semantic paths divided by required semantic paths
- Governance definition: cross-domain validation of relation-aware recovery under fixed SRP governance
- Evidence cost definition: scalar cost attached to the recovery case

## 4. Summary

| Metric | Value |
| --- | ---: |
| Case count | `18` |
| Mean semantic coverage | `0.534722` |
| Mean semantic drift | `0.327778` |
| Mean fact accuracy | `0.722222` |
| Mean relation accuracy | `0.555556` |
| Mean recovery accuracy | `0.430578` |
| Mean closure accuracy | `0.444444` |
| Mean path preservation | `0.333333` |
| Mean neighborhood completeness | `0.680556` |
| Mean hallucinated relation rate | `0.194444` |
| Mean evidence cost | `1.34` |

## 5. Domain Summary

### agent_planning

| Metric | Value |
| --- | ---: |
| mean_semantic_coverage | `0.465278` |
| mean_semantic_drift | `0.355556` |
| mean_fact_accuracy | `0.666667` |
| mean_relation_accuracy | `0.5` |
| mean_recovery_accuracy | `0.385979` |
| mean_closure_accuracy | `0.416667` |
| mean_path_preservation | `0.333333` |
| mean_neighborhood_completeness | `0.583333` |
| mean_hallucinated_relation_rate | `0.111111` |
| mean_evidence_cost | `1.44` |

### code_memory

| Metric | Value |
| --- | ---: |
| mean_semantic_coverage | `0.638889` |
| mean_semantic_drift | `0.227778` |
| mean_fact_accuracy | `0.833333` |
| mean_relation_accuracy | `0.666667` |
| mean_recovery_accuracy | `0.524802` |
| mean_closure_accuracy | `0.666667` |
| mean_path_preservation | `0.666667` |
| mean_neighborhood_completeness | `0.791667` |
| mean_hallucinated_relation_rate | `0.138889` |
| mean_evidence_cost | `1.26` |

### knowledge_reasoning

| Metric | Value |
| --- | ---: |
| mean_semantic_coverage | `0.5` |
| mean_semantic_drift | `0.4` |
| mean_fact_accuracy | `0.666667` |
| mean_relation_accuracy | `0.5` |
| mean_recovery_accuracy | `0.380952` |
| mean_closure_accuracy | `0.25` |
| mean_path_preservation | `0.0` |
| mean_neighborhood_completeness | `0.666667` |
| mean_hallucinated_relation_rate | `0.333333` |
| mean_evidence_cost | `1.32` |

## 6. Mode Summary

### relation_closure

| Metric | Value |
| --- | ---: |
| mean_semantic_coverage | `0.708333` |
| mean_semantic_drift | `0.111111` |
| mean_fact_accuracy | `0.888889` |
| mean_relation_accuracy | `0.833333` |
| mean_recovery_accuracy | `0.630952` |
| mean_closure_accuracy | `0.666667` |
| mean_path_preservation | `0.5` |
| mean_neighborhood_completeness | `0.758333` |
| mean_hallucinated_relation_rate | `0.0` |
| mean_evidence_cost | `1.563333` |

### relation_expansion

| Metric | Value |
| --- | ---: |
| mean_semantic_coverage | `0.708333` |
| mean_semantic_drift | `0.194445` |
| mean_fact_accuracy | `0.888889` |
| mean_relation_accuracy | `0.833333` |
| mean_recovery_accuracy | `0.494445` |
| mean_closure_accuracy | `0.666667` |
| mean_path_preservation | `0.5` |
| mean_neighborhood_completeness | `0.883333` |
| mean_hallucinated_relation_rate | `0.416667` |
| mean_evidence_cost | `1.34` |

### vector_only

| Metric | Value |
| --- | ---: |
| mean_semantic_coverage | `0.1875` |
| mean_semantic_drift | `0.677778` |
| mean_fact_accuracy | `0.388889` |
| mean_relation_accuracy | `0.0` |
| mean_recovery_accuracy | `0.166336` |
| mean_closure_accuracy | `0.0` |
| mean_path_preservation | `0.0` |
| mean_neighborhood_completeness | `0.4` |
| mean_hallucinated_relation_rate | `0.166667` |
| mean_evidence_cost | `1.116667` |

## 7. Interpretation

The cross-domain runs show that SRP preserves the relative advantage of relation-aware recovery across heterogeneous semantic workloads rather than only on a single graph-shaped prototype.
The report does not claim a universal optimum, and it does not claim uniform absolute fidelity across domains.

Domain-normalized comparison against vector-only recovery:

| Domain | Vector-only Closure | Relation-closure Closure | Delta |
| --- | ---: | ---: | ---: |
| Code memory | `0.0` | `1.0` | `+1.0` |
| Knowledge reasoning | `0.0` | `0.375` | `+0.375` |
| Agent planning | `0.0` | `0.625` | `+0.625` |

The normalized view makes the cross-domain pattern clearer: SRP retains the direction of improvement everywhere, but the magnitude of structural recovery remains workload dependent.

## 8. Relation to the Paper

Phase VIII-A extends the paper's evidence chain by testing whether relation-aware SRP behavior preserves its relative advantage across code evolution memory, knowledge reasoning, and agent planning workloads.

Generated: `2026-07-14T20:30:39.746427+00:00`
