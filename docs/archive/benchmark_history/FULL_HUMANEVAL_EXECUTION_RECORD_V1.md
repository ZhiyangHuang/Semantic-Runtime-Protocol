# Full HumanEval Execution Record V1

Date: 2026-07-21

## Authorization Basis

- HumanEval smoke closure: `READY_FOR_FULL_HUMANEVAL`
- full execution authorization: `AUTHORIZED`

## Repository Provenance

- commit hash: `be79305811f69c839c947e7018aa3559e7553d25`
- note: the full run uses the frozen HumanEval execution implementation and the shared benchmark artifact contract

## Execution Scope

- benchmark: `HumanEval`
- dataset source: `hf:openai/openai_humaneval|test`
- sample count: `164`
- variants: `baseline`, `srp`
- primary metric: `pass@1`
- sampling rule: first generation only
- execution model: isolated subprocess executor

## Model and Runtime

- model: `Qwen/Qwen3-4B-AWQ`
- prompt format: `humaneval_exec_v1`
- system prompt: `Write only the final Python code. Do not explain.`
- temperature: `0.0`
- max output tokens: `256`
- seed: `0`
- execution sandbox policy: `subprocess_isolation_v1`
- execution timeout seconds: `5.0`
- allow_network: `False`

## Output Artifacts

- output directory: `experiments/results/humaneval_full_v1/`
- expected artifact files:
  - `config.json`
  - `raw_predictions.jsonl`
  - `execution_results.json`
  - `metrics.json`
  - `metadata.json`
  - `report.md`

## Execution Command

Executed through the full HumanEval bridge runner with the frozen configuration:

```text
data_root = hf:openai/openai_humaneval|test
sample_limit = 164
model = Qwen/Qwen3-4B-AWQ
temperature = 0.0
max_output_tokens = 256
execution_timeout_seconds = 5.0
execution_sandbox_policy = subprocess_isolation_v1
output_dir = experiments/results/humaneval_full_v1/
```

## Expected Artifact Contract

- `config.json`
- `raw_predictions.jsonl`
- `execution_results.json`
- `metrics.json`
- `metadata.json`
- `report.md`

