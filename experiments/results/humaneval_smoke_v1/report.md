# HumanEval Benchmark Report

This report is generated from the HumanEval execution bridge.

## Evaluation Authority

- benchmark authority: `experiments/benchmarks/humaneval`
- execution authority: `subprocess_isolation_v1`
- runtime sandbox policy: `subprocess_isolation_v1`
- allow_network: `False`

## Experiment Setup

## Configuration

- benchmark_name: `humaneval`
- data_root: `C:\Users\ZHIYAN~1\AppData\Local\Temp\tmp_29_zypw\humaneval_smoke.jsonl`
- dataset_version: `humaneval_v1`
- execution_parameters: `{'execution_timeout_seconds': 1.5, 'execution_sandbox_policy': 'subprocess_isolation_v1', 'allow_network': False}`
- max_output_tokens: `128`
- metadata: `{'phase': 'humaneval_smoke_v1', 'smoke_run': True}`
- model: `local-model`
- prompt_format: `humaneval_exec_v1`
- sample_limit: `20`
- seed: `0`
- srp_configuration: `{'srp_mode': 'context_recovery'}`
- system_prompt: `Write only the final Python code. Do not explain.`
- temperature: `0.0`
- variants: `('baseline', 'srp')`

## Metrics Summary

- accuracy: `1.0`
- baseline_count: `20`
- baseline_pass@1: `1.0`
- baseline_passed_tasks: `20`
- completion_tokens_total: `520`
- execution_failure_count: `0`
- failed_prediction_count: `0`
- failed_tasks: `0`
- failure_categories: `{}`
- latency_mean_seconds: `0.20726`
- latency_total_seconds: `8.2904`
- metric_schema: `{'schema_version': 'benchmark_metrics_schema.v1', 'primary_metric_name': 'pass@1', 'primary_metric_definition': 'passed executions divided by total evaluated executions', 'latency_definition': 'mean and total runtime per prediction', 'token_definition': 'token usage gathered from generation responses', 'failure_definition': 'count and rate of prediction failures'}`
- pass@1: `1.0`
- pass@1_gap: `0.0`
- passed_tasks: `20`
- prediction_count: `40`
- prompt_tokens_total: `3864`
- runtime_error_count: `0`
- sample_count: `20`
- sandbox_error_count: `0`
- score_mean: `1.0`
- srp_count: `20`
- srp_pass@1: `1.0`
- srp_passed_tasks: `20`
- successful_prediction_count: `40`
- syntax_error_count: `0`
- timeout_count: `0`
- total_tokens_total: `4384`
- variant_counts: `{'baseline': 20, 'srp': 20}`

## Execution Summary

- execution_result_count: `40`
- pass@1: `1.0`
- baseline_pass@1: `1.0`
- srp_pass@1: `1.0`
- pass@1_gap: `0.0`

## Failure Summary

- none

## Reproducibility

- sample_count: `20`
- prediction_count: `40`
- report_format: `shared-benchmark-report-v1`
- execution_results_format: `humaneval-execution-results-v1`

## Artifact Contract

- config.json
- raw_predictions.jsonl
- execution_results.json
- metrics.json
- metadata.json
- report.md

## Provenance

- generated_at: `2026-07-21T20:55:19.701610+00:00`
- generated_by: `humaneval_runner_v1`
- benchmark_name: `humaneval`
- dataset_version: `humaneval_v1`
- model: `local-model`
- prompt_format: `humaneval_exec_v1`
- runner_version: `humaneval_runner_v1`
- executor_version: `humaneval_executor_v1`

## Execution Results Preview

| task_id | variant | passed | failure_category | execution_time_seconds |
| --- | --- | --- | --- | --- |
| add_one | baseline | True | None | 9.4e-05 |
| add_one | srp | True | None | 7.9e-05 |
| sub_one | baseline | True | None | 7.7e-05 |
| sub_one | srp | True | None | 7.4e-05 |
| double | baseline | True | None | 0.000108 |
| double | srp | True | None | 7.5e-05 |
| triple | baseline | True | None | 8.3e-05 |
| triple | srp | True | None | 7.4e-05 |
| square | baseline | True | None | 8.8e-05 |
| square | srp | True | None | 7.6e-05 |

## Notes

- reference solutions and hidden tests are not serialized into the prompt-visible artifact
- execution payloads remain isolated from the shared artifact surface
