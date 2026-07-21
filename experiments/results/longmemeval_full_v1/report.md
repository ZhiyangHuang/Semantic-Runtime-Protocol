# LongMemEval Bridge Report

This report packages the official LongMemEval external-validation evidence under the shared benchmark artifact surface.
The official scorer remains owned by `experiments/external_validation/`; the bridge only packages and maps the outputs.

## Evaluation Authority

- official scorer owner: `external_validation`
- srp diagnostics owner: `longmemeval_bridge`
- runtime contract owner: `external_validation`
- payload policy: `not_stored_in_repository`

## Bridge Summary

- bridge_name: `longmemeval`
- bridge_version: `bridge_migration_v1`
- bridge_output_dir: `experiments/results/longmemeval_full_v1`
- benchmark_name: `longmemeval`
- dataset_version: `2025`
- sample_count: `2`
- prediction_count: `24`
- official_metric_name: `official_metric_score`

## Official Result

## Official Benchmark Summary

- case_count: `24`
- semantic_coverage: `0.770833`
- semantic_drift: `0.320833`
- fact_accuracy: `0.916667`
- relation_accuracy: `0.625`
- recovery_accuracy: `0.809896`
- closure_accuracy: `0.625`
- neighborhood_completeness: `0.9375`
- hallucinated_relation_rate: `0.6875`
- evidence_cost: `1.8475`
- answer_accuracy: `0.888021`
- official_metric_score: `0.888021`

## SRP Diagnostics

## SRP Diagnostic Summary

- none

## Bridge Metrics

## Shared Metric Mapping

- artifact_files_count: `5`
- bridge_accuracy: `0.0`
- bridge_accuracy_gap: `1.0`
- bridge_srp_accuracy: `1.0`
- metric_schema_version: `benchmark_metrics_schema.v1`
- official_score_source: `external_validation`
- official_score_value: `0.888021`
- srp_diagnostics_case_count: `0`
- srp_diagnostics_source: `longmemeval_bridge`

## Failure Summary

- counts: `{'domain_mismatch': 9, 'evidence_failure': 24, 'relation_failure': 9, 'representation_failure': 3}`
- examples: `{'domain_mismatch': ['longmemeval:sliding_window:preference_revision', 'longmemeval:vector_rag:preference_revision', 'longmemeval:sliding_window:contradiction_resolution'], 'evidence_failure': ['longmemeval:full_context:preference_revision', 'longmemeval:sliding_window:preference_revision', 'longmemeval:vector_rag:preference_revision'], 'relation_failure': ['longmemeval:sliding_window:preference_revision', 'longmemeval:vector_rag:preference_revision', 'longmemeval:sliding_window:contradiction_resolution'], 'representation_failure': ['longmemeval:sliding_window:preference_revision', 'longmemeval:sliding_window:preference_revision', 'longmemeval:sliding_window:preference_revision']}`

## Benchmark Summary

### longmemeval
- semantic_coverage: `0.770833`
- semantic_drift: `0.320833`
- fact_accuracy: `0.916667`
- relation_accuracy: `0.625`
- recovery_accuracy: `0.809896`
- closure_accuracy: `0.625`
- neighborhood_completeness: `0.9375`
- hallucinated_relation_rate: `0.6875`
- evidence_cost: `1.8475`
- answer_accuracy: `0.888021`
- official_metric_score: `0.888021`
- case_count: `24`

## Baseline Summary

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
- case_count: `6`

### sliding_window
- semantic_coverage: `0.333334`
- semantic_drift: `0.733333`
- fact_accuracy: `0.666666`
- relation_accuracy: `0.0`
- recovery_accuracy: `0.40625`
- closure_accuracy: `0.0`
- neighborhood_completeness: `0.75`
- hallucinated_relation_rate: `1.0`
- evidence_cost: `0.48`
- answer_accuracy: `0.552084`
- official_metric_score: `0.552084`
- case_count: `6`

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
- case_count: `6`

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
- case_count: `6`

## Runtime Manifest

- provider: `local_vllm`
- backend: `vllm`
- endpoint: `http://172.25.253.78:8000`
- model: `Qwen/Qwen3-4B-AWQ`
- tokenizer: `Qwen/Qwen3-4B-AWQ`
- prompt_template_id: `longmemeval_shared_generation_prompt_v1`
- temperature: `0.0`
- max_output_tokens: `96`
- runtime_policy.same_endpoint_across_baselines: `True`
- runtime_policy.baseline_generation_backend: `shared`
- runtime_policy.srp_generation_backend: `shared`

## Provenance

- bridge_name: `longmemeval`
- bridge_version: `bridge_migration_v1`
- bridge_config_path: `C:\Users\ZhiyangHuang\Semantic-Runtime-Protocol\configs\external_validation_longmemeval_evidence.env`
- bridge_output_dir: `experiments/results/longmemeval_full_v1`
- official_scorer_owner: `external_validation`
- runtime_contract_owner: `external_validation`
- trace_count: `24`

## Artifact Contract

- source: `shared_benchmark_artifact_contract`
- files: `['config.json', 'raw_predictions.jsonl', 'metrics.json', 'metadata.json', 'report.md']`

## External Validation Evidence

The official LongMemEval evidence remains owned by `experiments/external_validation/` and is not reinterpreted here.
This bridge report preserves the official result, SRP diagnostics, and provenance without replacing scorer authority.

The shared writer captures artifact hashes in metadata.json after serialization.
