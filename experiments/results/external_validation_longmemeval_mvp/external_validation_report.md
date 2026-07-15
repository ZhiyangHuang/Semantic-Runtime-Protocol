# SRP External Validation Report

This report freezes the external-validation evidence package for SRP.
It is an evaluation report, not a calibration artifact, not a runtime policy, and not a new theory branch.

## 1. Frozen Scope

- Benchmarks: `longmemeval`
- Baselines: `full_context, sliding_window, vector_rag, srp`
- Seeds: `11, 23, 37`
- Data root: `data/longmemeval`

## 2. Summary

- Case count: `24`
- semantic_coverage: `0.770833`
- semantic_drift: `0.320833`
- fact_accuracy: `0.916667`
- relation_accuracy: `0.625`
- recovery_accuracy: `0.814421`
- closure_accuracy: `0.625`
- neighborhood_completeness: `0.9375`
- hallucinated_relation_rate: `0.6875`
- evidence_cost: `1.8475`
- answer_accuracy: `0.901596`
- official_metric_score: `0.901596`

## 3. Benchmark Summary

### longmemeval
- semantic_coverage: `0.770833`
- semantic_drift: `0.320833`
- fact_accuracy: `0.916667`
- relation_accuracy: `0.625`
- recovery_accuracy: `0.814421`
- closure_accuracy: `0.625`
- neighborhood_completeness: `0.9375`
- hallucinated_relation_rate: `0.6875`
- evidence_cost: `1.8475`
- answer_accuracy: `0.901596`
- official_metric_score: `0.901596`

## 4. Baseline Summary

### full_context
- semantic_coverage: `1.0`
- semantic_drift: `0.1`
- fact_accuracy: `1.0`
- relation_accuracy: `1.0`
- recovery_accuracy: `1.0`
- closure_accuracy: `1.0`
- neighborhood_completeness: `1.0`
- hallucinated_relation_rate: `0.5`
- evidence_cost: `5.5`
- answer_accuracy: `1.0`
- official_metric_score: `1.0`

### sliding_window
- semantic_coverage: `0.333334`
- semantic_drift: `0.733333`
- fact_accuracy: `0.666666`
- relation_accuracy: `0.0`
- recovery_accuracy: `0.42435`
- closure_accuracy: `0.0`
- neighborhood_completeness: `0.75`
- hallucinated_relation_rate: `1.0`
- evidence_cost: `0.48`
- answer_accuracy: `0.606383`
- official_metric_score: `0.606383`

### vector_rag
- semantic_coverage: `0.75`
- semantic_drift: `0.35`
- fact_accuracy: `1.0`
- relation_accuracy: `0.5`
- recovery_accuracy: `0.833334`
- closure_accuracy: `0.5`
- neighborhood_completeness: `1.0`
- hallucinated_relation_rate: `0.75`
- evidence_cost: `0.72`
- answer_accuracy: `1.0`
- official_metric_score: `1.0`

### srp
- semantic_coverage: `1.0`
- semantic_drift: `0.1`
- fact_accuracy: `1.0`
- relation_accuracy: `1.0`
- recovery_accuracy: `1.0`
- closure_accuracy: `1.0`
- neighborhood_completeness: `1.0`
- hallucinated_relation_rate: `0.5`
- evidence_cost: `0.69`
- answer_accuracy: `1.0`
- official_metric_score: `1.0`

## 5. Failure Summary

- domain_mismatch: `9`
- evidence_failure: `24`
- relation_failure: `9`
- representation_failure: `3`

### Failure Examples

- domain_mismatch: longmemeval:sliding_window:preference_revision, longmemeval:vector_rag:preference_revision, longmemeval:sliding_window:contradiction_resolution
- evidence_failure: longmemeval:full_context:preference_revision, longmemeval:sliding_window:preference_revision, longmemeval:vector_rag:preference_revision
- relation_failure: longmemeval:sliding_window:preference_revision, longmemeval:vector_rag:preference_revision, longmemeval:sliding_window:contradiction_resolution
- representation_failure: longmemeval:sliding_window:preference_revision, longmemeval:sliding_window:preference_revision, longmemeval:sliding_window:preference_revision

## 6. Pairwise Summary

### longmemeval
- full_context
  - srp_minus_baseline_coverage: `0.0`
  - srp_minus_baseline_drift: `0.0`
  - srp_minus_baseline_relation_accuracy: `0.0`
  - srp_minus_baseline_cost: `-4.81`
- sliding_window
  - srp_minus_baseline_coverage: `0.666666`
  - srp_minus_baseline_drift: `0.633333`
  - srp_minus_baseline_relation_accuracy: `1.0`
  - srp_minus_baseline_cost: `0.21`
- vector_rag
  - srp_minus_baseline_coverage: `0.25`
  - srp_minus_baseline_drift: `0.25`
  - srp_minus_baseline_relation_accuracy: `0.5`
  - srp_minus_baseline_cost: `-0.03`
