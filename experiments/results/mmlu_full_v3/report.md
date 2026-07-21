# mmlu Benchmark Report

This report is generated from the shared benchmark execution layer.

## Experiment Setup

- benchmark_name: `mmlu`
- data_root: `hf:cais/mmlu|all|test`
- dataset_version: `mmlu_v1`
- execution_parameters: `{'subjects': ()}`
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

- accuracy: `0.639688078621279`
- completion_tokens_total: `75442`
- failed_prediction_count: `0`
- latency_mean_seconds: `0.11274312063808574`
- latency_total_seconds: `3166.2778`
- metric_schema: `{'schema_version': 'benchmark_metrics_schema.v1', 'primary_metric_name': 'accuracy', 'primary_metric_definition': 'correct predictions divided by total evaluated predictions', 'latency_definition': 'mean and total runtime per prediction', 'token_definition': 'token usage gathered from generation responses', 'failure_definition': 'count and rate of prediction failures'}`
- prediction_count: `28084`
- prompt_tokens_total: `6700243`
- score_mean: `0.639688078621279`
- successful_prediction_count: `28084`
- total_tokens_total: `6775685`
- variant_counts: `{'baseline': 14042, 'srp': 14042}`

## Benchmark Metrics

- accuracy: `0.653183`
- accuracy_gap: `-0.02699`
- baseline_accuracy: `0.653183`
- benchmark_name: `mmlu`
- completion_tokens_total: `75442`
- correct_count: `9172`
- failed_prediction_count: `0`
- incorrect_count: `4870`
- invalid_output_count: `1`
- latency_mean_seconds: `0.11274312063808574`
- latency_total_seconds: `3166.2778`
- metric_schema: `{'schema_version': 'benchmark_metrics_schema.v1', 'primary_metric_name': 'accuracy', 'primary_metric_definition': 'correct predictions divided by total evaluated predictions', 'latency_definition': 'mean and total runtime per prediction', 'token_definition': 'token usage gathered from generation responses', 'failure_definition': 'count and rate of prediction failures'}`
- official_metric_name: `accuracy`
- prediction_count: `28084`
- prompt_tokens_total: `6700243`
- sample_count: `14042`
- score_mean: `0.639688078621279`
- srp_accuracy: `0.626193`
- srp_correct_count: `8793`
- srp_incorrect_count: `5249`
- srp_invalid_output_count: `0`
- successful_prediction_count: `28084`
- total_tokens_total: `6775685`
- variant_counts: `{'baseline': 14042, 'srp': 14042}`

## Reproducibility

- sample_count: `14042`
- prediction_count: `28084`
- report_format: `shared-benchmark-report-v1`

## Sample Predictions

| case_id | variant | prediction | is_correct | error |
| --- | --- | --- | --- | --- |
| mmlu_0 | baseline | B | True |  |
| mmlu_0 | srp | B | True |  |
| mmlu_1 | baseline | D | False |  |
| mmlu_1 | srp | A | False |  |
| mmlu_2 | baseline | C | False |  |
| mmlu_2 | srp | C | False |  |
| mmlu_3 | baseline | D | False |  |
| mmlu_3 | srp | D | False |  |
| mmlu_4 | baseline | B | True |  |
| mmlu_4 | srp | C | False |  |
