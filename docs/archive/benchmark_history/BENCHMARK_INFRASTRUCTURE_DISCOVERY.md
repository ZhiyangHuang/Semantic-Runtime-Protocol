# Benchmark Infrastructure Discovery

## Existing Evaluation Framework

Location:
- `experiments/validation/boundary_reporting/`
- `experiments/external_validation/`
- `experiments/real_world_validation/common/`
- `experiments/common/local_llm.py`
- `scripts/run_reproduction.py`

Purpose:
- `experiments/validation/boundary_reporting/` provides a generic case-adaptation, evaluation, replay-consistency, and artifact-writing pipeline.
- `experiments/external_validation/` provides a reusable benchmark adapter, memory-system baseline runner, metric aggregation, and report rendering path.
- `experiments/real_world_validation/common/` provides reusable dataset manifests, run config objects, claim mapping, decision logic, failure tracking, and bundle writing.
- `experiments/common/local_llm.py` provides a local OpenAI-compatible generation client with usage and latency reporting.
- `scripts/run_reproduction.py` provides a reusable orchestration pattern for stepwise experiment execution.

Reusable:
- Yes, but only at the infrastructure layer.
- The repo has a generic evaluation/reporting skeleton, not benchmark-specific MMLU, ARC, or HumanEval implementations.

## Model Execution Entry Point

File:
- `experiments/common/local_llm.py`

Function:
- `LocalOpenAICompatibleClient.generate_with_usage(...)`
- `build_local_client()`

Input:
- Prompt text
- Optional system prompt
- Max output tokens
- Temperature

Output:
- Generated text
- Raw text
- Usage payload
- Model identifier
- Latency in seconds

Notes:
- This is the clearest reusable generation entry point for new benchmark runners.
- It targets a local OpenAI-compatible `/v1/chat/completions` endpoint.

## SRP Integration Point

Where SRP modifies:
- `context`
- `memory`
- `prompt`
- `retrieval`
- `generation`

Observed integration patterns:
- `experiments/external_validation/runner.py` injects benchmark cases into a reusable memory system before retrieval.
- `experiments/real_world_validation/longmemeval/runner.py` bridges benchmark cases into SRP transition records and governance metrics.
- `experiments/validation/boundary_reporting/runner.py` adapts case bundles into governed decisions and replay checks.

Interpretation:
- SRP already has clear insertion points for benchmark-specific adapters.
- What is missing is a benchmark-facing execution layer that turns MMLU/ARC/HumanEval tasks into the repo's reusable case / record formats.

## Experiment Template

Existing example:
- Directory: `experiments/results/external_validation_longmemeval_reality_check_smoke_v2/`
- Command: the LongMemEval real-world validation and report-writing path under `experiments/real_world_validation/longmemeval/runner.py`

Additional reusable examples:
- `experiments/validation/boundary_reporting/runner.py`
- `experiments/external_validation/runner.py`
- `scripts/run_reproduction.py`

Common artifact pattern:
- `config.json`
- raw outputs or records
- `metrics.json` or summary JSON
- `report.md`
- `metadata.json`
- manifest / hash files

## Benchmark Adapter Feasibility

| Benchmark | Requires New Runner | Can Reuse Existing Components | Estimated Work |
|---|---|---|---|
| MMLU | Yes, benchmark-specific dataset loader and scorer adapter | Yes: local LLM client, report writer patterns, config/manifest patterns | Medium |
| ARC | Yes, benchmark-specific dataset loader and scorer adapter | Yes: local LLM client, report writer patterns, config/manifest patterns | Medium |
| HumanEval | Yes, benchmark-specific execution sandbox and pass@1 evaluator | Partially: local LLM client and artifact/report patterns; no sandbox found | High |

## External Dependency Check

Observed repository state:
- No `pyproject.toml` was found in the repository tree.
- No `requirements.txt`, `environment.yml`, `environment.yaml`, `poetry.lock`, or `uv.lock` was found in the repository tree.

Implication:
- The repository does not declare a benchmark dependency stack in a standard lockfile or package manifest.
- There is no visible evidence of bundled support for HuggingFace `datasets`, `lm-eval-harness`, or a HumanEval sandbox runtime.

## Recommendation

Choose one:
- B. Need minimal benchmark framework extension

Reason:
- The repo already contains reusable evaluation, reporting, and artifact-writing machinery.
- MMLU and ARC can likely be added by adaptering the existing generation/report flow.
- HumanEval still needs a new execution sandbox layer and pass@1 evaluator, so it is not a pure adapter-only change.

## Discovery Notes

- `experiments/validation/boundary_reporting/runner.py` already shows a stable pattern for replayable evaluation bundles.
- `experiments/external_validation/runner.py` already shows a stable pattern for benchmark adapters and report generation.
- `experiments/real_world_validation/longmemeval/runner.py` is the closest existing example of benchmark-to-SRP integration.
- The repository currently has a real LongMemEval evidence artifact, but no standalone MMLU, ARC, or HumanEval experiment directory.
