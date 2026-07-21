# SRP LongMemEval Reality Check Report

This report packages a minimal real-run external validation loop for SRP.
It preserves the official LongMemEval scorer and co-reports SRP diagnostics under a frozen runtime contract.

## 1. Frozen Scope

- Benchmark: `longmemeval`
- Baselines: `full_context, sliding_window, vector_rag, srp`
- Seeds: `11, 23, 37`
- Data root: `data/longmemeval`
- Sample limit: `2`

## 2. Runtime Contract

- provider: `local_vllm`
- backend: `vllm`
- endpoint: `http://localhost:8000`
- model: `Qwen/Qwen3-4B-AWQ`
- tokenizer: `Qwen/Qwen3-4B-AWQ`
- prompt_template_id: `longmemeval_shared_generation_prompt_v1`
- temperature: `0.0`
- max_output_tokens: `96`
- same_endpoint_across_baselines: `True`
- seed policy: `multi_seed`
- seed values: `11, 23, 37`
- context_window_tokens: `0`

## 3. Official Benchmark Result

- Case count: `1`
- answer_accuracy: `1.0`
- official_metric_score: `1.0`
- semantic_coverage: `0.0`
- semantic_drift: `0.0`
- relation_accuracy: `0.0`
- evidence_cost: `0.0`

## 4. SRP Diagnostics

- SRP case count: `1`
- semantic_coverage_mean: `1.0`
- semantic_drift_mean: `0.0`
- fact_accuracy_mean: `1.0`
- relation_accuracy_mean: `1.0`
- recovery_accuracy_mean: `1.0`
- closure_accuracy_mean: `1.0`
- hallucinated_relation_rate_mean: `0.0`
- evidence_cost_mean: `1.0`
- answer_accuracy_mean: `1.0`
- official_metric_score_mean: `1.0`

## 5. Negative Transition Signals

- record_count: `0`
- none: `1`

## 6. Benchmark Summary

### longmemeval
- case_count: `1`
- answer_accuracy: `1.0`

## 7. Failure Summary

- none: `1`

## 8. Comparison Snapshot

- none

## 9. Artifact Integrity

- runtime_hash: `3e4cd554e2e4e48f45c568f403c5d464d09a3d08921cd7fb70a22efba738ebbf`
- dataset_hash: `971e32c82c30e08948530350e6af623c0c71be94849d2abf2913472b642eb57f`
- report_hash: `24451633156ec78e6fe42de0187491989bd4a96a591a9d36dd56f0e1fab35b13`
- scorer_version: `external_validation_metrics_schema.v1`
- runtime_manifest_version: `external_validation_runtime_contract_v1`

## 10. Reality Check Note

The benchmark scorer remains official. SRP diagnostics are co-reported and do not replace benchmark scoring.
This package is a minimal real-run validation loop, not a benchmark leaderboard and not a new protocol definition.