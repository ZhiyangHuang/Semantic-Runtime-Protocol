# mmlu Benchmark Report

This report is generated from the shared benchmark execution layer.

## Experiment Setup

- benchmark_name: `mmlu`
- data_root: `hf:cais/mmlu|all|test`
- dataset_version: `mmlu_v1`
- execution_parameters: `{'subjects': ('all',)}`
- max_output_tokens: `8`
- metadata: `{}`
- model: `Qwen/Qwen3-4B-AWQ`
- prompt_format: `mmlu_mcq_v1`
- sample_limit: `0`
- seed: `0`
- srp_configuration: `{'srp_mode': 'context_recovery'}`
- system_prompt: `Answer with the single best choice label only.`
- temperature: `0.0`
- variants: `('baseline', 'srp')`

## Summary

- accuracy: `0.0`
- completion_tokens_total: `0`
- failed_prediction_count: `0`
- latency_mean_seconds: `0.0`
- latency_total_seconds: `0.0`
- metric_schema: `{'schema_version': 'benchmark_metrics_schema.v1', 'primary_metric_name': 'accuracy', 'primary_metric_definition': 'correct predictions divided by total evaluated predictions', 'latency_definition': 'mean and total runtime per prediction', 'token_definition': 'token usage gathered from generation responses', 'failure_definition': 'count and rate of prediction failures'}`
- prediction_count: `0`
- prompt_tokens_total: `0`
- score_mean: `0.0`
- successful_prediction_count: `0`
- total_tokens_total: `0`
- variant_counts: `{}`

## Benchmark Metrics

- accuracy: `0.0`
- accuracy_gap: `0.0`
- baseline_accuracy: `0.0`
- benchmark_name: `mmlu`
- completion_tokens_total: `0`
- correct_count: `0`
- failed_prediction_count: `0`
- incorrect_count: `0`
- invalid_output_count: `0`
- latency_mean_seconds: `0.0`
- latency_total_seconds: `0.0`
- metric_schema: `{'schema_version': 'benchmark_metrics_schema.v1', 'primary_metric_name': 'accuracy', 'primary_metric_definition': 'correct predictions divided by total evaluated predictions', 'latency_definition': 'mean and total runtime per prediction', 'token_definition': 'token usage gathered from generation responses', 'failure_definition': 'count and rate of prediction failures'}`
- official_metric_name: `accuracy`
- prediction_count: `0`
- prompt_tokens_total: `0`
- sample_count: `0`
- score_mean: `0.0`
- srp_accuracy: `0.0`
- srp_correct_count: `0`
- srp_incorrect_count: `0`
- srp_invalid_output_count: `0`
- successful_prediction_count: `0`
- total_tokens_total: `0`
- variant_counts: `{}`

## Reproducibility

- sample_count: `0`
- prediction_count: `0`
- report_format: `shared-benchmark-report-v1`
