# SRP LongMemEval Reality Check Report

This report packages a minimal real-run external validation loop for SRP.
It preserves the official LongMemEval scorer and co-reports SRP diagnostics under a frozen runtime contract.

## 1. Frozen Scope

- Benchmark: `longmemeval`
- Baselines: `full_context, sliding_window, vector_rag, srp`
- Seeds: `11, 23, 37`
- Data root: `data/longmemeval`
- Sample limit: `1`

## 2. Runtime Contract

- provider: `local_vllm`
- backend: `vllm`
- endpoint: `http://172.25.253.78:8000`
- model: `Qwen/Qwen3-4B-AWQ`
- tokenizer: `Qwen/Qwen3-4B-AWQ`
- prompt_template_id: `longmemeval_shared_generation_prompt_v1`
- temperature: `0.0`
- max_output_tokens: `96`
- same_endpoint_across_baselines: `True`

## 3. Official Benchmark Result

- Case count: `24`
- answer_accuracy: `0.888021`
- official_metric_score: `0.888021`
- semantic_coverage: `0.770833`
- semantic_drift: `0.320833`
- relation_accuracy: `0.625`
- evidence_cost: `1.8475`

## 4. SRP Diagnostics

- SRP case count: `6`
- semantic_coverage_mean: `1.0`
- semantic_drift_mean: `0.1`
- fact_accuracy_mean: `1.0`
- relation_accuracy_mean: `1.0`
- recovery_accuracy_mean: `1.0`
- closure_accuracy_mean: `1.0`
- hallucinated_relation_rate_mean: `0.5`
- evidence_cost_mean: `0.69`
- answer_accuracy_mean: `1.0`
- official_metric_score_mean: `1.0`

## 5. Benchmark Summary

### longmemeval
- case_count: `24`
- semantic_coverage: `0.770833`
- semantic_drift: `0.320833`
- fact_accuracy: `0.916667`
- relation_accuracy: `0.625`
- recovery_accuracy: `0.809896`
- closure_accuracy: `0.625`
- hallucinated_relation_rate: `0.6875`
- evidence_cost: `1.8475`
- answer_accuracy: `0.888021`
- official_metric_score: `0.888021`

## 6. Failure Summary

- counts: `{'domain_mismatch': 9, 'evidence_failure': 24, 'relation_failure': 9, 'representation_failure': 3}`
- examples: `{'domain_mismatch': ['longmemeval:sliding_window:preference_revision', 'longmemeval:vector_rag:preference_revision', 'longmemeval:sliding_window:contradiction_resolution'], 'evidence_failure': ['longmemeval:full_context:preference_revision', 'longmemeval:sliding_window:preference_revision', 'longmemeval:vector_rag:preference_revision'], 'relation_failure': ['longmemeval:sliding_window:preference_revision', 'longmemeval:vector_rag:preference_revision', 'longmemeval:sliding_window:contradiction_resolution'], 'representation_failure': ['longmemeval:sliding_window:preference_revision', 'longmemeval:sliding_window:preference_revision', 'longmemeval:sliding_window:preference_revision']}`

## 7. Comparison Snapshot

### full_context
- srp_minus_baseline_coverage: `0.0`
- srp_minus_baseline_drift: `0.0`
- srp_minus_baseline_relation_accuracy: `0.0`
- srp_minus_baseline_cost: `-4.81`

### sliding_window
- srp_minus_baseline_coverage: `0.666666`
- srp_minus_baseline_drift: `0.633333`
- srp_minus_baseline_relation_accuracy: `1.0`
- srp_minus_baseline_cost: `0.21`

### vector_rag
- srp_minus_baseline_coverage: `0.25`
- srp_minus_baseline_drift: `0.25`
- srp_minus_baseline_relation_accuracy: `0.5`
- srp_minus_baseline_cost: `-0.03`

## 8. Reality Check Note

The benchmark scorer remains official. SRP diagnostics are co-reported and do not replace benchmark scoring.
This package is a minimal real-run validation loop, not a benchmark leaderboard and not a new protocol definition.