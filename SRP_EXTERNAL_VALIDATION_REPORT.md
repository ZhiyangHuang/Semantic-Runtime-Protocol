# SRP External Validation Report

This report freezes the external-validation evidence package for SRP.
It is an evaluation report, not a calibration artifact, not a runtime policy, and not a new theory branch.

## 1. Frozen Scope

- Benchmarks: `locomo`
- Baselines: `full_context, sliding_window, vector_rag, srp`
- Seeds: `11, 23, 37`
- Data root: `data/locomo`

## 2. Summary

- Case count: `3648`
- semantic_coverage: `0.26692`
- semantic_drift: `0.690841`
- fact_accuracy: `0.268069`
- relation_accuracy: `0.265771`
- recovery_accuracy: `0.245932`
- closure_accuracy: `0.265771`
- neighborhood_completeness: `0.268092`
- hallucinated_relation_rate: `0.521886`
- evidence_cost: `252.818268`
- answer_accuracy: `0.203956`
- official_metric_score: `0.203956`

## 3. Benchmark Summary

### locomo
- semantic_coverage: `0.26692`
- semantic_drift: `0.690841`
- fact_accuracy: `0.268069`
- relation_accuracy: `0.265771`
- recovery_accuracy: `0.245932`
- closure_accuracy: `0.265771`
- neighborhood_completeness: `0.268092`
- hallucinated_relation_rate: `0.521886`
- evidence_cost: `252.818268`
- answer_accuracy: `0.203956`
- official_metric_score: `0.203956`

## 4. Baseline Summary

### full_context
- semantic_coverage: `1.0`
- semantic_drift: `0.198796`
- fact_accuracy: `1.0`
- relation_accuracy: `1.0`
- recovery_accuracy: `0.73289`
- closure_accuracy: `1.0`
- neighborhood_completeness: `1.0`
- hallucinated_relation_rate: `0.993982`
- evidence_cost: `1008.661184`
- answer_accuracy: `0.198669`
- official_metric_score: `0.198669`

### sliding_window
- semantic_coverage: `0.009868`
- semantic_drift: `0.792105`
- fact_accuracy: `0.009868`
- relation_accuracy: `0.009868`
- recovery_accuracy: `0.084582`
- closure_accuracy: `0.009868`
- neighborhood_completeness: `0.009868`
- hallucinated_relation_rate: `0.0`
- evidence_cost: `0.36`
- answer_accuracy: `0.23401`
- official_metric_score: `0.23401`

### vector_rag
- semantic_coverage: `0.018217`
- semantic_drift: `0.816786`
- fact_accuracy: `0.022729`
- relation_accuracy: `0.013706`
- recovery_accuracy: `0.075565`
- closure_accuracy: `0.013706`
- neighborhood_completeness: `0.022204`
- hallucinated_relation_rate: `0.156798`
- evidence_cost: `0.564342`
- answer_accuracy: `0.19026`
- official_metric_score: `0.19026`

### srp
- semantic_coverage: `0.039594`
- semantic_drift: `0.955678`
- fact_accuracy: `0.039677`
- relation_accuracy: `0.03951`
- recovery_accuracy: `0.090691`
- closure_accuracy: `0.03951`
- neighborhood_completeness: `0.040296`
- hallucinated_relation_rate: `0.936764`
- evidence_cost: `1.687544`
- answer_accuracy: `0.192886`
- official_metric_score: `0.192886`

## 5. Failure Summary

- cost_failure: `912`
- evidence_failure: `1922`
- long_chain_dependency_failure: `477`
- none: `24`
- relation_failure: `2673`
- representation_failure: `2672`

### Failure Examples

- cost_failure: locomo:full_context:conv-26:qa:0, locomo:full_context:conv-26:qa:1, locomo:full_context:conv-26:qa:2
- evidence_failure: locomo:full_context:conv-26:qa:0, locomo:srp:conv-26:qa:0, locomo:full_context:conv-26:qa:1
- long_chain_dependency_failure: locomo:sliding_window:conv-26:qa:2, locomo:vector_rag:conv-26:qa:2, locomo:srp:conv-26:qa:2
- relation_failure: locomo:sliding_window:conv-26:qa:0, locomo:vector_rag:conv-26:qa:0, locomo:sliding_window:conv-26:qa:1
- representation_failure: locomo:sliding_window:conv-26:qa:0, locomo:vector_rag:conv-26:qa:0, locomo:sliding_window:conv-26:qa:1

## 6. Pairwise Summary

### locomo
- full_context
  - srp_minus_baseline_coverage: `-0.960406`
  - srp_minus_baseline_drift: `-0.756882`
  - srp_minus_baseline_relation_accuracy: `-0.96049`
  - srp_minus_baseline_cost: `-1006.97364`
- sliding_window
  - srp_minus_baseline_coverage: `0.029726`
  - srp_minus_baseline_drift: `-0.163573`
  - srp_minus_baseline_relation_accuracy: `0.029642`
  - srp_minus_baseline_cost: `1.327544`
- vector_rag
  - srp_minus_baseline_coverage: `0.021377`
  - srp_minus_baseline_drift: `-0.138892`
  - srp_minus_baseline_relation_accuracy: `0.025804`
  - srp_minus_baseline_cost: `1.123202`
