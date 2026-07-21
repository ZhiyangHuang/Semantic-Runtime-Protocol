# arc Benchmark Report

This report is generated from the shared benchmark execution layer.

## Experiment Setup

- benchmark_name: `arc`
- data_root: `hf:allenai/ai2_arc|ARC-Easy|test`
- dataset_version: `arc_v1`
- execution_parameters: `{'subsets': ('ARC-Easy',), 'subset_selection': 'ARC-Easy', 'full_run': True}`
- max_output_tokens: `8`
- metadata: `{'phase': 'arc_full_v1', 'full_run': True}`
- model: `Qwen/Qwen3-4B-AWQ`
- prompt_format: `arc_mcq_v1`
- sample_limit: `0`
- seed: `0`
- srp_configuration: `{'srp_mode': 'context_recovery', 'full_run': True}`
- system_prompt: `Answer with the single best choice label only.`
- temperature: `0.0`
- variants: `('baseline', 'srp')`

## Summary

- accuracy: `0.8941498316498316`
- completion_tokens_total: `10611`
- failed_prediction_count: `0`
- latency_mean_seconds: `0.08561702441077441`
- latency_total_seconds: `406.8521`
- metric_schema: `{'schema_version': 'benchmark_metrics_schema.v1', 'primary_metric_name': 'accuracy', 'primary_metric_definition': 'correct predictions divided by total evaluated predictions', 'latency_definition': 'mean and total runtime per prediction', 'token_definition': 'token usage gathered from generation responses', 'failure_definition': 'count and rate of prediction failures'}`
- prediction_count: `4752`
- prompt_tokens_total: `758195`
- score_mean: `0.8941498316498316`
- successful_prediction_count: `4752`
- total_tokens_total: `768806`
- variant_counts: `{'baseline': 2376, 'srp': 2376}`

## Benchmark Metrics

- accuracy: `0.904461`
- accuracy_gap: `-0.020623`
- baseline_accuracy: `0.904461`
- benchmark_name: `arc`
- completion_tokens_total: `10611`
- correct_count: `2149`
- failed_prediction_count: `0`
- incorrect_count: `227`
- invalid_prediction_count: `0`
- latency_mean_seconds: `0.08561702441077441`
- latency_total_seconds: `406.8521`
- metric_schema: `{'schema_version': 'benchmark_metrics_schema.v1', 'primary_metric_name': 'accuracy', 'primary_metric_definition': 'correct predictions divided by total evaluated predictions', 'latency_definition': 'mean and total runtime per prediction', 'token_definition': 'token usage gathered from generation responses', 'failure_definition': 'count and rate of prediction failures'}`
- official_metric_name: `accuracy`
- prediction_count: `4752`
- prompt_tokens_total: `758195`
- sample_count: `2376`
- score_mean: `0.8941498316498316`
- srp_accuracy: `0.883838`
- srp_correct_count: `2100`
- srp_incorrect_count: `276`
- srp_invalid_prediction_count: `0`
- successful_prediction_count: `4752`
- total_tokens_total: `768806`
- variant_counts: `{'baseline': 2376, 'srp': 2376}`

## Reproducibility

- sample_count: `2376`
- prediction_count: `4752`
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
| Mercury_7037258 | srp | A | False |  |
