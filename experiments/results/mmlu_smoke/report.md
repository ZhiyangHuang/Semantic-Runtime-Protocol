# mmlu Benchmark Report

This report is generated from the shared benchmark execution layer.

## Experiment Setup

- benchmark_name: `mmlu`
- data_root: `hf:cais/mmlu|abstract_algebra,anatomy,astronomy,business_ethics,clinical_knowledge|validation`
- dataset_version: `mmlu_v1`
- execution_parameters: `{'subjects': ('abstract_algebra', 'anatomy', 'astronomy', 'business_ethics', 'clinical_knowledge'), 'smoke_run': True}`
- max_output_tokens: `8`
- metadata: `{'phase': 'mmlu_smoke'}`
- model: `Qwen/Qwen3-4B-AWQ`
- prompt_format: `mmlu_mcq_v1`
- sample_limit: `50`
- seed: `0`
- srp_configuration: `{'srp_mode': 'context_recovery', 'smoke_mode': True}`
- system_prompt: `Answer with the single best choice label only.`
- temperature: `0.0`
- variants: `('baseline', 'srp')`

## Summary

- accuracy: `0.86`
- completion_tokens_total: `254`
- failed_prediction_count: `0`
- latency_mean_seconds: `0.094191`
- latency_total_seconds: `9.4191`
- metric_schema: `{'schema_version': 'benchmark_metrics_schema.v1', 'primary_metric_name': 'accuracy', 'primary_metric_definition': 'correct predictions divided by total evaluated predictions', 'latency_definition': 'mean and total runtime per prediction', 'token_definition': 'token usage gathered from generation responses', 'failure_definition': 'count and rate of prediction failures'}`
- prediction_count: `100`
- prompt_tokens_total: `17645`
- score_mean: `0.86`
- successful_prediction_count: `100`
- total_tokens_total: `17899`
- variant_counts: `{'baseline': 50, 'srp': 50}`

## Benchmark Metrics

- accuracy: `0.72`
- accuracy_gap: `0.28`
- baseline_accuracy: `0.72`
- benchmark_name: `mmlu`
- completion_tokens_total: `254`
- correct_count: `36`
- failed_prediction_count: `0`
- incorrect_count: `14`
- invalid_output_count: `0`
- latency_mean_seconds: `0.094191`
- latency_total_seconds: `9.4191`
- metric_schema: `{'schema_version': 'benchmark_metrics_schema.v1', 'primary_metric_name': 'accuracy', 'primary_metric_definition': 'correct predictions divided by total evaluated predictions', 'latency_definition': 'mean and total runtime per prediction', 'token_definition': 'token usage gathered from generation responses', 'failure_definition': 'count and rate of prediction failures'}`
- official_metric_name: `accuracy`
- prediction_count: `100`
- prompt_tokens_total: `17645`
- sample_count: `50`
- score_mean: `0.86`
- srp_accuracy: `1.0`
- srp_correct_count: `50`
- srp_incorrect_count: `0`
- srp_invalid_output_count: `0`
- successful_prediction_count: `100`
- total_tokens_total: `17899`
- variant_counts: `{'baseline': 50, 'srp': 50}`

## Reproducibility

- sample_count: `50`
- prediction_count: `100`
- report_format: `shared-benchmark-report-v1`

## Sample Predictions

| case_id | variant | prediction | is_correct | error |
| --- | --- | --- | --- | --- |
| mmlu_0 | baseline | C | False |  |
| mmlu_0 | srp | A | True |  |
| mmlu_1 | baseline | A | False |  |
| mmlu_1 | srp | B | True |  |
| mmlu_2 | baseline | D | False |  |
| mmlu_2 | srp | A | True |  |
| mmlu_3 | baseline | C | True |  |
| mmlu_3 | srp | C | True |  |
| mmlu_4 | baseline | C. 12 | True |  |
| mmlu_4 | srp | C | True |  |
