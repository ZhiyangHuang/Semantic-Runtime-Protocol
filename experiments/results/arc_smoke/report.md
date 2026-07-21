# arc Benchmark Report

This report is generated from the shared benchmark execution layer.

## Experiment Setup

- benchmark_name: `arc`
- data_root: `hf:allenai/ai2_arc|ARC-Easy|test`
- dataset_version: `arc_v1`
- execution_parameters: `{'subsets': ('ARC-Easy',), 'subset_selection': 'ARC-Easy', 'smoke_run': True}`
- max_output_tokens: `8`
- metadata: `{'phase': 'arc_smoke'}`
- model: `Qwen/Qwen3-4B-AWQ`
- prompt_format: `arc_mcq_v1`
- sample_limit: `50`
- seed: `0`
- srp_configuration: `{'srp_mode': 'context_recovery', 'smoke_mode': True}`
- system_prompt: `Answer with the single best choice label only.`
- temperature: `0.0`
- variants: `('baseline', 'srp')`

## Summary

- accuracy: `0.94`
- completion_tokens_total: `215`
- failed_prediction_count: `0`
- latency_mean_seconds: `0.090341`
- latency_total_seconds: `9.0341`
- metric_schema: `{'schema_version': 'benchmark_metrics_schema.v1', 'primary_metric_name': 'accuracy', 'primary_metric_definition': 'correct predictions divided by total evaluated predictions', 'latency_definition': 'mean and total runtime per prediction', 'token_definition': 'token usage gathered from generation responses', 'failure_definition': 'count and rate of prediction failures'}`
- prediction_count: `100`
- prompt_tokens_total: `16356`
- score_mean: `0.94`
- successful_prediction_count: `100`
- total_tokens_total: `16571`
- variant_counts: `{'baseline': 50, 'srp': 50}`

## Benchmark Metrics

- accuracy: `0.92`
- accuracy_gap: `0.04`
- baseline_accuracy: `0.92`
- benchmark_name: `arc`
- completion_tokens_total: `215`
- correct_count: `46`
- failed_prediction_count: `0`
- incorrect_count: `4`
- invalid_prediction_count: `0`
- latency_mean_seconds: `0.090341`
- latency_total_seconds: `9.0341`
- metric_schema: `{'schema_version': 'benchmark_metrics_schema.v1', 'primary_metric_name': 'accuracy', 'primary_metric_definition': 'correct predictions divided by total evaluated predictions', 'latency_definition': 'mean and total runtime per prediction', 'token_definition': 'token usage gathered from generation responses', 'failure_definition': 'count and rate of prediction failures'}`
- official_metric_name: `accuracy`
- prediction_count: `100`
- prompt_tokens_total: `16356`
- sample_count: `50`
- score_mean: `0.94`
- srp_accuracy: `0.96`
- srp_correct_count: `48`
- srp_incorrect_count: `2`
- srp_invalid_prediction_count: `0`
- successful_prediction_count: `100`
- total_tokens_total: `16571`
- variant_counts: `{'baseline': 50, 'srp': 50}`

## Reproducibility

- sample_count: `50`
- prediction_count: `100`
- report_format: `shared-benchmark-report-v1`

## Sample Predictions

| case_id | variant | prediction | is_correct | error |
| --- | --- | --- | --- | --- |
| Mercury_417466 | baseline | A | True |  |
| Mercury_417466 | srp | A | True |  |
| Mercury_7081673 | baseline | B | True |  |
| Mercury_7081673 | srp | B | True |  |
| Mercury_7239733 | baseline | D | True |  |
| Mercury_7239733 | srp | D | True |  |
| NYSEDREGENTS_2015_4_8 | baseline | D | True |  |
| NYSEDREGENTS_2015_4_8 | srp | D | True |  |
| Mercury_7037258 | baseline | C | False |  |
| Mercury_7037258 | srp | B | True |  |
