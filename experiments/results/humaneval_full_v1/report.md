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
- data_root: `hf:openai/openai_humaneval|test`
- dataset_version: `humaneval_v1`
- execution_parameters: `{'execution_timeout_seconds': 5.0, 'execution_sandbox_policy': 'subprocess_isolation_v1', 'allow_network': False}`
- max_output_tokens: `256`
- metadata: `{'phase': 'humaneval_full_v1', 'full_run': True}`
- model: `Qwen/Qwen3-4B-AWQ`
- prompt_format: `humaneval_exec_v1`
- sample_limit: `164`
- seed: `0`
- srp_configuration: `{'srp_mode': 'context_recovery'}`
- system_prompt: `Write only the final Python code. Do not explain.`
- temperature: `0.0`
- variants: `('baseline', 'srp')`

## Metrics Summary

- accuracy: `0.9939024390243902`
- baseline_count: `164`
- baseline_pass@1: `0.987805`
- baseline_passed_tasks: `162`
- completion_tokens_total: `21579`
- execution_failure_count: `2`
- failed_prediction_count: `2`
- failed_tasks: `2`
- failure_categories: `{'syntax_error': 2}`
- latency_mean_seconds: `0.950734756097561`
- latency_total_seconds: `311.841`
- metric_schema: `{'schema_version': 'benchmark_metrics_schema.v1', 'primary_metric_name': 'pass@1', 'primary_metric_definition': 'passed executions divided by total evaluated executions', 'latency_definition': 'mean and total runtime per prediction', 'token_definition': 'token usage gathered from generation responses', 'failure_definition': 'count and rate of prediction failures'}`
- pass@1: `0.987805`
- pass@1_gap: `0.012195`
- passed_tasks: `162`
- prediction_count: `328`
- prompt_tokens_total: `72361`
- runtime_error_count: `0`
- sample_count: `164`
- sandbox_error_count: `0`
- score_mean: `0.9939024390243902`
- srp_count: `164`
- srp_pass@1: `1.0`
- srp_passed_tasks: `164`
- successful_prediction_count: `326`
- syntax_error_count: `2`
- timeout_count: `0`
- total_tokens_total: `93940`
- variant_counts: `{'baseline': 164, 'srp': 164}`

## Execution Summary

- execution_result_count: `328`
- pass@1: `0.987805`
- baseline_pass@1: `0.987805`
- srp_pass@1: `1.0`
- pass@1_gap: `0.012195`

## Failure Summary

- syntax_error: `2`

## Reproducibility

- sample_count: `164`
- prediction_count: `328`
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

- generated_at: `2026-07-21T21:10:55.543178+00:00`
- generated_by: `humaneval_runner_v1`
- benchmark_name: `humaneval`
- dataset_version: `humaneval_v1`
- model: `Qwen/Qwen3-4B-AWQ`
- prompt_format: `humaneval_exec_v1`
- runner_version: `humaneval_runner_v1`
- executor_version: `humaneval_executor_v1`

## Execution Results Preview

| task_id | variant | passed | failure_category | execution_time_seconds |
| --- | --- | --- | --- | --- |
| HumanEval/0 | baseline | True | None | 0.000245 |
| HumanEval/0 | srp | True | None | 0.000256 |
| HumanEval/1 | baseline | True | None | 0.000225 |
| HumanEval/1 | srp | True | None | 0.000253 |
| HumanEval/2 | baseline | True | None | 0.000129 |
| HumanEval/2 | srp | True | None | 0.000128 |
| HumanEval/3 | baseline | True | None | 0.000195 |
| HumanEval/3 | srp | True | None | 0.000192 |
| HumanEval/4 | baseline | True | None | 0.000192 |
| HumanEval/4 | srp | True | None | 0.001959 |

## Notes

- reference solutions and hidden tests are not serialized into the prompt-visible artifact
- execution payloads remain isolated from the shared artifact surface
