# SRP External Validation Report

This report freezes the external-validation evidence package for SRP.
It is an evaluation report, not a calibration artifact, not a runtime policy, and not a new theory branch.

## 1. Frozen Scope

- Benchmarks: `locomo, longmemeval, tgb2`
- Baselines: `full_context, sliding_window, summarization_memory, vector_rag, graph_memory, mem0, letta, graphiti, memmachine, srp`
- Seeds: `11, 23, 37`
- Data root: `fixtures`

## 2. Summary

- Case count: `180`
- semantic_coverage: `0.898264`
- semantic_drift: `0.1725`
- fact_accuracy: `0.946528`
- relation_accuracy: `0.85`
- recovery_accuracy: `0.705324`
- closure_accuracy: `0.85`
- neighborhood_completeness: `0.941667`
- hallucinated_relation_rate: `0.455556`
- evidence_cost: `1.331487`
- answer_accuracy: `0.319444`
- official_metric_score: `0.319444`

## 3. Benchmark Summary

### locomo
- semantic_coverage: `0.890625`
- semantic_drift: `0.1175`
- fact_accuracy: `0.93125`
- relation_accuracy: `0.85`
- recovery_accuracy: `0.910417`
- closure_accuracy: `0.85`
- neighborhood_completeness: `0.925`
- hallucinated_relation_rate: `0.15`
- evidence_cost: `1.30688`
- answer_accuracy: `0.95`
- official_metric_score: `0.95`

### longmemeval
- semantic_coverage: `0.908333`
- semantic_drift: `0.183333`
- fact_accuracy: `0.966667`
- relation_accuracy: `0.85`
- recovery_accuracy: `0.608334`
- closure_accuracy: `0.85`
- neighborhood_completeness: `0.975`
- hallucinated_relation_rate: `0.55`
- evidence_cost: `1.25361`
- answer_accuracy: `0.008333`
- official_metric_score: `0.008333`

### tgb2
- semantic_coverage: `0.895833`
- semantic_drift: `0.216666`
- fact_accuracy: `0.941667`
- relation_accuracy: `0.85`
- recovery_accuracy: `0.597223`
- closure_accuracy: `0.85`
- neighborhood_completeness: `0.925`
- hallucinated_relation_rate: `0.666667`
- evidence_cost: `1.43397`
- answer_accuracy: `0.0`
- official_metric_score: `0.0`

## 4. Baseline Summary

### full_context
- semantic_coverage: `1.0`
- semantic_drift: `0.094444`
- fact_accuracy: `1.0`
- relation_accuracy: `1.0`
- recovery_accuracy: `0.777778`
- closure_accuracy: `1.0`
- neighborhood_completeness: `1.0`
- hallucinated_relation_rate: `0.472222`
- evidence_cost: `6.0`
- answer_accuracy: `0.333333`
- official_metric_score: `0.333333`

### sliding_window
- semantic_coverage: `0.436111`
- semantic_drift: `0.551111`
- fact_accuracy: `0.705556`
- relation_accuracy: `0.166667`
- recovery_accuracy: `0.346296`
- closure_accuracy: `0.166667`
- neighborhood_completeness: `0.75`
- hallucinated_relation_rate: `0.5`
- evidence_cost: `0.44`
- answer_accuracy: `0.166667`
- official_metric_score: `0.166667`

### summarization_memory
- semantic_coverage: `0.888889`
- semantic_drift: `0.161111`
- fact_accuracy: `0.944445`
- relation_accuracy: `0.833333`
- recovery_accuracy: `0.712963`
- closure_accuracy: `0.833333`
- neighborhood_completeness: `0.916667`
- hallucinated_relation_rate: `0.361111`
- evidence_cost: `0.76`
- answer_accuracy: `0.361111`
- official_metric_score: `0.361111`

### vector_rag
- semantic_coverage: `0.699305`
- semantic_drift: `0.346111`
- fact_accuracy: `0.815278`
- relation_accuracy: `0.583333`
- recovery_accuracy: `0.577315`
- closure_accuracy: `0.583333`
- neighborhood_completeness: `0.75`
- hallucinated_relation_rate: `0.527778`
- evidence_cost: `0.74`
- answer_accuracy: `0.333333`
- official_metric_score: `0.333333`

