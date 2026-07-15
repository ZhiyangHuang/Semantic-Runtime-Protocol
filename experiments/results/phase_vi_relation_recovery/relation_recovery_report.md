# SRP Phase VI Relation-Aware Recovery Report

This report freezes the Phase VI-A relation-aware recovery evidence package for SRP.
It is an evaluation report, not a calibration artifact and not a runtime optimization artifact.

## 1. Purpose

Phase VI-A measures whether relation-aware recovery can preserve semantic structure during reconstruction under the same information budget.

## 2. Frozen Protocol

| Setting | Value |
| --- | --- |
| Phase | `phase_vi_relation_recovery` |
| Experiment name | `relation_aware_recovery` |
| Recovery modes | `vector_only, relation_expansion, relation_closure` |
| Baseline top_k | `2` |
| Baseline relation depth | `1` |
| Baseline closure validation | `True` |

The protocol keeps the original semantic state, available memory units, evidence budget, workload family, and evaluation schema fixed.
Only the recovery strategy changes across modes.

## 3. Metrics Schema

- Schema version: `phase_vi_relation_recovery_metrics_schema.v1`
- Coverage definition: matched semantic units divided by original semantic units
- Drift definition: weighted combination of fact drift, relation drift, and hallucinated relation rate
- Drift weights: `(0.4, 0.4, 0.2)`
- Closure definition: preserved semantic paths divided by required semantic paths
- Evidence cost definition: scalar cost attached to the recovery case

## 4. Recovery Modes

- vector-only recovery
- vector + relation expansion
- relation-closure recovery

## 5. Summary

| Metric | Value |
| --- | ---: |
| Case count | `12` |
| Mean semantic coverage | `0.623016` |
| Mean semantic drift | `0.220833` |
| Mean fact accuracy | `0.805556` |
| Mean relation accuracy | `0.694444` |
| Mean recovery accuracy | `0.561914` |
| Mean closure accuracy | `0.597222` |
| Mean path preservation | `0.5` |
| Mean neighborhood completeness | `0.7125` |
| Mean hallucinated relation rate | `0.104167` |
| Mean evidence cost | `1.47` |

## 6. Mode Summary

### relation_closure

| Metric | Value |
| --- | ---: |
| mean_semantic_coverage | `0.738095` |
| mean_semantic_drift | `0.083333` |
| mean_fact_accuracy | `0.916667` |
| mean_relation_accuracy | `0.875` |
| mean_recovery_accuracy | `0.697917` |
| mean_closure_accuracy | `0.8125` |
| mean_path_preservation | `0.75` |
| mean_neighborhood_completeness | `0.775` |
| mean_hallucinated_relation_rate | `0.0` |
| mean_evidence_cost | `1.715` |

### relation_expansion

| Metric | Value |
| --- | ---: |
| mean_semantic_coverage | `0.738095` |
| mean_semantic_drift | `0.145834` |
| mean_fact_accuracy | `0.916667` |
| mean_relation_accuracy | `0.875` |
| mean_recovery_accuracy | `0.599432` |
| mean_closure_accuracy | `0.8125` |
| mean_path_preservation | `0.75` |
| mean_neighborhood_completeness | `0.8875` |
| mean_hallucinated_relation_rate | `0.3125` |
| mean_evidence_cost | `1.47` |

### vector_only

| Metric | Value |
| --- | ---: |
| mean_semantic_coverage | `0.392857` |
| mean_semantic_drift | `0.433333` |
| mean_fact_accuracy | `0.583333` |
| mean_relation_accuracy | `0.333333` |
| mean_recovery_accuracy | `0.388393` |
| mean_closure_accuracy | `0.166667` |
| mean_path_preservation | `0.0` |
| mean_neighborhood_completeness | `0.475` |
| mean_hallucinated_relation_rate | `0.0` |
| mean_evidence_cost | `1.225` |

## 7. Per-Case Results

| Case | Category | Mode | Coverage | Drift | Fact Acc. | Relation Acc. | Closure Acc. | Path Pres. | Neighborhood | Hallucinated Rel. | Cost |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `relation_case_1_exact` | `exact_relation_preservation` | `vector_only` | `0.5` | `0.333333` | `0.666667` | `0.5` | `0.25` | `0.0` | `0.5` | `0.0` | `1.0` |
| `relation_case_1_exact` | `exact_relation_preservation` | `relation_expansion` | `0.833333` | `0.066667` | `1.0` | `1.0` | `1.0` | `1.0` | `1.0` | `0.333333` | `1.2` |
| `relation_case_1_exact` | `exact_relation_preservation` | `relation_closure` | `0.833333` | `0.0` | `1.0` | `1.0` | `1.0` | `1.0` | `0.75` | `0.0` | `1.4` |
| `relation_case_2_fact_preserved_relation_missing` | `fact_preserved_relation_missing` | `vector_only` | `0.5` | `0.333333` | `0.666667` | `0.5` | `0.25` | `0.0` | `0.5` | `0.0` | `1.1` |
| `relation_case_2_fact_preserved_relation_missing` | `fact_preserved_relation_missing` | `relation_expansion` | `0.833333` | `0.0` | `1.0` | `1.0` | `1.0` | `1.0` | `0.75` | `0.0` | `1.32` |
| `relation_case_2_fact_preserved_relation_missing` | `fact_preserved_relation_missing` | `relation_closure` | `0.833333` | `0.0` | `1.0` | `1.0` | `1.0` | `1.0` | `0.75` | `0.0` | `1.54` |
| `relation_case_3_multi_hop` | `multi_hop_relation` | `vector_only` | `0.428571` | `0.4` | `0.666667` | `0.333333` | `0.166667` | `0.0` | `0.5` | `0.0` | `1.3` |
| `relation_case_3_multi_hop` | `multi_hop_relation` | `relation_expansion` | `0.857143` | `0.05` | `1.0` | `1.0` | `1.0` | `1.0` | `1.0` | `0.25` | `1.56` |
| `relation_case_3_multi_hop` | `multi_hop_relation` | `relation_closure` | `0.857143` | `0.0` | `1.0` | `1.0` | `1.0` | `1.0` | `1.0` | `0.0` | `1.82` |
| `relation_case_4_conflicting_neighbors` | `conflicting_neighbors` | `vector_only` | `0.142857` | `0.666667` | `0.333333` | `0.0` | `0.0` | `0.0` | `0.4` | `0.0` | `1.5` |
| `relation_case_4_conflicting_neighbors` | `conflicting_neighbors` | `relation_expansion` | `0.428571` | `0.466667` | `0.666667` | `0.5` | `0.25` | `0.0` | `0.8` | `0.666667` | `1.8` |
| `relation_case_4_conflicting_neighbors` | `conflicting_neighbors` | `relation_closure` | `0.428571` | `0.333333` | `0.666667` | `0.5` | `0.25` | `0.0` | `0.6` | `0.0` | `2.1` |

## 8. Interpretation

The baseline protocol is intended to expose the tradeoff surface between semantic fidelity and reconstruction cost.
It does not claim a universally optimal recovery mode.

## 9. Relation to the Paper

Phase VI-A extends the paper's evidence chain by testing whether semantic neighborhoods can be reconstructed more faithfully than isolated units.

Generated: `2026-07-14T19:21:32.361532+00:00`