### graph_memory
- semantic_coverage: `1.0`
- semantic_drift: `0.094444`
- fact_accuracy: `1.0`
- relation_accuracy: `1.0`
- recovery_accuracy: `0.777778`
- closure_accuracy: `1.0`
- neighborhood_completeness: `1.0`
- hallucinated_relation_rate: `0.472222`
- evidence_cost: `0.94`
- answer_accuracy: `0.333333`
- official_metric_score: `0.333333`

### mem0
- semantic_coverage: `1.0`
- semantic_drift: `0.094444`
- fact_accuracy: `1.0`
- relation_accuracy: `1.0`
- recovery_accuracy: `0.777778`
- closure_accuracy: `1.0`
- neighborhood_completeness: `1.0`
- hallucinated_relation_rate: `0.472222`
- evidence_cost: `0.893`
- answer_accuracy: `0.333333`
- official_metric_score: `0.333333`

### letta
- semantic_coverage: `0.958333`
- semantic_drift: `0.105556`
- fact_accuracy: `1.0`
- relation_accuracy: `0.916667`
- recovery_accuracy: `0.75`
- closure_accuracy: `0.916667`
- neighborhood_completeness: `1.0`
- hallucinated_relation_rate: `0.361111`
- evidence_cost: `0.79`
- answer_accuracy: `0.333333`
- official_metric_score: `0.333333`

### graphiti
- semantic_coverage: `1.0`
- semantic_drift: `0.094444`
- fact_accuracy: `1.0`
- relation_accuracy: `1.0`
- recovery_accuracy: `0.777778`
- closure_accuracy: `1.0`
- neighborhood_completeness: `1.0`
- hallucinated_relation_rate: `0.472222`
- evidence_cost: `1.0152`
- answer_accuracy: `0.333333`
- official_metric_score: `0.333333`

### memmachine
- semantic_coverage: `1.0`
- semantic_drift: `0.094444`
- fact_accuracy: `1.0`
- relation_accuracy: `1.0`
- recovery_accuracy: `0.777778`
- closure_accuracy: `1.0`
- neighborhood_completeness: `1.0`
- hallucinated_relation_rate: `0.472222`
- evidence_cost: `1.006667`
- answer_accuracy: `0.333333`
- official_metric_score: `0.333333`

### srp
- semantic_coverage: `1.0`
- semantic_drift: `0.088889`
- fact_accuracy: `1.0`
- relation_accuracy: `1.0`
- recovery_accuracy: `0.777778`
- closure_accuracy: `1.0`
- neighborhood_completeness: `1.0`
- hallucinated_relation_rate: `0.444444`
- evidence_cost: `0.73`
- answer_accuracy: `0.333333`
- official_metric_score: `0.333333`

## 5. Failure Summary

- domain_mismatch: `18`
- evidence_failure: `132`
- none: `42`
- relation_failure: `24`
- representation_failure: `6`

### Failure Examples

- domain_mismatch: longmemeval:sliding_window:preference_revision, longmemeval:vector_rag:preference_revision, longmemeval:sliding_window:contradiction_resolution
- evidence_failure: locomo:full_context:session_pref_update, locomo:graph_memory:session_pref_update, locomo:mem0:session_pref_update
- relation_failure: locomo:sliding_window:session_pref_update, locomo:sliding_window:travel_memory, locomo:sliding_window:session_pref_update
- representation_failure: locomo:sliding_window:travel_memory, locomo:sliding_window:travel_memory, locomo:sliding_window:travel_memory

## 6. Pairwise Summary

### locomo
- srp_minus_baseline_coverage: `0.121528`
- srp_minus_baseline_drift: `0.075`
- srp_minus_baseline_relation_accuracy: `0.166667`
- srp_minus_baseline_cost: `-0.607644`

### longmemeval
- srp_minus_baseline_coverage: `0.101852`
- srp_minus_baseline_drift: `0.092593`
- srp_minus_baseline_relation_accuracy: `0.166667`
- srp_minus_baseline_cost: `-0.626233`

### tgb2
- srp_minus_baseline_coverage: `0.115741`
- srp_minus_baseline_drift: `0.111111`
- srp_minus_baseline_relation_accuracy: `0.166667`
- srp_minus_baseline_cost: `-0.771078`
